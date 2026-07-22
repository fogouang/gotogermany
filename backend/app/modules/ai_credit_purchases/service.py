"""
app/modules/ai_credit_purchases/service.py
"""
import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone

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
from app.modules.payments.pawapay import PawapayClient
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)

PRICE_PER_CREDIT: int = 50
MIN_PURCHASE: int = 5
MAX_PURCHASE: int = 500


class AICreditPurchaseService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AICreditPurchaseRepository(db)
        self.pawapay = PawapayClient()

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

    async def purchase_credits(self, user_id: UUID, data: CreditPurchaseRequest) -> CreditPurchaseResponse:
        if data.credits < MIN_PURCHASE or data.credits > MAX_PURCHASE:
            raise BadRequestException(
                detail=f"L'achat doit être compris entre {MIN_PURCHASE} et {MAX_PURCHASE} crédits."
            )

        total = data.credits * PRICE_PER_CREDIT
        ref = self._generate_reference()

        payment = Payment(
            user_id=user_id,
            level_id=None,
            plan_id=None,
            amount_gross=total,
            amount_paid=total,
            commission_due=0.0,
            currency="XAF",
            payment_status="PENDING",
            transaction_reference=ref,
            operator=data.operator,
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

        phone = data.phone_number.strip()
        if not phone.startswith("237"):
            phone = f"237{phone}"

        try:
            pawapay_response = await self.pawapay.initiate_deposit(
                deposit_id=str(payment.id),
                amount=total,
                phone_number=phone,
                provider="MTN_MOMO_CMR" if data.operator == "MTN" else "ORANGE_CMR",
                client_reference_id=ref,
                customer_message="Achat crédits IA GoToGermany",
                metadata={"app": "gotogermany"},
            )
        except Exception as e:
            await self.db.rollback()
            raise BadRequestException(detail=f"Erreur paiement : {e}")

        pawapay_status = pawapay_response.get("status")
        if pawapay_status == "REJECTED":
            failure = pawapay_response.get("failureReason", {})
            payment.payment_status = "FAILED"
            await self.db.commit()
            raise BadRequestException(
                detail=f"Paiement rejeté : {failure.get('failureMessage', 'Erreur inconnue')}"
            )

        payment.pawapay_deposit_id = str(payment.id)
        await self.db.commit()

        return CreditPurchaseResponse(
            payment_id=payment.id,
            invoice_number=ref,
            credits=data.credits,
            price_per_credit=float(PRICE_PER_CREDIT),
            total_amount=float(total),
            payment_status="PENDING",
            transaction_reference=ref,
        )

    async def on_payment_completed(self, payment: Payment) -> bool:
        """Crédite l'utilisateur après confirmation callback pawaPay.
        Retourne True si ce payment_id correspond bien à un achat de
        crédits (et crédite dans ce cas) — False sinon."""
        purchase = await self.repo.get_by_payment_id(payment.id)
        if not purchase:
            return False

        result = await self.db.execute(select(User).where(User.id == payment.user_id))
        user = result.scalar_one_or_none()
        if user:
            user.ai_credits += purchase.credits_purchased
            await self.db.flush()
            await self.db.commit()
            logger.info(f"User {user.id} crédité de {purchase.credits_purchased} crédits IA")

        return True

    async def grant_manual(self, data: ManualCreditGrantRequest, admin_id: UUID) -> ManualCreditGrantResponse:
        result = await self.db.execute(select(User).where(User.id == data.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException(resource="User", identifier=str(data.user_id))

        ref = f"GTG-M-CR-{uuid4().hex[:8].upper()}"

        payment = Payment(
            user_id=data.user_id,
            level_id=None,
            plan_id=None,
            amount_gross=data.credits * PRICE_PER_CREDIT,
            amount_paid=data.credits * PRICE_PER_CREDIT,
            commission_due=0.0,
            currency="XAF",
            payment_status="COMPLETED",
            transaction_reference=ref,
            operator="MANUAL",
            completed_at=datetime.now(timezone.utc),
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

    def _generate_reference(self) -> str:
        year = datetime.now().year
        return f"GTG-CR-{year}-{uuid4().hex[:6].upper()}"