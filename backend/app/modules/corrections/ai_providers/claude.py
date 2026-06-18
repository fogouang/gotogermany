"""
Provider Claude (Anthropic) pour correction IA - GotoGermany.

Utilisé comme :
- Fallback automatique quand Gemini est indisponible (503)
- Provider principal si configuré explicitement

Modèle : claude-haiku-4-5-20251001 (le moins cher, suffisant pour corrections)
Pricing : $1/MTok input, $5/MTok output
"""
import json
import logging
from typing import Any

import anthropic

from app.config import get_settings
from app.modules.corrections.ai_providers.base import AIProvider

settings = get_settings()
logger = logging.getLogger(__name__)

# Modèle utilisé — Haiku pour économie, Sonnet si qualité insuffisante
CLAUDE_MODEL = "claude-haiku-4-5-20251001"


class ClaudeProvider(AIProvider):
    """
    Provider Claude Anthropic.

    Responsabilité unique : envoyer le prompt à Claude et parser le JSON retourné.
    Ne connaît pas les examens, les niveaux ni la structure des tâches.
    """

    def __init__(self):
        if not getattr(settings, "ANTHROPIC_API_KEY", None):
            raise ValueError(
                "ANTHROPIC_API_KEY non configurée. "
                "Ajoutez-la dans votre fichier .env."
            )
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        self.model_id = CLAUDE_MODEL

    async def correct(self, prompt: str) -> dict[str, Any]:
        try:
            logger.debug(
                f"Sending prompt to Claude ({self.model_id}), length={len(prompt)}"
            )

            response = await self.client.messages.create(
                model=self.model_id,
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

            # Log usage pour suivi de consommation
            usage = response.usage
            logger.info(
                f"Claude correction completed — "
                f"input_tokens={usage.input_tokens}, "
                f"output_tokens={usage.output_tokens}, "
                f"cost_estimate=${self._estimate_cost(usage):.5f}"
            )

            content = response.content[0].text
            return self._parse_response(content)

        except anthropic.AuthenticationError:
            raise Exception(
                "Clé API Claude invalide. Vérifiez votre configuration ANTHROPIC_API_KEY."
            )
        except anthropic.RateLimitError:
            raise Exception(
                "Limite de débit Claude atteinte. Réessayez dans quelques instants."
            )
        except anthropic.APIStatusError as e:
            raise Exception(
                f"Erreur Claude API ({e.status_code}): {str(e)[:200]}"
            )
        except Exception as e:
            logger.error(f"Claude error: {e}")
            raise Exception(
                f"Erreur Claude inattendue: {str(e)[:200]}"
            )

    # ── Helpers ───────────────────────────────────────────────────────

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse la réponse JSON de Claude."""
        cleaned = content.strip()

        # Retirer les blocs markdown si présents
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
                    f"La réponse de Claude n'est pas un JSON valide: {str(e)}"
                )

    def _estimate_cost(self, usage: anthropic.types.Usage) -> float:
        """
        Estime le coût en USD pour cette requête.
        Haiku : $1/MTok input, $5/MTok output
        """
        input_cost  = (usage.input_tokens  / 1_000_000) * 1.0
        output_cost = (usage.output_tokens / 1_000_000) * 5.0
        return input_cost + output_cost