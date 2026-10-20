"""
app/modules/users/service.py
"""
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    StudentCreditAdjustRequest,
    StudentDetailedProgressResponse,
    StudentQuickCreateRequest,
    TeacherCreateRequest,
    UserChangePasswordRequest,
    UserUpdateRequest,
    DirectorCreateRequest,
    SecretaryCreateRequest,
    StudentCreateRequest,
)
from app.shared.exceptions.http import BadRequestException, ForbiddenException
from app.shared.security.password import hash_password, verify_password
from app.shared.utils.phone import normalize_phone

# Adresse interne des comptes créés sans email
PLACEHOLDER_EMAIL_DOMAIN = "@internal.gotogermany"

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

        if "phone" in update_data:
            await self._check_phone_available(update_data["phone"], current_user.id)

        if "target_level_id" in update_data:
            await self._check_target_level(current_user, update_data["target_level_id"])
            # Choisir un niveau du catalogue (B1/B2) = parcours examen
            update_data.setdefault("learning_track", "exam")

        if "learning_track" in update_data:
            if current_user.role != UserRole.student or current_user.branch_id:
                raise ForbiddenException(
                    detail="Le parcours est défini par votre centre."
                )

        if "whatsapp_opt_in" in update_data:
            if update_data["whatsapp_opt_in"]:
                phone = update_data.get("phone") or current_user.phone
                if not phone:
                    raise BadRequestException(
                        detail="Ajoutez d'abord votre numéro WhatsApp à votre profil."
                    )
                # On garde la date du premier accord s'il était déjà donné
                if not current_user.whatsapp_opt_in:
                    update_data["whatsapp_opt_in_at"] = datetime.now(timezone.utc)
            else:
                update_data["whatsapp_opt_in_at"] = None

        return await self.repo.update(current_user.id, **update_data)

    async def _check_target_level(self, user: User, level_id: UUID) -> None:
        """Niveau actif choisi par l'étudiant lui-même (préférence d'affichage)."""
        from sqlalchemy import func, select

        from app.modules.exams.models import Level, Subject

        if user.role != UserRole.student:
            raise ForbiddenException(detail="Seuls les étudiants choisissent un niveau.")
        if user.branch_id:
            # Élève de centre : niveau fixé par le centre, verrouillé côté front
            raise ForbiddenException(detail="Votre niveau est défini par votre centre.")

        level = await self.db.get(Level, level_id)
        if not level:
            raise BadRequestException(detail="Niveau introuvable.")

        subject_count = await self.db.scalar(
            select(func.count(Subject.id)).where(Subject.level_id == level_id)
        )
        if not subject_count:
            raise BadRequestException(detail="Ce niveau n'a pas encore de sujets.")

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

    @staticmethod
    def _normalized_phone(raw: str | None) -> str | None:
        try:
            return normalize_phone(raw)
        except ValueError:
            raise BadRequestException(detail="Numéro de téléphone invalide.")

    async def _check_phone_available(self, phone: str | None, exclude_user_id: UUID | None = None) -> None:
        """Un numéro = un compte (le numéro sert à se connecter)."""
        if not phone:
            return
        existing = await self.repo.find_by_phone(phone)
        if existing and existing.id != exclude_user_id:
            raise BadRequestException(detail="Ce numéro est déjà utilisé par un autre compte.")

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

    async def create_teacher(self, data: TeacherCreateRequest, staff: User) -> User:
        """Créé par le directeur (branch_id requis, doit appartenir à son
        centre) ou la secrétaire (sa propre succursale s'applique,
        branch_id fourni ignoré)."""
        from app.modules.centers.repository import BranchRepository

        branch_repo = BranchRepository(self.db)

        if staff.role == UserRole.center_director:
            if not data.branch_id:
                raise BadRequestException(detail="branch_id requis pour un directeur.")
            branch = await branch_repo.get_by_id_or_404(data.branch_id)
            if branch.center_id != staff.center_id:
                raise ForbiddenException(detail="Cette succursale n'appartient pas à votre centre.")
        elif staff.role == UserRole.branch_secretary:
            branch = await branch_repo.get_by_id_or_404(staff.branch_id)
        else:
            raise ForbiddenException(detail="Action réservée au staff de centre.")

        await self._check_email_available(data.email)
        return await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            is_active=True,
            is_admin=False,
            is_verified=True,
            role=UserRole.teacher,
            branch_id=branch.id,
        )
    
    async def toggle_teacher_active(self, teacher_id: UUID, staff: User) -> User:
        """Active/désactive un compte enseignant. Directeur : tout son
        centre. Secrétaire : sa succursale uniquement."""
        from app.modules.centers.repository import BranchRepository

        teacher = await self.repo.get_by_id_or_404(teacher_id)
        if teacher.role != UserRole.teacher:
            raise BadRequestException(detail="Cet utilisateur n'est pas un enseignant.")

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(teacher.branch_id)

        if staff.role == UserRole.branch_secretary:
            if teacher.branch_id != staff.branch_id:
                raise ForbiddenException(detail="Cet enseignant n'appartient pas à votre succursale.")
        elif staff.role == UserRole.center_director:
            if branch.center_id != staff.center_id:
                raise ForbiddenException(detail="Cet enseignant n'appartient pas à votre centre.")
        else:
            raise ForbiddenException(detail="Action réservée au staff de centre.")

        return await self.repo.update(teacher_id, is_active=not teacher.is_active)
      
    async def create_student(self, data: StudentCreateRequest, secretary: User) -> User:
        """Créé par la secrétaire. Le compte n'a pas encore accès aux sujets ni
        de crédits IA : l'accès et les crédits arrivent à l'activation
        (POST /sales/activations), quand le centre encaisse le paiement."""
        from app.modules.centers.repository import BranchRepository

        branch = await BranchRepository(self.db).get_by_id_or_404(secretary.branch_id)
        await self._check_email_available(data.email)
        phone = self._normalized_phone(data.phone)
        await self._check_phone_available(phone)

        student = await self.repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=phone,
            is_active=True,
            is_admin=False,
            is_verified=True,
            role=UserRole.student,
            branch_id=secretary.branch_id,
            ai_credits=0,
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


    async def get_student_progress_for_secretary(self, secretary: User) -> list[dict]:
        """Progression des étudiants — restreinte à la succursale de la secrétaire."""
        from app.modules.exam_sessions.repository import ExamSessionRepository
        students = await self.repo.find_students_by_branch(secretary.branch_id)
        return await self._build_progress_rows(students)


    async def get_student_progress_for_director(self, director: User) -> list[dict]:
        """Progression des étudiants — tout le centre, toutes succursales confondues."""
        students = await self.repo.find_students_by_center(director.center_id)
        return await self._build_progress_rows(students)

    async def get_student_progress_for_teacher(self, teacher: User) -> list[dict]:
        from app.modules.training_sessions.repository import TrainingSessionTeacherRepository

        teacher_link_repo = TrainingSessionTeacherRepository(self.db)
        student_ids = await teacher_link_repo.find_active_student_ids_for_teacher(teacher.id)
        students = await self.repo.find_by_ids(student_ids)
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


    async def list_students_for_secretary(self, secretary: User) -> list[User]:
        return await self.repo.find_students_by_branch(secretary.branch_id)

    async def list_students_for_director(self, director: User) -> list[User]:
        return await self.repo.find_students_by_center(director.center_id)
    
    async def list_secretaries_for_director(self, director: User) -> list[User]:
        return await self.repo.find_secretaries_by_center(director.center_id)
    
  


    async def _get_student_progress_detail_unscoped(
        self, student_id: UUID
    ) -> "StudentDetailedProgressResponse":
        """
        Vue détaillée d'un étudiant, avec ventilation par examen > sujet > module
        (score + compteurs de questions correctes/incorrectes/totales) et
        historique pour graphes. Pas de contrôle d'accès ici — le scope
        (secrétaire/directeur/enseignant) est vérifié en amont par l'appelant.
        """
        from app.modules.centers.repository import BranchRepository
        from app.modules.exam_sessions.repository import ExamSessionRepository
        from app.modules.users.schemas import (
            StudentDetailedProgressResponse,
            ExamProgressResponse,
            SubjectScoreBreakdown,
            ModuleScoreBreakdown,
            ScoreHistoryPoint,
        )

        student = await self.repo.get_by_id_or_404(student_id)
        if student.role != UserRole.student:
            raise BadRequestException(detail="Cet utilisateur n'est pas un étudiant.")

        branch_repo = BranchRepository(self.db)
        branch = await branch_repo.get_by_id_or_404(student.branch_id)

        session_repo = ExamSessionRepository(self.db)
        rows = await session_repo.get_detailed_sessions_for_user(student.id)

        # ── Regroupement à deux niveaux : exam -> subject -> modules ──
        exams_map: dict = {}
        score_history: list[ScoreHistoryPoint] = []

        for row in rows:
            eid = row["exam_id"]
            sid = row["subject_id"]

            if eid not in exams_map:
                exams_map[eid] = {"exam_name": row["exam_name"], "subjects": {}}

            subjects = exams_map[eid]["subjects"]
            if sid not in subjects:
                subjects[sid] = {
                    "subject_name": row["subject_name"],
                    "sessions": [],
                    "module_scores": {},
                }
            subjects[sid]["sessions"].append(row)

            for module_key, score in (row["score_breakdown"] or {}).items():
                if score is None:
                    continue
                label = _MODULE_LABELS.get(module_key, module_key.capitalize())
                counts = (row.get("module_question_counts") or {}).get(module_key, {})
                bucket = subjects[sid]["module_scores"].setdefault(
                    label, {"scores": [], "correct": 0, "incorrect": 0, "total": 0}
                )
                bucket["scores"].append(score)
                bucket["correct"] += counts.get("correct", 0)
                bucket["incorrect"] += counts.get("incorrect", 0)
                bucket["total"] += counts.get("total", 0)

            if row["score"] is not None and row["submitted_at"]:
                score_history.append(ScoreHistoryPoint(
                    date=row["submitted_at"],
                    score=row["score"],
                    exam_name=row["exam_name"],
                ))

        # ── Construction de la réponse à partir du regroupement ──
        exams_list: list[ExamProgressResponse] = []
        for eid, edata in exams_map.items():
            all_exam_sessions: list[dict] = []
            subjects_list: list[SubjectScoreBreakdown] = []

            for sid, sdata in edata["subjects"].items():
                sessions = sdata["sessions"]
                all_exam_sessions.extend(sessions)

                scores = [s["score"] for s in sessions if s["score"] is not None]
                dates = [s["submitted_at"] for s in sessions if s["submitted_at"]]

                modules = [
                    ModuleScoreBreakdown(
                        module_name=label,
                        average_score=sum(b["scores"]) / len(b["scores"]) if b["scores"] else None,
                        questions_correct=b["correct"],
                        questions_incorrect=b["incorrect"],
                        questions_total=b["total"],
                    )
                    for label, b in sdata["module_scores"].items()
                ]

                last_session_id = None
                if dates:
                    last_row = max(sessions, key=lambda s: s["submitted_at"] or datetime.min)
                    last_session_id = last_row.get("session_id")

                subjects_list.append(SubjectScoreBreakdown(
                    subject_id=sid,
                    subject_name=sdata["subject_name"],
                    total_sessions=len(sessions),
                    average_score=sum(scores) / len(scores) if scores else None,
                    last_session_at=max(dates) if dates else None,
                    last_session_id=last_session_id,
                    modules=modules,
                ))

            exam_scores = [s["score"] for s in all_exam_sessions if s["score"] is not None]
            exam_dates = [s["submitted_at"] for s in all_exam_sessions if s["submitted_at"]]

            exams_list.append(ExamProgressResponse(
                exam_id=eid,
                exam_name=edata["exam_name"],
                total_sessions=len(all_exam_sessions),
                average_score=sum(exam_scores) / len(exam_scores) if exam_scores else None,
                last_session_at=max(exam_dates) if exam_dates else None,
                subjects=subjects_list,
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
        
    async def get_student_progress_detail(
        self, student_id: UUID, requester: User
    ) -> "StudentDetailedProgressResponse":
        """Wrapper director/secretary — check de scope puis délègue à
        l'agrégation partagée avec la vue enseignant."""
        from app.modules.centers.repository import BranchRepository

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

        return await self._get_student_progress_detail_unscoped(student_id)

    async def get_student_progress_detail_for_teacher(
        self, student_id: UUID, teacher: User
    ) -> "StudentDetailedProgressResponse":
        from app.modules.training_sessions.service import TrainingSessionService

        await TrainingSessionService(self.db).assert_teacher_can_view_student(teacher, student_id)
        return await self._get_student_progress_detail_unscoped(student_id)
    
    async def create_student_quick(
        self, data: StudentQuickCreateRequest, staff: User
    ) -> User:
        from app.modules.centers.repository import BranchRepository
        from uuid import uuid4
        from app.shared.security.password import hash_password
        import secrets

        branch_repo = BranchRepository(self.db)

        if staff.role == UserRole.center_director:
            if not data.branch_id:
                raise BadRequestException(detail="branch_id requis pour un directeur.")
            branch = await branch_repo.get_by_id_or_404(data.branch_id)
            if branch.center_id != staff.center_id:
                raise ForbiddenException(detail="Cette succursale n'appartient pas à votre centre.")
            target_branch_id = branch.id
        else:
            branch = await branch_repo.get_by_id_or_404(staff.branch_id)
            target_branch_id = staff.branch_id

        placeholder_email = f"eleve-{uuid4().hex[:12]}{PLACEHOLDER_EMAIL_DOMAIN}"
        placeholder_password = secrets.token_urlsafe(24)
        phone = self._normalized_phone(data.phone)
        await self._check_phone_available(phone)

        return await self.repo.create(
            email=placeholder_email,
            hashed_password=hash_password(placeholder_password),
            full_name=data.full_name,
            phone=phone,
            is_active=True,
            is_admin=False,
            is_verified=False,
            role=UserRole.student,
            branch_id=target_branch_id,
            ai_credits=0,
        )
        
    async def list_teachers_for_director(self, director: User) -> list[User]:
        return await self.repo.find_teachers_by_center(director.center_id)

    async def list_teachers_for_secretary(self, secretary: User) -> list[User]:
        return await self.repo.find_teachers_by_branch(secretary.branch_id)
    
        # ── Inscriptions via le lien du centre ───

    async def _staff_branch_ids(self, staff: User) -> list[UUID]:
        """Secrétaire : sa succursale. Directeur : toutes celles du centre."""
        from app.modules.centers.repository import BranchRepository

        if staff.role == UserRole.branch_secretary and staff.branch_id:
            return [staff.branch_id]
        if staff.role == UserRole.center_director and staff.center_id:
            branches = await BranchRepository(self.db).find_by_center(staff.center_id)
            return [b.id for b in branches]
        raise ForbiddenException(detail="Action réservée aux secrétaires et directeurs.")

    async def list_join_requests(self, staff: User) -> list[dict]:
        from sqlalchemy import select
        from app.modules.centers.models import Branch

        branch_ids = await self._staff_branch_ids(staff)
        students = await self.repo.find_join_requests(branch_ids)
        if not students:
            return []

        result = await self.db.execute(select(Branch).where(Branch.id.in_(branch_ids)))
        branch_names = {b.id: b.name for b in result.scalars().all()}

        return [
            {
                "id": s.id,
                "full_name": s.full_name,
                "phone": s.phone,
                "email": None if s.email.endswith(PLACEHOLDER_EMAIL_DOMAIN) else s.email,
                "branch_id": s.requested_branch_id,
                "branch_name": branch_names.get(s.requested_branch_id, ""),
                "requested_at": s.join_requested_at,
            }
            for s in students
        ]

    async def _get_join_request(self, student_id: UUID, staff: User) -> User:
        student = await self.repo.get_by_id_or_404(student_id)
        if student.branch_id or not student.requested_branch_id:
            raise BadRequestException(detail="Cette inscription a déjà été traitée.")
        if student.requested_branch_id not in await self._staff_branch_ids(staff):
            raise ForbiddenException(detail="Cette inscription ne concerne pas votre succursale.")
        return student

    async def approve_join_request(
        self, student_id: UUID, target_level_id: UUID, staff: User
    ) -> User:
        """Validation : rattachement à la succursale et au niveau, rien de plus.
        Les crédits et l'accès aux sujets arrivent à l'activation, quand le
        centre encaisse le paiement de l'élève."""
        from app.modules.centers.repository import BranchRepository
        from app.modules.exams.models import Level

        student = await self._get_join_request(student_id, staff)
        branch = await BranchRepository(self.db).get_by_id_or_404(student.requested_branch_id)

        if not await self.db.get(Level, target_level_id):
            raise BadRequestException(detail="Niveau introuvable.")

        return await self.repo.update(
            student.id,
            branch_id=branch.id,
            requested_branch_id=None,
            join_requested_at=None,
            target_level_id=target_level_id,
            learning_track="exam",
        )

    async def reject_join_request(self, student_id: UUID, staff: User) -> None:
        """Refus : la demande est retirée, le compte reste un compte
        individuel sans crédit."""
        student = await self._get_join_request(student_id, staff)
        await self.repo.update(student.id, requested_branch_id=None, join_requested_at=None)