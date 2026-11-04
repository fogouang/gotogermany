"""
app/modules/payments/stripe_client.py

Paiement par carte (Visa, Mastercard) via Stripe Checkout, en euros.

  1. create_checkout_session() → page de paiement hébergée par Stripe (aucune
     donnée de carte ne passe par notre serveur), on redirige l'élève dessus
  2. Retour sur /dashboard/paiement/succes?ref=...
  3. Webhook signé + relecture de la session chez Stripe → paiement validé

Le fichier ne s'appelle pas stripe.py pour ne pas masquer le paquet « stripe ».
"""
import logging
import time

import stripe

from app.config import get_settings

logger = logging.getLogger(__name__)

# Une session non payée expire au bout d'une heure (minimum Stripe : 30 min)
SESSION_TTL_SECONDS = 60 * 60


class StripeClient:

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def create_checkout_session(
        self,
        *,
        reference: str,
        amount_cents: int,
        currency: str,
        product_name: str,
        description: str | None,
        customer_email: str | None,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """Crée la page de paiement Stripe. Retourne {"id", "url"}."""
        product_data = {"name": product_name[:250]}
        if description:
            product_data["description"] = description[:500]

        params = {
            "api_key": self.api_key,
            "idempotency_key": f"checkout-{reference}",
            "mode": "payment",
            "line_items": [
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": currency.lower(),
                        "unit_amount": int(amount_cents),
                        "product_data": product_data,
                    },
                }
            ],
            "client_reference_id": reference,
            "metadata": {"transaction_reference": reference, "app": "gotogermany"},
            "payment_intent_data": {
                "description": f"GoToGermany {reference}",
                "metadata": {"transaction_reference": reference, "app": "gotogermany"},
            },
            "success_url": success_url,
            "cancel_url": cancel_url,
            "expires_at": int(time.time()) + SESSION_TTL_SECONDS,
            "locale": "auto",
        }
        if customer_email:
            params["customer_email"] = customer_email

        session = await stripe.checkout.Session.create_async(**params)
        logger.info(f"Stripe checkout créé : {session.id} pour {reference} ({amount_cents} {currency})")
        return {"id": session.id, "url": session.url}

    async def retrieve_session(self, session_id: str) -> dict:
        """État d'une session : status (open/complete/expired), payment_status (paid/unpaid)."""
        s = await stripe.checkout.Session.retrieve_async(session_id, api_key=self.api_key)
        return {
            "id": s.id,
            "status": s.status,
            "payment_status": s.payment_status,
            "amount_total": s.amount_total,
            "currency": s.currency,
            "client_reference_id": s.client_reference_id,
            "payment_intent": s.payment_intent if isinstance(s.payment_intent, str) else None,
        }

    def verify_webhook(self, raw_body: bytes, signature: str | None) -> bool:
        """Vérifie l'en-tête Stripe-Signature avec le secret whsec_ du webhook."""
        if not self.webhook_secret or not signature:
            return False
        try:
            stripe.Webhook.construct_event(raw_body, signature, self.webhook_secret)
            return True
        except Exception as e:
            logger.warning(f"Webhook Stripe : signature invalide ({e})")
            return False