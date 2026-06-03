"""
Provider Gemini (Google) pour correction IA - GotoGermany.
"""
import json
import logging
from typing import Any

from google import genai

from app.config import get_settings
from app.modules.corrections.ai_providers.base import AIProvider

settings = get_settings()
logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Provider Gemini (Google).

    Responsabilité unique : envoyer le prompt à Gemini et parser le JSON retourné.
    Ne connaît pas les examens, les niveaux ni la structure des tâches.
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.5-flash-lite"

    async def correct(self, prompt: str) -> dict[str, Any]:
        """
        Envoyer le prompt à Gemini et retourner la réponse parsée.

        Args:
            prompt: Prompt complet déjà construit

        Returns:
            dict avec la correction complète

        Raises:
            Exception: Quota dépassé, clé invalide, erreur réseau
        """
        try:
            logger.debug(f"Sending prompt to Gemini ({self.model_id}), length={len(prompt)}")

            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt
            )

            result = self._parse_response(response.text)
            logger.info("Gemini correction completed successfully")
            return result

        except Exception as e:
            raise self._handle_error(e)

    # ------------------------------------------------------------------ #
    # Méthodes privées                                                     #
    # ------------------------------------------------------------------ #

    def _parse_response(self, content: str) -> dict[str, Any]:
        """
        Parser la réponse JSON de Gemini.

        Gemini peut parfois retourner le JSON enveloppé dans des balises markdown
        (```json ... ```). On nettoie ça avant de parser.

        Args:
            content: Texte brut retourné par Gemini

        Returns:
            dict parsé

        Raises:
            ValueError: Si le JSON est invalide et non récupérable
        """
        cleaned = content.strip()

        # Supprimer les balises markdown si présentes
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            # Retirer la première ligne (```json ou ```) et la dernière (```)
            cleaned = "\n".join(lines[1:-1]).strip()

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Raw content (first 500 chars): {content[:500]}")
            raise ValueError(
                f"La réponse du modèle n'est pas un JSON valide: {str(e)}"
            )

    def _handle_error(self, error: Exception) -> Exception:
        """
        Convertir les erreurs Gemini en messages lisibles.

        Args:
            error: Exception brute de l'API Gemini

        Returns:
            Exception avec message clair
        """
        error_msg = str(error)
        logger.error(f"Gemini API error: {error_msg}")

        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return Exception(
                "Quota Gemini dépassé. Veuillez réessayer dans quelques minutes "
                "ou utiliser une autre clé API."
            )
        if "401" in error_msg or "INVALID_API_KEY" in error_msg:
            return Exception(
                "Clé API Gemini invalide. Vérifiez votre configuration."
            )
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            return Exception(
                "Service Gemini temporairement indisponible. Réessayez dans un moment."
            )

        return Exception(f"Erreur Gemini API: {error_msg[:200]}")