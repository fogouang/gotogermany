"""
app/modules/payments/pawapay.py
"""
import httpx
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

PAWAPAY_BASE_URL = "https://api.pawapay.io"


class PawapayClient:

    def __init__(self):
        settings = get_settings()
        self.base_url = PAWAPAY_BASE_URL
        self.token = settings.PAWAPAY_API_TOKEN
        logger.info(f"PawapayClient init: base_url={self.base_url}, token_prefix={self.token[:20]}...")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def initiate_deposit(
        self,
        deposit_id: str,
        amount: int,
        phone_number: str,
        provider: str,
        client_reference_id: str,
        customer_message: str = "GoToGermany",
    ) -> dict:
        payload = {
            "depositId": deposit_id,
            "amount": str(amount),
            "currency": "XAF",
            "payer": {
                "type": "MMO",
                "accountDetails": {
                    "phoneNumber": phone_number,
                    "provider": provider,
                },
            },
            "clientReferenceId": client_reference_id,
            "customerMessage": customer_message,
        }
        logger.info(f"pawaPay initiate_deposit payload: {payload}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v2/deposits",
                json=payload,
                headers=self._headers(),
            )
            logger.info(f"pawaPay response: {response.status_code} {response.text}")
            response.raise_for_status()
            return response.json()

    async def get_deposit_status(self, deposit_id: str) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{self.base_url}/v2/deposits/{deposit_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def resend_callback(self, deposit_id: str) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.base_url}/v2/deposits/resend-callback/{deposit_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()