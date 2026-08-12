"""
app/modules/start_deutsch/import_service.py
"""
import json
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
from app.shared.exceptions.http import BadRequestException, NotFoundException

STORAGE_ROOT = Path("storage/start-deutsch")


class StartDeutschImportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Import JSON ──────────────────────────────────────

    async def import_from_json(self, json_bytes: bytes, replace: bool = False) -> dict:
        try:
            data = json.loads(json_bytes.decode("utf-8"))
        except Exception:
            raise BadRequestException(detail="Fichier JSON invalide.")

        level = data.get("level")
        if level not in ("A1", "A2"):
            raise BadRequestException(detail="Le JSON doit contenir 'level': 'A1' ou 'A2'.")

        total_questions = 0
        log = []

        # 1. Subject — TOUJOURS un nouveau, numéroté (comme "Sujet 1", "Sujet 2"
        # pour B1/B2). Avant ce fix, on cherchait "le" sujet du niveau et on
        # fusionnait dedans — ce qui plafonnait à UN SEUL sujet par niveau au
        # total, et faisait ignorer silencieusement tout import suivant
        # (chaque Teil "existait déjà"). `replace` n'a donc plus lieu d'être
        # ici : un import = un sujet neuf, jamais de fusion. Gardé au niveau
        # du endpoint pour compatibilité, mais ignoré côté service.
        result = await self.db.execute(
            select(func.max(StartDeutschSubject.subject_number)).where(StartDeutschSubject.level == level)
        )
        next_number = (result.scalar() or 0) + 1

        base_title = data.get("title", f"Start Deutsch {level}")
        subject = StartDeutschSubject(
            level=level,
            subject_number=next_number,
            title=f"{base_title} — Sujet {next_number}",
            description=data.get("description"),
            is_active=True,
        )
        self.db.add(subject)
        await self.db.flush()
        log.append(f"✅ Subject créé : {subject.title} (subject_number={next_number})")

        # 2. Modules → Teile → Questions (toujours neufs, pas de vérification
        # d'existence nécessaire puisque le Subject est garanti nouveau)
        for order, module_data in enumerate(data.get("modules", [])):
            module_slug = module_data["slug"]

            module = StartDeutschModule(
                subject_id=subject.id,
                slug=module_slug,
                order=order,
                max_score=module_data.get("max_score", 25),
            )
            self.db.add(module)
            await self.db.flush()
            log.append(f"  ✅ Module : {module_slug}")

            for teil_data in module_data.get("teile", []):
                teil_number = teil_data["teil_number"]
                format_type = teil_data.get("format_type", "")

                teil = StartDeutschTeil(
                    module_id=module.id,
                    teil_number=teil_number,
                    format_type=format_type,
                    instructions=teil_data.get("instructions"),
                    max_score=teil_data.get("max_score", 5),
                    shared_content=build_teil_shared_content(teil_data, format_type),
                )
                self.db.add(teil)
                await self.db.flush()

                parser = PARSERS.get(format_type)
                if not parser:
                    log.append(f"    ❌ format_type '{format_type}' non supporté.")
                    continue

                questions_data = parser(teil_data)
                if questions_data:
                    instances = [StartDeutschQuestion(teil_id=teil.id, **q) for q in questions_data]
                    self.db.add_all(instances)
                    total_questions += len(instances)
                    log.append(f"    ✅ Teil {teil_number} ({format_type}) — {len(instances)} question(s)")

        await self.db.commit()

        return {
            "success": True,
            "subject_id": str(subject.id),
            "subject_number": next_number,
            "level": level,
            "total_questions": total_questions,
            "log": log,
        }

    # ── Import Audio ──────────────────────────────────────

    async def import_audio_files(self, subject_id, files: list[UploadFile]) -> dict:
        """
        Convention de nommage : hoeren_teil1.mp3, hoeren_teil2.mp3...
        Un seul fichier audio par Teil (jamais par question).

        ⚠️ Ciblé par subject_id (pas juste "level") depuis qu'il peut exister
        plusieurs sujets par niveau — sinon le Teil1 du Sujet 1 et le Teil1
        du Sujet 2 (même niveau) pointeraient vers le MÊME fichier physique
        (collision de nom hoeren_teil1.mp3). Le chemin de stockage inclut
        donc le numéro de sujet : <level>/subject<N>/hoeren/<filename>.
        """
        subject = await self.db.get(StartDeutschSubject, subject_id)
        if not subject:
            raise NotFoundException(detail=f"Subject Start Deutsch '{subject_id}' introuvable.")

        result = await self.db.execute(
            select(StartDeutschModule).where(
                StartDeutschModule.subject_id == subject.id,
                StartDeutschModule.slug == "hoeren",
            )
        )
        hoeren_module = result.scalar_one_or_none()
        if not hoeren_module:
            raise NotFoundException(detail=f"Module Hören introuvable pour ce sujet.")

        subject_folder = f"{subject.level.lower()}/subject{subject.subject_number}"
        storage_dir = STORAGE_ROOT / subject_folder / "hoeren"
        storage_dir.mkdir(parents=True, exist_ok=True)

        updated, skipped, log = 0, 0, []

        for upload in files:
            filename = upload.filename or ""
            if not filename.lower().endswith(".mp3"):
                log.append(f"⚠️ {filename} — pas un MP3, ignoré.")
                skipped += 1
                continue

            base = Path(filename).stem  # ex: hoeren_teil1
            try:
                teil_part = next(p for p in base.split("_") if p.startswith("teil"))
                teil_number = int(teil_part.replace("teil", ""))
            except (StopIteration, ValueError):
                log.append(f"⚠️ {filename} — nom non reconnu (attendu hoeren_teilN.mp3), ignoré.")
                skipped += 1
                continue

            result = await self.db.execute(
                select(StartDeutschTeil).where(
                    StartDeutschTeil.module_id == hoeren_module.id,
                    StartDeutschTeil.teil_number == teil_number,
                )
            )
            teil = result.scalar_one_or_none()
            if not teil:
                log.append(f"⚠️ {filename} — Teil {teil_number} introuvable.")
                skipped += 1
                continue

            dest_path = storage_dir / filename
            content = await upload.read()
            dest_path.write_bytes(content)

            teil.audio_file = f"{subject_folder}/hoeren/{filename}"
            updated += 1
            log.append(f"✅ {filename} → Teil {teil_number}")

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

    # ── Import Images ─────────────────────────────────────

    async def import_images(self, subject_id, files: list[UploadFile]) -> dict:
        """
        Dépôt simple : les fichiers sont copiés tels quels sous
        storage/start-deutsch/<level>/subject<N>/images/. Aucune mise à jour
        de DB — le JSON importé doit déjà référencer le bon nom de fichier
        dans content.options[].image_file / shared_content.images[].image_file
        / cards[].image_file. Ciblé par subject_id pour la même raison que
        import_audio_files (éviter les collisions entre sujets du même niveau).
        """
        subject = await self.db.get(StartDeutschSubject, subject_id)
        if not subject:
            raise NotFoundException(detail=f"Subject Start Deutsch '{subject_id}' introuvable.")

        subject_folder = f"{subject.level.lower()}/subject{subject.subject_number}"
        storage_dir = STORAGE_ROOT / subject_folder / "images"
        storage_dir.mkdir(parents=True, exist_ok=True)

        saved, log = 0, []
        for upload in files:
            filename = upload.filename or ""
            ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
            if ext not in ("png", "jpg", "jpeg", "webp"):
                log.append(f"⚠️ {filename} — extension non supportée, ignoré.")
                continue

            dest_path = storage_dir / filename
            content = await upload.read()
            dest_path.write_bytes(content)
            saved += 1
            log.append(f"✅ {filename} déposé.")

        return {
            "success": True,
            "subject_id": str(subject.id),
            "subject_number": subject.subject_number,
            "level": subject.level,
            "files_saved": saved,
            "log": log,
        }