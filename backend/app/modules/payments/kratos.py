"""
app/modules/payments/kratos.py

Client Kratos Pay, API « transactions » (Mobile Money Cameroun : Orange Money, MTN MoMo).

  POST /transactions          → crée une collecte (réponse : uuid + status pending)
  GET  /transactions/{uuid}   → statut d'une transaction
  Webhook                     → POST sur notre serveur à chaque changement de statut

Authentification : Authorization: Bearer sk_live_… (ou sk_test_…) + X-Application-ID.
Le paiement est asynchrone : l'élève confirme sur son téléphone, le statut final
arrive par webhook ou en relisant la transaction.
"""
import base64
import hashlib
import hmac
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Codes provider Kratos. Les clés reprennent les providers déjà utilisés
# avec pawaPay, pour ne rien changer côté front et base.
KRATOS_PROVIDERS = {
    "ORANGE_CMR": "orange_money_cm",
    "MTN_MOMO_CMR": "mtn_momo_cm",
}

# Statuts Kratos (casse variable) -> statuts internes
_COMPLETED = {"SUCCESS", "SUCCESSFUL", "SUCCEEDED", "COMPLETED", "PAID"}
_FAILED = {"FAILED", "FAILURE", "CANCELLED", "CANCELED", "EXPIRED", "REJECTED", "DECLINED"}


class KratosError(Exception):
    """Erreur renvoyée par Kratos (success: false) ou réponse illisible."""

    def __init__(self, message: str, code: str | None = None, details: dict | None = None,
                 request_id: str | None = None, http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.request_id = request_id
        self.http_status = http_status


class KratosClient:

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.KRATOS_BASE_URL.rstrip("/")
        self.api_key = settings.KRATOS_API_KEY
        self.app_id = settings.KRATOS_APP_ID
        mode = "test" if self.api_key.startswith("sk_test_") else "live"
        logger.info(f"KratosClient init: base_url={self.base_url}, mode={mode}")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Application-ID": self.app_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ── Utilitaires ──────────────────────────────────────

    @staticmethod
    def provider_for(provider: str) -> str:
        """ORANGE_CMR -> orange_money_cm. Lève ValueError si l'opérateur n'est pas géré."""
        code = KRATOS_PROVIDERS.get(provider)
        if not code:
            raise ValueError(f"Opérateur non pris en charge par Kratos : {provider}")
        return code

    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        """Kratos attend le numéro local, sans indicatif : 696246686."""
        digits = "".join(c for c in phone_number if c.isdigit())
        if len(digits) == 12 and digits.startswith("237"):
            digits = digits[3:]
        return digits

    @staticmethod
    def internal_status(kratos_status: str | None) -> str:
        """pending / success / failed (toute casse) -> PENDING / COMPLETED / FAILED."""
        value = (kratos_status or "").strip().upper()
        if value in _COMPLETED:
            return "COMPLETED"
        if value in _FAILED:
            return "FAILED"
        return "PENDING"

    @staticmethod
    def _data(payload: dict) -> dict:
        data = payload.get("data")
        return data if isinstance(data, dict) else payload

    async def _parse(self, response: httpx.Response, action: str) -> dict:
        request_id = None
        try:
            body = response.json()
            request_id = (body.get("meta") or {}).get("request_id")
        except ValueError:
            body = None

        logger.info(
            f"Kratos {action} → {response.status_code} "
            f"(request_id={request_id or response.headers.get('x-request-id')}) {response.text}"
        )

        if body is None:
            raise KratosError(
                f"Réponse Kratos illisible (HTTP {response.status_code})",
                http_status=response.status_code,
            )
        if body.get("success") is False or response.status_code >= 400:
            error = body.get("error") or {}
            raise KratosError(
                error.get("message") or body.get("message") or f"Erreur Kratos (HTTP {response.status_code})",
                code=error.get("code"),
                details=error.get("details"),
                request_id=request_id,
                http_status=response.status_code,
            )
        return self._data(body)

    # ── API ──────────────────────────────────────────────

    async def create_collection(
        self,
        idempotency_key: str,
        amount: int,
        phone_number: str,
        provider: str,
        description: str = "GoToGermany",
    ) -> dict:
        """
        Crée une collecte Mobile Money. Retourne `data` : uuid, status (pending), reference…
        idempotency_key = notre transaction_reference : un renvoi après timeout
        récupère la même transaction au lieu d'en créer une deuxième.
        """
        payload = {
            "type": "collection",
            "provider": self.provider_for(provider),
            "amount": int(amount),
            "currency": "XAF",
            "phone_number": self.normalize_phone(phone_number),
            "idempotency_key": idempotency_key,
            "metadata": {"description": description[:120], "reference": idempotency_key},
        }
        logger.info(f"Kratos collection payload: {payload}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/transactions", json=payload, headers=self._headers()
            )
        return await self._parse(response, "POST /transactions")

    async def get_transaction(self, uuid: str) -> dict:
        """Relit une transaction (statut à jour)."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{self.base_url}/transactions/{uuid}", headers=self._headers()
            )
        return await self._parse(response, f"GET /transactions/{uuid}")

    # ── Webhook ──────────────────────────────────────────

    @staticmethod
    def verify_signature(raw_body: bytes, signature: str | None) -> bool:
        """
        HMAC du corps brut, comparé à l'en-tête X-Mok-Signature.
        Algorithme et encodage non documentés : SHA-256 par défaut,
        signature acceptée en hex ou en base64 (éventuellement préfixée « sha256= »).
        """
        settings = get_settings()
        secret = settings.KRATOS_WEBHOOK_SECRET
        if not secret or not signature:
            return False
        received = signature.strip()
        if "=" in received and received.split("=", 1)[0].lower() in ("sha256", "sha512"):
            received = received.split("=", 1)[1]

        algo = hashlib.sha512 if settings.KRATOS_WEBHOOK_ALGO == "sha512" else hashlib.sha256
        digest = hmac.new(secret.encode(), raw_body, algo).digest()
        candidates = (digest.hex(), base64.b64encode(digest).decode())
        return any(hmac.compare_digest(received, c) for c in candidates)

    @staticmethod
    def parse_webhook(payload: dict) -> tuple[str | None, str | None, str]:
        """
        (uuid Kratos, notre référence, statut interne). Format non documenté :
        on lit à plat ou sous « data », et l'événement en secours.
        """
        data = KratosClient._data(payload)
        uuid = data.get("uuid") or data.get("id")
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        reference = data.get("idempotency_key") or metadata.get("reference")

        status = data.get("status")
        if not status:
            event = str(payload.get("event") or payload.get("type") or "").lower()
            if event.endswith(".success") or event.endswith(".succeeded"):
                status = "SUCCESS"
            elif event.endswith(".failed"):
                status = "FAILED"
        return (str(uuid) if uuid else None), reference, KratosClient.internal_status(status)