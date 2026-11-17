"""
app/modules/corrections/response_normalizer.py

Normalise la sortie brute (hétérogène selon provider/level) des prompts de
correction Schreiben vers UN SEUL contrat, consommé tel quel par le frontend :

{
  "overall_score": int,
  "max_score": int,
  "passed": bool,
  "score_percentage": float,
  "appreciation": str,
  "criteria": [{"key": str, "label": str, "score": float, "max_score": float, "feedback": str}],
  "tasks": [{
      "key": str, "label": str,
      "corrected_text": str,          # texte du candidat, fautes corrigées uniquement
      "model_text": str,              # Mustertext (version améliorée attendue)
      "main_strengths": list[str], "main_weaknesses": list[str],
      # optionnels, présents seulement si le barème le prévoit (ÖSD B2, ECL, TestDaF) :
      "score": float | None, "max_score": float | None, "sub_criteria": list[dict] | None,
  }],
  "corrections_list": list[dict],
  "suggestions": list[str],
}

Garanties appliquées ici, indépendamment de ce que renvoie l'IA :
- corrections_list ne contient que de vraies corrections de langue
  (_clean_corrections : pas de commentaires de contenu, pas de passages entiers)
- hors sujet (thema_verfehlt = true) : règle propre à chaque examen
  (telc : plafonds Leitpunkte/total ; Goethe : plafond Erfüllung ;
   ECL / ÖSD B2 / TestDaF : tâche à 0)
- longueur, calculée sur les vrais textes du candidat (task_texts) :
  telc (pénalité sous 80 / 100 mots), ECL (plafonds sous 70 % / 50 %)
- telc et Goethe : total recalculé depuis les critères, réussite à 60 %
- rebuild_corrected_text() : corrected_text reconstruit depuis le texte original
  + corrections, appelé par les services qui ont le texte original

Les clés de tâche (main_strengths / main_weaknesses / model_text) suivent
exactement schemas.TaskFeedback : une clé différente est ignorée par Pydantic
et n'atteint jamais le frontend.

Formes gérées : nested (Goethe B2, Goethe/ÖSD B1), flat (telc B1/B2),
osd_b2 (ÖSD B2), ecl (ECL B1/B2, esquisse), testdaf (TestDaF, esquisse).

Pour ajouter un nouvel examen/niveau : ajouter une entrée à CRITERIA_CONFIG
(et, si son schéma JSON de sortie est vraiment différent des formes gérées
ici, une nouvelle fonction _normalize_xxx). Le store Pinia et les pages Vue
n'ont plus jamais besoin d'être touchés pour ça.
"""
from __future__ import annotations

from difflib import SequenceMatcher

TASK_LABELS = {"task1": "Teil 1", "task2": "Teil 2", "task3": "Teil 3"}

# Au-delà, "error" est un passage entier : c'est une remarque de contenu, pas une faute
MAX_ERROR_WORDS = 25

# Une vraie correction ressemble à l'erreur (quelques lettres ou mots changés).
# Phrase de 5 mots ou plus remplacée par un texte très différent = commentaire de contenu.
MIN_SIMILARITY_LONG_ERROR = 0.5
CONTENT_COMMENT_MARKERS = (
    "nicht relevant", "irrelevant", "inhaltlich", "thema verfehlt",
    "gehört nicht zum thema", "nicht zum thema", "themenfremd",
)

# Règles appliquées par le backend (l'IA ne les respecte pas de façon fiable) :
# - "off_topic" : si une tâche a thema_verfehlt = true
#     "cap"         : plafond du critère
#     "shares"      : part de chaque tâche dans le critère ; une tâche hors sujet
#                     garde au plus 1/3 de sa part (Goethe/ÖSD B1)
#     "overall_cap" : plafond du total
# - "length" : texte de la tâche 1 sous min_words -> pénalité sur le critère (telc)
CRITERIA_CONFIG: dict[tuple[str, str], dict] = {
    ("goethe", "b2"): {
        "shape": "nested",
        "criteria": [
            ("erfullung", "Erfüllung", 25),
            ("koharenz", "Kohärenz", 25),
            ("wortschatz", "Wortschatz", 25),
            ("korrektheit", "Korrektheit", 25),
        ],
        "task_keys": ["task1", "task2"],
        "off_topic": {"criterion": "erfullung", "cap": 6},
    },
    ("goethe", "b1"): {
        "shape": "nested",
        "criteria": [
            ("erfullung", "Erfüllung", 25),
            ("koharenz", "Kohärenz", 25),
            ("wortschatz", "Wortschatz", 25),
            ("strukturen", "Strukturen", 25),
        ],
        "task_keys": ["task1", "task2", "task3"],
        "off_topic": {"criterion": "erfullung", "shares": {"task1": 10, "task2": 10, "task3": 5}},
    },
    ("osd", "b1"): {
        # Même prompt/schéma que goethe b1 (get_goethe_osd_b1_prompt sert les deux)
        "shape": "nested",
        "criteria": [
            ("erfullung", "Erfüllung", 25),
            ("koharenz", "Kohärenz", 25),
            ("wortschatz", "Wortschatz", 25),
            ("strukturen", "Strukturen", 25),
        ],
        "task_keys": ["task1", "task2", "task3"],
        "off_topic": {"criterion": "erfullung", "shares": {"task1": 10, "task2": 10, "task3": 5}},
    },
    ("telc", "b1"): {
        "shape": "flat",
        "criteria": [
            ("leitpunkte", "Leitpunkte", 15),
            ("gestaltung", "Gestaltung", 15),
            ("richtigkeit", "Richtigkeit", 15),
        ],
        "task_keys": ["task1"],
        "off_topic": {"criterion": "leitpunkte", "cap": 4, "overall_cap": 20},
        "length": {"criterion": "leitpunkte", "min_words": 80, "penalty": 3},
    },
    ("telc", "b2"): {
        "shape": "flat",
        "criteria": [
            ("aufgabenbewaeltigung", "Aufgabenbewältigung", 15),
            ("gestaltung", "Gestaltung", 15),
            ("richtigkeit", "Richtigkeit", 15),
        ],
        "task_keys": ["task1"],
        "off_topic": {"criterion": "aufgabenbewaeltigung", "cap": 4, "overall_cap": 20},
        "length": {"criterion": "aufgabenbewaeltigung", "min_words": 100, "penalty": 4},
    },
    ("osd", "b2"): {
        "shape": "osd_b2",
        "task_keys": ["task1", "task2"],
    },
    # ── Esquisses à valider ──
    ("ecl", "b1"): {"shape": "ecl", "task_keys": ["task1", "task2"]},
    ("ecl", "b2"): {"shape": "ecl", "task_keys": ["task1", "task2"]},
    ("testdaf", "b2"): {"shape": "testdaf", "task_keys": ["task1", "task2"]},
    ("testdaf", "c1"): {"shape": "testdaf", "task_keys": ["task1", "task2"]},
}


def normalize_correction_result(
    provider: str,
    level: str,
    ai_result: dict,
    task_texts: list[str] | None = None,
) -> dict:
    """task_texts (optionnel, même ordre que les tâches) : textes du candidat,
    utilisés pour les règles de longueur appliquées par le backend (telc, ECL)."""
    key = (provider.lower().strip().replace("ö", "o"), level.lower().strip())
    config = CRITERIA_CONFIG.get(key)
    if config is None:
        raise ValueError(
            f"Barème inconnu pour {provider} {level} : ajoute une entrée à CRITERIA_CONFIG."
        )

    shape = config["shape"]
    if shape == "nested":
        return _normalize_nested(ai_result, config)
    if shape == "flat":
        return _normalize_flat(ai_result, config, task_texts)
    if shape == "osd_b2":
        return _normalize_osd_b2(ai_result, config)
    if shape == "ecl":
        return _normalize_ecl(ai_result, config, key[1], task_texts)
    if shape == "testdaf":
        return _normalize_testdaf(ai_result, config)
    raise ValueError(f"Shape inconnu: {shape}")


# ─────────────────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────────────────

def _clamp(value, maximum: float) -> float:
    """Borne une note entre 0 et maximum (valeur invalide -> 0)."""
    try:
        return max(0, min(float(value), maximum))
    except (TypeError, ValueError):
        return 0


def _word_count(text: str) -> int:
    return len((text or "").split())


def _task_base(key: str, label: str, t: dict) -> dict:
    """Champs communs d'une tâche, alignés sur schemas.TaskFeedback."""
    return {
        "key": key,
        "label": label,
        "corrected_text": t.get("corrected_text", "") or "",
        "model_text": t.get("model_text", "") or "",
        "main_strengths": t.get("main_strengths", []) or [],
        "main_weaknesses": t.get("main_weaknesses", []) or [],
    }


def _off_topic(t: dict) -> bool:
    """Tâche déclarée hors sujet par l'IA (champ booléen thema_verfehlt)."""
    return t.get("thema_verfehlt") is True


def _clean_corrections(items) -> list[dict]:
    """
    Ne garde que les vraies corrections de langue :
    - error et correction non vides et différents
    - pas de commentaire de contenu (crochets, parenthèses, "nicht relevant", "inhaltlich"...)
    - pas de passage entier (plus de MAX_ERROR_WORDS mots)
    - pas de phrase remplacée par un texte sans rapport (similarité trop faible)
    """
    cleaned: list[dict] = []
    for c in items or []:
        if not isinstance(c, dict):
            continue
        err = str(c.get("error", "") or "").strip()
        cor = str(c.get("correction", "") or "").strip()
        expl = str(c.get("explanation", "") or "").strip()
        if not err or not cor or err == cor:
            continue
        if cor.startswith(("[", "(")) or err.startswith(("[", "(")):
            continue
        if len(err.split()) > MAX_ERROR_WORDS:
            continue
        # Ajout d'un complément entre parenthèses ou crochets (ex. "(Straße, PLZ Ort)") :
        # remarque de forme ou de contenu, pas une correction de langue
        if cor.startswith(err) and cor[len(err):].strip().startswith(("(", "[")):
            continue
        if cor.endswith(err) and cor[: len(cor) - len(err)].strip().endswith((")", "]")):
            continue
        lowered = f"{cor} {expl}".lower()
        if any(marker in lowered for marker in CONTENT_COMMENT_MARKERS):
            continue
        if len(err.split()) >= 5 and SequenceMatcher(None, err, cor).ratio() < MIN_SIMILARITY_LONG_ERROR:
            continue
        cleaned.append(c)
    return cleaned


def rebuild_corrected_text(
    original: str,
    corrections: list[dict],
    task_number: int,
) -> tuple[str, list[dict]]:
    """
    corrected_text déterministe : texte original du candidat + corrections de
    cette tâche, chacune appliquée une fois. Aucun ajout ni suppression possible.

    Retourne (texte_corrigé, corrections_appliquées). Seules les corrections
    réellement appliquées sont renvoyées : l'appelant remplace la liste par
    celles-ci, donc liste et texte correspondent toujours exactement.
    Ignorées : "error" introuvable mot pour mot dans l'original, ou correction
    qui ne fait qu'ajouter ce qui est déjà là (ex. un point final déjà présent).
    Retourne ("", []) si l'original est vide (l'appelant garde alors le texte de l'IA).
    """
    if not original:
        return "", []
    text = original
    applied: list[dict] = []
    for c in corrections or []:
        if str(c.get("task", "1") or "1") != str(task_number):
            continue
        err = str(c.get("error", "") or "")
        cor = str(c.get("correction", "") or "")
        idx = text.find(err) if err else -1
        if idx < 0:
            continue
        before, after = text[:idx], text[idx + len(err):]
        # Ajout d'un texte déjà présent juste après (ex. "am Meer" -> "am Meer." devant ".")
        if cor.startswith(err) and after.startswith(cor[len(err):]):
            continue
        # Ajout d'un texte déjà présent juste avant
        if cor.endswith(err) and before.endswith(cor[: len(cor) - len(err)]):
            continue
        text = before + cor + after
        applied.append(c)
    return text, applied


# ─────────────────────────────────────────────────────────
# Goethe / ÖSD B1 / telc / ÖSD B2
# ─────────────────────────────────────────────────────────

def _normalize_nested(ai_result: dict, config: dict) -> dict:
    """
    Goethe B2 / Goethe-ÖSD B1 : global_assessment + criteria_scores + task_feedbacks.
    Hors sujet (task_feedbacks.taskN.thema_verfehlt) : plafond sur Erfüllung
    (Goethe B2 : 6/25 ; B1 : la tâche garde au plus 1/3 de sa part).
    Total recalculé = somme des critères, réussite à 60 %.
    """
    ga = ai_result.get("global_assessment", {})
    raw_scores = ai_result.get("criteria_scores", {})
    task_feedbacks = ai_result.get("task_feedbacks", {})

    max_by_key = {p: m for p, _, m in config["criteria"]}
    scores = {p: _clamp(raw_scores.get(f"{p}_score", 0), m) for p, _, m in config["criteria"]}

    off_tasks = [k for k in config["task_keys"] if _off_topic(task_feedbacks.get(k, {}) or {})]
    rule = config.get("off_topic")
    if off_tasks and rule:
        crit = rule["criterion"]
        if "cap" in rule:
            scores[crit] = min(scores[crit], rule["cap"])
        elif "shares" in rule:
            reduction = sum(rule["shares"].get(k, 0) * 2 / 3 for k in off_tasks)
            scores[crit] = min(scores[crit], max(0, max_by_key[crit] - reduction))
        scores[crit] = round(scores[crit], 1)

    max_score = sum(max_by_key.values())
    overall = round(sum(scores.values()))

    criteria = [
        {
            "key": prefix,
            "label": label,
            "score": scores[prefix],
            "max_score": max_pts,
            "feedback": raw_scores.get(f"{prefix}_feedback", ""),
        }
        for prefix, label, max_pts in config["criteria"]
    ]

    tasks = [
        _task_base(tkey, TASK_LABELS.get(tkey, tkey), task_feedbacks.get(tkey, {}))
        for tkey in config["task_keys"]
    ]

    return {
        "overall_score": overall,
        "max_score": max_score,
        "passed": overall >= max_score * 0.6,
        "score_percentage": round(overall / max_score * 100, 1) if max_score else 0,
        "appreciation": ga.get("appreciation", ""),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": _clean_corrections(ai_result.get("corrections")),
        "suggestions": ai_result.get("suggestions", []),
    }


def _normalize_flat(ai_result: dict, config: dict, task_texts: list[str] | None = None) -> dict:
    """
    telc B1 / telc B2 : tout au niveau racine, une seule tâche.
    Hors sujet (thema_verfehlt à la racine) : critère de contenu plafonné à 4/15
    et total plafonné à 20/45. Texte trop court (sous 80 / 100 mots) : pénalité
    sur le critère de contenu. Total recalculé = somme des critères, réussite à 60 %.
    """
    scores = {p: _clamp(ai_result.get(f"{p}_score", 0), m) for p, _, m in config["criteria"]}

    off = _off_topic(ai_result)
    rule = config.get("off_topic")
    if off and rule:
        crit = rule["criterion"]
        scores[crit] = min(scores[crit], rule["cap"])

    length = config.get("length")
    text = task_texts[0] if task_texts else ""
    if length and text.strip() and _word_count(text) < length["min_words"]:
        crit = length["criterion"]
        scores[crit] = max(0, scores[crit] - length["penalty"])

    max_score = sum(m for _, _, m in config["criteria"])
    overall = round(sum(scores.values()))
    if off and rule and rule.get("overall_cap") is not None:
        overall = min(overall, rule["overall_cap"])

    criteria = [
        {
            "key": prefix,
            "label": label,
            "score": scores[prefix],
            "max_score": max_pts,
            "feedback": ai_result.get(f"{prefix}_feedback", ""),
        }
        for prefix, label, max_pts in config["criteria"]
    ]

    # Le prompt telc ne renvoie pas de strengths/weaknesses : listes vides via _task_base
    tasks = [_task_base("task1", TASK_LABELS["task1"], ai_result)]

    return {
        "overall_score": overall,
        "max_score": max_score,
        "passed": overall >= max_score * 0.6,
        "score_percentage": round(overall / max_score * 100, 1) if max_score else 0,
        "appreciation": ai_result.get("appreciation", ""),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": _clean_corrections(ai_result.get("corrections")),
        "suggestions": ai_result.get("suggestions", []),
    }


def _normalize_osd_b2(ai_result: dict, config: dict) -> dict:
    """
    ÖSD B2 : deux tâches indépendantes, chacune notée A/K/T/L + malus F.
    On agrège les composantes des deux tâches pour reconstituer une liste de
    "critères" globale cohérente avec les autres examens (panneau "Critères"
    de l'UI), tout en gardant le détail A/K/T/L/F par tâche dans `tasks`.

    Tâche hors sujet (thema_verfehlt) : tous ses critères à 0 (règle ÖSD).
    overall_score = somme des deux task_score (bornés à 15), recalculée ici.

    `passed` est calculé sur 60 % de 30 comme repère interne à la plateforme,
    ce n'est PAS le seuil de certification ÖSD officiel (qui dépend du total
    combiné Lesen+Hören+Schreiben). `floor_reached` expose le plancher officiel (>= 10/30).
    """
    ga = ai_result.get("global_assessment", {})

    def apply_off_topic(t: dict) -> dict:
        if _off_topic(t):
            return {**t, "a_score": 0, "k_score": 0, "t_score": 0, "l_score": 0,
                    "f_malus": 0, "task_score": 0}
        return t

    t1 = apply_off_topic(ai_result.get("task1", {}) or {})
    t2 = apply_off_topic(ai_result.get("task2", {}) or {})

    overall = _clamp(t1.get("task_score", 0), 15) + _clamp(t2.get("task_score", 0), 15)
    max_score = 30  # 15 + 15

    def agg(field: str) -> float:
        return t1.get(field, 0) + t2.get(field, 0)

    a_total = agg("a_score")
    k_total = agg("k_score")
    t_total = agg("t_score")
    l_total = agg("l_score")
    f_malus_total = agg("f_malus")  # 0 ou négatif

    criteria = [
        {"key": "aufgabe", "label": "Aufgabe", "score": a_total, "max_score": 10, "feedback": ""},
        {"key": "gestaltung", "label": "Kommunikative Gestaltung", "score": k_total, "max_score": 4, "feedback": ""},
        {"key": "koharenz", "label": "Textkohärenz", "score": t_total, "max_score": 6, "feedback": ""},
        {"key": "lexik", "label": "Lexik/Ausdruck", "score": l_total, "max_score": 10, "feedback": ""},
        # Formale Richtigkeit est un malus (0 à -6 au total), présenté en score positif inversé pour l'UI
        {
            "key": "richtigkeit",
            "label": "Formale Richtigkeit",
            "score": max(0, 6 + f_malus_total),
            "max_score": 6,
            "feedback": "",
        },
    ]

    tasks = [
        {
            **_task_base(tkey, TASK_LABELS.get(tkey, tkey), t),
            "score": _clamp(t.get("task_score", 0), 15),
            "max_score": 15,
            "sub_criteria": [
                {"key": "a", "label": "Aufgabe", "score": t.get("a_score", 0), "max_score": 5},
                {"key": "k", "label": "Gestaltung", "score": t.get("k_score", 0), "max_score": 2},
                {"key": "t", "label": "Kohärenz", "score": t.get("t_score", 0), "max_score": 3},
                {"key": "l", "label": "Lexik", "score": t.get("l_score", 0), "max_score": 5},
                {"key": "f", "label": "Richtigkeit (Malus)", "score": t.get("f_malus", 0), "max_score": 0},
            ],
        }
        for tkey, t in [("task1", t1), ("task2", t2)]
    ]

    return {
        "overall_score": overall,
        "max_score": max_score,
        "passed": overall >= max_score * 0.6,
        "floor_reached": overall >= 10,
        "score_percentage": round(overall / max_score * 100, 1) if max_score else 0,
        "appreciation": ga.get("appreciation", ""),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": _clean_corrections(ai_result.get("corrections")),
        "suggestions": ai_result.get("suggestions", []),
    }


# ─────────────────────────────────────────────────────────
# ECL B1 / B2 (esquisse à valider)
# ─────────────────────────────────────────────────────────

ECL_CRITERIA = [
    ("formale_korrektheit", "Formale Korrektheit"),
    ("schriftliche_korrektheit", "Schriftliche Korrektheit"),
    ("wortschatz", "Wortschatz"),
    ("stil", "Stil"),
    ("kommunikative_wirksamkeit", "Kommunikative Wirksamkeit"),
]

# Longueur du texte, vérifiée par le backend (l'IA n'applique pas ces plafonds de façon fiable)
ECL_WORD_TARGET = {"b1": 100, "b2": 150}
ECL_SHORT_RATIO = 0.7        # moins de 70 % des mots : Kommunikative Wirksamkeit max 2
ECL_VERY_SHORT_RATIO = 0.5   # moins de 50 % : les 5 critères max 2 (règle plateforme, 0 = désactivé)
ECL_SHORT_CAP = 2


def _normalize_ecl(
    ai_result: dict,
    config: dict,
    level: str = "b1",
    task_texts: list[str] | None = None,
) -> dict:
    """ECL B1/B2 : 5 critères 0-5 par texte (25/texte), note = moyenne des 2 textes (max 25).
    HYPOTHÈSE à valider : moyenne des deux textes. Les scores sont recalculés ici,
    sans faire confiance aux totaux renvoyés par l'IA.
    Texte hors sujet (thema_verfehlt) : Kommunikative Wirksamkeit forcée à 0,
    donc texte entier à 0 (règle officielle ECL).
    Texte trop court : plafonds ECL_SHORT_RATIO / ECL_VERY_SHORT_RATIO."""
    ga = ai_result.get("global_assessment", {})

    target = ECL_WORD_TARGET.get(level, 100)
    raw: dict[str, dict] = {}
    for i, k in enumerate(config["task_keys"]):
        t = ai_result.get(k, {}) or {}
        if _off_topic(t):
            t = {**t, "kommunikative_wirksamkeit": 0}

        # Plafonds de longueur, calculés sur le vrai nombre de mots du candidat
        text = task_texts[i] if task_texts and i < len(task_texts) else ""
        if text.strip():
            ratio = _word_count(text) / target
            if ratio < ECL_VERY_SHORT_RATIO:
                t = {**t, **{c: min(_clamp(t.get(c, 0), 5), ECL_SHORT_CAP) for c, _ in ECL_CRITERIA}}
            elif ratio < ECL_SHORT_RATIO:
                t = {**t, "kommunikative_wirksamkeit": min(
                    _clamp(t.get("kommunikative_wirksamkeit", 0), 5), ECL_SHORT_CAP
                )}

        raw[k] = t

    def task_score(t: dict) -> float:
        # Kommunikative Wirksamkeit = 0 -> le texte entier vaut 0 (règle officielle)
        if _clamp(t.get("kommunikative_wirksamkeit", 0), 5) == 0:
            return 0
        return sum(_clamp(t.get(k, 0), 5) for k, _ in ECL_CRITERIA)

    scores = {k: task_score(t) for k, t in raw.items()}
    overall = round(sum(scores.values()) / max(len(scores), 1))
    max_score = 25

    criteria = [
        {
            "key": key,
            "label": label,
            "score": round(sum(_clamp(t.get(key, 0), 5) for t in raw.values()) / max(len(raw), 1), 1),
            "max_score": 5,
            "feedback": "",
        }
        for key, label in ECL_CRITERIA
    ]

    tasks = [
        {
            **_task_base(tkey, f"Text {i + 1}", t),
            "score": scores[tkey],
            "max_score": 25,
            "sub_criteria": [
                {"key": key, "label": label, "score": _clamp(t.get(key, 0), 5), "max_score": 5}
                for key, label in ECL_CRITERIA
            ],
        }
        for i, (tkey, t) in enumerate(raw.items())
    ]

    return {
        "overall_score": overall,
        "max_score": max_score,
        "passed": overall >= 15,  # 60 % par module (règle ECL 2026)
        "score_percentage": round(overall / max_score * 100, 1),
        "appreciation": ga.get("appreciation", ""),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": _clean_corrections(ai_result.get("corrections")),
        "suggestions": ai_result.get("suggestions", []),
    }


# ─────────────────────────────────────────────────────────
# TestDaF (esquisse à valider)
# ─────────────────────────────────────────────────────────

TESTDAF_CRITERIA = [
    ("inhalt_score", "Aufgabenbewältigung", 4),
    ("aufbau_score", "Textaufbau", 3),
    ("sprache_score", "Sprachliche Realisierung", 3),
]


def _testdaf_level(points: float) -> str:
    # HYPOTHÈSE : seuils indicatifs sur 20 (cf. testdaf_prompt.py)
    if points >= 16:
        return "TDN 5"
    if points >= 13:
        return "TDN 4"
    if points >= 9:
        return "TDN 3"
    return "unter TDN 3"


def _normalize_testdaf(ai_result: dict, config: dict) -> dict:
    """TestDaF digital : 2 tâches à 10 points (HYPOTHÈSE), total 20, niveau TDN estimé.
    Tâche hors sujet (thema_verfehlt) : tâche à 0 point."""
    ga = ai_result.get("global_assessment", {})

    raw: dict[str, dict] = {}
    for k in config["task_keys"]:
        t = ai_result.get(k, {}) or {}
        if _off_topic(t):
            t = {**t, "inhalt_score": 0, "aufbau_score": 0, "sprache_score": 0}
        raw[k] = t

    def task_score(t: dict) -> float:
        return sum(_clamp(t.get(key, 0), mx) for key, _, mx in TESTDAF_CRITERIA)

    scores = {k: task_score(t) for k, t in raw.items()}
    overall = round(sum(scores.values()))
    max_score = 20
    tdn = _testdaf_level(overall)

    criteria = [
        {
            "key": key.replace("_score", ""),
            "label": label,
            "score": sum(_clamp(t.get(key, 0), mx) for t in raw.values()),
            "max_score": mx * len(raw),
            "feedback": "",
        }
        for key, label, mx in TESTDAF_CRITERIA
    ]

    labels = {"task1": "Aufgabe 1 (Argumentation)", "task2": "Aufgabe 2 (Zusammenfassung)"}
    tasks = [
        {
            **_task_base(tkey, labels.get(tkey, tkey), t),
            "score": scores[tkey],
            "max_score": 10,
            "sub_criteria": [
                {
                    "key": key.replace("_score", ""),
                    "label": label,
                    "score": _clamp(t.get(key, 0), mx),
                    "max_score": mx,
                }
                for key, label, mx in TESTDAF_CRITERIA
            ],
        }
        for tkey, t in raw.items()
    ]

    return {
        "overall_score": overall,
        "max_score": max_score,
        # TestDaF n'a pas de "réussi" : repère interne = niveau TDN 3 estimé atteint
        "passed": overall >= 9,
        "score_percentage": round(overall / max_score * 100, 1),
        "appreciation": f"Geschätztes Niveau: {tdn}. {ga.get('appreciation', '')}".strip(),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": _clean_corrections(ai_result.get("corrections")),
        "suggestions": ai_result.get("suggestions", []),
    }