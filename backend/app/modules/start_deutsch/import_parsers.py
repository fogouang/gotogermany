"""
app/modules/start_deutsch/import_parsers.py

Parsers JSON vers questions, un par format_type Start Deutsch.

Chaque Teil porte une liste "questions" numérotée, sauf form_fill, free_text
et les formats sprechen_*, qui forment une tâche unique (question_number = 1).
"""


def parse_mc_text(teil_data: dict) -> list[dict]:
    return [{
        "question_number": q["number"],
        "content": {"question": q["question"], "options": q["options"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "image_file": None,
    } for q in teil_data.get("questions", [])]


def parse_mc_image(teil_data: dict) -> list[dict]:
    """Options en images : label + image_file."""
    return [{
        "question_number": q["number"],
        "content": {"question": q.get("question", ""), "options": q["options"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "image_file": None,
    } for q in teil_data.get("questions", [])]


def parse_true_false(teil_data: dict) -> list[dict]:
    """
    Deux cas :
    - texte commun au Teil (Lesen Teil 1, Hören Teil 2) : il est rangé dans
      shared_content par build_teil_shared_content, la question ne garde que
      l'énoncé ;
    - un texte par question (Lesen Teil 3, panneaux) : chaque question porte
      son context, son text et son statement.
    """
    questions = []
    for q in teil_data.get("questions", []):
        content = {"statement": q["statement"]}
        if "text" in q:
            content["text"] = q["text"]
        if "context" in q:
            content["context"] = q["context"]
        questions.append({
            "question_number": q["number"],
            "content": content,
            "correct_answer": {"answer": q["answer"]},  # "richtig" | "falsch"
            "points": 1,
            "image_file": None,
        })
    return questions


def parse_ja_nein(teil_data: dict) -> list[dict]:
    return [{
        "question_number": q["number"],
        "content": {"statement": q["statement"]},
        "correct_answer": {"answer": q["answer"]},  # "ja" | "nein"
        "points": 1,
        "image_file": None,
    } for q in teil_data.get("questions", [])]


def parse_matching_2options(teil_data: dict) -> list[dict]:
    return [{
        "question_number": q["number"],
        "content": {"scenario": q["scenario"], "options": q["options"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "image_file": None,
    } for q in teil_data.get("questions", [])]


def parse_matching_with_distractor(teil_data: dict) -> list[dict]:
    """Les annonces sont communes au Teil (shared_content.ads)."""
    return [{
        "question_number": p["number"],
        "content": {"profile": p["profile"]},
        "correct_answer": {"answer": p["answer"]},  # lettre, ou "X" sans solution
        "points": 1,
        "image_file": None,
    } for p in teil_data.get("profiles", [])]


def parse_image_day_matching(teil_data: dict) -> list[dict]:
    """Les images sont communes au Teil (shared_content.images)."""
    return [{
        "question_number": d["number"],
        "content": {"day": d["day"]},
        "correct_answer": {"answer": d["answer"]},
        "points": 1,
        "image_file": None,
    } for d in teil_data.get("days", [])]


def parse_form_fill(teil_data: dict) -> list[dict]:
    """Une question pour tout le formulaire.
    fields = [{"number": 1, "label": "Alter", "correct_value": "22"}, ...]
    """
    fields = teil_data.get("fields", [])
    return [{
        "question_number": 1,
        "content": {
            "prompt_text": teil_data.get("prompt_text", ""),
            "fields": [{"number": f["number"], "label": f["label"]} for f in fields],
        },
        "correct_answer": {"fields": {str(f["number"]): f["correct_value"] for f in fields}},
        "points": teil_data.get("max_score", 5),
        "image_file": None,
    }]


def parse_free_text(teil_data: dict) -> list[dict]:
    """Pas de correct_answer : la production est corrigée par l'IA
    (StartDeutschSchreibenCorrection)."""
    return [{
        "question_number": 1,
        "content": {
            "prompt": teil_data.get("prompt", ""),
            "content_points": teil_data.get("content_points", []),
            "min_words": teil_data.get("min_words"),
            "max_words": teil_data.get("max_words"),
        },
        "correct_answer": None,
        "points": teil_data.get("max_score", 10),
        "image_file": None,
    }]


# ── Sprechen : affichage seulement, pas encore de correction ─────────

def parse_sprechen_group_intro(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {"prompts": teil_data.get("prompts", [])},  # ["Name?", "Alter?", ...]
        "correct_answer": None,
        "points": teil_data.get("max_score", 0),
        "image_file": None,
    }]


def parse_sprechen_group_word_card(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {"theme": teil_data.get("theme", ""), "cards": teil_data.get("cards", [])},
        "correct_answer": None,
        "points": teil_data.get("max_score", 0),
        "image_file": None,
    }]


def parse_sprechen_group_image_card(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {"cards": teil_data.get("cards", [])},  # [{"image_file": "..."}]
        "correct_answer": None,
        "points": teil_data.get("max_score", 0),
        "image_file": None,
    }]


def parse_sprechen_duo_question_card(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {"cards": teil_data.get("cards", [])},  # ["Geburtstag?", "Wohnort?", ...]
        "correct_answer": None,
        "points": teil_data.get("max_score", 0),
        "image_file": None,
    }]


def parse_sprechen_duo_monologue_card(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {
            "central_question": teil_data.get("central_question", ""),
            "sub_prompts": teil_data.get("sub_prompts", []),
        },
        "correct_answer": None,
        "points": teil_data.get("max_score", 0),
        "image_file": None,
    }]


def parse_sprechen_duo_negotiation(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {
            "scenario": teil_data.get("scenario", ""),
            "schedule_a": teil_data.get("schedule_a", {}),
            "schedule_b": teil_data.get("schedule_b", {}),
        },
        "correct_answer": None,
        "points": teil_data.get("max_score", 0),
        "image_file": None,
    }]


PARSERS = {
    "mc_text": parse_mc_text,
    "mc_image": parse_mc_image,
    "true_false": parse_true_false,
    "ja_nein": parse_ja_nein,
    "matching_2options": parse_matching_2options,
    "matching_with_distractor": parse_matching_with_distractor,
    "image_day_matching": parse_image_day_matching,
    "form_fill": parse_form_fill,
    "free_text": parse_free_text,
    "sprechen_group_intro": parse_sprechen_group_intro,
    "sprechen_group_word_card": parse_sprechen_group_word_card,
    "sprechen_group_image_card": parse_sprechen_group_image_card,
    "sprechen_duo_question_card": parse_sprechen_duo_question_card,
    "sprechen_duo_monologue_card": parse_sprechen_duo_monologue_card,
    "sprechen_duo_negotiation": parse_sprechen_duo_negotiation,
}


def build_teil_shared_content(teil_data: dict, format_type: str) -> dict | None:
    """Contenu commun à toutes les questions du Teil : annonces, images ou texte."""
    if format_type == "matching_with_distractor":
        return {"ads": teil_data.get("ads", [])}
    if format_type == "image_day_matching":
        return {"images": teil_data.get("images", [])}
    if format_type in ("true_false", "ja_nein", "mc_text"):
        # mc_text : texte présent en Lesen A2 (article, e-mail), absent en Hören
        text = teil_data.get("text", "")
        return {"text": text} if text else None
    return None