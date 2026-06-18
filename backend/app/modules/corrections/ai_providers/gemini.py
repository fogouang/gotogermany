"""
Provider Gemini (Google) pour correction IA - GotoGermany.
Fallback automatique vers Claude Haiku si Gemini est indisponible (503).
"""
import json
import logging
from typing import Any

import anthropic
from google import genai
from google.genai import errors as genai_errors

from app.config import get_settings
from app.modules.corrections.ai_providers.base import AIProvider

settings = get_settings()
logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Provider Gemini (Google) avec fallback Claude Haiku.

    Flow :
    1. Essaie Gemini 2.5 Flash Lite
    2. Si 503 UNAVAILABLE → bascule sur Claude Haiku 4.5
    3. Si Claude aussi indisponible → lève une exception claire
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.5-flash-lite"

        # Fallback Claude — None si pas de clé configurée
        self._claude = None
        if getattr(settings, "ANTHROPIC_API_KEY", None):
            self._claude = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )

    async def correct(self, prompt: str) -> dict[str, Any]:
        # ── Tentative Gemini ──────────────────────────────────────────
        try:
            logger.debug(
                f"Sending prompt to Gemini ({self.model_id}), length={len(prompt)}"
            )
            response = await self.client.aio.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={
                    "max_output_tokens": 8192,
                    "temperature": 0.3,
                    "response_mime_type": "application/json",
                },
            )
            result = self._parse_response(response.text)
            logger.info("Gemini correction completed successfully")
            return result

        except genai_errors.ServerError as e:
            # 503 UNAVAILABLE → fallback Claude
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                logger.warning(
                    "Gemini 503 — basculement sur Claude Haiku fallback"
                )
                return await self._correct_with_claude(prompt)
            raise self._handle_error(e)

        except Exception as e:
            raise self._handle_error(e)

    # ── Fallback Claude ───────────────────────────────────────────────

    async def _correct_with_claude(self, prompt: str) -> dict[str, Any]:
        """
        Correction via Claude Haiku 4.5 si Gemini est indisponible.
        Haiku est le modèle le moins cher (~$0.005/correction).
        """
        if not self._claude:
            raise Exception(
                "Service de correction temporairement indisponible. "
                "Réessayez dans quelques minutes."
            )

        try:
            logger.debug("Sending prompt to Claude Haiku fallback")
            response = await self._claude.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                        + "\n\nRéponds UNIQUEMENT en JSON valide, sans texte avant ni après.",
                    }
                ],
            )
            content = response.content[0].text
            result = self._parse_response(content)
            logger.info("Claude Haiku fallback correction completed successfully")
            return result

        except Exception as e:
            logger.error(f"Claude fallback error: {e}")
            raise Exception(
                "Service de correction temporairement indisponible. "
                "Réessayez dans quelques minutes."
            )

    # ── Helpers ───────────────────────────────────────────────────────

    def _parse_response(self, content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1]).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON tronqué détecté, tentative de réparation: {e}")
            try:
                open_braces = cleaned.count("{")
                close_braces = cleaned.count("}")
                if open_braces > close_braces:
                    cleaned += "}" * (open_braces - close_braces)
                return json.loads(cleaned)
            except json.JSONDecodeError:
                logger.error(f"JSON parse error: {e}")
                logger.debug(f"Raw content (first 500 chars): {content[:500]}")
                raise ValueError(
                    f"La réponse du modèle n'est pas un JSON valide: {str(e)}"
                )

    def _handle_error(self, error: Exception) -> Exception:
        error_msg = str(error)
        logger.error(f"Gemini API error: {error_msg}")

        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return Exception(
                "Quota Gemini dépassé. Veuillez réessayer dans quelques minutes."
            )
        if "401" in error_msg or "INVALID_API_KEY" in error_msg:
            return Exception(
                "Clé API Gemini invalide. Vérifiez votre configuration."
            )
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            return Exception(
                "Service de correction temporairement indisponible. "
                "Réessayez dans un moment."
            )
        return Exception(f"Erreur Gemini API: {error_msg[:200]}")