"""
app/modules/start_deutsch/import_parsers.py

Parsers JSON → dicts de questions, un par format_type. Même principe que
app/modules/exams/import_parsers.py, adapté aux 15 format_type Start Deutsch.

Convention générale : chaque teil_data a une clé "questions" (liste
d'items numérotés), sauf form_fill/free_text/sprechen_* qui représentent
une tâche unique (question_number=1).
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
    """Options = images (label + image_file), pas de texte."""
    return [{
        "question_number": q["number"],
        "content": {"question": q.get("question", ""), "options": q["options"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "image_file": None,
    } for q in teil_data.get("questions", [])]


def parse_true_false(teil_data: dict) -> list[dict]:
    """
    Deux formes possibles selon le Teil :
    - texte partagé (Lesen Teil1, Hören Teil2) : teil_data["text"] au niveau
      du Teil (capturé à part par build_teil_shared_content), question =
      juste {"statement": ...}
    - textes indépendants (Lesen Teil3 "Hinweisschilder", multi_text=True) :
      chaque question porte SON PROPRE {"context": ..., "text": ..., "statement": ...}
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
    """Le pool d'annonces (ads) est partagé au niveau du Teil (shared_content),
    pas répété par question — cf. _build_teil_shared_content."""
    return [{
        "question_number": p["number"],
        "content": {"profile": p["profile"]},
        "correct_answer": {"answer": p["answer"]},  # lettre, ou "X" si pas de solution
        "points": 1,
        "image_file": None,
    } for p in teil_data.get("profiles", [])]


def parse_image_day_matching(teil_data: dict) -> list[dict]:
    """Le pool d'images est partagé au niveau du Teil (shared_content)."""
    return [{
        "question_number": d["number"],
        "content": {"day": d["day"]},
        "correct_answer": {"answer": d["answer"]},
        "points": 1,
        "image_file": None,
    } for d in teil_data.get("days", [])]


def parse_form_fill(teil_data: dict) -> list[dict]:
    """Une seule question représentant tout le formulaire.
    teil_data['fields'] = [{"number": 1, "label": "Alter", "correct_value": "22"}, ...]
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
    """Une seule question — pas de correct_answer, corrigée via l'IA
    (StartDeutschSchreibenCorrection), pas via ce mécanisme."""
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


# ── Sprechen — structure minimale (V1 : pas encore de correction/agent) ────

def parse_sprechen_group_intro(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "content": {"prompts": teil_data.get("prompts", [])},  # ex: ["Name?","Alter?",...]
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
        "content": {"cards": teil_data.get("cards", [])},  # ex: ["Geburtstag?","Wohnort?",...]
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
    """Pool d'options / texte partagé par tout le Teil.

    ⚠️ Corrige un bug réel : teil_data["text"] (la lettre/l'annonce que
    TOUTES les questions true_false/ja_nein du Teil partagent) était
    silencieusement ignoré — seuls matching_with_distractor/
    image_day_matching étaient gérés ici, donc le texte source
    n'atteignait jamais la DB (ni donc le frontend).
    """
    if format_type == "matching_with_distractor":
        return {"ads": teil_data.get("ads", [])}
    if format_type == "image_day_matching":
        return {"images": teil_data.get("images", [])}
    if format_type in ("true_false", "ja_nein"):
        text = teil_data.get("text", "")
        return {"text": text} if text else None
    if format_type == "mc_text":
        # mc_text sert pour Hören (5 messages indépendants, pas de texte
        # partagé — teil_data["text"] absent) ET pour Lesen A2 (1 article/
        # email partagé, shared_text=True côté structure). On ne capture
        # que si un texte partagé existe réellement.
        text = teil_data.get("text", "")
        return {"text": text} if text else None
    return None