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
      "key": str, "label": str, "corrected_text": str,
      "strengths": list[str], "weaknesses": list[str],
      # optionnels, présents seulement si le barème le prévoit (ÖSD B2, ECL, TestDaF) :
      "score": float | None, "max_score": float | None, "sub_criteria": list[dict] | None,
  }],
  "corrections_list": list[dict],
  "suggestions": list[str],
}

Formes gérées : nested (Goethe B2, Goethe/ÖSD B1), flat (telc B1/B2),
osd_b2 (ÖSD B2), ecl (ECL B1/B2, esquisse), testdaf (TestDaF, esquisse).

Pour ajouter un nouvel examen/niveau : ajouter une entrée à CRITERIA_CONFIG
(et, si son schéma JSON de sortie est vraiment différent des formes gérées
ici, une nouvelle fonction _normalize_xxx). Le store Pinia et les pages Vue
n'ont plus jamais besoin d'être touchés pour ça.
"""
from __future__ import annotations

TASK_LABELS = {"task1": "Teil 1", "task2": "Teil 2", "task3": "Teil 3"}

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
    },
    ("telc", "b1"): {
        "shape": "flat",
        "criteria": [
            ("leitpunkte", "Leitpunkte", 15),
            ("gestaltung", "Gestaltung", 15),
            ("richtigkeit", "Richtigkeit", 15),
        ],
        "task_keys": ["task1"],
    },
    ("telc", "b2"): {
        "shape": "flat",
        "criteria": [
            ("aufgabenbewaeltigung", "Aufgabenbewältigung", 15),
            ("gestaltung", "Gestaltung", 15),
            ("richtigkeit", "Richtigkeit", 15),
        ],
        "task_keys": ["task1"],
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


def normalize_correction_result(provider: str, level: str, ai_result: dict) -> dict:
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
        return _normalize_flat(ai_result, config)
    if shape == "osd_b2":
        return _normalize_osd_b2(ai_result, config)
    if shape == "ecl":
        return _normalize_ecl(ai_result, config)
    if shape == "testdaf":
        return _normalize_testdaf(ai_result, config)
    raise ValueError(f"Shape inconnu: {shape}")


# ─────────────────────────────────────────────────────────
# Utilitaire
# ─────────────────────────────────────────────────────────

def _clamp(value, maximum: float) -> float:
    """Borne une note entre 0 et maximum (valeur invalide -> 0)."""
    try:
        return max(0, min(float(value), maximum))
    except (TypeError, ValueError):
        return 0


# ─────────────────────────────────────────────────────────
# Goethe / ÖSD B1 / telc / ÖSD B2
# ─────────────────────────────────────────────────────────

def _normalize_nested(ai_result: dict, config: dict) -> dict:
    """Goethe B2 / Goethe-ÖSD B1 : global_assessment + criteria_scores + task_feedbacks."""
    ga = ai_result.get("global_assessment", {})
    scores = ai_result.get("criteria_scores", {})
    task_feedbacks = ai_result.get("task_feedbacks", {})

    overall = ga.get("overall_score", 0)
    max_score = sum(m for _, _, m in config["criteria"])

    criteria = [
        {
            "key": prefix,
            "label": label,
            "score": scores.get(f"{prefix}_score", 0),
            "max_score": max_pts,
            "feedback": scores.get(f"{prefix}_feedback", ""),
        }
        for prefix, label, max_pts in config["criteria"]
    ]

    tasks = [
        {
            "key": tkey,
            "label": TASK_LABELS.get(tkey, tkey),
            "corrected_text": task_feedbacks.get(tkey, {}).get("corrected_text", ""),
            "strengths": task_feedbacks.get(tkey, {}).get("main_strengths", []),
            "weaknesses": task_feedbacks.get(tkey, {}).get("main_weaknesses", []),
        }
        for tkey in config["task_keys"]
    ]

    return {
        "overall_score": overall,
        "max_score": max_score,
        "passed": ga.get("passed", overall >= max_score * 0.6),
        "score_percentage": round(overall / max_score * 100, 1) if max_score else 0,
        "appreciation": ga.get("appreciation", ""),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": ai_result.get("corrections", []),
        "suggestions": ai_result.get("suggestions", []),
    }


def _normalize_flat(ai_result: dict, config: dict) -> dict:
    """telc B1 / telc B2 : tout au niveau racine, une seule tâche."""
    overall = ai_result.get("overall_score", 0)
    max_score = sum(m for _, _, m in config["criteria"])

    criteria = [
        {
            "key": prefix,
            "label": label,
            "score": ai_result.get(f"{prefix}_score", 0),
            "max_score": max_pts,
            "feedback": ai_result.get(f"{prefix}_feedback", ""),
        }
        for prefix, label, max_pts in config["criteria"]
    ]

    tasks = [
        {
            "key": "task1",
            "label": TASK_LABELS["task1"],
            "corrected_text": ai_result.get("corrected_text", ""),
            "strengths": [],
            "weaknesses": [],
        }
    ]

    return {
        "overall_score": overall,
        "max_score": max_score,
        "passed": ai_result.get("passed", overall >= max_score * 0.6),
        "score_percentage": round(overall / max_score * 100, 1) if max_score else 0,
        "appreciation": ai_result.get("appreciation", ""),
        "criteria": criteria,
        "tasks": tasks,
        "corrections_list": ai_result.get("corrections", []),
        "suggestions": ai_result.get("suggestions", []),
    }


def _normalize_osd_b2(ai_result: dict, config: dict) -> dict:
    """
    ÖSD B2 : deux tâches indépendantes, chacune notée A/K/T/L + malus F.
    On agrège les composantes des deux tâches pour reconstituer une liste de
    "critères" globale cohérente avec les autres examens (panneau "Critères"
    de l'UI), tout en gardant le détail A/K/T/L/F par tâche dans `tasks`.

    `passed` est calculé sur 60 % de 30 comme repère interne à la plateforme,
    ce n'est PAS le seuil de certification ÖSD officiel (qui dépend du total
    combiné Lesen+Hören+Schreiben). `floor_reached` expose le plancher officiel (>= 10/30).
    """
    ga = ai_result.get("global_assessment", {})
    t1 = ai_result.get("task1", {})
    t2 = ai_result.get("task2", {})

    overall = ga.get("overall_score", 0)
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
            "key": tkey,
            "label": TASK_LABELS.get(tkey, tkey),
            "corrected_text": t.get("corrected_text", ""),
            "strengths": t.get("main_strengths", []),
            "weaknesses": t.get("main_weaknesses", []),
            "score": t.get("task_score", 0),
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
        "corrections_list": ai_result.get("corrections", []),
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


def _normalize_ecl(ai_result: dict, config: dict) -> dict:
    """ECL B1/B2 : 5 critères 0-5 par texte (25/texte), note = moyenne des 2 textes (max 25).
    HYPOTHÈSE à valider : moyenne des deux textes. Les scores sont recalculés ici,
    sans faire confiance aux totaux renvoyés par l'IA."""
    ga = ai_result.get("global_assessment", {})
    raw = {k: ai_result.get(k, {}) for k in config["task_keys"]}

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
            "key": tkey,
            "label": f"Text {i + 1}",
            "corrected_text": t.get("corrected_text", ""),
            "strengths": t.get("main_strengths", []),
            "weaknesses": t.get("main_weaknesses", []),
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
        "corrections_list": ai_result.get("corrections", []),
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
    """TestDaF digital : 2 tâches à 10 points (HYPOTHÈSE), total 20, niveau TDN estimé."""
    ga = ai_result.get("global_assessment", {})
    raw = {k: ai_result.get(k, {}) for k in config["task_keys"]}

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
            "key": tkey,
            "label": labels.get(tkey, tkey),
            "corrected_text": t.get("corrected_text", ""),
            "strengths": t.get("main_strengths", []),
            "weaknesses": t.get("main_weaknesses", []),
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
        "corrections_list": ai_result.get("corrections", []),
        "suggestions": ai_result.get("suggestions", []),
    }