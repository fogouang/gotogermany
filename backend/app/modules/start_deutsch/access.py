"""
app/modules/start_deutsch/access.py

Accès aux sujets Start Deutsch, mêmes règles que les sujets B :
- sujet privé : devoir non rendu, admin, ou élève indépendant ;
- ensuite, accès payant par niveau (A1, A2) : sujets 1 à 3 libres pour
  l'indépendant, accès + classe en cours pour l'élève de centre.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.start_deutsch.models import StartDeutschSubject
from app.modules.users.models import User
from app.shared.exceptions.http import ForbiddenException


async def is_sd_assignment_session(db: AsyncSession, session_id: UUID) -> bool:
    """Vrai si la session Start Deutsch est la copie d'un devoir."""
    from app.modules.assignments.models import AssignmentSubmission

    result = await db.execute(
        select(AssignmentSubmission.id).where(AssignmentSubmission.sd_session_id == session_id).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def require_sd_subject_access(db: AsyncSession, user: User, subject: StartDeutschSubject) -> None:
    """Sujet privé puis accès payant, dans cet ordre (comme ExamAccessService pour les B)."""
    from app.modules.assignments.service import AssignmentService
    from app.modules.exam_access.service import ExamAccessService
    from app.modules.exam_access.visibility import can_see_private

    if subject.is_private:
        if user.is_admin:
            return
        # Devoir non rendu sur ce sujet : toujours ouvert, payé ou non
        if await AssignmentService(db).student_has_open_sd_assignment(user.id, subject.id):
            return
        if not can_see_private(user):
            raise ForbiddenException(detail="Ce sujet n'est accessible que dans le cadre d'un devoir.")
        # Élève indépendant : sujet comme les autres, règles d'accès ci-dessous

    await ExamAccessService(db).require_sd_subject_access(user, subject)