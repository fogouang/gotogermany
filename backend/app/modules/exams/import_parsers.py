"""
app/modules/exams/import_parsers.py

Parsers JSON → dicts de questions.
Partagés entre scripts/import_exam.py et import_service.py
"""

def parse_richtig_falsch(teil_data: dict) -> list[dict]:
    questions = []
    if "audios" in teil_data:
        for audio in teil_data.get("audios", []):
            audio_file = audio.get("audio_file", "")
            if audio_file:
                audio_file = audio_file.replace("\\", "/")
            for q in audio.get("questions", []):
                questions.append({
                    "question_number": q["number"],
                    "question_type": "richtig_falsch",
                    "content": {
                        "statement": q["statement"],
                        "audio_type": audio.get("audio_type", ""),
                        "transcription": audio.get("transcription", ""),
                        "audio_number": audio.get("audio_number"),
                        "max_plays": teil_data.get("max_plays", 2),
                    },
                    "correct_answer": {"answer": q["answer"]},
                    "points": 1,
                    "audio_file": audio_file or None,
                })
        return questions
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "richtig_falsch",
            "content": {"statement": q["statement"]},
            "correct_answer": {"answer": q["answer"]},
            "points": 1,
            "audio_file": None,
        })
    return questions


def parse_ja_nein(teil_data: dict) -> list[dict]:
    return [{
        "question_number": q["number"],
        "question_type": "ja_nein",
        "content": {
            "author": q.get("author", ""),
            "text": q.get("text", ""),
            "statement": q.get("statement", ""),
        },
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_qcm_abc(teil_data: dict) -> list[dict]:
    questions = []
    if "texts" in teil_data:
        for text_block in teil_data["texts"]:
            stimulus = text_block.get("stimulus_text", "")
            for q in text_block.get("questions", []):
                questions.append({
                    "question_number": q["number"],
                    "question_type": "qcm_abc",
                    "content": {"stem": q["stem"], "options": q["options"], "stimulus_text": stimulus},
                    "correct_answer": {"answer": q["answer"]},
                    "points": 1, "audio_file": None,
                })
    else:
        for q in teil_data.get("questions", []):
            questions.append({
                "question_number": q["number"],
                "question_type": "qcm_abc",
                "content": {"stem": q["stem"], "options": q["options"]},
                "correct_answer": {"answer": q["answer"]},
                "points": 1, "audio_file": None,
            })
    return questions


def parse_matching(teil_data: dict) -> list[dict]:
    anzeigen = teil_data.get("anzeigen", {})
    return [{
        "question_number": q["number"],
        "question_type": "matching",
        "content": {"situation": q["situation"], "anzeigen": anzeigen},
        "correct_answer": {"answer": q["answer"]},
        "points": 1, "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_mixed_richtig_falsch_qcm(teil_data: dict) -> list[dict]:
    questions = []
    for audio in teil_data.get("audios", []):
        audio_file = (audio.get("audio_file", "") or "").replace("\\", "/")
        for q in audio.get("questions", []):
            q_type = q.get("type", "richtig_falsch")
            content = {
                "audio_type": audio.get("audio_type", ""),
                "transcription": audio.get("transcription", ""),
                "audio_number": audio.get("audio_number"),
            }
            if q_type == "richtig_falsch":
                content["statement"] = q["statement"]
            else:
                content["stem"] = q["stem"]
                content["options"] = q["options"]
            questions.append({
                "question_number": q["number"],
                "question_type": q_type,
                "content": content,
                "correct_answer": {"answer": q["answer"]},
                "points": 1,
                "audio_file": audio_file or None,
            })
    return questions


def parse_zuordnung_speaker(teil_data: dict) -> list[dict]:
    speakers = teil_data.get("speakers", {})
    return [{
        "question_number": q["number"],
        "question_type": "zuordnung_speaker",
        "content": {"statement": q["statement"], "speakers": speakers},
        "correct_answer": {"answer": q["answer"]},
        "points": 1, "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_free_text(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "question_type": "free_text",
        "content": {
            "scenario": teil_data.get("scenario", ""),
            "prompts": teil_data.get("prompts", []),
            "word_count_target": teil_data.get("word_count_target", 80),
            "text_type": teil_data.get("text_type", ""),
            "register": teil_data.get("register", "informell"),
            "stimulus": teil_data.get("stimulus", ""),
            "stimulus_author": teil_data.get("stimulus_author", ""),
            "stimulus_email": teil_data.get("stimulus_email", {}),
        },
        "correct_answer": {
            "musterlösung": teil_data.get("musterlösung", ""),
            "scoring_criteria": teil_data.get("scoring_criteria", {}),
        },
        "points": teil_data.get("max_score", 40),
        "audio_file": None,
    }]


def parse_oral(teil_data: dict, question_type: str) -> list[dict]:
    content = {
        "scenario": teil_data.get("scenario", ""),
        "prompts": teil_data.get("prompts", []),
        "tasks": teil_data.get("tasks", []),
    }
    if "themes" in teil_data:
        content["themes"] = teil_data["themes"]
    return [{
        "question_number": 1,
        "question_type": question_type,
        "content": content,
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 32),
        "audio_file": None,
    }]


def parse_zuordnung_titre(teil_data: dict) -> list[dict]:
    titres = teil_data.get("titres", {})
    return [{
        "question_number": q["number"],
        "question_type": "zuordnung_titre",
        "content": {"stimulus_text": q["stimulus_text"], "titres": titres},
        "correct_answer": {"answer": q["answer"]},
        "points": 5, "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_selektives_matching(teil_data: dict) -> list[dict]:
    anzeigen = teil_data.get("anzeigen", {})
    return [{
        "question_number": q["number"],
        "question_type": "selektives_matching",
        "content": {"situation": q["situation"], "anzeigen": anzeigen},
        "correct_answer": {"answer": q["answer"]},
        "points": 1, "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_qcm_gap_fill(teil_data: dict) -> list[dict]:
    text_with_gaps = teil_data.get("text_with_gaps", "")
    return [{
        "question_number": q["number"],
        "question_type": "qcm_gap_fill",
        "content": {"text_with_gaps": text_with_gaps, "gap_number": q["number"], "options": q["options"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1, "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_word_bank_gap_fill(teil_data: dict) -> list[dict]:
    text_with_gaps = teil_data.get("text_with_gaps", "")
    word_bank = teil_data.get("word_bank", {})
    return [{
        "question_number": q["number"],
        "question_type": "word_bank_gap_fill",
        "content": {"text_with_gaps": text_with_gaps, "gap_number": q["number"], "word_bank": word_bank},
        "correct_answer": {"answer": q["answer"]},
        "points": 1, "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_oral_kennenlernen(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "question_type": "oral_kennenlernen",
        "content": {"topics": teil_data.get("topics", []), "instructions": teil_data.get("instructions", "")},
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 15),
        "audio_file": None,
    }]


def parse_oral_thema(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "question_type": "oral_thema",
        "content": {
            "topic": teil_data.get("topic", ""),
            "opinion_a": teil_data.get("opinion_a", {}),
            "opinion_b": teil_data.get("opinion_b", {}),
            "instructions": teil_data.get("instructions", ""),
        },
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 30),
        "audio_file": None,
    }]


PARSERS = {
    "richtig_falsch":           parse_richtig_falsch,
    "ja_nein":                  parse_ja_nein,
    "qcm_abc":                  parse_qcm_abc,
    "matching":                 parse_matching,
    "mixed_richtig_falsch_qcm": parse_mixed_richtig_falsch_qcm,
    "zuordnung_speaker":        parse_zuordnung_speaker,
    "free_text":                parse_free_text,
    "oral_interaction":         lambda d: parse_oral(d, "oral_interaction"),
    "oral_monologue":           lambda d: parse_oral(d, "oral_monologue"),
    "oral_feedback":            lambda d: parse_oral(d, "oral_feedback"),
    "zuordnung_titre":          parse_zuordnung_titre,
    "selektives_matching":      parse_selektives_matching,
    "qcm_gap_fill":             parse_qcm_gap_fill,
    "word_bank_gap_fill":       parse_word_bank_gap_fill,
    "oral_kennenlernen":        parse_oral_kennenlernen,
    "oral_thema":               parse_oral_thema,
}