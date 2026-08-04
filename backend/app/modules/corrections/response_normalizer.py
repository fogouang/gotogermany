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
      # optionnels, présents seulement si le barème le prévoit (ex. ÖSD B2) :
      "score": float | None, "max_score": float | None, "sub_criteria": list[dict] | None,
  }],
  "corrections_list": list[dict],
  "suggestions": list[str],
}

Pour ajouter un nouvel examen/niveau : ajouter une entrée à CRITERIA_CONFIG
(et, si son schéma JSON de sortie est vraiment différent des 3 formes gérées
ici, une nouvelle fonction _normalize_xxx). Le store Pinia et les pages Vue
n'ont plus jamais besoin d'être touchés pour ça.
"""
from __future__ import annotations

TASK_LABELS = {"task1": "Teil 1", "task2": "Teil 2", "task3": "Teil 3"}

# (provider, level) -> config. Les 4 tuples nested/flat couvrent Goethe B2,
# Goethe/ÖSD B1, telc B1, telc B2. ÖSD B2 a sa propre forme (osd_b2).
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
}


def normalize_correction_result(provider: str, level: str, ai_result: dict) -> dict:
    key = (provider.lower(), level.lower())
    config = CRITERIA_CONFIG.get(key)
    if config is None:
        raise ValueError(
            f"Barème inconnu pour {provider} {level} — ajoute une entrée à CRITERIA_CONFIG."
        )

    shape = config["shape"]
    if shape == "nested":
        return _normalize_nested(ai_result, config)
    if shape == "flat":
        return _normalize_flat(ai_result, config)
    if shape == "osd_b2":
        return _normalize_osd_b2(ai_result, config)
    raise ValueError(f"Shape inconnu: {shape}")


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

    ⚠️ `passed` ici est calculé sur 60% de 30 comme repère de performance
    interne à la plateforme — ce n'est PAS le seuil de certification ÖSD
    officiel (qui dépend du total combiné Lesen+Hören+Schreiben). Le champ
    `floor_reached` expose le vrai plancher officiel (>=10/30).
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
        # Formale Richtigkeit est un malus (0 à -6 au total) — présenté en score positif inversé pour l'UI
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