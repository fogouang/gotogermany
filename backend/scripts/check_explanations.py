"""
scripts/check_explanations.py
Combien de questions ont une explication, par sujet, pour un examen.
Usage : uv run python -m scripts.check_explanations telc_b2
"""
import asyncio
import sys

from sqlalchemy import text

from app.shared.database.session import SessionLocal as AsyncSessionLocal
from app.modules.exams.models import Exam, Level, Subject, Module, Teil
from app.modules.questions.models import Question

# Noms de tables lus dans les modèles (aucune configuration des relations nécessaire)
SQL = f"""
SELECT s.subject_number,
       count(*) FILTER (WHERE q.correct_answer ? 'explanation') AS avec_explication,
       count(*) AS questions
FROM {Question.__tablename__} q
JOIN {Teil.__tablename__}    t ON t.id = q.teil_id
JOIN {Module.__tablename__}  m ON m.id = t.module_id
JOIN {Subject.__tablename__} s ON s.id = m.subject_id
JOIN {Level.__tablename__}   l ON l.id = s.level_id
JOIN {Exam.__tablename__}    e ON e.id = l.exam_id
WHERE e.slug = :slug
GROUP BY s.subject_number
ORDER BY s.subject_number
"""


async def main(slug: str) -> None:
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(text(SQL), {"slug": slug})).all()
        print(f"\n{'Sujet':>6}  Explications")
        for number, with_expl, total in rows:
            print(f"{number:>6}  {with_expl}/{total}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "telc_b2"))