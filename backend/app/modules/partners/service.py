"""
app/modules/partners/service.py
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partners.models import Partner
from app.modules.partners.repository import PartnerRepository
from app.modules.partners.schemas import (
    PartnerCreateRequest,
    PartnerStatsResponse,
    PartnerUpdateRequest,
)
from app.shared.exceptions.http import BadRequestException


class PartnerService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PartnerRepository(db)

    async def get_all(self) -> list[Partner]:
        return list(await self.repo.get_all(skip=0, limit=1000))

    async def get_by_id(self, partner_id: UUID) -> Partner:
        return await self.repo.get_by_id_or_404(partner_id)

    async def create(self, data: PartnerCreateRequest) -> Partner:
        existing = await self.repo.find_by_email(str(data.contact_email))
        if existing:
            raise BadRequestException(
                detail=f"Un partenaire avec l'email '{data.contact_email}' existe déjà."
            )
        return await self.repo.create(**data.model_dump())

    async def update(self, partner_id: UUID, data: PartnerUpdateRequest) -> Partner:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return await self.repo.get_by_id_or_404(partner_id)
        return await self.repo.update(partner_id, **update_data)

    async def delete(self, partner_id: UUID) -> bool:
        return await self.repo.delete(partner_id)

    async def get_stats(self, partner_id: UUID) -> PartnerStatsResponse:
        """Stats d'un partenaire — codes + utilisations + commissions."""
        partner = await self.repo.get_by_id_or_404(partner_id)

        # Charger les codes promo du partenaire
        from app.modules.promo_codes.repository import PromoCodeRepository
        from sqlalchemy import select, func
        from app.modules.promo_codes.models import PromoCode
        from app.modules.payments.models import Payment

        promo_repo = PromoCodeRepository(self.db)
        codes = await promo_repo.get_by_partner(partner_id)

        total_codes = len(codes)
        active_codes = sum(1 for c in codes if c.is_active)
        total_uses = sum(c.used_count for c in codes)

        # Commissions dues — somme des payments liés aux codes de ce partenaire
        code_ids = [c.id for c in codes]
        total_commission = 0.0
        if code_ids:
            result = await self.db.execute(
                select(func.sum(Payment.commission_due))
                .where(
                    Payment.promo_code_id.in_(code_ids),
                    Payment.payment_status == "COMPLETED",
                )
            )
            total_commission = result.scalar_one_or_none() or 0.0

        return PartnerStatsResponse(
            partner_id=partner.id,
            partner_name=partner.name,
            total_codes=total_codes,
            active_codes=active_codes,
            total_uses=total_uses,
            total_commission_due=total_commission,
        )