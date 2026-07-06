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
    content = {
        "word_count_target": teil_data.get("word_count_target", 80),
        "text_type": teil_data.get("text_type", ""),
        "register": teil_data.get("register", "informell"),
    }

    # TELC — réponse à un e-mail reçu
    if teil_data.get("stimulus_email"):
        content["stimulus_email"] = teil_data["stimulus_email"]

    # Goethe — commentaire d'une citation de forum
    if teil_data.get("stimulus"):
        content["stimulus"] = teil_data["stimulus"]
        content["stimulus_author"] = teil_data.get("stimulus_author", "")

    # Sujet simple : topic (Goethe forum) ou scenario (Goethe/TELC message)
    if teil_data.get("topic"):
        content["topic"] = teil_data["topic"]

    # "scenario" (Goethe/TELC) ou "situation" (Goethe-ÖSD B1) — même rôle
    if teil_data.get("scenario"):
        content["scenario"] = teil_data["scenario"]
    elif teil_data.get("situation"):
        content["scenario"] = teil_data["situation"]

    if teil_data.get("recipient"):
        content["recipient"] = teil_data["recipient"]

    # Détecte en amont si on est dans le cas "variantes d'opinion" (ÖSD B2),
    # qui gère prompts/leitpunkte lui-même plus bas — évite un double
    # remplissage de content["prompts"] à partir des mêmes leitpunkte.
    has_opinion_variants = bool(
        teil_data.get("variante_a") or teil_data.get("variante_b")
    )

    # "prompts" (Goethe/TELC) ou "leitpunkte" (Goethe-ÖSD B1) — même rôle
    if teil_data.get("prompts"):
        content["prompts"] = teil_data["prompts"]
    elif teil_data.get("leitpunkte") and not has_opinion_variants:
        content["prompts"] = teil_data["leitpunkte"]

    # TELC/ÖSD B2 — choix entre 2 thèmes de lettre ("themen" liste)
    if teil_data.get("themen"):
        content["themes"] = {
            str(th["nummer"]): {
                "titel": th.get("titel", ""),
                "stimulus": th.get("stimulus", ""),
                "prompts": th.get("prompts", []),
            }
            for th in teil_data["themen"]
        }

    # ÖSD — e-mail de réclamation structurée (promesses vs réalité)
    if teil_data.get("versprechen") or teil_data.get("probleme"):
        content["info_comparison"] = {
            "anbieter": teil_data.get("anbieter", ""),
            "situation": teil_data.get("situation", ""),
            "versprechen": teil_data.get("versprechen", []),
            "probleme": teil_data.get("probleme", []),
            "kontakt": teil_data.get("kontakt", ""),
        }

    # ÖSD — choix entre 2 variantes d'opinion + leitpunkte communs
    if has_opinion_variants:
        variants = {}
        for key in ("a", "b"):
            v = teil_data.get(f"variante_{key}")
            if v:
                variants[key] = {
                    "thema": v.get("thema", ""),
                    "aussagen": v.get("aeusserungen") or v.get("schlagzeilen") or [],
                }
        content["opinion_variants"] = variants
        content["leitpunkte"] = teil_data.get("leitpunkte", [])

    return [{
        "question_number": 1,
        "question_type": "free_text",
        "content": content,
        "correct_answer": {
            "musterlösung": teil_data.get("musterlösung", "") or teil_data.get("musterloesung", ""),
            "musterloesung_thema1": teil_data.get("musterloesung_thema1", ""),
            "musterloesung_thema2": teil_data.get("musterloesung_thema2", ""),
            "scoring_criteria": teil_data.get("scoring_criteria", {}),
        },
        "points": teil_data.get("max_score", 40),
        "audio_file": None,
    }]

def parse_oral(teil_data: dict, question_type: str) -> list[dict]:
    content = {
        "scenario": teil_data.get("scenario", ""),
        "prompts": teil_data.get("prompts") or teil_data.get("leitpunkte", []),
        "tasks": teil_data.get("tasks", []),
    }
    if "titel" in teil_data:
        content["titel"] = teil_data["titel"]
    if "themes" in teil_data:
        content["themes"] = teil_data["themes"]
    #  Diskussion (TELC B2 Teil 2) — titre + thème résumé
    if "diskussion_titel" in teil_data:
        content["diskussion_titel"] = teil_data["diskussion_titel"]
    if "diskussion_thema" in teil_data:
        content["diskussion_thema"] = teil_data["diskussion_thema"]
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

    # Structure Goethe/TELC : "questions" avec number/stimulus_text/answer
    if teil_data.get("questions"):
        return [{
            "question_number": q["number"],
            "question_type": "zuordnung_titre",
            "content": {"stimulus_text": q["stimulus_text"], "titres": titres},
            "correct_answer": {"answer": q["answer"]},
            "points": 5,
            "audio_file": None,
        } for q in teil_data["questions"]]

    # Structure ÖSD B2 : "texte" avec text_number/content/answer
    if teil_data.get("texte"):
        return [{
            "question_number": q["text_number"],
            "question_type": "zuordnung_titre",
            "content": {"stimulus_text": q["content"], "titres": titres},
            "correct_answer": {"answer": q["answer"]},
            "points": 5,
            "audio_file": None,
        } for q in teil_data["texte"]]

    return []


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
    content = {
        "topics": teil_data.get("topics", []),
        "instructions": teil_data.get("instructions", ""),
    }
    # ÖSD — variante avec situation/thema/hinweis/leitfragen
    if teil_data.get("situation"):
        content["situation"] = teil_data["situation"]
        content["thema"] = teil_data.get("thema", "")
        content["hinweis"] = teil_data.get("hinweis", "")
        content["leitfragen"] = teil_data.get("leitfragen", [])
    return [{
        "question_number": 1,
        "question_type": "oral_kennenlernen",
        "content": content,
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 15),
        "audio_file": None,
    }]


def parse_oral_monologue(teil_data: dict) -> list[dict]:
    content = {}
    # Goethe B2 — choix candidat_a/candidat_b (thema1/thema2 + leitpunkte)
    if teil_data.get("kandidat_a") or teil_data.get("kandidat_b"):
        content["kandidat_a"] = teil_data.get("kandidat_a", {})
        content["kandidat_b"] = teil_data.get("kandidat_b", {})
    # TELC B2 / Goethe B1 — thèmes avec Folien/slides
    if teil_data.get("themes"):
        content["themes"] = teil_data["themes"]
    if teil_data.get("titel"):
        content["titel"] = teil_data["titel"]
    if teil_data.get("sprachliche_mittel"):
        content["sprachliche_mittel"] = teil_data["sprachliche_mittel"]
    return [{
        "question_number": 1,
        "question_type": "oral_monologue",
        "content": content,
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 32),
        "audio_file": None,
    }]



def parse_oral_discussion(teil_data: dict) -> list[dict]:
    content = {
        "question": teil_data.get("question", ""),
        "tasks": teil_data.get("tasks", []),
        "hints": teil_data.get("hints", []),
    }
    return [{
        "question_number": 1,
        "question_type": "oral_discussion",
        "content": content,
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 32),
        "audio_file": None,
    }]

def parse_oral_thema(teil_data: dict) -> list[dict]:
    return [{
        "question_number": 1,
        "question_type": "oral_thema",
        "content": {
            "topic": teil_data.get("topic", ""),
            "person_a": teil_data.get("person_a", {}),
            "person_b": teil_data.get("person_b", {}),
            "instructions": teil_data.get("instructions", ""),
        },
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 30),
        "audio_file": None,
    }]

def parse_zuordnung_personen(teil_data: dict) -> list[dict]:
    persons = teil_data.get("persons", {})
    return [{
        "question_number": q["number"],
        "question_type": "zuordnung_personen",
        "content": {
            "statement": q["statement"],
            "persons": {
                key: {
                    "name": p.get("name", key.upper()),
                    "text": p.get("text", "")
                }
                for key, p in persons.items()
            }
        },
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_lueckentext_saetze(teil_data: dict) -> list[dict]:
    candidates = teil_data.get("candidates", {})
    article_text = teil_data.get("article_text", "")
    article_title = teil_data.get("article_title", "")
    return [{
        "question_number": q["number"],
        "question_type": "lueckentext_saetze",
        "content": {
            "gap_number": q["number"],
            "article_text": article_text,
            "article_title": article_title,
            "candidates": candidates,
        },
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_zuordnung_meinungen(teil_data: dict) -> list[dict]:
    opinions = teil_data.get("opinions", {})
    return [{
        "question_number": q["number"],
        "question_type": "zuordnung_meinungen",
        "content": {
            "title": q["title"],
            "opinions": {
                key: {
                    "author": op.get("author", ""),
                    "text": op.get("text", "")
                }
                for key, op in opinions.items()
            }
        },
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_zuordnung_paragraphen(teil_data: dict) -> list[dict]:
    headings = teil_data.get("headings", {})
    paragraphs = teil_data.get("paragraphs", {})
    return [{
        "question_number": q["number"],
        "question_type": "zuordnung_paragraphen",
        "content": {
            "paragraph_number": q.get("paragraph", ""),
            "paragraph_text": paragraphs.get(f"p{q['paragraph']}", {}).get("text", ""),
            "headings": headings,
        },
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]
    
def parse_gap_fill_letters(teil_data: dict) -> list[dict]:
    """Lesen ÖSD Teil 3 — texte continu, lacunes de quelques lettres."""
    return [{
        "question_number": q["number"],
        "question_type": "gap_fill_letters",
        "content": {"visible_text": q["visible_text"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_gap_fill_words(teil_data: dict) -> list[dict]:
    """Lesen ÖSD Teil 4 — texte à trous, réponse libre (pas de choix)."""
    text_with_gaps = teil_data.get("text_with_gaps", "")
    return [{
        "question_number": q["number"],
        "question_type": "gap_fill_words",
        "content": {"text_with_gaps": text_with_gaps, "gap_number": q["number"]},
        "correct_answer": {"answer": q["answer"]},
        "points": 1,
        "audio_file": None,
    } for q in teil_data.get("questions", [])]


def parse_tableau_mixed(teil_data: dict) -> list[dict]:
    """Hören ÖSD Teil 2 — tableau comparatif, une question par ligne (zeile)."""
    spalten = teil_data.get("spalten", [])
    audio_file = (teil_data.get("audio_file") or "").replace("\\", "/")
    questions = []
    for row in teil_data.get("tableau", []):
        questions.append({
            "question_number": row["zeile_number"],
            "question_type": "tableau_mixed",
            "content": {
                "zeile_name": row["zeile_name"],
                "type": row["type"],
                "spalten": spalten,
                "options": row.get("options", []),
            },
            "correct_answer": {"answers": row["answers"]},
            "points": 1,
            "audio_file": audio_file or None,
        })
    return questions


def parse_bildbeschreibung(teil_data: dict) -> list[dict]:
    """Sprechen — description/interprétation d'image, choix parmi 3 par candidat."""
    content = {
        "kandidat_a": teil_data.get("kandidat_a", {}),
        "kandidat_b": teil_data.get("kandidat_b", {}),
        "sprachliche_mittel": teil_data.get("sprachliche_mittel", []),
        "instructions": teil_data.get("instructions", ""),
        "hinweis": teil_data.get("hinweis", ""),
    }
    return [{
        "question_number": 1,
        "question_type": "bildbeschreibung",
        "content": content,
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 10),
        "audio_file": None,
    }]


def parse_oral_meinungsaustausch(teil_data: dict) -> list[dict]:
    """Sprechen — échange d'opinions, deux positions contradictoires à défendre."""
    content = {
        "thema": teil_data.get("thema", ""),
        "person1": teil_data.get("person1", {}),
        "person2": teil_data.get("person2", {}),
        "sprachliche_mittel": teil_data.get("sprachliche_mittel", []),
        "instructions": teil_data.get("instructions", ""),
    }
    return [{
        "question_number": 1,
        "question_type": "oral_meinungsaustausch",
        "content": content,
        "correct_answer": {"scoring_criteria": teil_data.get("scoring_criteria", {})},
        "points": teil_data.get("max_score", 10),
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
    "oral_monologue":           parse_oral_monologue,
    "oral_feedback":            lambda d: parse_oral(d, "oral_feedback"),
    "zuordnung_titre":          parse_zuordnung_titre,
    "selektives_matching":      parse_selektives_matching,
    "qcm_gap_fill":             parse_qcm_gap_fill,
    "word_bank_gap_fill":       parse_word_bank_gap_fill,
    "oral_kennenlernen":        parse_oral_kennenlernen,
    "oral_thema":               parse_oral_thema,
    "zuordnung_personen":       parse_zuordnung_personen,
    "lueckentext_saetze":       parse_lueckentext_saetze,
    "zuordnung_meinungen":      parse_zuordnung_meinungen,
    "zuordnung_paragraphen":    parse_zuordnung_paragraphen,
    "oral_discussion":          parse_oral_discussion,
    "gap_fill_letters":         parse_gap_fill_letters,        
    "gap_fill_words":           parse_gap_fill_words,         
    "tableau_mixed":            parse_tableau_mixed,          
    "bildbeschreibung":         parse_bildbeschreibung,        
    "oral_meinungsaustausch":   parse_oral_meinungsaustausch,  
}