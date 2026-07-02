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
    r'^(?P<module>[a-z]+)_teil(?P<teil>\d+)(?:_(?P<key>[a-z0-9_]+))?\.(?P<ext>[a-z0-9]+)$',
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
        teil_id: uuid.UUID | None = None,
    ) -> dict:
        results = {"updated": 0, "not_found": [], "errors": []}

        subject = await self._find_subject(exam_id, subject_number)
        if not subject:
            return {"error": f"Sujet {subject_number} introuvable"}

        forced_teil = None
        forced_module = None
        if teil_id:
            forced_teil = await self.db.get(Teil, teil_id)
            if not forced_teil:
                return {"error": f"Teil {teil_id} introuvable"}
            forced_module = await self.db.get(Module, forced_teil.module_id)
            if not forced_module:
                return {"error": f"Module introuvable pour le Teil {teil_id}"}

        save_dir = STORAGE_ROOT / "exams" / str(exam_id) / "subjects" / str(subject.id)
        save_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            filename = file.filename or ""

            parts = filename.rsplit('.', 2)
            if len(parts) == 3:
                ext1, ext2 = parts[1].lower(), parts[2].lower()
                if ext1 in IMAGE_EXTENSIONS and ext2 in IMAGE_EXTENSIONS:
                    filename = f"{parts[0]}.{ext1}"

            match = PATTERN.match(filename)
            if not match:
                results["not_found"].append(f"{filename} — nom invalide")
                continue

            ext = match.group("ext").lower()
            if ext not in IMAGE_EXTENSIONS:
                results["not_found"].append(f"{filename} — extension non supportée ({ext})")
                continue

            key = (match.group("key") or "image").lower()

            if forced_teil:
                teil = forced_teil
                module_slug = forced_module.slug.lower()
                teil_number = forced_teil.teil_number
            else:
                module_slug = match.group("module").lower()
                teil_number = int(match.group("teil"))
                teil = await self._find_teil(subject.id, module_slug, teil_number)
                if not teil:
                    results["not_found"].append(f"{filename} — Teil {teil_number} ({module_slug}) introuvable")
                    continue

            dest_filename = f"{module_slug}_teil{teil_number}_{key}.{ext}"
            dest_path = save_dir / dest_filename
            file.file.seek(0)
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            relative_path = f"exams/{exam_id}/subjects/{subject.id}/{dest_filename}"

            config = dict(teil.config or {})
            config = self._set_image_in_config(config, key, relative_path)
            teil.config = config
            flag_modified(teil, "config")

            results["updated"] += 1

        await self.db.commit()
        results["log"] = (
            [f"✅ {results['updated']} image(s) associée(s)"] +
            [f"⚠️ {n}" for n in results["not_found"]]
        )
        return results

    def _set_image_in_config(self, config: dict, key: str, path: str) -> dict:
        audio_match = re.match(r'^audio(\d+)$', key)
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
        elif audio_match:
            num = audio_match.group(1)
            if "audio_images" not in config:
                config["audio_images"] = {}
            config["audio_images"][num] = path
        
        elif key.startswith("anzeige_"):
            letter = key.split("_", 1)[1]
            if "anzeigen" not in config:
                config["anzeigen"] = {}
            existing = config["anzeigen"].get(letter)
            if isinstance(existing, str):
                # texte déjà présent en string simple → on le convertit en objet
                config["anzeigen"][letter] = {"text": existing, "image": path}
            elif isinstance(existing, dict):
                config["anzeigen"][letter]["image"] = path
            else:
                config["anzeigen"][letter] = {"image": path}
                
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