"""
app/modules/payments/repository.py
"""
import time
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment
from app.shared.database.repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):

    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def find_by_transaction_ref(self, transaction_ref: str) -> Payment | None:
        """Trouver par transaction_reference (notre ref interne)."""
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_reference == transaction_ref)
        )
        return result.scalar_one_or_none()

    async def find_by_mycoolpay_ref(self, mycoolpay_ref: str) -> Payment | None:
        """Trouver par référence My-CoolPay."""
        result = await self.db.execute(
            select(Payment).where(Payment.mycoolpay_ref == mycoolpay_ref)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_completed_by_user(self, user_id: UUID) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
            .where(Payment.user_id == user_id, Payment.payment_status == "COMPLETED")
            .order_by(Payment.completed_at.desc())
        )
        return list(result.scalars().all())

    async def generate_transaction_reference(self) -> str:
        """
        Génère une référence unique : GTG-YYYY-XXXXX-TIMESTAMP
        Ex: GTG-2026-00042-1745123456
        """
        year = datetime.now().year
        prefix = f"GTG-{year}-"

        result = await self.db.execute(
            select(Payment.transaction_reference)
            .where(Payment.transaction_reference.like(f"{prefix}%"))
            .order_by(Payment.created_at.desc())
            .limit(1)
        )
        last = result.scalar_one_or_none()

        if last:
            parts = last.split("-")
            try:
                next_number = int(parts[2]) + 1
            except (IndexError, ValueError):
                next_number = 1
        else:
            next_number = 1

        timestamp = int(time.time())
        return f"{prefix}{next_number:05d}-{timestamp}"

    async def get_summary(self) -> dict:
        """Stats paiements pour le dashboard admin."""
        result = await self.db.execute(
            select(
                func.count(Payment.id).label("total"),
                func.count(Payment.id).filter(Payment.payment_status == "COMPLETED").label("completed"),
                func.count(Payment.id).filter(Payment.payment_status == "FAILED").label("failed"),
                func.coalesce(func.sum(Payment.amount_paid).filter(Payment.payment_status == "COMPLETED"), 0).label("revenue"),
                func.coalesce(func.sum(Payment.amount_gross - Payment.amount_paid).filter(Payment.payment_status == "COMPLETED"), 0).label("discounts"),
                func.coalesce(func.sum(Payment.commission_due).filter(Payment.payment_status == "COMPLETED"), 0.0).label("commissions"),
            )
        )
        row = result.one()
        return {
            "total_payments": row.total,
            "total_completed": row.completed,
            "total_failed": row.failed,
            "total_revenue": row.revenue,
            "total_discounts": row.discounts,
            "total_commissions_due": row.commissions,
        }