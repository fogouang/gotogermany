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
    exam_id: uuid.UUID
    plan_id: uuid.UUID          # ← ajouter
    promo_code: str | None = None
    operator: str = Field(max_length=30)
    phone_number: str = Field(max_length=20)

class WebhookPayload(BaseSchema):
    """
    Payload reçu de My-CoolPay après confirmation du paiement.
    Champs selon doc My-CoolPay.
    """
    transaction_ref: str
    transaction_type: str
    transaction_amount: float
    transaction_currency: str
    transaction_operator: str
    app_transaction_ref: str        # notre transaction_reference interne
    transaction_status: str         # "SUCCESS" | "FAILED"
    signature: str                  # MD5 à vérifier


# ─────────────────────────────────────────────
# Responses
# ─────────────────────────────────────────────

class PaymentInitiateResponse(BaseSchema):
    """Retourné après création du payin My-CoolPay."""
    payment_id: uuid.UUID
    transaction_reference: str      # notre ref interne
    amount_gross: int
    amount_paid: int                # après réduction promo
    discount_amount: int
    currency: str
    ussd_code: str | None           # ex: "#150*50#" pour composer sur le téléphone
    message: str                    # instruction à afficher à l'étudiant


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
    exam_id: uuid.UUID
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
    """Response étendue pour l'admin — inclut user et détails partenaire."""
    user_id: uuid.UUID
    mycoolpay_ref: str | None
    promo_code: str | None          # le code saisi, pas juste l'ID


class PaymentSummaryResponse(BaseSchema):
    """Stats paiements pour le dashboard admin."""
    total_payments: int
    total_completed: int
    total_failed: int
    total_revenue: int              # somme amount_paid des COMPLETED
    total_discounts: int            # somme des réductions accordées
    total_commissions_due: float    # somme des commissions à verser