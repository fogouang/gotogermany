"""
app/modules/users/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserChangePasswordRequest,
    UserUpdateRequest,
    DirectorCreateRequest,
    SecretaryCreateRequest,
    StudentCreateRequest,
    StudentTargetUpdateRequest,
)
from app.shared.exceptions.http import BadRequestException, ForbiddenException, NotFoundException
from app.shared.security.password import hash_password, verify_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_me(self, current_user: User) -> User:
        """Retourne l'utilisateur courant — déjà résolu par la dependency."""
        return current_user

    async def update_me(self, current_user: User, data: UserUpdateRequest) -> User:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return current_user
        return await self.repo.update(current_user.id, **update_data)

    async def change_password(
        self, current_user: User, data: UserChangePasswordRequest
    ) -> User:
        if not verify_password(data.current_password, current_user.hashed_password):
            raise BadRequestException(detail="Mot de passe actuel incorrect.")
        if data.current_password == data.new_password:
            raise BadRequestException(
                detail="Le nouveau mot de passe doit être différent de l'actuel."
            )
        return await self.repo.update(
            current_user.id,
            hashed_password=hash_password(data.new_password),
        )

    # ── Admin ────────────────────────────────────────────
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return list(await self.repo.get_all(skip=skip, limit=limit))

    async def get_by_id(self, user_id: UUID) -> User:
        return await self.repo.get_by_id_or_404(user_id)

    async def toggle_active(self, user_id: UUID, current_user: User) -> User:
        """Active ou désactive un compte utilisateur."""
        if current_user.id == user_id:
            raise BadRequestException(detail="Vous ne pouvez pas désactiver votre propre compte.")
        user = await self.repo.get_by_id_or_404(user_id)
        return await self.repo.update(user_id, is_active=not user.is_active)

    async def delete(self, user_id: UUID, current_user: User) -> bool:
        if current_user.id == user_id:
            raise BadRequestException(detail="Vous ne pouvez pas supprimer votre propre compte.")
        return await self.repo.delete(user_id)

    # ── Licence de centre : création de comptes ──────────

    async def _check_email_available(self, email: str) -> None:
        existing = await self.repo.find_by_email(email)
        if existing:
            raise BadRequestException(detail="Cet email est déjà utilisé.")

    async def create_director(self, data: DirectorCreateRequest) -> User:
        """Créé par l'admin ITIA, une fois la licence négociée/payée."""
        await self._check_email_available(data.email)
        return await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            is_active=True,
            is_admin=False,
            is_verified=True,  # créé directement par ITIA, pas de vérif email nécessaire
            role=UserRole.center_director,
            center_id=data.center_id,
        )

    async def create_secretary(self, data: SecretaryCreateRequest, director: User) -> User:
        """Créé par le directeur — la branch doit appartenir à son propre centre."""
        from app.modules.centers.repository import BranchRepository

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(data.branch_id)
        if branch.center_id != director.center_id:
            raise ForbiddenException(detail="Cette succursale n'appartient pas à votre centre.")

        await self._check_email_available(data.email)
        return await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            is_active=True,
            is_admin=False,
            is_verified=True,
            role=UserRole.branch_secretary,
            branch_id=branch.id,
        )

    async def create_student(self, data: StudentCreateRequest, secretary: User) -> User:
            """Créé par la secrétaire — vérifie le quota de la licence du centre avant création."""
            from app.modules.centers.service import CenterService
            from app.modules.centers.repository import BranchRepository
            from app.modules.exams.repository import LevelRepository

            branch_repo = BranchRepository(self.db)
            branch = await branch_repo.get_by_id_or_404(secretary.branch_id)

            await CenterService(self.db).check_quota_available(branch.center_id)
            await LevelRepository(self.db).get_by_id_or_404(data.target_level_id)

            await self._check_email_available(data.email)
            return await self.repo.create(
                email=data.email,
                hashed_password=hash_password(data.password),
                full_name=data.full_name,
                phone=data.phone,
                is_active=True,
                is_admin=False,
                is_verified=True,
                role=UserRole.student,
                branch_id=secretary.branch_id,
                target_level_id=data.target_level_id,
                ai_credits=2,  # crédits IA pour étudiant de centre — valeur provisoire, à revoir après optimisation du coût de correction
            )

    async def update_student_target(
            self, student_id: UUID, data: StudentTargetUpdateRequest, secretary: User
        ) -> User:
            """Modifie le level ciblé — ne consomme pas une nouvelle place de quota."""
            from app.modules.exams.repository import LevelRepository

            student = await self.repo.get_by_id_or_404(student_id)
            if student.branch_id != secretary.branch_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre succursale.")
            if student.role != UserRole.student:
                raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

            await LevelRepository(self.db).get_by_id_or_404(data.target_level_id)

            return await self.repo.update(
                student.id,
                target_level_id=data.target_level_id,
            )

    async def list_students_for_secretary(self, secretary: User) -> list[User]:
        return await self.repo.find_students_by_branch(secretary.branch_id)

    async def list_students_for_director(self, director: User) -> list[User]:
        return await self.repo.find_students_by_center(director.center_id)
    
    async def list_secretaries_for_director(self, director: User) -> list[User]:
        return await self.repo.find_secretaries_by_center(director.center_id)