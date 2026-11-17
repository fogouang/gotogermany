"""
Provider Claude (Anthropic) pour correction IA - GotoGermany.

Utilisé comme :
- Provider principal si AI_PROVIDER=claude
- Fallback automatique quand Gemini est indisponible (503), via gemini.py

Modèle : claude-sonnet-4-6 (suit fiablement les règles de correction longues ;
Haiku produisait de fausses fautes et des notes instables sur la même copie)
Pricing : $3/MTok input, $15/MTok output (~0,03-0,05 $ par correction)

temperature = 0 : la même copie donne le même résultat à chaque correction.

max_tokens = 8192 : la sortie contient corrected_text ET model_text par tâche
(jusqu'à 3 tâches pour Goethe/ÖSD B1). Une réponse coupée par la limite
(stop_reason == "max_tokens") lève une erreur explicite au lieu d'être
"réparée" en un JSON incomplet.
"""
import json
import logging
from typing import Any

import anthropic

from app.config import get_settings
from app.modules.corrections.ai_providers.base import AIProvider

settings = get_settings()
logger = logging.getLogger(__name__)

# Sonnet pour la fiabilité des corrections (Haiku : fausses fautes, notes instables)
CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS = 8192

# Tarifs du modèle ci-dessus, en USD par million de tokens
PRICE_INPUT_PER_MTOK = 3.0
PRICE_OUTPUT_PER_MTOK = 15.0


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
                max_tokens=CLAUDE_MAX_TOKENS,
                temperature=0,
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
                f"Claude correction completed ({self.model_id}): "
                f"input_tokens={usage.input_tokens}, "
                f"output_tokens={usage.output_tokens}, "
                f"stop_reason={response.stop_reason}, "
                f"cost_estimate=${self._estimate_cost(usage):.5f}"
            )

            # Réponse coupée par la limite : JSON forcément incomplet
            if response.stop_reason == "max_tokens":
                raise ValueError(
                    f"Réponse Claude tronquée (limite de {CLAUDE_MAX_TOKENS} tokens atteinte)."
                )

            content = response.content[0].text
            result = self._parse_response(content)
            # Coût réel joint au résultat (lu par le simulateur, ignoré par le normalizer)
            result["_usage"] = {
                "model": self.model_id,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cost_usd": round(self._estimate_cost(usage), 5),
            }
            return result

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
                    f"La réponse de Claude n'est pas un JSON valide: {str(e)}"
                )

    def _estimate_cost(self, usage: anthropic.types.Usage) -> float:
        """Estime le coût en USD de la requête, aux tarifs de CLAUDE_MODEL."""
        input_cost = (usage.input_tokens / 1_000_000) * PRICE_INPUT_PER_MTOK
        output_cost = (usage.output_tokens / 1_000_000) * PRICE_OUTPUT_PER_MTOK
        return input_cost + output_cost