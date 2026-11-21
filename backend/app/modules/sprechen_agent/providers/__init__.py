"""
sprechen_agent.providers
==========================
Registre des profils par organisme d'examen.

Pour ajouter un organisme (Goethe, ÖSD, ECL, TestDaF) : créer son
fichier (ex. goethe.py) avec une classe ProviderProfile, puis l'ajouter
à _PROFILES ci-dessous. Tant qu'un organisme n'est pas enregistré ici,
get_profile() renvoie None et mapping.py garde la logique générique.
"""

from __future__ import annotations

from .base import ProviderProfile
from .goethe import GoetheProfile
from .telc import TelcProfile

_PROFILES: dict[str, ProviderProfile] = {
    "telc": TelcProfile(),
    "goethe": GoetheProfile(),
}

# Mêmes alias que router.SPRECHEN_PROVIDERS
_ALIASES: dict[str, str] = {
    "ösd": "oesd",
    "osd": "oesd",
}


def get_profile(provider: str | None) -> ProviderProfile | None:
    key = (provider or "").strip().lower()
    key = _ALIASES.get(key, key)
    return _PROFILES.get(key)