"""
app/modules/payments/service.py

Flow pawaPay :
  1. initiate_payment() → crée Payment(PENDING) → appelle pawaPay deposit
  2. Callback → handle_callback() → update COMPLETED/FAILED
  3. Si COMPLETED → _grant_level_access() → ExamAccess créé avec expires_at
  4. Facture PDF générée automatiquement
"""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment
from app.modules.payments.pawapay import PawapayClient
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import ManualPaymentRequest, PawapayCallbackPayload, PaymentInitiateRequest
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class PaymentService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaymentRepository(db)
        self.pawapay = PawapayClient()

    # ── Initiation ───────────────────────────────────────

    async def initiate_payment(
        self,
        data: PaymentInitiateRequest,
        current_user: User,
    ) -> dict:
        """
        Initie un paiement mobile money pour l'accès à un level.

        Steps :
          1. Charger Level + Plan
          2. Vérifier code promo si fourni → calculer réduction + commission
          3. Créer Payment(PENDING)
          4. Appeler pawaPay deposit
          5. Stocker pawapay_deposit_id
        """
        from app.modules.exams.models import Level
        from app.modules.plans.models import Plan

        # 1. Vérifier level
        level = await self.db.get(Level, data.level_id)
        if not level:
            raise NotFoundException(resource="Level", identifier=str(data.level_id))

        # 2. Vérifier plan
        plan = await self.db.get(Plan, data.plan_id)
        if not plan or not plan.is_active:
            raise NotFoundException(resource="Plan", identifier=str(data.plan_id))

        # 3. Code promo (optionnel)
        promo_code_id = None
        amount_gross = plan.price
        amount_paid = plan.price
        commission_due = 0.0

        if data.promo_code:
            promo_result = await self._apply_promo_code(
                code=data.promo_code,
                amount=amount_gross,
            )
            if promo_result:
                promo_code_id = promo_result["promo_code_id"]
                amount_paid = promo_result["amount_paid"]
                commission_due = promo_result["commission_due"]

        # 4. Générer référence interne
        transaction_reference = await self.repo.generate_transaction_reference()

        # 5. Créer Payment PENDING
        payment = await self.repo.create(
            user_id=current_user.id,
            level_id=data.level_id,
            plan_id=data.plan_id,
            promo_code_id=promo_code_id,
            amount_gross=amount_gross,
            amount_paid=amount_paid,
            commission_due=commission_due,
            currency="XAF",
            payment_status="PENDING",
            transaction_reference=transaction_reference,
            operator=data.operator,
        )

        # 6. Appeler pawaPay
        try:
            pawapay_response = await self.pawapay.initiate_deposit(
                deposit_id=str(payment.id),
                amount=amount_paid,
                phone_number=data.phone_number,
                provider="MTN_MOMO_CMR" if data.operator == "MTN" else "ORANGE_CMR",
                client_reference_id=transaction_reference,
                customer_message="GoToGermany",
            )
        except Exception as e:
            await self.repo.update(payment.id, payment_status="FAILED")
            raise BadRequestException(detail=f"Erreur paiement : {str(e)}")

        pawapay_status = pawapay_response.get("status")
        if pawapay_status == "REJECTED":
            failure = pawapay_response.get("failureReason", {})
            await self.repo.update(payment.id, payment_status="FAILED")
            raise BadRequestException(
                detail=f"Paiement rejeté : {failure.get('failureMessage', 'Erreur inconnue')}"
            )

        await self.repo.update(payment.id, pawapay_deposit_id=str(payment.id))

        return {
            "payment_id": payment.id,
            "transaction_reference": transaction_reference,
            "amount_gross": amount_gross,
            "amount_paid": amount_paid,
            "discount_amount": amount_gross - amount_paid,
            "currency": "XAF",
            "message": "Confirmez le paiement sur votre téléphone mobile.",
        }

    # ── Callback pawaPay ─────────────────────────────────

    async def handle_callback(self, payload: PawapayCallbackPayload) -> bool:
        """
        Traite le callback pawaPay.
        COMPLETED → grant level access + facture
        FAILED → marque comme échoué
        """
        payment = await self.repo.get_by_id(UUID(payload.depositId))
        if not payment:
            logger.error(f"Payment introuvable pour depositId: {payload.depositId}")
            raise NotFoundException(resource="Payment", identifier=payload.depositId)

        if payment.payment_status == "COMPLETED":
            logger.info(f"Payment {payment.id} déjà COMPLETED — ignoré")
            return True

        if payload.status == "COMPLETED":
            await self.repo.update(
                payment.id,
                payment_status="COMPLETED",
                pawapay_deposit_id=payload.depositId,
                completed_at=datetime.now(timezone.utc),
                webhook_payload=payload.model_dump(),
            )
            await self._grant_level_access(payment)
            await self._generate_invoice(payment)

        elif payload.status == "FAILED":
            await self.repo.update(
                payment.id,
                payment_status="FAILED",
                webhook_payload=payload.model_dump(),
            )

        return True

    # ── Grant Level Access ───────────────────────────────

    async def _grant_level_access(self, payment: Payment) -> None:
        """
        Crée ou renouvelle l'ExamAccess (sur level_id) après paiement réussi.
        expires_at = now + plan.duration_days
        """
        from app.modules.exam_access.models import ExamAccess
        from app.modules.exam_access.repository import ExamAccessRepository
        from app.modules.plans.models import Plan

        plan = await self.db.get(Plan, payment.plan_id)
        if not plan:
            logger.error(f"Plan {payment.plan_id} introuvable pour payment {payment.id}")
            return

        expires_at = datetime.now(timezone.utc) + timedelta(days=plan.duration_days)
        repo = ExamAccessRepository(self.db)

        existing = await repo.find_by_user_and_level(payment.user_id, payment.level_id)
        if existing:
            await repo.update(
                existing.id,
                expires_at=expires_at,
                payment_id=payment.id,
                access_type="paid",
            )
            logger.info(
                f"ExamAccess renouvelé — user {payment.user_id} "
                f"level {payment.level_id} — expires {expires_at}"
            )
        else:
            access = ExamAccess(
                user_id=payment.user_id,
                level_id=payment.level_id,
                access_type="paid",
                payment_id=payment.id,
                expires_at=expires_at,
                granted_at=datetime.now(timezone.utc),
            )
            self.db.add(access)
            await self.db.flush()
            logger.info(
                f"ExamAccess créé — user {payment.user_id} "
                f"level {payment.level_id} — expires {expires_at}"
            )

        await self.db.commit()

    # ── Facture ──────────────────────────────────────────

    async def _generate_invoice(self, payment: Payment) -> None:
        try:
            from app.modules.invoices.service import InvoiceService
            await InvoiceService(self.db).generate_invoice_for_payment(payment.id)
        except Exception as e:
            logger.error(f"Erreur génération facture payment {payment.id}: {e}")

    # ── Code promo ───────────────────────────────────────

    async def _apply_promo_code(self, code: str, amount: int) -> dict | None:
        from app.modules.promo_codes.models import PromoCode
        from sqlalchemy import select

        result = await self.db.execute(
            select(PromoCode).where(
                PromoCode.code == code.upper(),
                PromoCode.is_active == True,
            )
        )
        promo = result.scalar_one_or_none()

        if not promo:
            raise BadRequestException(detail=f"Code promo '{code}' invalide ou expiré.")

        discount = int(amount * promo.discount_rate / 100)
        amount_paid = amount - discount
        commission_due = round(amount_paid * promo.commission_rate / 100, 2)

        return {
            "promo_code_id": promo.id,
            "amount_paid": amount_paid,
            "commission_due": commission_due,
        }

    # ── Queries ──────────────────────────────────────────

    async def get_by_id(self, payment_id: UUID) -> Payment:
        payment = await self.repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundException(resource="Payment", identifier=str(payment_id))
        return payment

    async def get_status(self, transaction_reference: str, current_user: User) -> dict:
        """Polling statut — appelé par le frontend toutes les 5s."""
        payment = await self.repo.find_by_transaction_ref(transaction_reference)
        if not payment or payment.user_id != current_user.id:
            raise NotFoundException(resource="Payment", identifier=transaction_reference)

        from app.modules.exam_access.repository import ExamAccessRepository
        repo = ExamAccessRepository(self.db)
        level_access_granted = await repo.user_has_access(payment.user_id, payment.level_id)

        return {
            "payment_id": payment.id,
            "transaction_reference": payment.transaction_reference,
            "payment_status": payment.payment_status,
            "amount_paid": payment.amount_paid,
            "currency": payment.currency,
            "operator": payment.operator,
            "completed_at": payment.completed_at,
            "exam_access_granted": level_access_granted,
        }

    async def get_my_payments(self, current_user: User) -> list[Payment]:
        return await self.repo.get_by_user(current_user.id)

    # ── Paiement manuel ──────────────────────────────────

    async def create_manual_payment(
        self,
        data: ManualPaymentRequest,
        admin: User,
    ) -> dict:
        """
        Admin crée un paiement validé manuellement.
        Virement, cash, bon, correction admin.
        """
        from app.modules.exams.models import Level
        from app.modules.plans.models import Plan

        # 1. Vérifier level
        level = await self.db.get(Level, data.level_id)
        if not level:
            raise NotFoundException(resource="Level", identifier=str(data.level_id))

        # 2. Vérifier plan
        plan = await self.db.get(Plan, data.plan_id)
        if not plan or not plan.is_active:
            raise NotFoundException(resource="Plan", identifier=str(data.plan_id))

        # 3. Générer référence manuelle
        transaction_reference = await self.repo.generate_transaction_reference()
        transaction_reference = transaction_reference.replace("GTG-", "GTG-M-", 1)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=plan.duration_days)

        # 4. Créer Payment COMPLETED
        payment = await self.repo.create(
            user_id=data.user_id,
            level_id=data.level_id,
            plan_id=data.plan_id,
            promo_code_id=None,
            amount_gross=plan.price,
            amount_paid=plan.price,
            commission_due=0.0,
            currency="XAF",
            payment_status="COMPLETED",
            transaction_reference=transaction_reference,
            operator="MANUAL",
            completed_at=now,
            pawapay_deposit_id=None,
        )

        # 5. Accorder l'accès level
        await self._grant_level_access(payment)

        # 6. Générer facture
        await self._generate_invoice(payment)

        logger.info(
            f"Paiement manuel créé par admin {admin.id} "
            f"pour user {data.user_id} — level {data.level_id} "
            f"— ref {transaction_reference}"
            + (f" — note: {data.note}" if data.note else "")
        )

        return {
            "payment_id": payment.id,
            "transaction_reference": transaction_reference,
            "user_id": data.user_id,
            "level_id": data.level_id,
            "amount_paid": plan.price,
            "expires_at": expires_at,
            "note": data.note,
        }

    async def get_manual_payments(self, limit: int = 20) -> list[Payment]:
        """Liste les paiements manuels pour l'admin."""
        return await self.repo.get_manual_payments(limit=limit)