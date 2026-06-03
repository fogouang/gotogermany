"""
Interface abstraite pour les providers IA de correction.
"""
from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """
    Interface commune pour tous les providers IA.

    Le provider a une seule responsabilité :
    - Envoyer un prompt déjà construit au modèle
    - Parser la réponse JSON et la retourner

    La logique métier (construction du prompt, grilles de notation,
    structure des tâches) est gérée en dehors du provider.
    """

    @abstractmethod
    async def correct(self, prompt: str) -> dict[str, Any]:
        """
        Envoyer un prompt au modèle et retourner la réponse parsée.

        Args:
            prompt: Prompt complet déjà construit (grille + tâches + instructions JSON)

        Returns:
            dict avec la correction complète (scores, feedbacks, corrections, suggestions)

        Raises:
            Exception: Quota dépassé, clé invalide, erreur réseau, etc.
        """
        pass