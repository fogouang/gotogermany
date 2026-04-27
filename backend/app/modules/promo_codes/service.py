"""
app/modules/promo_codes/service.py
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.promo_codes.models import PromoCode
from app.modules.promo_codes.repository import PromoCodeRepository
from app.modules.promo_codes.schemas import (
    PromoCodeCreateRequest,
    PromoCodeUpdateRequest,
    PromoCodeValidateResponse,
)
from app.modules.exams.repository import ExamRepository
from app.shared.exceptions.http import BadRequestException, NotFoundException


class PromoCodeService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PromoCodeRepository(db)
        self.exam_repo = ExamRepository(db)

    async def get_all(self) -> list[PromoCode]:
        return list(await self.repo.get_all(skip=0, limit=1000))

    async def get_by_id(self, code_id: UUID) -> PromoCode:
        return await self.repo.get_by_id_or_404(code_id)

    async def create(self, data: PromoCodeCreateRequest) -> PromoCode:
        # Force le code en majuscules
        code_upper = data.code.upper()

        existing = await self.repo.find_by_code(code_upper)
        if existing:
            raise BadRequestException(
                detail=f"Le code '{code_upper}' existe déjà."
            )

        payload = data.model_dump()
        payload["code"] = code_upper
        return await self.repo.create(**payload)

    async def update(
        self, code_id: UUID, data: PromoCodeUpdateRequest
    ) -> PromoCode:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.repo.get_by_id_or_404(code_id)
        return await self.repo.update(code_id, **update_data)

    async def delete(self, code_id: UUID) -> bool:
        return await self.repo.delete(code_id)

    async def validate(
        self, code: str, exam_id: UUID
    ) -> PromoCodeValidateResponse:
        """
        Valide un code promo avant paiement.
        Retourne la réduction applicable sur le prix de l'exam.
        """
        # Récupérer le prix de l'exam
        # TODO: quand table pricing sera en place, charger le vrai prix
        # Pour l'instant on utilise une valeur fictive de 5000 XAF
        exam = await self.exam_repo.get_by_id(exam_id)
        if not exam:
            raise NotFoundException(resource="Exam", identifier=str(exam_id))

        amount_gross = 5000  # TODO: remplacer par pricing réel

        promo = await self.repo.find_by_code(code.upper())

        if not promo:
            return PromoCodeValidateResponse(
                code=code.upper(),
                is_valid=False,
                message="Code promo invalide.",
            )

        if not promo.is_active:
            return PromoCodeValidateResponse(
                code=code.upper(),
                is_valid=False,
                message="Ce code promo est désactivé.",
            )

        now = datetime.now(timezone.utc)
        if promo.expires_at and promo.expires_at < now:
            return PromoCodeValidateResponse(
                code=code.upper(),
                is_valid=False,
                message="Ce code promo est expiré.",
            )

        if promo.is_exhausted:
            return PromoCodeValidateResponse(
                code=code.upper(),
                is_valid=False,
                message="Ce code promo a atteint sa limite d'utilisations.",
            )

        # Calculer la réduction
        discount_amount = promo.compute_discount(amount_gross)
        amount_paid = amount_gross - discount_amount

        return PromoCodeValidateResponse(
            code=promo.code,
            is_valid=True,
            discount_type=promo.discount_type,
            discount_value=promo.discount_value,
            amount_gross=amount_gross,
            amount_paid=amount_paid,
            discount_amount=discount_amount,
            message=f"Code valide — réduction de {discount_amount} XAF appliquée.",
        )