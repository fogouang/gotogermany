"""
app/modules/payments/schemas.py

Flow complet :
  1. POST /payments/initiate      → PaymentInitiateRequest
                                  ← PaymentInitiateResponse  (USSD code + ref)
  2. GET  /payments/{ref}/status  ← PaymentStatusResponse
  3. POST /payments/webhook       → WebhookPayload (My-CoolPay → backend)
"""
import uuid
from datetime import datetime
from typing import Any
from pydantic import Field
from app.shared.schemas.base import BaseSchema


# ─────────────────────────────────────────────
# Requests
# ─────────────────────────────────────────────

class PaymentInitiateRequest(BaseSchema):
    """L'étudiant initie un paiement pour un exam."""
    level_id: uuid.UUID
    plan_id: uuid.UUID          # ← ajouter
    promo_code: str | None = None
    operator: str = Field(max_length=30)
    phone_number: str = Field(max_length=20)

# Supprimer WebhookPayload, remplacer par :
class PawapayCallbackPayload(BaseSchema):
    depositId: str
    status: str                     # COMPLETED | FAILED
    amount: str
    currency: str
    country: str
    payer: dict
    created: datetime
    customerMessage: str | None = None
    providerTransactionId: str | None = None
    failureReason: dict | None = None
    metadata: dict | None = None

# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────
class PaymentInitiateResponse(BaseSchema):
    payment_id: uuid.UUID
    transaction_reference: str
    amount_gross: int
    amount_paid: int
    discount_amount: int
    currency: str
    message: str   # "Confirmez le paiement sur votre téléphone"


class PaymentStatusResponse(BaseSchema):
    """Statut d'un paiement — polled par le frontend."""
    payment_id: uuid.UUID
    transaction_reference: str
    payment_status: str             # PENDING | COMPLETED | FAILED
    amount_paid: int
    currency: str
    operator: str | None
    completed_at: datetime | None
    exam_access_granted: bool       # True si ExamAccess créé

class PaymentResponse(BaseSchema):
    """Response complète d'un paiement — historique."""
    id: uuid.UUID
    level_id: uuid.UUID
    plan_id: uuid.UUID          # ← ajouter aussi
    promo_code_id: uuid.UUID | None
    amount_gross: int
    amount_paid: int
    discount_amount: int        # ← garder le field, supprimer le @property
    commission_due: float
    currency: str
    payment_status: str
    transaction_reference: str
    operator: str | None
    completed_at: datetime | None
    created_at: datetime

class PaymentAdminResponse(PaymentResponse):
    user_id: uuid.UUID
    user_email: str | None = None
    user_name: str | None = None
    level_name: str | None = None
    pawapay_deposit_id: str | None = None
    expires_at: str | None = None  # depuis ExamAccess       # le code saisi, pas juste l'ID


class PaymentSummaryResponse(BaseSchema):
    """Stats paiements pour le dashboard admin."""
    total_payments: int
    total_completed: int
    total_failed: int
    total_revenue: int              # somme amount_paid des COMPLETED
    total_discounts: int            # somme des réductions accordées
    total_commissions_due: float    # somme des commissions à verser
    

class ManualPaymentRequest(BaseSchema):
    """Admin valide manuellement un accès exam (MyCoolPay indisponible, virement, cash)."""
    user_id: uuid.UUID
    level_id: uuid.UUID
    plan_id: uuid.UUID
    note: str | None = Field(
        None,
        max_length=500,
        description="Ex: 'Virement Orange Money reçu le 16/06/2026'",
    )


class ManualPaymentResponse(BaseSchema):
    """Réponse après création d'un paiement manuel."""
    payment_id: uuid.UUID
    transaction_reference: str
    user_id: uuid.UUID
    level_id: uuid.UUID
    amount_paid: int
    expires_at: datetime
    note: str | None