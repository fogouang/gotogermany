"""
app/modules/exams/import_service.py

Import d'un sujet complet depuis un JSON généré par le pipeline.
Le JSON est validé ENTIÈREMENT avant toute écriture en base : un barème
incohérent (max_score manquant, somme des Teile différente du module,
format inconnu, Teil sans question) bloque l'import.
"""
import json
import re
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exams.import_parsers import PARSERS
from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.modules.questions.models import Question
from app.shared.exceptions.http import BadRequestException, NotFoundException


def _extract_provider(data: dict) -> str:
    mapping = {
        "telc": "TELC", "goethe": "Goethe", "ösd": "ÖSD", "osd": "ÖSD",
        "testdaf": "TestDaF", "ecl": "ECL",
    }
    provider = data.get("provider", "").lower().strip()
    if provider in mapping:
        return mapping[provider]

    name = data.get("name", "").lower()
    if "testdaf" in name:
        return "TestDaF"
    if re.search(r"\becl\b", name):
        return "ECL"
    if "telc" in name:
        return "TELC"
    if "ösd" in name or "osd" in name:
        return "ÖSD"
    if "goethe" in name:
        return "Goethe"
    return "Unknown"


def _normalize_slug(value: str) -> str:
    """'Hörverstehen' -> 'hoerverstehen', 'mündlicher ausdruck' -> 'muendlicher_ausdruck'."""
    s = (value or "").strip().lower()
    for src, dst in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(src, dst)
    s = re.sub(r"[\s\-]+", "_", s)
    return re.sub(r"[^a-z0-9_]", "", s)

# Variantes de format_type rencontrées dans les JSON du pipeline
FORMAT_ALIASES = {
    "zuordnung_paragrafen": "zuordnung_paragraphen",
}


def _normalize_format(value: str) -> str:
    """'lückentext_sätze' -> 'lueckentext_saetze', 'zuordnung_paragrafen' -> 'zuordnung_paragraphen'."""
    fmt = _normalize_slug(value)
    return FORMAT_ALIASES.get(fmt, fmt)


# Champs de contexte d'un Teil gardés tels quels dans Teil.config (affichage).
# Jamais de solution ici : config est envoyé à l'apprenant.
TEIL_DISPLAY_KEYS = (
    "name", "topic", "thema", "situation", "article_title", "document_type",
    "person", "speaker", "radio_name", "institution", "fragestellung",
    "stimulus_anzeige", "speakers", "beispiel", "hinweis", "wortschatz_thema",
    "reading_time_seconds", "reading_time_announcement", "preparation_minutes",
)

# scoring_model par défaut quand le JSON n'en fournit pas
DEFAULT_SCORING_MODEL = {
    "TELC": "per_module_weighted",
}

# Règles de réussite par défaut, écrites dans Level.exam_config à l'import
DEFAULT_PASS_RULES = {
    "ECL": {"pass_rule": "each_module", "module_min": 60},
    # Seuils indicatifs en % (les seuils officiels varient selon la session)
    "TestDaF": {"pass_rule": "tdn_levels", "tdn_thresholds": {"5": 78, "4": 63, "3": 45}},
}

# Teile notés en nombre d'items, module ramené à 100 (ex. Goethe : 30 items -> 100)
SCALED_PROVIDERS = {"Goethe"}

# Somme des max_score des Teile = max_score du module, obligatoirement
STRICT_SUM_PROVIDERS = {"TELC", "ÖSD"}


def _is_auto_format(format_type: str) -> bool:
    """Formats corrigés automatiquement (une réponse attendue par question)."""
    return not (
        format_type == "free_text"
        or format_type.startswith("oral_")
        or format_type == "bildbeschreibung"
    )


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_exam_json(data: dict, provider: str) -> tuple[list[str], list[str]]:
    """Retourne (erreurs bloquantes, avertissements)."""
    errors: list[str] = []
    warnings: list[str] = []

    modules = data.get("modules") or []
    if not modules:
        errors.append("Aucun module dans le JSON.")

    seen_slugs: set[str] = set()

    for m in modules:
        name = m.get("name") or m.get("slug") or "?"
        slug = _normalize_slug(m.get("slug", ""))

        if not slug:
            errors.append(f"Module '{name}' : champ 'slug' manquant.")
        elif slug in seen_slugs:
            errors.append(f"Module '{name}' : slug '{slug}' en double.")
        seen_slugs.add(slug)

        mmax = m.get("max_score")
        if not _is_number(mmax) or mmax <= 0:
            errors.append(f"Module '{name}' : max_score manquant ou nul.")
            mmax = None

        teile = m.get("teile") or []
        if not teile:
            errors.append(f"Module '{name}' : aucun Teil.")
            continue

        teile_total = 0.0
        seen_teile: set = set()

        for t in teile:
            tn = t.get("teil_number")
            label = f"{name} Teil {tn if tn is not None else '?'}"

            if tn is None:
                errors.append(f"{label} : champ 'teil_number' manquant.")
            elif tn in seen_teile:
                errors.append(f"{label} : numéro de Teil en double.")
            seen_teile.add(tn)

            fmt = _normalize_format(t.get("format_type", ""))
            parser = PARSERS.get(fmt)
            if not parser:
                errors.append(f"{label} : format '{fmt}' non supporté.")
                continue

            tmax = t.get("max_score")
            if not _is_number(tmax) or tmax <= 0:
                errors.append(f"{label} : max_score manquant ou nul.")
                tmax = None
            else:
                teile_total += tmax

            try:
                questions = parser(t)
            except (KeyError, TypeError, AttributeError) as exc:
                errors.append(f"{label} : structure invalide (champ {exc} manquant ou mal formé).")
                continue

            if not questions:
                errors.append(f"{label} : aucune question trouvée.")
            elif (
                provider in SCALED_PROVIDERS
                and _is_auto_format(fmt)
                and tmax
                and len(questions) != tmax
            ):
                warnings.append(
                    f"{label} : {len(questions)} question(s) pour un max_score de {tmax:g} "
                    f"(question manquante ?)."
                )

        if mmax and teile_total and abs(teile_total - mmax) > 0.01:
            msg = (
                f"Module '{name}' : somme des Teile ({teile_total:g}) "
                f"différente du max du module ({mmax:g})."
            )
            if provider in STRICT_SUM_PROVIDERS:
                errors.append(msg)
            elif provider not in SCALED_PROVIDERS:
                warnings.append(msg)

    return errors, warnings


def _build_teil_config(teil_data: dict, format_type: str) -> dict | None:
    config = {}

    # Champs globaux présents sur n'importe quel format
    if "stimulus_text" in teil_data:
        config["stimulus_text"] = teil_data["stimulus_text"]
    if "texts" in teil_data:
        config["texts"] = teil_data["texts"]

    if format_type == "richtig_falsch":
        if "context" in teil_data:
            config["context"] = teil_data["context"]
            config["transcription"] = teil_data.get("transcription", "")
            config["audio_file"] = teil_data.get("audio_file", "")

    if format_type == "ja_nein":
        config["topic"] = teil_data.get("topic", "")

    if format_type == "matching":
        config["anzeigen"] = teil_data.get("anzeigen", {})

    if format_type == "zuordnung_speaker":
        config["speakers"] = teil_data.get("speakers", {})
        config["transcription"] = teil_data.get("transcription", "")

    if format_type == "qcm_abc":
        if "context" in teil_data:
            config["context"] = teil_data["context"]
            config["transcription"] = teil_data.get("transcription", "")
            config["audio_file"] = teil_data.get("audio_file", "")

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

    if format_type == "zuordnung_personen":
        config["persons"] = teil_data.get("persons", {})

    if format_type == "lueckentext_saetze":
        config["article_text"] = teil_data.get("article_text", "")
        config["article_title"] = teil_data.get("article_title", "")
        config["candidates"] = teil_data.get("candidates", {})

    if format_type == "zuordnung_meinungen":
        config["opinions"] = teil_data.get("opinions", {})
        config["topic"] = teil_data.get("topic", "")

    if format_type == "zuordnung_paragraphen":
        config["headings"] = teil_data.get("headings", {})
        config["paragraphs"] = teil_data.get("paragraphs", {})

    # free_text : Schreiben (Goethe et TELC)
    if format_type == "free_text":
        if "stimulus_email" in teil_data:
            config["stimulus_email"] = teil_data["stimulus_email"]
        if "stimulus" in teil_data:
            config["stimulus"] = teil_data["stimulus"]
            config["stimulus_author"] = teil_data.get("stimulus_author", "")
        if "scenario" in teil_data:
            config["scenario"] = teil_data["scenario"]
        if "prompts" in teil_data:
            config["prompts"] = teil_data["prompts"]
        config["word_count_target"] = teil_data.get("word_count_target", 80)
        config["register"] = teil_data.get("register", "informell")
        config["text_type"] = teil_data.get("text_type", "")

    # Champs Hören
    if "audios" in teil_data:
        config["audios"] = teil_data.get("audios", [])
    if "transcription" in teil_data and "transcription" not in config:
        config["transcription"] = teil_data["transcription"]
    if "context" in teil_data and "context" not in config:
        config["context"] = teil_data["context"]
    if "audio_file" in teil_data and "audio_file" not in config:
        config["audio_file"] = teil_data["audio_file"]

    # Nombre d'écoutes : 'ecoutes' (pipeline actuel) ou 'max_plays' (ancien format)
    plays = teil_data.get("ecoutes") or teil_data.get("max_plays")
    if plays:
        config["max_plays"] = plays
    elif "audios" in teil_data:
        config["max_plays"] = 2

    if format_type == "gap_fill_letters":
        config["beispiele"] = teil_data.get("beispiele", [])
        config["thema"] = teil_data.get("thema", "")

    if format_type == "gap_fill_words":
        config["text_with_gaps"] = teil_data.get("text_with_gaps", "")
        config["beispiel"] = teil_data.get("beispiel", {})

    if format_type == "tableau_mixed":
        config["spalten"] = teil_data.get("spalten", [])
        config["zeilen"] = teil_data.get("zeilen", [])
        config["thema"] = teil_data.get("thema", "")
        config["transcription"] = teil_data.get("transcription", "")

    if format_type == "bildbeschreibung":
        config["kandidat_a"] = teil_data.get("kandidat_a", {})
        config["kandidat_b"] = teil_data.get("kandidat_b", {})

    if format_type == "oral_meinungsaustausch":
        config["thema"] = teil_data.get("thema", "")
        config["person1"] = teil_data.get("person1", {})
        config["person2"] = teil_data.get("person2", {})

    # Contexte commun à tout le Teil (nom, thème, article, Beispiel, temps de lecture...)
    for key in TEIL_DISPLAY_KEYS:
        if key in teil_data and key not in config:
            config[key] = teil_data[key]

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

        # 0. Lecture seule : exam existant éventuel (pour connaître le provider)
        result = await self.db.execute(select(Exam).where(Exam.slug == slug))
        exam = result.scalar_one_or_none()
        provider = exam.provider if exam else _extract_provider(data)

        # 1. Validation complète AVANT toute écriture
        errors, warnings = _validate_exam_json(data, provider)
        if errors:
            raise BadRequestException(
                detail="Import refusé, barème ou structure incohérents :\n- " + "\n- ".join(errors)
            )
        log.extend(f"⚠️ {w}" for w in warnings)

        # 2. Exam
        if exam:
            log.append(f"⚠️ Exam '{slug}' existe déjà.")
        else:
            exam = Exam(
                name=data["name"],
                slug=slug,
                provider=provider,
                description=None,
                is_active=True,
            )
            self.db.add(exam)
            await self.db.flush()
            log.append(f"✅ Exam créé : {exam.name}")

        # 3. Level
        cefr_code = data.get("cefr_code", "B1")
        result = await self.db.execute(
            select(Level).where(
                Level.exam_id == exam.id,
                Level.cefr_code == cefr_code,
            )
        )
        level = result.scalar_one_or_none()
        # Goethe : 'pass_threshold_percent' ; TELC : pas de scoring_model dans le JSON
        pass_threshold = data.get("pass_threshold") or data.get("pass_threshold_percent") or 60
        scoring_model = data.get("scoring_model") or DEFAULT_SCORING_MODEL.get(exam.provider)
        if level:
            log.append(f"⚠️ Level '{cefr_code}' existe déjà.")
        else:
            level = Level(
                exam_id=exam.id,
                cefr_code=cefr_code,
                total_pass_score=pass_threshold,
                scoring_notes=scoring_model or "",
                display_order=0,
                is_free=False,
                exam_config={
                    "scoring_model": scoring_model,
                    "pass_threshold": pass_threshold,
                    **DEFAULT_PASS_RULES.get(exam.provider, {}),
                },
            )
            self.db.add(level)
            await self.db.flush()
            log.append(f"✅ Level créé : {cefr_code}")

        # 4. Subject
        result = await self.db.execute(
            select(func.max(Subject.subject_number)).where(Subject.level_id == level.id)
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

        # 5. Modules → Teile → Questions
        for order, module_data in enumerate(data.get("modules", [])):
            module = Module(
                subject_id=subject.id,
                slug=_normalize_slug(module_data["slug"]),
                name=module_data["name"],
                time_limit_minutes=module_data.get("time_limit_minutes", 60),
                max_score=module_data["max_score"],
                display_order=order,
            )
            self.db.add(module)
            await self.db.flush()
            log.append(f"  ✅ Module : {module.name} ({module.slug})")

            for teil_data in module_data.get("teile", []):
                teil_number = teil_data["teil_number"]
                format_type = _normalize_format(teil_data.get("format_type", ""))

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
                    log.append(f"    ⚠️ Teil {teil_number} existe, ignoré.")
                    continue
                else:
                    teil = Teil(
                        module_id=module.id,
                        teil_number=teil_number,
                        format_type=format_type,
                        instructions=teil_data.get("instructions"),
                        max_score=teil_data["max_score"],
                        time_minutes=teil_data.get("time_minutes") or teil_data.get("duration_minutes"),
                        config=_build_teil_config(teil_data, format_type),
                    )
                    self.db.add(teil)
                    await self.db.flush()

                questions_data = PARSERS[format_type](teil_data)
                instances = [Question(teil_id=teil.id, **q) for q in questions_data]
                self.db.add_all(instances)
                total_questions += len(instances)
                log.append(
                    f"    ✅ Teil {teil_number} ({format_type}) : "
                    f"{len(instances)} questions, {teil.max_score:g} pts"
                )

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
                or_(
                    Module.slug.ilike("%horen%"),
                    Module.slug.ilike("%hören%"),
                    Module.slug.ilike("%hoerverstehen%"),
                    Module.slug.ilike("%hörverstehen%"),
                ),
            ),
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
                log.append(f"⚠️ {filename} : pas un MP3, ignoré.")
                skipped += 1
                continue

            base = Path(filename).stem  # ex: horen_teil1_audio1
            parts = base.split("_")

            # Extraire teil_number
            try:
                teil_part = next(p for p in parts if p.startswith("teil"))
                teil_number = int(teil_part.replace("teil", ""))
            except (StopIteration, ValueError):
                log.append(f"⚠️ {filename} : nom non reconnu (attendu : horen_teilN_audioM.mp3), ignoré.")
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
                log.append(f"⚠️ {filename} : Teil {teil_number} introuvable.")
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
                # Teil avec plusieurs audios : matcher par audio_number dans content
                for q in questions:
                    content_data = q.content or {}
                    if content_data.get("audio_number") == audio_number:
                        q.audio_file = relative_path
                        q_updated += 1
            else:
                # Teil avec 1 seul audio long : toutes les questions du teil
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