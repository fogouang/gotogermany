"""
app/modules/ai_credit_purchases/service.py
"""
import logging
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_credit_purchases.repository import AICreditPurchaseRepository
from app.modules.ai_credit_purchases.schemas import (
    CreditBalanceResponse,
    CreditPricingResponse,
    CreditPurchaseHistoryItem,
    CreditPurchaseHistoryResponse,
    CreditPurchaseRequest,
    CreditPurchaseResponse,
    ManualCreditGrantRequest,
    ManualCreditGrantResponse,
)
from app.modules.payments.models import Payment
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)

PRICE_PER_CREDIT: int = 50   # FCFA — ajuster selon ton pricing
MIN_PURCHASE: int = 5
MAX_PURCHASE: int = 500


class AICreditPurchaseService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AICreditPurchaseRepository(db)

    # =========================================================================
    # PRICING
    # =========================================================================

    def get_pricing_info(self) -> CreditPricingResponse:
        examples = [
            {"credits": q, "price": q * PRICE_PER_CREDIT}
            for q in [5, 10, 20, 50, 100]
        ]
        return CreditPricingResponse(
            price_per_credit=PRICE_PER_CREDIT,
            min_purchase=MIN_PURCHASE,
            max_purchase=MAX_PURCHASE,
            examples=examples,
        )

    # =========================================================================
    # ACHAT VIA MYCOOLPAY
    # =========================================================================

    async def purchase_credits(self, user_id: UUID, data: CreditPurchaseRequest) -> CreditPurchaseResponse:
        from app.modules.payments.mycoolpay import MyCoolPayClient

        total = data.credits * PRICE_PER_CREDIT
        ref = self._generate_reference()

        payment = Payment(
            user_id=user_id,
            exam_id=None,
            plan_id=None,
            amount_gross=total,
            amount_paid=total,
            commission_due=0.0,
            currency="XAF",
            payment_status="PENDING",
            transaction_reference=ref,
            operator=data.payment_method.upper(),
        )
        self.db.add(payment)
        await self.db.flush()

        await self.repo.create(
            payment_id=payment.id,
            user_id=user_id,
            credits_purchased=data.credits,
            price_per_credit=float(PRICE_PER_CREDIT),
            total_amount=float(total),
        )

        try:
            coolpay = MyCoolPayClient()
            coolpay_response = await coolpay.create_payin(
                transaction_amount=total,
                customer_phone_number=data.phone_number,
                app_transaction_ref=ref,
                transaction_reason=f"Achat {data.credits} crédits IA GoToGermany",
            )
        except Exception as e:
            await self.db.rollback()
            raise BadRequestException(detail=f"Erreur paiement : {e}")

        mycoolpay_ref = coolpay_response.get("transaction_ref")
        if mycoolpay_ref:
            payment.mycoolpay_ref = mycoolpay_ref

        await self.db.commit()

        return CreditPurchaseResponse(
            payment_id=payment.id,
            invoice_number=ref,          # pas de table invoices séparée ici
            credits=data.credits,
            price_per_credit=float(PRICE_PER_CREDIT),
            total_amount=float(total),
            payment_status="PENDING",
            ussd=coolpay_response.get("ussd"),
            action=coolpay_response.get("action"),
            redirect_url=coolpay_response.get("redirect_url"),
            transaction_reference=ref,
        )

    # =========================================================================
    # WEBHOOK — appelé depuis PaymentService.handle_webhook()
    # =========================================================================

    async def on_payment_completed(self, payment: Payment) -> None:
        """Crédite l'utilisateur après confirmation webhook."""
        purchase = await self.repo.get_by_payment_id(payment.id)
        if not purchase:
            return

        result = await self.db.execute(select(User).where(User.id == payment.user_id))
        user = result.scalar_one_or_none()
        if user:
            user.ai_credits += purchase.credits_purchased
            await self.db.flush()
            logger.info(f"User {user.id} crédité de {purchase.credits_purchased} crédits IA")

    # =========================================================================
    # ACCORD MANUEL — Admin
    # =========================================================================

    async def grant_manual(self, data: ManualCreditGrantRequest, admin_id: UUID) -> ManualCreditGrantResponse:
        result = await self.db.execute(select(User).where(User.id == data.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException(resource="User", identifier=str(data.user_id))

        ref = f"GTG-M-CR-{uuid4().hex[:8].upper()}"

        payment = Payment(
            user_id=data.user_id,
            exam_id=None,
            plan_id=None,
            amount_gross=data.credits * PRICE_PER_CREDIT,
            amount_paid=data.credits * PRICE_PER_CREDIT,
            commission_due=0.0,
            currency="XAF",
            payment_status="COMPLETED",
            transaction_reference=ref,
            operator="MANUAL",
            completed_at=datetime.utcnow(),
        )
        self.db.add(payment)
        await self.db.flush()

        await self.repo.create(
            payment_id=payment.id,
            user_id=data.user_id,
            credits_purchased=data.credits,
            price_per_credit=float(PRICE_PER_CREDIT),
            total_amount=float(data.credits * PRICE_PER_CREDIT),
        )

        user.ai_credits += data.credits
        await self.db.flush()
        await self.db.commit()

        logger.info(f"Admin {admin_id} — accord manuel {data.credits} crédits → user {data.user_id}")

        return ManualCreditGrantResponse(
            user_id=data.user_id,
            credits_granted=data.credits,
            new_balance=user.ai_credits,
        )

    # =========================================================================
    # HISTORIQUE & BALANCE
    # =========================================================================

    async def get_purchase_history(self, user_id: UUID) -> CreditPurchaseHistoryResponse:
        rows = await self.repo.get_user_history(user_id)
        stats = await self.repo.get_user_stats(user_id)

        items = [
            CreditPurchaseHistoryItem(
                id=purchase.id,
                payment_id=purchase.payment_id,
                credits_purchased=purchase.credits_purchased,
                price_per_credit=float(purchase.price_per_credit),
                total_amount=float(purchase.total_amount),
                payment_method=payment.operator or "mobile_money",
                payment_status=payment.payment_status,
                transaction_reference=payment.transaction_reference,
                created_at=payment.created_at,
            )
            for purchase, payment in rows
        ]

        return CreditPurchaseHistoryResponse(
            purchases=items,
            total_spent=stats["total_spent"],
            total_credits_purchased=stats["total_credits_purchased"],
        )

    async def get_balance(self, user_id: UUID) -> CreditBalanceResponse:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException(resource="User", identifier=str(user_id))
        return CreditBalanceResponse(
            ai_credits=user.ai_credits,
            price_per_credit=PRICE_PER_CREDIT,
        )

    async def get_admin_history(self, limit: int = 20) -> list[CreditPurchaseHistoryItem]:
        """Historique global des crédits accordés manuellement — pour l'admin."""
        rows = await self.repo.get_all_manual(limit=limit)
        return [
            CreditPurchaseHistoryItem(
                id=purchase.id,
                payment_id=purchase.payment_id,
                credits_purchased=purchase.credits_purchased,
                price_per_credit=float(purchase.price_per_credit),
                total_amount=float(purchase.total_amount),
                payment_method=payment.operator or "MANUAL",
                payment_status=payment.payment_status,
                transaction_reference=payment.transaction_reference,
                created_at=payment.created_at,
            )
            for purchase, payment in rows
        ]
        
    # =========================================================================
    # HELPERS
    # =========================================================================

    def _generate_reference(self) -> str:
        year = datetime.now().year
        return f"GTG-CR-{year}-{uuid4().hex[:6].upper()}"