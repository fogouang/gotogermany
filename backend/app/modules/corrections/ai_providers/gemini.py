"""
Provider Gemini (Google) pour correction IA - GotoGermany.
Fallback automatique vers Claude Haiku si Gemini est indisponible (503).

Limite de sortie : 8192 tokens pour Gemini ET pour le fallback Claude
(la sortie contient corrected_text + model_text par tâche). Une réponse
coupée par la limite (Gemini finish_reason MAX_TOKENS / Claude stop_reason
max_tokens) lève une erreur explicite au lieu d'être "réparée" en JSON incomplet.

temperature = 0 : la même copie donne le même résultat à chaque correction.

Coût : chaque résultat porte une clé "_usage" {model, input_tokens,
output_tokens, cost_usd}, affichée en développement sur la page de résultat
du simulateur et ignorée par le response_normalizer.
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

MAX_OUTPUT_TOKENS = 8192
GEMINI_MODEL = "gemini-2.5-flash-lite"
CLAUDE_FALLBACK_MODEL = "claude-haiku-4-5-20251001"

# Tarifs en USD par million de tokens, pour l'affichage du coût
GEMINI_PRICE_INPUT_PER_MTOK = 0.10
GEMINI_PRICE_OUTPUT_PER_MTOK = 0.40
CLAUDE_FALLBACK_PRICE_INPUT_PER_MTOK = 1.0
CLAUDE_FALLBACK_PRICE_OUTPUT_PER_MTOK = 5.0


def _usage(model: str, input_tokens: int, output_tokens: int,
           price_in: float, price_out: float) -> dict[str, Any]:
    """Coût réel d'un appel, joint au résultat sous la clé "_usage"."""
    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(
            input_tokens / 1_000_000 * price_in + output_tokens / 1_000_000 * price_out,
            5,
        ),
    }


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
        self.model_id = GEMINI_MODEL

        # Fallback Claude : None si pas de clé configurée
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
                    "max_output_tokens": MAX_OUTPUT_TOKENS,
                    "temperature": 0,
                    "response_mime_type": "application/json",
                },
            )

            # Réponse coupée par la limite : JSON forcément incomplet
            candidates = getattr(response, "candidates", None) or []
            finish_reason = str(getattr(candidates[0], "finish_reason", "")) if candidates else ""
            if "MAX_TOKENS" in finish_reason:
                raise ValueError(
                    f"Réponse Gemini tronquée (limite de {MAX_OUTPUT_TOKENS} tokens atteinte)."
                )

            result = self._parse_response(response.text)

            meta = getattr(response, "usage_metadata", None)
            result["_usage"] = _usage(
                self.model_id,
                getattr(meta, "prompt_token_count", 0) or 0,
                getattr(meta, "candidates_token_count", 0) or 0,
                GEMINI_PRICE_INPUT_PER_MTOK,
                GEMINI_PRICE_OUTPUT_PER_MTOK,
            )
            logger.info(
                f"Gemini correction completed ({self.model_id}): "
                f"cost_estimate=${result['_usage']['cost_usd']:.5f}"
            )
            return result

        except genai_errors.ServerError as e:
            # 503 UNAVAILABLE → fallback Claude
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                logger.warning(
                    "Gemini 503 : basculement sur Claude Haiku fallback"
                )
                return await self._correct_with_claude(prompt)
            raise self._handle_error(e)

        except Exception as e:
            raise self._handle_error(e)

    # ── Fallback Claude ───────────────────────────────────────────────

    async def _correct_with_claude(self, prompt: str) -> dict[str, Any]:
        """
        Correction via Claude Haiku 4.5 si Gemini est indisponible.
        Haiku est le modèle le moins cher (~$0.01-0.02/correction avec Mustertext).
        """
        if not self._claude:
            raise Exception(
                "Service de correction temporairement indisponible. "
                "Réessayez dans quelques minutes."
            )

        try:
            logger.debug("Sending prompt to Claude Haiku fallback")
            response = await self._claude.messages.create(
                model=CLAUDE_FALLBACK_MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                        + "\n\nRéponds UNIQUEMENT en JSON valide, sans texte avant ni après.",
                    }
                ],
            )

            if response.stop_reason == "max_tokens":
                raise ValueError(
                    f"Réponse Claude tronquée (limite de {MAX_OUTPUT_TOKENS} tokens atteinte)."
                )

            content = response.content[0].text
            result = self._parse_response(content)
            result["_usage"] = _usage(
                CLAUDE_FALLBACK_MODEL,
                response.usage.input_tokens,
                response.usage.output_tokens,
                CLAUDE_FALLBACK_PRICE_INPUT_PER_MTOK,
                CLAUDE_FALLBACK_PRICE_OUTPUT_PER_MTOK,
            )
            logger.info(
                f"Claude Haiku fallback correction completed: "
                f"output_tokens={response.usage.output_tokens}, "
                f"cost_estimate=${result['_usage']['cost_usd']:.5f}"
            )
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
            logger.warning(f"JSON invalide détecté, tentative de réparation: {e}")
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