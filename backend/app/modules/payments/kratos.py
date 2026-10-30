"""
app/modules/payments/kratos.py

Client Kratos Pay (Mobile Money Cameroun : Orange Money, MTN MoMo).
Même rôle que PawapayClient : le service de paiement appelle ce client,
la confirmation finale arrive par webhook (seul SUCCESS vaut paiement).

Carte (Visa, Mastercard) : pas encore d'API documentée par Kratos.
À ajouter ici dès qu'ils fournissent le flux (page de paiement hébergée probable).
"""
import base64
import hashlib
import hmac
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Codes opérateur Kratos. Les clés reprennent les providers déjà utilisés
# avec pawaPay, pour ne rien changer côté front et base.
KRATOS_OPERATORS = {
    "ORANGE_CMR": "orange_money_cm",
    "MTN_MOMO_CMR": "mtn_momo_cm",
}

# Statuts Kratos -> statuts internes (mêmes valeurs qu'avec pawaPay)
KRATOS_STATUS_MAP = {
    "SUCCESS": "COMPLETED",
    "FAILED": "FAILED",
    "PENDING": "PENDING",
}


class KratosError(Exception):
    """Erreur renvoyée par Kratos (success: false) ou réponse illisible."""

    def __init__(self, message: str, code: str | None = None, details: dict | None = None,
                 request_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.request_id = request_id


class KratosClient:

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.KRATOS_BASE_URL.rstrip("/")
        self.public_key = settings.KRATOS_PUBLIC_KEY
        self.env = settings.KRATOS_ENV  # "live" ou "sandbox"
        logger.info(f"KratosClient init: base_url={self.base_url}, env={self.env}")

    def _headers(self) -> dict:
        return {
            "X-MoK-Public-Key": self.public_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v1/{self.env}/{path.lstrip('/')}"

    @staticmethod
    def operator_for(provider: str) -> str:
        """ORANGE_CMR -> orange_money_cm. Lève ValueError si l'opérateur n'est pas géré."""
        operator = KRATOS_OPERATORS.get(provider)
        if not operator:
            raise ValueError(f"Opérateur non pris en charge par Kratos : {provider}")
        return operator

    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        """Kratos attend l'indicatif sans « + » : 237690000000."""
        digits = "".join(c for c in phone_number if c.isdigit())
        if len(digits) == 9:  # numéro local camerounais
            digits = f"237{digits}"
        return digits

    @staticmethod
    def verify_signature(raw_body: bytes, signature: str | None) -> bool:
        """
        Webhook : HMAC du corps brut, comparé à l'en-tête X-Mok-Signature.
        La doc ne précise ni l'algorithme ni l'encodage : SHA-256 par défaut,
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
    def parse_webhook(payload: dict) -> tuple[str | None, str]:
        """
        (référence, statut interne) depuis le webhook. Le format exact n'est pas
        documenté : on lit la référence et le statut à plat ou sous « data »,
        et l'événement (payin.success / payin.failed) en secours.
        """
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        reference = data.get("reference") or payload.get("reference")
        status = data.get("status") or payload.get("status")
        if not status:
            event = str(payload.get("event") or payload.get("type") or "").lower()
            if event.endswith(".success"):
                status = "SUCCESS"
            elif event.endswith(".failed"):
                status = "FAILED"
        return reference, KratosClient.internal_status(status)

    @staticmethod
    def internal_status(kratos_status: str | None) -> str:
        return KRATOS_STATUS_MAP.get((kratos_status or "").upper(), "PENDING")

    async def initiate_payin(
        self,
        reference: str,
        amount: int,
        phone_number: str,
        provider: str,
        description: str = "GoToGermany",
    ) -> dict:
        """
        Encaissement Mobile Money. Réponse SUCCESS (paiement immédiat),
        PENDING (l'élève valide sur son téléphone, le webhook suivra) ou FAILED.
        """
        payload = {
            "amount": int(amount),
            "currency": "XAF",
            "phoneNumber": self.normalize_phone(phone_number),
            "operator": self.operator_for(provider),
            "reference": reference,
            "description": description[:120],
        }

        logger.info(f"Kratos payin payload: {payload}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self._url("payin"), json=payload, headers=self._headers())
        logger.info(
            f"Kratos payin response: POST {self._url('payin')} → {response.status_code} {response.text}"
        )

        try:
            data = response.json()
        except ValueError:
            raise KratosError(f"Réponse Kratos illisible (HTTP {response.status_code})")

        # Kratos peut répondre HTTP 2xx avec success: false : on lit toujours le corps
        if data.get("success") is False or response.status_code >= 400:
            error = data.get("error") or {}
            raise KratosError(
                error.get("message") or f"Paiement refusé par Kratos (HTTP {response.status_code})",
                code=error.get("code"),
                details=error.get("details"),
                request_id=(data.get("meta") or {}).get("request_id"),
            )
        return data