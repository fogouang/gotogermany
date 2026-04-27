"""
app/modules/payments/service.py

Flow My-CoolPay :
  1. initiate_payment() → crée Payment(PENDING) → appelle payin My-CoolPay
  2. Webhook → handle_webhook() → update COMPLETED/FAILED
  3. Si COMPLETED → _grant_exam_access() → ExamAccess créé avec expires_at
  4. Facture PDF générée automatiquement
"""
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment
from app.modules.payments.mycoolpay import MyCoolPayClient
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import PaymentInitiateRequest, WebhookPayload
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class PaymentService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaymentRepository(db)
        self.mycoolpay = MyCoolPayClient()

    # ── Initiation ───────────────────────────────────────

    async def initiate_payment(
        self,
        data: PaymentInitiateRequest,
        current_user: User,
    ) -> dict:
        """
        Initie un paiement mobile money pour l'accès à un exam.

        Steps :
          1. Charger Exam + Plan
          2. Vérifier code promo si fourni → calculer réduction + commission
          3. Créer Payment(PENDING)
          4. Appeler My-CoolPay payin
          5. Stocker mycoolpay_ref + operator
        """
        from app.modules.exams.models import Exam
        from app.modules.plans.models import Plan

        # 1. Vérifier exam
        exam = await self.db.get(Exam, data.exam_id)
        if not exam or not exam.is_active:
            raise NotFoundException(resource="Exam", identifier=str(data.exam_id))

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

        reason = f"Accès {exam.name} — {plan.name}"

        # 5. Créer Payment PENDING
        payment = await self.repo.create(
            user_id=current_user.id,
            exam_id=data.exam_id,
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

        # 6. Appeler My-CoolPay payin
        try:
            mycoolpay_response = await self.mycoolpay.create_payin(
                transaction_amount=amount_paid,
                customer_phone_number=data.phone_number,
                app_transaction_ref=transaction_reference,
                transaction_reason=reason,
                customer_name=current_user.full_name,
                customer_email=current_user.email,
            )
        except Exception as e:
            # Annuler le paiement si My-CoolPay échoue
            await self.repo.update(payment.id, payment_status="FAILED")
            raise BadRequestException(detail=f"Erreur paiement : {str(e)}")

        # 7. Stocker mycoolpay_ref
        mycoolpay_ref = mycoolpay_response.get("transaction_ref")
        if mycoolpay_ref:
            await self.repo.update(payment.id, mycoolpay_ref=mycoolpay_ref)

        return {
            "payment_id": payment.id,
            "transaction_reference": transaction_reference,
            "amount_gross": amount_gross,
            "amount_paid": amount_paid,
            "discount_amount": amount_gross - amount_paid,
            "currency": "XAF",
            "ussd_code": mycoolpay_response.get("ussd"),
            "message": mycoolpay_response.get("message", "Composez le code USSD pour confirmer le paiement."),
        }

    # ── Webhook ──────────────────────────────────────────

    async def handle_webhook(self, webhook_data: WebhookPayload) -> bool:
        """
        Traite le callback My-CoolPay.
        Vérification signature → update statut → grant ExamAccess si succès.
        """
        # 1. Vérifier signature MD5
        is_valid = self.mycoolpay.verify_webhook_signature(
            transaction_ref=webhook_data.transaction_ref,
            transaction_type=webhook_data.transaction_type,
            transaction_amount=webhook_data.transaction_amount,
            transaction_currency=webhook_data.transaction_currency,
            transaction_operator=webhook_data.transaction_operator,
            signature=webhook_data.signature,
        )
        if not is_valid:
            logger.warning(f"Webhook signature invalide pour {webhook_data.transaction_ref}")
            raise BadRequestException(detail="Signature invalide")

        # 2. Trouver le paiement via notre transaction_reference
        payment = await self.repo.find_by_transaction_ref(webhook_data.app_transaction_ref)
        if not payment:
            logger.error(f"Payment introuvable pour ref: {webhook_data.app_transaction_ref}")
            raise NotFoundException(resource="Payment", identifier=webhook_data.app_transaction_ref)

        # 3. Ignorer si déjà traité
        if payment.payment_status == "COMPLETED":
            logger.info(f"Payment {payment.id} déjà COMPLETED — ignoré")
            return True

        # 4. Update statut
        if webhook_data.transaction_status == "SUCCESS":
            await self.repo.update(
                payment.id,
                payment_status="COMPLETED",
                mycoolpay_ref=webhook_data.transaction_ref,
                operator=webhook_data.transaction_operator,
                completed_at=datetime.now(timezone.utc),
                webhook_payload=webhook_data.model_dump(),
            )
            # 5. Créer ExamAccess
            await self._grant_exam_access(payment)
            # 6. Générer facture
            await self._generate_invoice(payment)

        elif webhook_data.transaction_status in ("FAILED", "CANCELED"):
            await self.repo.update(
                payment.id,
                payment_status="FAILED",
                webhook_payload=webhook_data.model_dump(),
            )

        return True

    # ── Grant ExamAccess ─────────────────────────────────

    async def _grant_exam_access(self, payment: Payment) -> None:
        """
        Crée ou renouvelle l'ExamAccess après paiement réussi.
        expires_at = now + plan.duration_days
        """
        from app.modules.exam_access.models import ExamAccess
        from app.modules.exam_access.repository import ExamAccessRepository
        from app.modules.plans.models import Plan
        from sqlalchemy import select

        plan = await self.db.get(Plan, payment.plan_id)
        if not plan:
            logger.error(f"Plan {payment.plan_id} introuvable pour payment {payment.id}")
            return

        expires_at = datetime.now(timezone.utc) + timedelta(days=plan.duration_days)
        repo = ExamAccessRepository(self.db)

        # Vérifier si accès existant → renouveler
        existing = await repo.find_by_user_and_exam(payment.user_id, payment.exam_id)

        if existing:
            # Renouvellement — prolonger depuis maintenant
            await repo.update(
                existing.id,
                expires_at=expires_at,
                payment_id=payment.id,
                access_type="paid",
            )
            logger.info(f"ExamAccess renouvelé pour user {payment.user_id} — expires {expires_at}")
        else:
            # Nouvel accès
            access = ExamAccess(
                user_id=payment.user_id,
                exam_id=payment.exam_id,
                access_type="paid",
                payment_id=payment.id,
                expires_at=expires_at,
                granted_at=datetime.now(timezone.utc),
            )
            self.db.add(access)
            await self.db.flush()
            logger.info(f"ExamAccess créé pour user {payment.user_id} — expires {expires_at}")

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
        """
        Vérifie et applique un code promo.
        Retourne dict avec promo_code_id, amount_paid, commission_due.
        Retourne None si code invalide.
        """
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

        # Calculer réduction
        discount = int(amount * promo.discount_rate / 100)
        amount_paid = amount - discount

        # Calculer commission partenaire sur montant payé
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
        exam_access_granted = await repo.user_has_access(payment.user_id, payment.exam_id)

        return {
            "payment_id": payment.id,
            "transaction_reference": payment.transaction_reference,
            "payment_status": payment.payment_status,
            "amount_paid": payment.amount_paid,
            "currency": payment.currency,
            "operator": payment.operator,
            "completed_at": payment.completed_at,
            "exam_access_granted": exam_access_granted,
        }

    async def get_my_payments(self, current_user: User) -> list[Payment]:
        return await self.repo.get_by_user(current_user.id)