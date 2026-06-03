"""
app/modules/exams/image_import_service.py
"""
from __future__ import annotations
import re
import shutil
import uuid
import logging
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.modules.exams.models import Exam, Level, Subject, Module, Teil

logger = logging.getLogger(__name__)

STORAGE_ROOT = Path("storage/images")

# Accepte toutes les extensions image courantes
PATTERN = re.compile(
    r'^(?P<module>[a-z]+)_teil(?P<teil>\d+)_(?P<key>[a-z0-9_]+)\.(?P<ext>[a-z0-9]+)$',
    re.IGNORECASE
)

IMAGE_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'svg',
    'tiff', 'tif', 'avif', 'heic', 'heif',
}


class TeilImageImportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_teil_images(
        self,
        exam_id: uuid.UUID,
        files: list[UploadFile],
        subject_number: int,
    ) -> dict:
        results = {"updated": 0, "not_found": [], "errors": []}

        subject = await self._find_subject(exam_id, subject_number)
        if not subject:
            return {"error": f"Sujet {subject_number} introuvable"}

        logger.info(f"Subject trouvé: {subject.id} — sujet {subject_number}")

        save_dir = STORAGE_ROOT / "exams" / str(exam_id) / "subjects" / str(subject.id)
        save_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            filename = file.filename or ""
            logger.info(f"Traitement fichier: {filename}")
            
            parts = filename.rsplit('.', 2)
            if len(parts) == 3:
                # ex: lesen_teil1_person_a.png.jpg → garder lesen_teil1_person_a.png
                ext1 = parts[1].lower()
                ext2 = parts[2].lower()
                if ext1 in IMAGE_EXTENSIONS and ext2 in IMAGE_EXTENSIONS:
                    filename = f"{parts[0]}.{ext1}"
                    logger.info(f"Double extension nettoyée: {file.filename} → {filename}")

            match = PATTERN.match(filename)
    
            match = PATTERN.match(filename)
            if not match:
                logger.warning(f"Nom invalide: {filename}")
                results["not_found"].append(f"{filename} — nom invalide")
                continue

            ext = match.group("ext").lower()
            if ext not in IMAGE_EXTENSIONS:
                logger.warning(f"Extension non supportée: {ext}")
                results["not_found"].append(f"{filename} — extension non supportée ({ext})")
                continue

            module_slug = match.group("module").lower()
            teil_number = int(match.group("teil"))
            key         = match.group("key").lower()

            logger.info(f"  module={module_slug} teil={teil_number} key={key} ext={ext}")

            teil = await self._find_teil(subject.id, module_slug, teil_number)
            if not teil:
                logger.warning(f"Teil introuvable: {module_slug} teil {teil_number}")
                results["not_found"].append(f"{filename} — Teil {teil_number} ({module_slug}) introuvable")
                continue

            logger.info(f"  Teil trouvé: {teil.id}")

            # Sauvegarder le fichier
            dest_filename = f"{module_slug}_teil{teil_number}_{key}.{ext}"
            dest_path = save_dir / dest_filename
            file.file.seek(0)
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            relative_path = f"exams/{exam_id}/subjects/{subject.id}/{dest_filename}"
            logger.info(f"  Fichier sauvegardé: {relative_path}")

            # Mettre à jour le config
            config = dict(teil.config or {})
            config = self._set_image_in_config(config, key, relative_path)

            # ← flag_modified obligatoire pour JSONB
            teil.config = config
            flag_modified(teil, "config")

            results["updated"] += 1
            logger.info(f"  Config mis à jour ✓")

        await self.db.commit()
        logger.info(f"Commit OK — {results['updated']} image(s) associée(s)")

        results["log"] = (
            [f"✅ {results['updated']} image(s) associée(s)"] +
            [f"⚠️ {n}" for n in results["not_found"]] +
            [f"❌ {e}" for e in results["errors"]]
        )
        return results

    def _set_image_in_config(self, config: dict, key: str, path: str) -> dict:
        if key.startswith("person_"):
            letter = key.split("_", 1)[1]
            if "persons" not in config:
                config["persons"] = {}
            if letter not in config["persons"]:
                config["persons"][letter] = {}
            config["persons"][letter]["image"] = path

        elif key.startswith("speaker_"):
            letter = key.split("_", 1)[1]
            if "speakers" not in config:
                config["speakers"] = {}
            existing = config["speakers"].get(letter)
            if isinstance(existing, str):
                config["speakers"][letter] = {"name": existing, "image": path}
            elif isinstance(existing, dict):
                config["speakers"][letter]["image"] = path
            else:
                config["speakers"][letter] = {"image": path}

        elif key == "article":
            config["article_image"] = path
            
        elif key == "stimulus":
            config["stimulus_image"] = path

        elif key == "topic":
            config["topic_image"] = path

        elif key == "image":
            config["image"] = path

        else:
            # Clé générique — on la stocke directement
            config[f"{key}_image"] = path

        return config

    async def _find_subject(self, exam_id: uuid.UUID, subject_number: int) -> Subject | None:
        result = await self.db.execute(
            select(Subject)
            .join(Level, Level.id == Subject.level_id)
            .where(
                Level.exam_id == exam_id,
                Subject.subject_number == subject_number,
            )
        )
        return result.scalar_one_or_none()

    async def _find_teil(
        self,
        subject_id: uuid.UUID,
        module_slug: str,
        teil_number: int,
    ) -> Teil | None:
        result = await self.db.execute(
            select(Teil)
            .join(Module, Module.id == Teil.module_id)
            .where(
                Module.subject_id == subject_id,
                Module.slug.ilike(f"%{module_slug}%"),
                Teil.teil_number == teil_number,
            )
        )
        return result.scalar_one_or_none()