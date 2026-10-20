"""
app/modules/exam_access/visibility.py

Sujets privés :
- can_see_private      : qui peut voir / ouvrir un sujet privé en entraînement libre
                         (admin et élève indépendant ; jamais l'élève de centre,
                         pour qui les sujets privés sont réservés aux devoirs).
- is_assignment_session: la session est-elle la copie d'un devoir ? Ce critère,
                         et non plus subject.is_private, décide si l'on masque le
                         résultat et si l'IA peut corriger.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def can_see_private(user) -> bool:
    if user is None:
        return False
    if user.is_admin:
        return True
    from app.modules.users.models import UserRole

    return user.role == UserRole.student and not user.branch_id


async def is_assignment_session(db: AsyncSession, session_id: UUID) -> bool:
    from app.modules.assignments.models import AssignmentSubmission

    result = await db.execute(
        select(AssignmentSubmission.id)
        .where(AssignmentSubmission.exam_session_id == session_id)
        .limit(1)
    )
    return result.scalar_one_or_none() is not None