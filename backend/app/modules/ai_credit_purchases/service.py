"""
app/modules/ai_credit_purchases/service.py

Achat de crédits IA :
  - Mobile Money via Kratos (MTN, Orange), en FCFA
  - Carte bancaire via Stripe Checkout, en euros

Le statut est suivi comme pour les formules : GET /payments/status/{ref} relit
la transaction chez Kratos ou Stripe, et PaymentService._complete_payment()
appelle on_payment_completed() qui crédite l'élève.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.modules.ai_credit_purchases.repository import AICreditPurchaseRepository
from app.modules.ai_credit_purchases.schemas import (
    CreditBalanceResponse,
    CreditCardPurchaseRequest,
    CreditCardPurchaseResponse,
    CreditPricingResponse,
    CreditPurchaseHistoryItem,
    CreditPurchaseHistoryResponse,
    CreditPurchaseRequest,
    CreditPurchaseResponse,
    ManualCreditGrantRequest,
    ManualCreditGrantResponse,
)
from app.modules.payments.kratos import KratosClient, KratosError
from app.modules.payments.models import Payment
from app.modules.payments.stripe_client import StripeClient
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)

PRICE_PER_CREDIT: int = 50
MIN_PURCHASE: int = 5
MAX_PURCHASE: int = 500

# Page des crédits côté front (retour après paiement par carte)
CREDITS_PAGE_PATH = "/dashboard/credits"


class AICreditPurchaseService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AICreditPurchaseRepository(db)
        self.kratos = KratosClient()
        self.stripe = StripeClient()

    # ── Prix ─────────────────────────────────────────────

    async def _price_eur(self) -> float | None:
        """Prix d'un crédit en euros : réglage app_settings « ai_credit_price_eur », sinon .env."""
        from app.modules.settings.models import AppSetting

        row = (
            await self.db.execute(select(AppSetting).where(AppSetting.key == "ai_credit_price_eur"))
        ).scalar_one_or_none()
        raw = row.value if row else get_settings().AI_CREDIT_PRICE_EUR
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        return value if value > 0 else None

    async def get_pricing_info(self) -> CreditPricingResponse:
        examples = [
            {"credits": q, "price": q * PRICE_PER_CREDIT}
            for q in [5, 10, 20, 50, 100]
        ]
        price_eur = await self._price_eur() if self.stripe.enabled else None
        return CreditPricingResponse(
            price_per_credit=PRICE_PER_CREDIT,
            price_per_credit_eur=price_eur,
            min_purchase=MIN_PURCHASE,
            max_purchase=MAX_PURCHASE,
            examples=examples,
        )

    def _check_quantity(self, credits: int) -> None:
        if credits < MIN_PURCHASE or credits > MAX_PURCHASE:
            raise BadRequestException(
                detail=f"L'achat doit être compris entre {MIN_PURCHASE} et {MAX_PURCHASE} crédits."
            )

    async def _create_pending(
        self, user_id: UUID, credits: int, operator: str,
        charged_amount: int | None = None, charged_currency: str | None = None,
    ) -> tuple[Payment, str, int]:
        total = credits * PRICE_PER_CREDIT
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
            operator=operator,
            charged_amount=charged_amount,
            charged_currency=charged_currency,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.repo.create(
            payment_id=payment.id,
            user_id=user_id,
            credits_purchased=credits,
            price_per_credit=float(PRICE_PER_CREDIT),
            total_amount=float(total),
        )
        return payment, ref, total

    # ── Mobile Money (Kratos) ────────────────────────────

    async def purchase_credits(self, user_id: UUID, data: CreditPurchaseRequest) -> CreditPurchaseResponse:
        self._check_quantity(data.credits)
        payment, ref, total = await self._create_pending(user_id, data.credits, data.operator)

        try:
            tx = await self.kratos.create_collection(
                idempotency_key=ref,
                amount=total,
                phone_number=data.phone_number.strip(),
                provider="MTN_MOMO_CMR" if data.operator == "MTN" else "ORANGE_CMR",
                description=f"Crédits IA GoToGermany {ref}",
            )
        except KratosError as e:
            await self.db.rollback()
            logger.error(f"Kratos crédits refusé {ref} : {e} (code={e.code}, request_id={e.request_id})")
            raise BadRequestException(detail=f"Paiement refusé : {e}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Kratos crédits erreur {ref} : {e}")
            raise BadRequestException(detail="Le service de paiement est indisponible, réessayez.")

        # L'uuid Kratos est rangé dans pawapay_deposit_id, comme pour les formules
        if tx.get("uuid"):
            payment.pawapay_deposit_id = str(tx["uuid"])
        await self.db.commit()

        status = self.kratos.internal_status(tx.get("status"))
        if status != "PENDING":
            from app.modules.payments.service import PaymentService

            ps = PaymentService(self.db)
            if status == "COMPLETED":
                await ps._complete_payment(payment, tx)
            else:
                await ps._fail_payment(payment, tx)

        return CreditPurchaseResponse(
            payment_id=payment.id,
            invoice_number=ref,
            credits=data.credits,
            price_per_credit=float(PRICE_PER_CREDIT),
            total_amount=float(total),
            payment_status=status,
            transaction_reference=ref,
        )

    # ── Carte bancaire (Stripe) ──────────────────────────

    async def purchase_credits_card(self, user: User, data: CreditCardPurchaseRequest) -> CreditCardPurchaseResponse:
        self._check_quantity(data.credits)
        if not self.stripe.enabled:
            raise BadRequestException(detail="Le paiement par carte n'est pas disponible pour le moment.")
        price_eur = await self._price_eur()
        if not price_eur:
            raise BadRequestException(detail="Les crédits ne sont pas encore disponibles par carte.")

        eur_cents = int(round(data.credits * price_eur * 100))
        if eur_cents < 50:
            raise BadRequestException(detail="Montant trop faible pour un paiement par carte (minimum 0,50 €).")

        payment, ref, _ = await self._create_pending(
            user.id, data.credits, "STRIPE", charged_amount=eur_cents, charged_currency="EUR"
        )
        await self.db.commit()

        base = get_settings().FRONTEND_BASE_URL.rstrip("/")
        page = f"{base}/{data.locale}{CREDITS_PAGE_PATH}"
        try:
            session = await self.stripe.create_checkout_session(
                reference=ref,
                amount_cents=eur_cents,
                currency="EUR",
                product_name=f"GoToGermany · {data.credits} crédits IA",
                description="Crédits pour les corrections IA (Schreiben, Sprechen)",
                customer_email=user.email,
                success_url=f"{page}?ref={ref}",
                cancel_url=f"{page}?cancelled=1",
            )
        except Exception as e:
            payment.payment_status = "FAILED"
            await self.db.commit()
            logger.error(f"Stripe checkout crédits impossible pour {ref} : {e}")
            raise BadRequestException(detail="Le paiement par carte est indisponible, réessayez plus tard.")

        payment.provider_ref = session["id"]
        await self.db.commit()

        return CreditCardPurchaseResponse(
            payment_id=payment.id,
            transaction_reference=ref,
            checkout_url=session["url"],
            credits=data.credits,
            amount_eur=eur_cents / 100,
        )

    # ── Crédit après paiement ────────────────────────────

    async def on_payment_completed(self, payment: Payment) -> bool:
        """Crédite l'utilisateur après confirmation du paiement.
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

    # ── Lecture ──────────────────────────────────────────

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
                charged_amount=payment.charged_amount / 100 if payment.charged_amount else None,
                charged_currency=payment.charged_currency,
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