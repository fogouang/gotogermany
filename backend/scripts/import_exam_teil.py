"""
scripts/import_exam.py

Importe un fichier JSON d'examen complet en base de données.
Supporte Goethe-ÖSD B1 ET TELC Deutsch B1.

Usage :
    uv run python scripts/import_exam.py path/to/exam.json
    uv run python scripts/import_exam.py path/to/exam.json --replace

Options :
    --replace   Supprime et réinsère les questions si le teil existe déjà.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
import app.shared.database.registry  # noqa

from app.shared.database.session import SessionLocal as AsyncSessionLocal
from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.modules.questions.models import Question
from sqlalchemy import select, func


# ─────────────────────────────────────────────
# Parsers existants (Goethe-ÖSD)
# ─────────────────────────────────────────────

def parse_richtig_falsch(teil_data: dict) -> list[dict]:
    """
    Gère 2 cas :
    - Lesen/Hören Teil simple : questions[] avec statement
    - Hören TELC : audios[] avec questions[] imbriquées (1 question par audio)
    """
    questions = []

    # Cas TELC Hören Teil 1 et Teil 3 : audios[]
    if "audios" in teil_data:
        for audio in teil_data.get("audios", []):
            audio_file = audio.get("audio_file", "")
            if audio_file:
                audio_file = audio_file.replace("\\", "/")
            transcription = audio.get("transcription", "")
            audio_type = audio.get("audio_type", "")
            max_plays = teil_data.get("max_plays", 2)

            for q in audio.get("questions", []):
                questions.append({
                    "question_number": q["number"],
                    "question_type": "richtig_falsch",
                    "content": {
                        "statement": q["statement"],
                        "audio_type": audio_type,
                        "transcription": transcription,
                        "audio_number": audio.get("audio_number"),
                        "max_plays": max_plays,
                    },
                    "correct_answer": {"answer": q["answer"]},
                    "points": 1,
                    "audio_file": audio_file or None,
                })
        return questions

    # Cas standard : questions[] directes
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
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
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
        })
    return questions


def parse_qcm_abc(teil_data: dict) -> list[dict]:
    questions = []

    if "texts" in teil_data:
        for text_block in teil_data["texts"]:
            stimulus = text_block.get("stimulus_text", "")
            for q in text_block.get("questions", []):
                questions.append({
                    "question_number": q["number"],
                    "question_type": "qcm_abc",
                    "content": {
                        "stem": q["stem"],
                        "options": q["options"],
                        "stimulus_text": stimulus,
                    },
                    "correct_answer": {"answer": q["answer"]},
                    "points": 1,
                    "audio_file": None,
                })
    else:
        for q in teil_data.get("questions", []):
            questions.append({
                "question_number": q["number"],
                "question_type": "qcm_abc",
                "content": {
                    "stem": q["stem"],
                    "options": q["options"],
                },
                "correct_answer": {"answer": q["answer"]},
                "points": 1,
                "audio_file": None,
            })
    return questions


def parse_matching(teil_data: dict) -> list[dict]:
    anzeigen = teil_data.get("anzeigen", {})
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "matching",
            "content": {
                "situation": q["situation"],
                "anzeigen": anzeigen,
            },
            "correct_answer": {"answer": q["answer"]},
            "points": 1,
            "audio_file": None,
        })
    return questions


def parse_mixed_richtig_falsch_qcm(teil_data: dict) -> list[dict]:
    """Goethe Hören Teil 1 — mix richtig_falsch + qcm par audio."""
    questions = []
    for audio in teil_data.get("audios", []):
        audio_file = audio.get("audio_file", "")
        if audio_file:
            audio_file = audio_file.replace("\\", "/")
        transcription = audio.get("transcription", "")
        audio_type = audio.get("audio_type", "")

        for q in audio.get("questions", []):
            q_type = q.get("type", "richtig_falsch")
            content: dict = {
                "audio_type": audio_type,
                "transcription": transcription,
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
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "zuordnung_speaker",
            "content": {
                "statement": q["statement"],
                "speakers": speakers,
            },
            "correct_answer": {"answer": q["answer"]},
            "points": 1,
            "audio_file": None,
        })
    return questions


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
            # TELC : stimulus email reçu
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
    content: dict = {
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
        "correct_answer": {
            "scoring_criteria": teil_data.get("scoring_criteria", {})
        },
        "points": teil_data.get("max_score", 32),
        "audio_file": None,
    }]


# ─────────────────────────────────────────────
# Nouveaux parsers TELC
# ─────────────────────────────────────────────

def parse_zuordnung_titre(teil_data: dict) -> list[dict]:
    """
    TELC Lesen Teil 1 — Globalverstehen.
    5 textes, 10 titres (a-j), associer chaque texte au bon titre.
    """
    titres = teil_data.get("titres", {})
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "zuordnung_titre",
            "content": {
                "stimulus_text": q["stimulus_text"],
                "titres": titres,
            },
            "correct_answer": {"answer": q["answer"]},
            "points": 5,
            "audio_file": None,
        })
    return questions


def parse_selektives_matching(teil_data: dict) -> list[dict]:
    """
    TELC Lesen Teil 3 — Selektives Verstehen.
    10 situations, 12 annonces (a-l), réponse possible = lettre ou "x".
    """
    anzeigen = teil_data.get("anzeigen", {})
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "selektives_matching",
            "content": {
                "situation": q["situation"],
                "anzeigen": anzeigen,
            },
            "correct_answer": {"answer": q["answer"]},
            "points": 1,
            "audio_file": None,
        })
    return questions


def parse_qcm_gap_fill(teil_data: dict) -> list[dict]:
    """
    TELC Sprachbausteine Teil 1 — Grammatik.
    Texte à trous, QCM a/b/c pour chaque lacune.
    """
    text_with_gaps = teil_data.get("text_with_gaps", "")
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "qcm_gap_fill",
            "content": {
                "text_with_gaps": text_with_gaps,
                "gap_number": q["number"],
                "options": q["options"],
            },
            "correct_answer": {"answer": q["answer"]},
            "points": 1,
            "audio_file": None,
        })
    return questions


def parse_word_bank_gap_fill(teil_data: dict) -> list[dict]:
    """
    TELC Sprachbausteine Teil 2 — Lexik.
    Texte à trous + liste de 15 mots (a-o), choisir les 10 corrects.
    """
    text_with_gaps = teil_data.get("text_with_gaps", "")
    word_bank = teil_data.get("word_bank", {})
    questions = []
    for q in teil_data.get("questions", []):
        questions.append({
            "question_number": q["number"],
            "question_type": "word_bank_gap_fill",
            "content": {
                "text_with_gaps": text_with_gaps,
                "gap_number": q["number"],
                "word_bank": word_bank,
            },
            "correct_answer": {"answer": q["answer"]},
            "points": 1,
            "audio_file": None,
        })
    return questions


def parse_oral_kennenlernen(teil_data: dict) -> list[dict]:
    """
    TELC Sprechen Teil 1 — Einander kennenlernen.
    Liste de topics de conversation, pas de planification.
    """
    return [{
        "question_number": 1,
        "question_type": "oral_kennenlernen",
        "content": {
            "topics": teil_data.get("topics", []),
            "instructions": teil_data.get("instructions", ""),
        },
        "correct_answer": {
            "scoring_criteria": teil_data.get("scoring_criteria", {})
        },
        "points": teil_data.get("max_score", 15),
        "audio_file": None,
    }]


def parse_oral_thema(teil_data: dict) -> list[dict]:
    """
    TELC Sprechen Teil 2 — Über ein Thema sprechen.
    2 opinions contraires sur un thème, discussion.
    """
    return [{
        "question_number": 1,
        "question_type": "oral_thema",
        "content": {
            "topic": teil_data.get("topic", ""),
            "opinion_a": teil_data.get("opinion_a", {}),
            "opinion_b": teil_data.get("opinion_b", {}),
            "instructions": teil_data.get("instructions", ""),
        },
        "correct_answer": {
            "scoring_criteria": teil_data.get("scoring_criteria", {})
        },
        "points": teil_data.get("max_score", 30),
        "audio_file": None,
    }]


# ─────────────────────────────────────────────
# Dispatch parsers — Goethe + TELC
# ─────────────────────────────────────────────

PARSERS = {
    # Goethe-ÖSD
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

    # TELC uniquement
    "zuordnung_titre":          parse_zuordnung_titre,
    "selektives_matching":      parse_selektives_matching,
    "qcm_gap_fill":             parse_qcm_gap_fill,
    "word_bank_gap_fill":       parse_word_bank_gap_fill,
    "oral_kennenlernen":        parse_oral_kennenlernen,
    "oral_thema":               parse_oral_thema,
}


# ─────────────────────────────────────────────
# Config Teil (JSONB)
# ─────────────────────────────────────────────

def build_teil_config(teil_data: dict, format_type: str) -> dict | None:
    config = {}

    # Goethe
    if format_type == "richtig_falsch":
        if "stimulus_text" in teil_data:
            config["stimulus_text"] = teil_data["stimulus_text"]
        if "context" in teil_data:
            config["context"] = teil_data["context"]
            config["transcription"] = teil_data.get("transcription", "")
            config["audio_file"] = teil_data.get("audio_file", "")
        # TELC : max_plays
        if "max_plays" in teil_data:
            config["max_plays"] = teil_data["max_plays"]

    if format_type == "ja_nein":
        config["topic"] = teil_data.get("topic", "")

    if format_type == "matching":
        config["anzeigen"] = teil_data.get("anzeigen", {})

    if format_type == "zuordnung_speaker":
        config["speakers"] = teil_data.get("speakers", {})
        config["transcription"] = teil_data.get("transcription", "")

    if format_type == "qcm_abc":
        if "stimulus_text" in teil_data:
            config["stimulus_text"] = teil_data["stimulus_text"]
        if "context" in teil_data:
            config["context"] = teil_data["context"]
            config["transcription"] = teil_data.get("transcription", "")
            config["audio_file"] = teil_data.get("audio_file", "")
        if "max_plays" in teil_data:
            config["max_plays"] = teil_data["max_plays"]

    # TELC
    if format_type == "zuordnung_titre":
        config["titres"] = teil_data.get("titres", {})

    if format_type == "selektives_matching":
        config["anzeigen"] = teil_data.get("anzeigen", {})
        config["context"] = teil_data.get("context", "")

    if format_type == "qcm_gap_fill":
        config["text_with_gaps"] = teil_data.get("text_with_gaps", "")

    if format_type == "word_bank_gap_fill":
        config["text_with_gaps"] = teil_data.get("text_with_gaps", "")
        config["word_bank"] = teil_data.get("word_bank", {})

    if format_type == "oral_kennenlernen":
        config["topics"] = teil_data.get("topics", [])

    if format_type == "oral_thema":
        config["topic"] = teil_data.get("topic", "")
        config["opinion_a"] = teil_data.get("opinion_a", {})
        config["opinion_b"] = teil_data.get("opinion_b", {})

    # Hören TELC multi-audios (richtig_falsch avec audios[])
    if format_type == "richtig_falsch" and "audios" in teil_data:
        config["max_plays"] = teil_data.get("max_plays", 2)

    return config or None


# ─────────────────────────────────────────────
# Import principal
# ─────────────────────────────────────────────

async def import_exam(json_path: str, replace: bool = False) -> None:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    async with AsyncSessionLocal() as db:

        # ── 1. Exam ──────────────────────────────────────
        slug = data["slug"]
        result = await db.execute(select(Exam).where(Exam.slug == slug))
        exam = result.scalar_one_or_none()

        if exam:
            print(f"⚠️  Exam '{slug}' existe déjà (id={exam.id}) — on continue.")
        else:
            exam = Exam(
                name=data["name"],
                slug=slug,
                provider=_extract_provider(data),
                description=None,
                is_active=True,
            )
            db.add(exam)
            await db.flush()
            print(f"✅ Exam créé : {exam.name} (id={exam.id})")

        # ── 2. Level ─────────────────────────────────────
        cefr_code = data.get("cefr_code", "B1")
        result = await db.execute(
            select(Level).where(
                Level.exam_id == exam.id,
                Level.cefr_code == cefr_code,
            )
        )
        level = result.scalar_one_or_none()

        if level:
            print(f"⚠️  Level '{cefr_code}' existe déjà — on continue.")
        else:
            level = Level(
                exam_id=exam.id,
                cefr_code=cefr_code,
                total_pass_score=data.get("pass_threshold", 60),
                scoring_notes=data.get("scoring_model", ""),
                display_order=0,
                is_free=False,
                exam_config={
                    "scoring_model": data.get("scoring_model"),
                    "pass_threshold": data.get("pass_threshold"),
                },
            )
            db.add(level)
            await db.flush()
            print(f"✅ Level créé : {cefr_code} (id={level.id})")

        # ── 3. Subject ───────────────────────────────────
        result = await db.execute(
            select(func.count()).select_from(Subject).where(Subject.level_id == level.id)
        )
        subject_count = result.scalar() or 0
        next_number = subject_count + 1

        subject = Subject(
            level_id=level.id,
            subject_number=next_number,
            name=f"Sujet {next_number}",
            is_active=True,
        )
        db.add(subject)
        await db.flush()
        print(f"✅ Subject créé : Sujet {next_number} (id={subject.id})")

        # ── 4. Modules → Teile → Questions ───────────────
        total_questions = 0

        for order, module_data in enumerate(data.get("modules", [])):
            module_slug = module_data["slug"]

            module = Module(
                subject_id=subject.id,
                slug=module_slug,
                name=module_data["name"],
                time_limit_minutes=module_data.get("time_limit_minutes", 60),
                max_score=module_data.get("max_score", 100),
                display_order=order,
            )
            db.add(module)
            await db.flush()
            print(f"  ✅ Module : {module.name} (id={module.id})")


            for teil_data in module_data.get("teile", []):
                teil_number = teil_data["teil_number"]
                format_type = teil_data.get("format_type", "")

                result = await db.execute(
                    select(Teil).where(
                        Teil.module_id == module.id,
                        Teil.teil_number == teil_number,
                    )
                )
                teil = result.scalar_one_or_none()

                if teil and not replace:
                    print(f"    ⚠️  Teil {teil_number} existe déjà — ignoré (--replace pour forcer).")
                    continue

                if teil and replace:
                    from sqlalchemy import delete
                    await db.execute(
                        delete(Question).where(Question.teil_id == teil.id)
                    )
                    print(f"    🔄 Teil {teil_number} — questions supprimées.")
                else:
                    teil_config = build_teil_config(teil_data, format_type)
                    teil = Teil(
                        module_id=module.id,
                        teil_number=teil_number,
                        format_type=format_type,
                        instructions=teil_data.get("instructions"),
                        max_score=teil_data.get("max_score", 0),
                        time_minutes=teil_data.get("time_minutes"),
                        config=teil_config,
                    )
                    db.add(teil)
                    await db.flush()
                    print(f"    ✅ Teil {teil_number} ({format_type})")

                parser = PARSERS.get(format_type)
                if not parser:
                    print(f"    ❌ format_type '{format_type}' non supporté — ignoré.")
                    continue

                questions_data = parser(teil_data)
                instances = [
                    Question(teil_id=teil.id, **q)
                    for q in questions_data
                ]
                db.add_all(instances)
                total_questions += len(instances)
                print(f"       → {len(instances)} question(s)")

        await db.commit()
        print(f"\n🎉 Import terminé — {total_questions} questions insérées.")
        print(f"   Exam ID  : {exam.id}")
        print(f"   Level ID : {level.id}")
        print(f"\n   Accorder l'accès :")
        print(f"   POST /api/v1/access/admin/grant?user_id=<uid>&exam_id={exam.id}")


def _extract_provider(data: dict) -> str:
    name = data.get("name", "").lower()
    provider = data.get("provider", "").lower()

    if "telc" in name or "telc" in provider:
        return "TELC"
    if "goethe" in name:
        return "Goethe"
    if "ösd" in name or "osd" in name:
        return "ÖSD"
    return "Unknown"


# ─────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/import_exam.py <path/to/exam.json> [--replace]")
        sys.exit(1)

    json_path = sys.argv[1]
    replace = "--replace" in sys.argv

    if not Path(json_path).exists():
        print(f"❌ Fichier introuvable : {json_path}")
        sys.exit(1)

    asyncio.run(import_exam(json_path, replace=replace))