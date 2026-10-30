"""
app/modules/payments/service.py

Flow Kratos Pay (Mobile Money) :
  1. initiate_payment() → crée Payment(PENDING) → appelle Kratos payin
     (reference Kratos = transaction_reference)
  2. Réponse immédiate SUCCESS → paiement validé tout de suite
     Réponse PENDING → l'élève confirme sur son téléphone, le webhook suivra
  3. Webhook → handle_kratos_webhook() → COMPLETED / FAILED
  4. Si COMPLETED → _grant_level_access() → ExamAccess créé avec expires_at
  5. Facture PDF générée automatiquement

Le callback pawaPay reste en place pour les paiements lancés avant la bascule.
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.kratos import KratosClient, KratosError
from app.modules.payments.models import Payment
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import ManualPaymentRequest, PawapayCallbackPayload, PaymentInitiateRequest
from app.modules.users.models import User
from app.shared.exceptions.http import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


def _serialize_payload(data: dict) -> dict:
    """Sérialise un dict pour stockage JSONB — convertit datetime en str."""
    return json.loads(json.dumps(data, default=str))


class PaymentService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaymentRepository(db)
        self.kratos = KratosClient()

    # ── Initiation ───────────────────────────────────────

    async def initiate_payment(
        self,
        data: PaymentInitiateRequest,
        current_user: User,
    ) -> dict:
        from app.modules.exams.models import Level
        from app.modules.plans.models import Plan

        # Niveau d'examen, ou Start Deutsch A1/A2 (validé par le schéma)
        if data.level_id and not await self.db.get(Level, data.level_id):
            raise NotFoundException(resource="Level", identifier=str(data.level_id))

        plan = await self.db.get(Plan, data.plan_id)
        if not plan or not plan.is_active:
            raise NotFoundException(resource="Plan", identifier=str(data.plan_id))

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

        transaction_reference = await self.repo.generate_transaction_reference()

        payment = await self.repo.create(
            user_id=current_user.id,
            level_id=data.level_id,
            sd_level=data.sd_level,
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

        try:
            kratos_response = await self.kratos.initiate_payin(
                reference=transaction_reference,
                amount=amount_paid,
                phone_number=data.phone_number.strip(),
                provider="MTN_MOMO_CMR" if data.operator == "MTN" else "ORANGE_CMR",
                description=f"GoToGermany {transaction_reference}",
            )
        except KratosError as e:
            await self.repo.update(payment.id, payment_status="FAILED")
            logger.error(
                f"Kratos payin refusé {transaction_reference} : {e} "
                f"(code={e.code}, details={e.details}, request_id={e.request_id})"
            )
            raise BadRequestException(detail=f"Paiement refusé : {e}")
        except Exception as e:
            await self.repo.update(payment.id, payment_status="FAILED")
            logger.error(f"Kratos payin erreur {transaction_reference} : {e}")
            raise BadRequestException(detail="Le service de paiement est indisponible, réessayez.")

        status = self.kratos.internal_status(kratos_response.get("status"))

        if status == "FAILED":
            await self._fail_payment(payment, kratos_response)
            raise BadRequestException(
                detail=f"Paiement refusé : {kratos_response.get('gatewayMessage') or 'erreur inconnue'}"
            )

        if status == "COMPLETED":
            # Paiement validé directement dans la réponse
            await self._complete_payment(payment, kratos_response)
            message = "Paiement confirmé."
        else:
            await self.repo.update(payment.id, webhook_payload=_serialize_payload(kratos_response))
            message = "Confirmez le paiement sur votre téléphone mobile."

        return {
            "payment_id": payment.id,
            "transaction_reference": transaction_reference,
            "amount_gross": amount_gross,
            "amount_paid": amount_paid,
            "discount_amount": amount_gross - amount_paid,
            "currency": "XAF",
            "message": message,
        }

    # ── Validation / échec (communs à Kratos et pawaPay) ──

    async def _complete_payment(self, payment: Payment, raw_payload: dict) -> None:
        """Passe le paiement en COMPLETED puis donne l'accès, la facture et la commission."""
        # Relecture : un webhook et la réponse directe peuvent arriver presque ensemble
        payment = await self.repo.get_by_id(payment.id)
        if payment.payment_status == "COMPLETED":
            logger.info(f"Payment {payment.id} déjà COMPLETED — ignoré")
            return

        await self.repo.update(
            payment.id,
            payment_status="COMPLETED",
            completed_at=datetime.now(timezone.utc),
            webhook_payload=_serialize_payload(raw_payload),
        )
        logger.info(f"Payment {payment.id} → COMPLETED")

        # Achat de crédits IA — court-circuite l'accès exam si c'est le cas
        from app.modules.ai_credit_purchases.service import AICreditPurchaseService
        is_credit_purchase = await AICreditPurchaseService(self.db).on_payment_completed(payment)

        if not is_credit_purchase:
            await self._grant_level_access(payment)

        await self._generate_invoice(payment)

        from app.modules.referrals.service import ReferralService
        await ReferralService(self.db).record_payment_earning(
            payment_id=payment.id,
            payer_user_id=payment.user_id,
            payment_amount=payment.amount_paid,
        )

    async def _fail_payment(self, payment: Payment, raw_payload: dict) -> None:
        if payment.payment_status == "COMPLETED":
            # Un échec tardif ne défait jamais un paiement déjà validé
            logger.warning(f"Échec reçu pour payment {payment.id} déjà COMPLETED — ignoré")
            return
        await self.repo.update(
            payment.id,
            payment_status="FAILED",
            webhook_payload=_serialize_payload(raw_payload),
        )
        logger.info(f"Payment {payment.id} → FAILED")

    # ── Webhook Kratos ───────────────────────────────────

    async def handle_kratos_webhook(self, payload: dict) -> bool:
        """
        Webhook Kratos (signature vérifiée par le router quand elle est disponible).
        Retourne False si la référence est inconnue ou si le montant ne correspond pas.
        """
        reference, status = KratosClient.parse_webhook(payload)
        logger.info(f"Webhook Kratos — reference={reference} status={status}")

        if not reference:
            logger.error(f"Webhook Kratos sans référence : {payload}")
            return False

        payment = await self.repo.find_by_transaction_ref(reference)
        if not payment:
            logger.error(f"Payment introuvable pour la référence Kratos {reference}")
            return False

        # Sans signature vérifiable : le montant annoncé doit correspondre au paiement
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        amount = data.get("amount")
        if amount is not None:
            try:
                montant_ok = int(float(amount)) == int(payment.amount_paid)
            except (TypeError, ValueError):
                montant_ok = False
            if not montant_ok:
                logger.error(
                    f"Webhook Kratos {reference} : montant {amount} différent de "
                    f"{payment.amount_paid}, ignoré"
                )
                return False

        if status == "COMPLETED":
            await self._complete_payment(payment, payload)
        elif status == "FAILED":
            await self._fail_payment(payment, payload)
        return True
    

    # ── Callback pawaPay (paiements lancés avant la bascule) ──

    async def handle_callback(self, payload: PawapayCallbackPayload) -> bool:
        logger.info(f"Callback pawaPay reçu — depositId={payload.depositId} status={payload.status}")

        payment = await self.repo.get_by_id(UUID(payload.depositId))
        if not payment:
            logger.error(f"Payment introuvable pour depositId: {payload.depositId}")
            raise NotFoundException(resource="Payment", identifier=payload.depositId)

        if payload.status == "COMPLETED":
            await self._complete_payment(payment, payload.model_dump())
        elif payload.status == "FAILED":
            await self._fail_payment(payment, payload.model_dump())
        return True

    # ── Grant Level Access ───────────────────────────────

    async def _grant_level_access(self, payment: Payment) -> None:
        if payment.level_id is None and payment.sd_level is None:
            # Pas un accès exam (ex. achat de crédits IA)
            return

        from app.modules.exam_access.models import ExamAccess
        from app.modules.exam_access.repository import ExamAccessRepository
        from app.modules.plans.models import Plan

        plan = await self.db.get(Plan, payment.plan_id) if payment.plan_id else None
        if payment.plan_id and not plan:
            logger.error(f"Plan {payment.plan_id} introuvable pour payment {payment.id}")
            return

        if payment.duration_days:
            duration = payment.duration_days
        elif plan:
            duration = plan.duration_days
        else:
            return

        now = datetime.now(timezone.utc)
        repo = ExamAccessRepository(self.db)
        if payment.sd_level:
            existing = await repo.find_by_user_and_sd_level(payment.user_id, payment.sd_level)
        else:
            existing = await repo.find_by_user_and_level(payment.user_id, payment.level_id)
        level_label = payment.sd_level or payment.level_id

        # Meme paiement deja traite (webhook recu deux fois) : pas de credits en double
        already_applied = existing is not None and existing.payment_id == payment.id

        # Renouvellement avant échéance : les jours restants sont conservés
        start = existing.expires_at if existing and existing.expires_at and existing.expires_at > now else now
        expires_at = start + timedelta(days=duration)

        if existing:
            await repo.update(
                existing.id,
                expires_at=expires_at,
                payment_id=payment.id,
                access_type="paid",
            )
            logger.info(f"ExamAccess renouvelé : user {payment.user_id} level {level_label} jusqu'au {expires_at}")
        else:
            self.db.add(ExamAccess(
                user_id=payment.user_id,
                level_id=payment.level_id,
                sd_level=payment.sd_level,
                access_type="paid",
                payment_id=payment.id,
                expires_at=expires_at,
                granted_at=now,
            ))
            await self.db.flush()
            logger.info(f"ExamAccess créé : user {payment.user_id} level {level_label} jusqu'au {expires_at}")

        from app.modules.users.models import User

        student = await self.db.get(User, payment.user_id)
        if student:
            # Echeance affichee dans la liste des eleves (la plus lointaine si plusieurs niveaux)
            if not student.access_expires_at or student.access_expires_at < expires_at:
                student.access_expires_at = expires_at

            # Credits IA inclus dans la formule (paiement en ligne ou activation par un centre)
            if plan and plan.ai_credits and not already_applied:
                student.ai_credits = (student.ai_credits or 0) + plan.ai_credits
                logger.info(
                    f"Credits IA : +{plan.ai_credits} pour user {payment.user_id} "
                    f"(plan {plan.id}, payment {payment.id})"
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
        payment = await self.repo.find_by_transaction_ref(transaction_reference)
        if not payment or payment.user_id != current_user.id:
            raise NotFoundException(resource="Payment", identifier=transaction_reference)

        from app.modules.exam_access.repository import ExamAccessRepository
        repo = ExamAccessRepository(self.db)
        if payment.sd_level:
            level_access_granted = await repo.user_has_sd_access(payment.user_id, payment.sd_level)
        elif payment.level_id:
            level_access_granted = await repo.user_has_access(payment.user_id, payment.level_id)
        else:
            level_access_granted = False

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

    async def _daily_pass_price(self) -> int:
        """Prix d'une journée (réglage app_settings "daily_pass_price", 1000 par défaut)."""
        from sqlalchemy import select
        from app.modules.settings.models import AppSetting

        row = (
            await self.db.execute(select(AppSetting).where(AppSetting.key == "daily_pass_price"))
        ).scalar_one_or_none()
        try:
            return int(row.value) if row else 1000
        except ValueError:
            return 1000

    async def create_manual_payment(
        self,
        data: ManualPaymentRequest,
        admin: User,
    ) -> dict:
        from app.modules.exams.models import Level
        from app.modules.plans.models import Plan

        if data.level_id and not await self.db.get(Level, data.level_id):
            raise NotFoundException(resource="Level", identifier=str(data.level_id))

        plan = None
        if data.days:
            # Pass journalier : géré uniquement par l'admin, sans commission partenaire
            amount = data.days * await self._daily_pass_price()
            duration_days = data.days
        else:
            plan = await self.db.get(Plan, data.plan_id)
            if not plan or not plan.is_active:
                raise NotFoundException(resource="Plan", identifier=str(data.plan_id))
            amount = plan.price
            duration_days = None

        transaction_reference = await self.repo.generate_transaction_reference()
        transaction_reference = transaction_reference.replace("GTG-", "GTG-M-", 1)
        now = datetime.now(timezone.utc)

        payment = await self.repo.create(
            user_id=data.user_id,
            level_id=data.level_id,
            sd_level=data.sd_level,
            plan_id=plan.id if plan else None,
            duration_days=duration_days,
            promo_code_id=None,
            amount_gross=amount,
            amount_paid=amount,
            commission_due=0.0,
            currency="XAF",
            payment_status="COMPLETED",
            transaction_reference=transaction_reference,
            operator="MANUAL",
            completed_at=now,
            pawapay_deposit_id=None,
            validated_manually_by=admin.id,
        )

        await self._grant_level_access(payment)
        await self._generate_invoice(payment)

        # Commission ambassadeur uniquement sur les formules, jamais sur le pass journalier
        if plan:
            from app.modules.referrals.service import ReferralService
            await ReferralService(self.db).record_payment_earning(
                payment_id=payment.id, payer_user_id=data.user_id, payment_amount=amount
            )

        from app.modules.exam_access.repository import ExamAccessRepository
        access_repo = ExamAccessRepository(self.db)
        if data.sd_level:
            access = await access_repo.find_by_user_and_sd_level(data.user_id, data.sd_level)
        else:
            access = await access_repo.find_by_user_and_level(data.user_id, data.level_id)

        logger.info(
            f"Paiement manuel {transaction_reference} par {admin.id} pour user {data.user_id} : "
            + (f"pass {data.days} jour(s)" if data.days else f"formule {plan.id}")
            + f", {amount} FCFA"
            + (f", note : {data.note}" if data.note else "")
        )

        return {
            "payment_id": payment.id,
            "transaction_reference": transaction_reference,
            "user_id": data.user_id,
            "level_id": data.level_id,
            "sd_level": data.sd_level,
            "amount_paid": amount,
            "expires_at": access.expires_at if access else None,
            "note": data.note,
        }

    async def get_manual_payments(self, limit: int = 20) -> list[Payment]:
        return await self.repo.get_manual_payments(limit=limit)