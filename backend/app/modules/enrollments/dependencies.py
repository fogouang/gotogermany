"""
app/modules/enrollments/dependencies.py
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.dependencies import get_current_director_or_secretary
from app.modules.centers.models import Branch
from app.modules.users.models import User, UserRole
from app.shared.database.session import get_db
from app.shared.exceptions.http import ForbiddenException


class CenterScope(BaseModel):
    model_config = ConfigDict(frozen=True)

    center_id: UUID
    branch_id: UUID | None
    is_director: bool


async def get_current_center_scope(
    current_user: User = Depends(get_current_director_or_secretary),
    db: AsyncSession = Depends(get_db),
) -> CenterScope:
    if current_user.role == UserRole.center_director:
        if current_user.center_id is None:
            raise ForbiddenException(detail="Ce directeur n'est rattaché à aucun centre.")
        return CenterScope(center_id=current_user.center_id, branch_id=None, is_director=True)

    stmt = select(Branch.id, Branch.center_id).where(Branch.id == current_user.branch_id)
    result = await db.execute(stmt)
    row = result.one_or_none()
    if row is None:
        raise ForbiddenException(detail="Cette secrétaire n'est rattachée à aucune succursale valide.")
    branch_id, center_id = row
    return CenterScope(center_id=center_id, branch_id=branch_id, is_director=False)


CurrentCenterScope = Annotated[CenterScope, Depends(get_current_center_scope)]