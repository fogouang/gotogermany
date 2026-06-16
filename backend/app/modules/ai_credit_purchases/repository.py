"""
app/modules/ai_credit_purchases/repository.py
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_credit_purchases.models import AICreditPurchase
from app.modules.payments.models import Payment


class AICreditPurchaseRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **data) -> AICreditPurchase:
        purchase = AICreditPurchase(**data)
        self.db.add(purchase)
        await self.db.flush()
        await self.db.refresh(purchase)
        return purchase

    async def get_by_payment_id(self, payment_id: UUID) -> AICreditPurchase | None:
        result = await self.db.execute(
            select(AICreditPurchase).where(AICreditPurchase.payment_id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_user_history(self, user_id: UUID, limit: int = 50):
        query = (
            select(AICreditPurchase, Payment)
            .join(Payment, AICreditPurchase.payment_id == Payment.id)
            .where(AICreditPurchase.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.all())

    async def get_user_stats(self, user_id: UUID) -> dict:
        query = (
            select(
                func.coalesce(func.sum(AICreditPurchase.total_amount), 0).label("total_spent"),
                func.coalesce(func.sum(AICreditPurchase.credits_purchased), 0).label("total_credits"),
            )
            .join(Payment, AICreditPurchase.payment_id == Payment.id)
            .where(
                AICreditPurchase.user_id == user_id,
                Payment.payment_status == "COMPLETED",   # string direct
            )
        )
        result = await self.db.execute(query)
        row = result.one()
        return {
            "total_spent": float(row.total_spent),
            "total_credits_purchased": int(row.total_credits),
        }
        
    async def get_all_manual(self, limit: int = 20) -> list[tuple]:
        """
        Tous les achats de crédits avec operator=MANUAL — pour l'admin.
        Jointure Payment pour avoir user_id, status, date.
        """
        query = (
            select(AICreditPurchase, Payment)
            .join(Payment, AICreditPurchase.payment_id == Payment.id)
            .where(Payment.operator == "MANUAL")
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.all())