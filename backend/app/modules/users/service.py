"""
app/modules/users/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    StudentAccessDatesUpdateRequest,
    StudentCreditAdjustRequest,
    StudentDetailedProgressResponse,
    UserChangePasswordRequest,
    UserUpdateRequest,
    DirectorCreateRequest,
    SecretaryCreateRequest,
    StudentCreateRequest,
    StudentTargetUpdateRequest,
)
from app.shared.exceptions.http import BadRequestException, ForbiddenException, NotFoundException
from app.shared.security.password import hash_password, verify_password

# Normalise les différents slugs de module selon le provider
# (TELC: leseverstehen/hoerverstehen/muendlicher_ausdruck ;
#  Goethe/ÖSD: lesen/horen/sprechen) vers un même libellé affiché.
_MODULE_LABELS = {
    "lesen": "Lesen",
    "leseverstehen": "Lesen",
    "horen": "Hören",
    "hoeren": "Hören",
    "hoerverstehen": "Hören",
    "schreiben": "Schreiben",
    "schriftlicher_ausdruck": "Schreiben",
    "sprechen": "Sprechen",
    "muendlicher_ausdruck": "Sprechen",
    "sprachbausteine": "Sprachbausteine",
}
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
        """Créé par la secrétaire — vérifie le quota, puis prélève les crédits
        par défaut du centre sur le pool."""
        from app.modules.centers.service import CenterService
        from app.modules.centers.repository import BranchRepository
        from app.modules.exams.repository import LevelRepository

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(secretary.branch_id)

        center_service = CenterService(self.db)
        await center_service.check_quota_available(branch.center_id)
        await LevelRepository(self.db).get_by_id_or_404(data.target_level_id)
        await self._check_email_available(data.email)

        center = await center_service.center_repo.get_by_id_or_404(branch.center_id)
        default_credits = center.default_credits_per_student

        if center.ai_credit_pool_balance < default_credits:
            raise BadRequestException(
                detail=(
                    f"Pool de crédits insuffisant pour créer un nouvel étudiant "
                    f"({center.ai_credit_pool_balance} restants, {default_credits} requis). "
                    "Contactez ITIA pour un rechargement."
                )
            )

        student = await self.repo.create(
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
            ai_credits=default_credits,
            access_duration_days=data.access_duration_days or 30,
        )

        # Prélèvement du pool + journalisation de la création elle-même
        await center_service.center_repo.update(
            branch.center_id,
            ai_credit_pool_balance=center.ai_credit_pool_balance - default_credits,
        )
        await center_service.credit_txn_repo.create(
            center_id=branch.center_id,
            student_id=student.id,
            performed_by=secretary.id,
            amount=default_credits,
            pool_balance_after=center.ai_credit_pool_balance - default_credits,
            reason="Attribution initiale à la création du compte",
        )

        return student


    async def adjust_student_credits(
        self, student_id: UUID, data: StudentCreditAdjustRequest, performer: User
    ) -> User:
        """Secrétaire (sa branche) ou directeur (tout son centre) rechargent
        un étudiant précis. Vérifie le scope avant de déléguer au CenterService."""
        from app.modules.centers.service import CenterService
        from app.modules.centers.repository import BranchRepository

        student = await self.repo.get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(student.branch_id)

        if performer.role == UserRole.branch_secretary:
            if student.branch_id != performer.branch_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre succursale.")
        elif performer.role == UserRole.center_director:
            if branch.center_id != performer.center_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")
        else:
            raise ForbiddenException(detail="Action réservée aux secrétaires et directeurs.")

        return await CenterService(self.db).adjust_student_credits(
            center_id=branch.center_id,
            student=student,
            amount=data.amount,
            performed_by=performer,
            reason=data.reason,
        )


    async def toggle_student_active(self, student_id: UUID, director: User) -> User:
        """Directeur active/désactive un étudiant de son propre centre.
        Ne libère jamais le quota consommé (règle permanente/cumulative)."""
        from app.modules.centers.repository import BranchRepository

        student = await self.repo.get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(student.branch_id)
        if branch.center_id != director.center_id:
            raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")

        return await self.repo.update(student_id, is_active=not student.is_active)


    async def update_student_access_dates(
        self, student_id: UUID, data: StudentAccessDatesUpdateRequest, director: User
    ) -> User:
        """Directeur ajuste manuellement la fenêtre d'accès d'un étudiant précis."""
        from app.modules.centers.repository import BranchRepository

        student = await self.repo.get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(student.branch_id)
        if branch.center_id != director.center_id:
            raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")

        update_data = {}
        if data.access_expires_at is not None:
            update_data["access_expires_at"] = data.access_expires_at
        if data.access_duration_days is not None:
            update_data["access_duration_days"] = data.access_duration_days

        if not update_data:
            return student

        return await self.repo.update(student_id, **update_data)


    async def get_student_progress_for_secretary(self, secretary: User) -> list[dict]:
        """Progression des étudiants — restreinte à la succursale de la secrétaire."""
        from app.modules.exam_sessions.repository import ExamSessionRepository
        students = await self.repo.find_students_by_branch(secretary.branch_id)
        return await self._build_progress_rows(students)


    async def get_student_progress_for_director(self, director: User) -> list[dict]:
        """Progression des étudiants — tout le centre, toutes succursales confondues."""
        students = await self.repo.find_students_by_center(director.center_id)
        return await self._build_progress_rows(students)


    async def _build_progress_rows(self, students: list[User]) -> list[dict]:
        """Agrège sessions/scores par étudiant. À adapter selon le repository
        exam_sessions réel — squelette fourni, je n'ai pas ce fichier sous les yeux."""
        from app.modules.exam_sessions.repository import ExamSessionRepository

        session_repo = ExamSessionRepository(self.db)
        rows = []
        for student in students:
            stats = await session_repo.get_stats_for_user(student.id)  # méthode à confirmer/créer
            rows.append({
                "student_id": student.id,
                "student_name": student.full_name,
                "branch_name": student.branch.name if student.branch else "",
                "total_sessions": stats.get("total_sessions", 0),
                "average_score": stats.get("average_score"),
                "last_session_at": stats.get("last_session_at"),
                "ai_credits_remaining": student.ai_credits,
            })
        return rows

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
    
  


    async def get_student_progress_detail(
        self, student_id: UUID, requester: User
    ) -> "StudentDetailedProgressResponse":
        """
        Vue détaillée d'un étudiant, avec ventilation par examen/module et
        historique pour graphes. Secrétaire limitée à sa succursale,
        directeur à tout son centre.
        """
        from app.modules.centers.repository import BranchRepository
        from app.modules.exam_sessions.repository import ExamSessionRepository
        from app.modules.users.schemas import (
            StudentDetailedProgressResponse,
            ExamProgressResponse,
            ModuleScoreBreakdown,
            ScoreHistoryPoint,
        )

        student = await self.repo.get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(student.branch_id)

        if requester.role == UserRole.branch_secretary:
            if student.branch_id != requester.branch_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre succursale.")
        elif requester.role == UserRole.center_director:
            if branch.center_id != requester.center_id:
                raise ForbiddenException(detail="Cet étudiant n'appartient pas à votre centre.")
        else:
            raise ForbiddenException(detail="Action réservée aux secrétaires et directeurs.")

        session_repo = ExamSessionRepository(self.db)
        rows = await session_repo.get_detailed_sessions_for_user(student.id)

        exams_map: dict = {}
        score_history: list[ScoreHistoryPoint] = []

        for row in rows:
            eid = row["exam_id"]
            if eid not in exams_map:
                exams_map[eid] = {
                    "exam_name": row["exam_name"],
                    "sessions": [],
                    "module_scores": {},
                }
            exams_map[eid]["sessions"].append(row)

            for module_key, score in (row["score_breakdown"] or {}).items():
                if score is None:
                    continue
                label = _MODULE_LABELS.get(module_key, module_key.capitalize())
                exams_map[eid]["module_scores"].setdefault(label, []).append(score)

            if row["score"] is not None and row["submitted_at"]:
                score_history.append(ScoreHistoryPoint(
                    date=row["submitted_at"],
                    score=row["score"],
                    exam_name=row["exam_name"],
                ))

        exams_list: list[ExamProgressResponse] = []
        for eid, data in exams_map.items():
            sessions = data["sessions"]
            scores = [s["score"] for s in sessions if s["score"] is not None]
            submitted_dates = [s["submitted_at"] for s in sessions if s["submitted_at"]]

            modules = [
                ModuleScoreBreakdown(
                    module_name=label,
                    average_score=sum(vals) / len(vals) if vals else None,
                )
                for label, vals in data["module_scores"].items()
            ]

            exams_list.append(ExamProgressResponse(
                exam_id=eid,
                exam_name=data["exam_name"],
                total_sessions=len(sessions),
                average_score=sum(scores) / len(scores) if scores else None,
                last_session_at=max(submitted_dates) if submitted_dates else None,
                modules=modules,
            ))

        all_scores = [r["score"] for r in rows if r["score"] is not None]
        all_dates = [r["submitted_at"] for r in rows if r["submitted_at"]]

        return StudentDetailedProgressResponse(
            student_id=student.id,
            student_name=student.full_name,
            branch_name=branch.name,
            ai_credits_remaining=student.ai_credits,
            total_sessions=len(rows),
            overall_average_score=sum(all_scores) / len(all_scores) if all_scores else None,
            last_session_at=max(all_dates) if all_dates else None,
            exams=exams_list,
            score_history=score_history,
        )