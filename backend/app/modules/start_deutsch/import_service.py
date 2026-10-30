"""
app/modules/start_deutsch/import_service.py

Import d'un sujet Start Deutsch (A1, A2) : JSON, audio du Hören, images.
"""
import json
import re
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.start_deutsch.import_parsers import PARSERS, build_teil_shared_content
from app.modules.start_deutsch.models import (
    StartDeutschModule,
    StartDeutschQuestion,
    StartDeutschSubject,
    StartDeutschTeil,
)
from app.modules.start_deutsch.repository import SubjectRepository
from app.shared.exceptions.http import BadRequestException, NotFoundException

STORAGE_ROOT = Path("storage/start-deutsch")
IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "webp")
AUDIO_NAME = re.compile(r"^hoeren_teil(\d+)\.mp3$", re.IGNORECASE)

MODULE_LABELS = {
    "lesen": "Lesen",
    "hoeren": "Hören",
    "schreiben": "Schreiben",
    "sprechen": "Sprechen",
}

FORMAT_LABELS = {
    "mc_text": "QCM",
    "mc_image": "QCM en images",
    "true_false": "Richtig / Falsch",
    "ja_nein": "Ja / Nein",
    "matching_2options": "Choix entre deux annonces",
    "matching_with_distractor": "Annonces à associer",
    "image_day_matching": "Images et jours",
    "form_fill": "Formulaire",
    "free_text": "Texte libre",
    "sprechen_group_intro": "Se présenter",
    "sprechen_group_word_card": "Cartes mots",
    "sprechen_group_image_card": "Cartes images",
    "sprechen_duo_question_card": "Cartes questions",
    "sprechen_duo_monologue_card": "Parler de soi",
    "sprechen_duo_negotiation": "Trouver un rendez-vous",
}


def _subject_folder(subject: StartDeutschSubject) -> str:
    """Dossier de stockage d'un sujet : <niveau>/subject<N>."""
    return f"{subject.level.lower()}/subject{subject.subject_number}"


def _teil_image_files(teil: StartDeutschTeil) -> list[str]:
    """Noms d'images attendus par un Teil, dans l'ordre du sujet."""
    names: list[str] = []
    for img in (teil.shared_content or {}).get("images") or []:
        if isinstance(img, dict) and img.get("image_file"):
            names.append(img["image_file"])
    for question in sorted(teil.questions, key=lambda q: q.question_number):
        content = question.content or {}
        for item in (content.get("options") or []) + (content.get("cards") or []):
            if isinstance(item, dict) and item.get("image_file"):
                names.append(item["image_file"])
        if question.image_file:
            names.append(question.image_file)
    return list(dict.fromkeys(names))


class StartDeutschImportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Import JSON ──────────────────────────────────────

    async def import_from_json(self, json_bytes: bytes) -> dict:
        try:
            data = json.loads(json_bytes.decode("utf-8"))
        except Exception:
            raise BadRequestException(detail="Fichier JSON invalide.")

        level = data.get("level")
        if level not in ("A1", "A2"):
            raise BadRequestException(detail="Le JSON doit contenir 'level': 'A1' ou 'A2'.")

        modules_data = data.get("modules") or []
        if not modules_data:
            raise BadRequestException(detail="Le JSON ne contient aucun module.")

        # Format inconnu : on refuse tout le fichier avant d'écrire en base
        unknown = [
            f"{module_data.get('slug')} Teil {teil_data.get('teil_number')} ({teil_data.get('format_type')})"
            for module_data in modules_data
            for teil_data in module_data.get("teile", [])
            if teil_data.get("format_type") not in PARSERS
        ]
        if unknown:
            raise BadRequestException(detail="Format non pris en charge : " + ", ".join(unknown))

        # Chaque import crée un nouveau sujet, numéroté à la suite de ceux du niveau
        result = await self.db.execute(
            select(func.max(StartDeutschSubject.subject_number)).where(StartDeutschSubject.level == level)
        )
        next_number = (result.scalar() or 0) + 1

        subject = StartDeutschSubject(
            level=level,
            subject_number=next_number,
            title=data.get("title") or f"Start Deutsch {level[-1]} · Sujet {next_number}",
            description=data.get("description"),
            is_active=True,
        )
        self.db.add(subject)
        await self.db.flush()

        log = [f"Sujet créé : {subject.title} (n°{next_number})"]
        teile_summary = []
        total_questions = 0

        for order, module_data in enumerate(modules_data):
            module_slug = module_data["slug"]
            module_label = MODULE_LABELS.get(module_slug, module_slug)

            module = StartDeutschModule(
                subject_id=subject.id,
                slug=module_slug,
                order=order,
                max_score=module_data.get("max_score", 25),
            )
            self.db.add(module)
            await self.db.flush()

            for teil_data in module_data.get("teile", []):
                teil_number = teil_data["teil_number"]
                format_type = teil_data["format_type"]

                shared_content = build_teil_shared_content(teil_data, format_type)
                # Hören : le texte est la transcription de l'audio, jamais montrée pendant l'épreuve
                if module_slug == "hoeren" and shared_content and "text" in shared_content:
                    shared_content = {"transcript": shared_content.pop("text")}

                teil = StartDeutschTeil(
                    module_id=module.id,
                    teil_number=teil_number,
                    format_type=format_type,
                    instructions=teil_data.get("instructions"),
                    max_score=teil_data.get("max_score", 5),
                    shared_content=shared_content,
                )
                self.db.add(teil)
                await self.db.flush()

                questions_data = PARSERS[format_type](teil_data)
                self.db.add_all(StartDeutschQuestion(teil_id=teil.id, **q) for q in questions_data)
                total_questions += len(questions_data)

                format_label = FORMAT_LABELS.get(format_type, format_type)
                log.append(
                    f"{module_label} Teil {teil_number} · {format_label} · {len(questions_data)} question(s)"
                )
                teile_summary.append({
                    "module": module_slug,
                    "teil_number": teil_number,
                    "format_type": format_type,
                    "questions": len(questions_data),
                })

        await self.db.commit()

        return {
            "success": True,
            "subject_id": str(subject.id),
            "subject_number": next_number,
            "title": subject.title,
            "level": level,
            "total_questions": total_questions,
            "teile": teile_summary,
            "log": log,
        }

    # ── Import audio ──────────────────────────────────────

    async def import_audio_files(self, subject_id, files: list[UploadFile]) -> dict:
        """Un fichier par Teil du Hören : hoeren_teil1.mp3, hoeren_teil2.mp3...
        Rangé dans <niveau>/subject<N>/hoeren/ pour que deux sujets du même
        niveau ne partagent jamais un fichier."""
        subject = await self.db.get(StartDeutschSubject, subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet Start Deutsch introuvable.")

        result = await self.db.execute(
            select(StartDeutschModule).where(
                StartDeutschModule.subject_id == subject.id,
                StartDeutschModule.slug == "hoeren",
            )
        )
        hoeren_module = result.scalar_one_or_none()
        if not hoeren_module:
            raise NotFoundException(detail="Ce sujet n'a pas de module Hören.")

        subject_folder = _subject_folder(subject)
        storage_dir = STORAGE_ROOT / subject_folder / "hoeren"
        storage_dir.mkdir(parents=True, exist_ok=True)

        updated, skipped, log = 0, 0, []

        for upload in files:
            filename = upload.filename or ""
            match = AUDIO_NAME.match(filename)
            if not match:
                log.append(f"{filename} ignoré : nom attendu hoeren_teilN.mp3")
                skipped += 1
                continue

            teil_number = int(match.group(1))
            result = await self.db.execute(
                select(StartDeutschTeil).where(
                    StartDeutschTeil.module_id == hoeren_module.id,
                    StartDeutschTeil.teil_number == teil_number,
                )
            )
            teil = result.scalar_one_or_none()
            if not teil:
                log.append(f"{filename} ignoré : le Hören n'a pas de Teil {teil_number}")
                skipped += 1
                continue

            filename = filename.lower()
            (storage_dir / filename).write_bytes(await upload.read())
            teil.audio_file = f"{subject_folder}/hoeren/{filename}"
            updated += 1
            log.append(f"{filename} associé au Teil {teil_number}")

        await self.db.commit()

        return {
            "success": True,
            "subject_id": str(subject.id),
            "subject_number": subject.subject_number,
            "level": subject.level,
            "files_processed": len(files) - skipped,
            "files_skipped": skipped,
            "teile_updated": updated,
            "log": log,
        }

    # ── Import images ─────────────────────────────────────

    async def import_images(self, subject_id, files: list[UploadFile]) -> dict:
        """Les images sont déposées dans <niveau>/subject<N>/images/ sous le nom
        exact cité par le JSON (image_file). Un fichier que le sujet ne cite
        pas est ignoré : il ne serait jamais affiché."""
        subject = await SubjectRepository(self.db).get_full_tree(subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet Start Deutsch introuvable.")

        expected = {
            name.lower(): name
            for module in subject.modules
            for teil in module.teile
            for name in _teil_image_files(teil)
        }

        storage_dir = STORAGE_ROOT / _subject_folder(subject) / "images"
        storage_dir.mkdir(parents=True, exist_ok=True)

        saved, skipped, log = 0, 0, []
        for upload in files:
            filename = upload.filename or ""
            ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
            if ext not in IMAGE_EXTENSIONS:
                log.append(f"{filename} ignoré : format non pris en charge")
                skipped += 1
                continue

            target = expected.get(filename.lower())
            if not target:
                log.append(f"{filename} ignoré : aucun image_file de ce nom dans le sujet")
                skipped += 1
                continue

            (storage_dir / target).write_bytes(await upload.read())
            saved += 1
            log.append(f"{target} déposé")

        return {
            "success": True,
            "subject_id": str(subject.id),
            "subject_number": subject.subject_number,
            "level": subject.level,
            "files_saved": saved,
            "files_skipped": skipped,
            "log": log,
        }

    # ── État des médias d'un sujet ────────────────────────

    async def media_status(self, subject_id) -> dict:
        """Fichiers audio et images attendus par le sujet, et ceux déjà présents."""
        subject = await SubjectRepository(self.db).get_full_tree(subject_id)
        if not subject:
            raise NotFoundException(detail="Sujet Start Deutsch introuvable.")

        images_dir = STORAGE_ROOT / _subject_folder(subject) / "images"
        audio, images = [], []

        for module in sorted(subject.modules, key=lambda m: m.order):
            for teil in sorted(module.teile, key=lambda t: t.teil_number):
                if module.slug == "hoeren":
                    audio.append({
                        "teil_number": teil.teil_number,
                        "filename": f"hoeren_teil{teil.teil_number}.mp3",
                        "imported": bool(teil.audio_file) and (STORAGE_ROOT / teil.audio_file).exists(),
                    })
                for name in _teil_image_files(teil):
                    images.append({
                        "filename": name,
                        "module": module.slug,
                        "teil_number": teil.teil_number,
                        "imported": (images_dir / name).exists(),
                    })

        return {"subject_id": str(subject.id), "audio": audio, "images": images}