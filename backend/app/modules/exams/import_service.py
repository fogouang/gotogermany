"""
app/modules/exams/import_service.py
"""
import json
import io
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.modules.questions.models import Question
from app.shared.exceptions.http import BadRequestException, NotFoundException


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


def _build_teil_config(teil_data: dict, format_type: str) -> dict | None:
    config = {}
    if format_type == "richtig_falsch":
        if "stimulus_text" in teil_data:
            config["stimulus_text"] = teil_data["stimulus_text"]
        if "context" in teil_data:
            config["context"] = teil_data["context"]
            config["transcription"] = teil_data.get("transcription", "")
            config["audio_file"] = teil_data.get("audio_file", "")
        if "max_plays" in teil_data:
            config["max_plays"] = teil_data["max_plays"]
        if "audios" in teil_data:
            config["max_plays"] = teil_data.get("max_plays", 2)
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
    return config or None


class ExamImportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Import JSON ──────────────────────────────────────

    async def import_from_json(
        self,
        json_bytes: bytes,
        replace: bool = False,
    ) -> dict:
        try:
            data = json.loads(json_bytes.decode("utf-8"))
        except Exception:
            raise BadRequestException(detail="Fichier JSON invalide.")

        slug = data.get("slug")
        if not slug:
            raise BadRequestException(detail="Le JSON doit contenir un champ 'slug'.")

        total_questions = 0
        log = []

        # 1. Exam
        result = await self.db.execute(select(Exam).where(Exam.slug == slug))
        exam = result.scalar_one_or_none()
        if exam:
            log.append(f"⚠️ Exam '{slug}' existe déjà.")
        else:
            exam = Exam(
                name=data["name"],
                slug=slug,
                provider=_extract_provider(data),
                description=None,
                is_active=True,
            )
            self.db.add(exam)
            await self.db.flush()
            log.append(f"✅ Exam créé : {exam.name}")

        # 2. Level
        cefr_code = data.get("cefr_code", "B1")
        result = await self.db.execute(
            select(Level).where(
                Level.exam_id == exam.id,
                Level.cefr_code == cefr_code,
            )
        )
        level = result.scalar_one_or_none()
        if level:
            log.append(f"⚠️ Level '{cefr_code}' existe déjà.")
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
            self.db.add(level)
            await self.db.flush()
            log.append(f"✅ Level créé : {cefr_code}")

        # 3. Subject
        result = await self.db.execute(
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
        self.db.add(subject)
        await self.db.flush()
        log.append(f"✅ Subject créé : Sujet {next_number}")

        # 4. Modules → Teile → Questions
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
            self.db.add(module)
            await self.db.flush()
            log.append(f"  ✅ Module : {module.name}")

            for teil_data in module_data.get("teile", []):
                teil_number = teil_data["teil_number"]
                format_type = teil_data.get("format_type", "")

                result = await self.db.execute(
                    select(Teil).where(
                        Teil.module_id == module.id,
                        Teil.teil_number == teil_number,
                    )
                )
                teil = result.scalar_one_or_none()

                if teil and replace:
                    await self.db.execute(
                        delete(Question).where(Question.teil_id == teil.id)
                    )
                elif teil:
                    log.append(f"    ⚠️ Teil {teil_number} existe — ignoré.")
                    continue
                else:
                    teil_config = _build_teil_config(teil_data, format_type)
                    teil = Teil(
                        module_id=module.id,
                        teil_number=teil_number,
                        format_type=format_type,
                        instructions=teil_data.get("instructions"),
                        max_score=teil_data.get("max_score", 0),
                        time_minutes=teil_data.get("time_minutes"),
                        config=teil_config,
                    )
                    self.db.add(teil)
                    await self.db.flush()

                from app.modules.exams.import_parsers import PARSERS
                parser = PARSERS.get(format_type)
                if not parser:
                    log.append(f"    ❌ format '{format_type}' non supporté.")
                    continue

                questions_data = parser(teil_data)
                if questions_data:
                    instances = [Question(teil_id=teil.id, **q) for q in questions_data]
                    self.db.add_all(instances)
                    total_questions += len(instances)
                    log.append(f"    ✅ Teil {teil_number} ({format_type}) — {len(instances)} questions")

        await self.db.commit()

        return {
            "success": True,
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "subject_id": str(subject.id),
            "subject_number": next_number,
            "total_questions": total_questions,
            "log": log,
        }

    # ── Import Audio (multi-fichiers) ────────────────────

    async def import_audio_files(
        self,
        exam_id: UUID,
        files: list[UploadFile],
        subject_number: int,
    ) -> dict:
        """
        Reçoit plusieurs fichiers MP3 et les associe aux questions.

        Convention de nommage (générée par generate_telc_b1.py) :
          horen_teil1_audio1.mp3  → Hören, Teil 1, audio_number 1
          horen_teil1_audio2.mp3  → Hören, Teil 1, audio_number 2
          horen_teil2.mp3         → Hören, Teil 2 (1 seul audio long)
          horen_teil3_audio1.mp3  → Hören, Teil 3, audio_number 1
        """
        # Vérifier exam
        result = await self.db.execute(select(Exam).where(Exam.id == exam_id))
        exam = result.scalar_one_or_none()
        if not exam:
            raise NotFoundException(resource="Exam", identifier=str(exam_id))

        # Trouver le subject
        result = await self.db.execute(
            select(Subject)
            .join(Level, Level.id == Subject.level_id)
            .where(
                Level.exam_id == exam_id,
                Subject.subject_number == subject_number,
            )
        )
        subject = result.scalar_one_or_none()
        if not subject:
            raise NotFoundException(
                resource="Subject",
                identifier=f"Sujet {subject_number} de l'exam {exam_id}"
            )

        # Dossier de destination
        storage_dir = Path(f"storage/audio/exams/{exam_id}/subjects/{subject.id}")
        storage_dir.mkdir(parents=True, exist_ok=True)

        updated = 0
        skipped = 0
        log = []

        # Trouver le module Hören une seule fois
        result = await self.db.execute(
            select(Module).where(
                Module.subject_id == subject.id,
                Module.slug.ilike("%horen%"),
            )
        )
        horen_module = result.scalar_one_or_none()
        if not horen_module:
            raise NotFoundException(
                resource="Module Hören",
                identifier=f"Sujet {subject_number}"
            )

        for upload in files:
            filename = upload.filename or ""
            if not filename.lower().endswith(".mp3"):
                log.append(f"⚠️ {filename} — pas un MP3, ignoré.")
                skipped += 1
                continue

            base = Path(filename).stem  # ex: horen_teil1_audio1
            parts = base.split("_")

            # Extraire teil_number
            try:
                teil_part = next(p for p in parts if p.startswith("teil"))
                teil_number = int(teil_part.replace("teil", ""))
            except (StopIteration, ValueError):
                log.append(f"⚠️ {filename} — nom non reconnu (attendu: horen_teilN_audioM.mp3), ignoré.")
                skipped += 1
                continue

            # Extraire audio_number (optionnel)
            audio_number = None
            for p in parts:
                if p.startswith("audio"):
                    try:
                        audio_number = int(p.replace("audio", ""))
                    except ValueError:
                        pass
                    break

            # Trouver le Teil
            result = await self.db.execute(
                select(Teil).where(
                    Teil.module_id == horen_module.id,
                    Teil.teil_number == teil_number,
                )
            )
            teil = result.scalar_one_or_none()
            if not teil:
                log.append(f"⚠️ {filename} — Teil {teil_number} introuvable.")
                skipped += 1
                continue

            # Sauvegarder le fichier
            dest_path = storage_dir / filename
            content = await upload.read()
            dest_path.write_bytes(content)
            relative_path = f"exams/{exam_id}/subjects/{subject.id}/{filename}"

            # Mettre à jour les questions
            result = await self.db.execute(
                select(Question).where(Question.teil_id == teil.id)
            )
            questions = result.scalars().all()

            q_updated = 0
            if audio_number is not None:
                # Teil avec plusieurs audios — matcher par audio_number dans content
                for q in questions:
                    content_data = q.content or {}
                    if content_data.get("audio_number") == audio_number:
                        q.audio_file = relative_path
                        q_updated += 1
            else:
                # Teil avec 1 seul audio long — toutes les questions du teil
                for q in questions:
                    q.audio_file = relative_path
                    q_updated += 1
                # Mettre à jour aussi le config du Teil
                config = dict(teil.config or {})
                config["audio_file"] = relative_path
                teil.config = config

            updated += q_updated
            log.append(f"✅ {filename} → {q_updated} question(s) mises à jour")

        await self.db.commit()

        return {
            "success": True,
            "exam_id": str(exam_id),
            "subject_number": subject_number,
            "files_processed": len(files) - skipped,
            "files_skipped": skipped,
            "questions_updated": updated,
            "log": log,
        }