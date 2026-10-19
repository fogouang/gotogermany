"""
app/modules/centers/service.py
"""
import secrets
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.centers.models import Center, Branch, CenterCreditTransaction
from app.modules.centers.repository import (
    CenterRepository,
    BranchRepository,
    CenterCreditTransactionRepository,
)
from app.modules.centers.schemas import (
    CenterCreateRequest,
    BranchCreateRequest,
    CenterCreditTransactionResponse,
    CenterUpdateRequest,
)
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException


class CenterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.center_repo = CenterRepository(db)
        self.branch_repo = BranchRepository(db)
        self.credit_txn_repo = CenterCreditTransactionRepository(db)

    # ── Admin ─────────────────────────────────

    async def create_center(self, data: CenterCreateRequest) -> Center:
        center = await self.center_repo.create(
            name=data.name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            is_active=True,
        )
        # Branche "principale" créée automatiquement, transparente pour le centre
        await self.branch_repo.create(
            center_id=center.id,
            name=f"{center.name} (Principal)",
            is_main=True,
        )
        return center

    async def create_branch(self, center_id: UUID, data: BranchCreateRequest) -> Branch:
        center = await self.center_repo.get_by_id_or_404(center_id)
        return await self.branch_repo.create(
            center_id=center.id,
            name=data.name,
            is_main=data.is_main,
        )

    async def list_centers(self, skip: int = 0, limit: int = 100) -> list[Center]:
        return list(await self.center_repo.get_all(skip=skip, limit=limit))

    async def toggle_active(self, center_id: UUID) -> Center:
        """Désactive/réactive un centre. Ne supprime rien."""
        center = await self.center_repo.get_by_id_or_404(center_id)
        return await self.center_repo.update(center_id, is_active=not center.is_active)

    # ── Directeur ─────────────────────────────

    async def list_my_branches(self, center_id: UUID) -> list[Branch]:
        return await self.branch_repo.find_by_center(center_id)

    async def update_my_center(self, center_id: UUID, data: CenterUpdateRequest) -> Center:
        """Le directeur renseigne l'adresse affichée sur les reçus PDF de son centre."""
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.center_repo.get_by_id_or_404(center_id)
        return await self.center_repo.update(center_id, **update_data)

    async def update_my_logo(self, center_id: UUID, logo_path: str) -> Center:
        return await self.center_repo.update(center_id, logo_path=logo_path)

    # ── Pool de crédits IA ────────────────────

    async def recharge_pool(
        self, center_id: UUID, amount: int, admin: User, reason: str | None = None
    ) -> Center:
        """Rechargement manuel du pool du centre : admin uniquement."""
        center = await self.center_repo.get_by_id_or_404(center_id)
        new_balance = center.ai_credit_pool_balance + amount
        return await self.center_repo.update(center_id, ai_credit_pool_balance=new_balance)

    async def update_default_credits(
        self, center_id: UUID, default_credits: int, director: User
    ) -> Center:
        return await self.center_repo.update(
            center_id, default_credits_per_student=default_credits
        )

    async def adjust_student_credits(
        self,
        center_id: UUID,
        student: User,
        amount: int,
        performed_by: User,
        reason: str | None = None,
    ) -> User:
        """Rechargement individuel d'un étudiant, prélevé du pool du centre et journalisé."""
        center = await self.center_repo.get_by_id_or_404(center_id)

        if center.ai_credit_pool_balance < amount:
            raise BadRequestException(
                detail=(
                    f"Pool de crédits insuffisant pour ce centre "
                    f"({center.ai_credit_pool_balance} restants). "
                    "Contactez GoToGermany pour un rechargement."
                )
            )

        new_pool_balance = center.ai_credit_pool_balance - amount
        await self.center_repo.update(center_id, ai_credit_pool_balance=new_pool_balance)

        from app.modules.users.repository import UserRepository
        updated_student = await UserRepository(self.db).update(
            student.id, ai_credits=student.ai_credits + amount
        )

        await self.credit_txn_repo.create(
            center_id=center_id,
            student_id=student.id,
            performed_by=performed_by.id,
            amount=amount,
            pool_balance_after=new_pool_balance,
            reason=reason,
        )
        return updated_student

    async def get_credit_transactions_for_director(
        self, center_id: UUID
    ) -> list[CenterCreditTransactionResponse]:
        transactions = await self.credit_txn_repo.find_by_center(center_id)
        return [_to_transaction_response(t) for t in transactions]

    async def get_credit_transactions_for_secretary(
        self, secretary: User
    ) -> list[CenterCreditTransactionResponse]:
        transactions = await self.credit_txn_repo.find_by_performer(secretary.id)
        return [_to_transaction_response(t) for t in transactions]

    # ── Lien d'inscription des élèves ─────────

    async def center_id_for_staff(self, user: User) -> UUID:
        """Directeur : son centre. Secrétaire : le centre de sa succursale."""
        if user.center_id:
            return user.center_id
        if user.branch_id:
            branch = await self.branch_repo.get_by_id_or_404(user.branch_id)
            return branch.center_id
        raise BadRequestException(detail="Aucun centre rattaché à ce compte.")

    async def get_join_link(self, center_id: UUID) -> Center:
        """Crée le jeton à la première consultation."""
        center = await self.center_repo.get_by_id_or_404(center_id)
        if not center.join_token:
            center = await self.center_repo.update(center_id, join_token=_new_join_token())
        return center

    async def regenerate_join_link(self, center_id: UUID) -> Center:
        """L'ancien lien cesse immédiatement de fonctionner."""
        return await self.center_repo.update(center_id, join_token=_new_join_token())

    async def set_join_enabled(self, center_id: UUID, enabled: bool) -> Center:
        await self.get_join_link(center_id)
        return await self.center_repo.update(center_id, join_enabled=enabled)

    async def find_open_center_by_join_token(self, token: str) -> Center | None:
        """Centre dont le lien est valide : jeton connu, lien actif, centre actif."""
        center = await self.center_repo.find_by_join_token(token)
        if center is None or not center.join_enabled or not center.is_active:
            return None
        return center

    async def resolve_join_branch(self, token: str, branch_id: UUID | None) -> Branch:
        center = await self.find_open_center_by_join_token(token)
        if center is None:
            raise BadRequestException(detail="Ce lien d'inscription n'est plus valide.")
        if branch_id is None:
            raise BadRequestException(detail="Choisissez votre succursale.")
        branch = await self.branch_repo.get_by_id(branch_id)
        if branch is None or branch.center_id != center.id:
            raise BadRequestException(detail="Cette succursale n'appartient pas à ce centre.")
        return branch


def _new_join_token() -> str:
    return secrets.token_urlsafe(16)


def _to_transaction_response(txn: CenterCreditTransaction) -> CenterCreditTransactionResponse:
    return CenterCreditTransactionResponse(
        id=txn.id,
        student_id=txn.student_id,
        student_name=txn.student.full_name if txn.student else "",
        performed_by=txn.performed_by,
        performer_name=txn.performer.full_name if txn.performer else "",
        amount=txn.amount,
        pool_balance_after=txn.pool_balance_after,
        reason=txn.reason,
        created_at=txn.created_at,
    )