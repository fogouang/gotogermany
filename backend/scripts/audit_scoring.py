"""
backend/scripts/audit_scoring.py

Audit LECTURE SEULE du barème de tous les sujets en base.
Ne modifie rien.

Pour chaque (fournisseur, niveau), regroupe les sujets de même structure et
affiche, par module et par Teil : nb de questions, somme des points en base,
max_score du Teil, max_score du module, puis signale les incohérences.

Usage (depuis G:\\german-test\\backend, venv actif) :
    python -m scripts.audit_scoring
    python -m scripts.audit_scoring --csv audit_scoring.csv
"""
import argparse
import asyncio
import csv
import os
import sys
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

import app.shared.database.registry  # noqa: F401  (enregistre tous les modèles)
from app.modules.exams.models import Exam, Level, Module, Subject, Teil

ORAL_SLUGS = {"sprechen", "muendlicher_ausdruck", "mündlicher_ausdruck"}


def _db_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            url = os.environ.get("DATABASE_URL")
        except ImportError:
            pass
    if not url:
        sys.exit("DATABASE_URL introuvable (variable d'environnement ou .env).")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _level_code(level: Level | None) -> str:
    if level is None:
        return "?"
    for attr in ("code", "cefr_code", "slug", "name"):
        value = getattr(level, attr, None)
        if value:
            return str(value)
    return "?"


def _fmt(x: float) -> str:
    return f"{x:g}"


def _teil_info(teil: Teil) -> dict:
    questions = list(teil.questions)
    n = len(questions)
    raw = sum(float(q.points or 0) for q in questions)
    tmax = float(teil.max_score or 0)
    auto = n > 0 and all(q.is_auto_correctable for q in questions)

    flags = []
    if n == 0:
        flags.append("TEIL_VIDE")
    if tmax <= 0:
        flags.append("TEIL_MAX_0")
    if n and tmax > 0 and abs(raw - tmax) > 0.01:
        flags.append("POINTS_BRUTS!=MAX_TEIL")

    return {
        "teil": teil.teil_number,
        "format": teil.format_type,
        "n": n,
        "raw": raw,
        "tmax": tmax,
        "auto": auto,
        "par_question": (tmax / n) if (auto and n and tmax > 0) else None,
        "flags": flags,
    }


def _module_info(module: Module) -> dict:
    teile = [_teil_info(t) for t in sorted(module.teile, key=lambda t: t.teil_number)]
    mmax = float(module.max_score or 0)
    somme_teile = sum(t["tmax"] for t in teile)

    flags = []
    if abs(somme_teile - mmax) > 0.01:
        flags.append(f"SOMME_TEILE({_fmt(somme_teile)})!=MAX_MODULE({_fmt(mmax)})")

    return {
        "slug": module.slug,
        "name": module.name,
        "mmax": mmax,
        "time": module.time_limit_minutes,
        "oral": module.slug in ORAL_SLUGS,
        "teile": teile,
        "flags": flags,
    }


def _signature(modules: list[dict]) -> tuple:
    return tuple(
        (
            m["slug"], m["mmax"],
            tuple((t["teil"], t["format"], t["n"], t["raw"], t["tmax"]) for t in m["teile"]),
        )
        for m in modules
    )


async def main(csv_path: str | None) -> None:
    engine = create_async_engine(_db_url())
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        exams = {e.id: e for e in (await db.execute(select(Exam))).scalars()}
        levels = {lv.id: lv for lv in (await db.execute(select(Level))).scalars()}
        subjects = (
            await db.execute(
                select(Subject).options(
                    selectinload(Subject.modules)
                    .selectinload(Module.teile)
                    .selectinload(Teil.questions)
                )
            )
        ).scalars().all()

    await engine.dispose()

    # (provider, niveau) -> signature -> {"modules", "subjects"}
    groups: dict = defaultdict(dict)
    level_by_key: dict = {}
    csv_rows = []

    for s in subjects:
        level = levels.get(s.level_id)
        exam = exams.get(level.exam_id) if level else None
        provider = exam.provider if exam else "?"
        key = (provider, _level_code(level))
        level_by_key[key] = level

        modules = [
            _module_info(m)
            for m in sorted(s.modules, key=lambda m: m.display_order or 0)
        ]
        sig = _signature(modules)
        bucket = groups[key].setdefault(sig, {"modules": modules, "subjects": []})
        label = f"#{s.subject_number}" + (" (privé)" if s.is_private else "")
        bucket["subjects"].append(label)

        for m in modules:
            for t in m["teile"]:
                csv_rows.append({
                    "provider": provider,
                    "niveau": key[1],
                    "sujet": s.subject_number,
                    "prive": s.is_private,
                    "module": m["slug"],
                    "module_max": m["mmax"],
                    "teil": t["teil"],
                    "format": t["format"],
                    "nb_questions": t["n"],
                    "points_bruts": t["raw"],
                    "teil_max": t["tmax"],
                    "pts_par_question": t["par_question"],
                    "flags": " | ".join(t["flags"] + m["flags"]),
                })

    total_flags = 0
    for key in sorted(groups):
        provider, code = key
        level = level_by_key.get(key)
        print("=" * 78)
        print(f"{provider} {code}")
        if level is not None:
            print(
                f"  total_pass_score = {getattr(level, 'total_pass_score', None)}"
                f"  |  exam_config = {getattr(level, 'exam_config', None)}"
            )

        for sig, bucket in groups[key].items():
            modules = bucket["modules"]
            ecrit = sum(m["mmax"] for m in modules if not m["oral"])
            oral = sum(m["mmax"] for m in modules if m["oral"])
            print("-" * 78)
            print(f"  Sujets ({len(bucket['subjects'])}) : {', '.join(bucket['subjects'])}")
            print(f"  Total écrit = {_fmt(ecrit)}  |  Total oral = {_fmt(oral)}")

            for m in modules:
                tag = " [oral]" if m["oral"] else ""
                print(
                    f"   {m['slug']}{tag}  max={_fmt(m['mmax'])}  "
                    f"temps={m['time']} min  {' '.join(m['flags'])}"
                )
                total_flags += len(m["flags"])
                for t in m["teile"]:
                    pq = f"{t['par_question']:g}/q" if t["par_question"] else "-"
                    print(
                        f"      T{t['teil']} {t['format']:<26} q={t['n']:<3} "
                        f"bruts={_fmt(t['raw']):<6} max={_fmt(t['tmax']):<6} "
                        f"officiel={pq:<8} {' '.join(t['flags'])}"
                    )
                    total_flags += len(t["flags"])

    print("=" * 78)
    print(f"{len(subjects)} sujets analysés, {total_flags} signalements.")

    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()), delimiter=";")
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"CSV écrit : {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=None, help="Chemin du CSV détaillé (optionnel)")
    args = parser.parse_args()
    asyncio.run(main(args.csv))