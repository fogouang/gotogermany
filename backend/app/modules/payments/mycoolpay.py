"""
Client My-CoolPay - Intégration réelle.
"""

import hashlib
import logging
from typing import Any

import httpx

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MyCoolPayClient:
    """
    Client pour l'API My-CoolPay.
    
    Documentation: https://documenter.getpostman.com/view/17178321/UV5ZCx8f
    """
    
    def __init__(self):
        self.public_key = settings.MYCOOLPAY_PUBLIC_KEY
        self.private_key = settings.MYCOOLPAY_PRIVATE_KEY
        self.base_url = settings.MYCOOLPAY_BASE_URL
        self.callback_url = settings.MYCOOLPAY_CALLBACK_URL
    
    async def create_paylink(
        self,
        transaction_amount: float,
        app_transaction_ref: str,
        transaction_reason: str,
        customer_name: str | None = None,
        customer_phone_number: str | None = None,
        customer_email: str | None = None,
        customer_lang: str = "fr"
    ) -> dict[str, Any]:
        """
        Créer un lien de paiement (Paylink).
        
        L'utilisateur sera redirigé vers My-CoolPay pour payer.
        
        Args:
            transaction_amount: Montant en FCFA
            app_transaction_ref: Référence unique dans notre système (invoice_number)
            transaction_reason: Raison du paiement
            customer_name: Nom du client
            customer_phone_number: Téléphone du client
            customer_email: Email du client
            customer_lang: Langue (en/fr)
            
        Returns:
            dict avec payment_url et transaction_ref
            
        Raises:
            Exception: Si erreur API
        """
        url = f"{self.base_url}/{self.public_key}/paylink"
        
        payload = {
            "transaction_amount": int(transaction_amount),  # Doit être int
            "transaction_currency": "XAF",
            "transaction_reason": transaction_reason,
            "app_transaction_ref": app_transaction_ref,
            "customer_name": customer_name,
            "customer_phone_number": customer_phone_number,
            "customer_email": customer_email,
            "customer_lang": customer_lang
        }
        
        # Enlever les None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"Paylink created: {data}")
                
                return data
        
        except httpx.HTTPError as e:
            logger.error(f"My-CoolPay API error: {e}")
            raise Exception(f"Erreur My-CoolPay: {str(e)}")
    
    async def create_payin(
        self,
        transaction_amount: float,
        customer_phone_number: str,
        app_transaction_ref: str,
        transaction_reason: str,
        customer_name: str | None = None,
        customer_email: str | None = None,
        customer_lang: str = "fr"
    ) -> dict[str, Any]:
        """
        Initier un paiement synchrone (Payin).
        
        Utilisé pour mobile money direct.
        
        Args:
            transaction_amount: Montant en FCFA
            customer_phone_number: Téléphone (requis)
            app_transaction_ref: Référence unique
            transaction_reason: Raison
            customer_name: Nom
            customer_email: Email
            customer_lang: Langue
            
        Returns:
            dict avec transaction_ref, action, ussd
        """
        url = f"{self.base_url}/{self.public_key}/payin"
        
        payload = {
            "transaction_amount": int(transaction_amount),
            "transaction_currency": "XAF",
            "transaction_reason": transaction_reason,
            "app_transaction_ref": app_transaction_ref,
            "customer_phone_number": customer_phone_number,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_lang": customer_lang
        }
        
        payload = {k: v for k, v in payload.items() if v is not None}
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"Payin created: {data}")
                
                return data
        
        except httpx.HTTPStatusError as e:
            # e.response est disponible pour les erreurs 4xx/5xx
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text

            logger.error(f"My-CoolPay Payin error {e.response.status_code}: {error_detail}")
            logger.error(f"Request payload was: {e.request.json() if hasattr(e.request, 'json') else 'N/A'}")

            raise Exception(f"Erreur My-CoolPay ({e.response.status_code}): {error_detail}")
        except httpx.HTTPError as e:
            logger.error(f"My-CoolPay connection error: {str(e)}")
            raise Exception(f"Erreur connexion My-CoolPay: {str(e)}")
        
    
    async def check_status(self, transaction_ref: str) -> dict[str, Any]:
        """
        Vérifier le statut d'une transaction.
        
        Args:
            transaction_ref: Référence My-CoolPay
            
        Returns:
            dict avec status, transaction details
        """
        url = f"{self.base_url}/{self.public_key}/checkStatus/{transaction_ref}"
        
        headers = {
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Check status error: {e}")
            raise Exception(f"Erreur vérification: {str(e)}")
    
    def verify_webhook_signature(
        self,
        transaction_ref: str,
        transaction_type: str,
        transaction_amount: float,
        transaction_currency: str,
        transaction_operator: str,
        signature: str
    ) -> bool:
        """
        Vérifier la signature MD5 du webhook.
        
        Formula:
        signature = md5(
            transaction_ref +
            transaction_type +
            transaction_amount +
            transaction_currency +
            transaction_operator +
            private_key
        )
        
        Args:
            transaction_ref: Référence transaction
            transaction_type: PAYIN ou PAYOUT
            transaction_amount: Montant (nombre)
            transaction_currency: XAF
            transaction_operator: CM_MOMO, CM_OM, CARD, MCP
            signature: Signature reçue
            
        Returns:
            True si signature valide
        """
        # Convertir amount en string sans zéros non significatifs
        amount_str = str(int(transaction_amount)) if transaction_amount == int(transaction_amount) else str(transaction_amount)
        
        # Construire la chaîne à hasher
        data = (
            transaction_ref +
            transaction_type +
            amount_str +
            transaction_currency +
            transaction_operator +
            self.private_key
        )
        
        # Calculer MD5
        expected_signature = hashlib.md5(data.encode()).hexdigest()
        
        # Comparaison
        is_valid = expected_signature == signature
        
        if not is_valid:
            logger.warning(f"Invalid signature! Expected: {expected_signature}, Got: {signature}")
            logger.debug(f"Data used: {data}")
        
        return is_valid
    
    async def get_balance(self) -> dict[str, Any]:
        """
        Récupérer le solde de l'application.
        
        Returns:
            dict avec balance
        """
        url = f"{self.base_url}/{self.public_key}/balance"
        
        headers = {
            "Accept": "application/json",
            "X-PRIVATE-KEY": self.private_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Get balance error: {e}")
            raise Exception(f"Erreur récupération solde: {str(e)}")