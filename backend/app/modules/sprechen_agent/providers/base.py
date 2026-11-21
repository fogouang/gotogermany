"""
sprechen_agent.providers.base
================================
Contrat commun à tous les organismes d'examen (telc, Goethe, ÖSD, ECL,
TestDaF).

Un profil d'organisme décide, Teil par Teil, de la séquence d'étapes
de l'IA : rôle, qui ouvre, durée cible, consignes, phases à suivre,
types de questions à varier. Quand il ne connaît pas un Teil (ou un
niveau), il renvoie None et mapping.py applique la logique générique
existante. Un organisme pas encore traité garde donc exactement son
comportement actuel.

Ce module ne doit JAMAIS importer mapping.py (mapping.py importe les
profils) : le contenu normalisé du Teil est passé en argument.
"""

from __future__ import annotations

from typing import Any

from ..session_state import AgentRole, SequenceStep

# Règles de partenaire communes à tous les organismes, ajoutées aux
# consignes de chaque étape où l'IA joue le partenaire.
PARTNER_RULES = (
    "Partner rules: keep each of your turns short (2 to 4 sentences) so the "
    "student does most of the talking. Always react to what the student just "
    "said before adding something new. Never dominate, never lecture. If the "
    "student is stuck, rephrase your last question more simply or ask an easier "
    "one, but never give them the answer or vocabulary."
)


# Voix Gemini Live fixes par rôle : une voix pour l'évaluateur, une
# autre pour le partenaire (le même "candidat" pendant tout l'oral,
# qu'il présente, discute ou défende une position). Sans voix fixée,
# chaque nouveau segment pouvait partir sur une voix différente.
EXAMINER_VOICE = "Kore"
PARTNER_VOICE = "Aoede"

# Identité fixe par rôle : chaque segment est une nouvelle connexion
# sans mémoire, donc sans nom imposé l'IA en inventait un nouveau à
# chaque fois (Alex, puis Klara...).
EXAMINER_NAME = "Frau Wagner"
PARTNER_NAME = "Klara"

ROLE_VOICES: dict[AgentRole, str] = {
    AgentRole.EXAMINER: EXAMINER_VOICE,
    AgentRole.PARTNER: PARTNER_VOICE,
    AgentRole.PRESENTER: PARTNER_VOICE,
    AgentRole.ASSIGNED_POSITION: PARTNER_VOICE,
    AgentRole.SILENT_LISTENER: PARTNER_VOICE,
}


def voice_for_role(role: AgentRole) -> str:
    return ROLE_VOICES.get(role, PARTNER_VOICE)


def persona_name_for_role(role: AgentRole) -> str:
    return EXAMINER_NAME if role == AgentRole.EXAMINER else PARTNER_NAME


def normalize_level(level: str | None) -> str:
    """'b2', 'B2 ', 'B2.1' -> 'B2'."""
    return (level or "").strip().upper()[:2]


def teil_seconds(teil_raw: dict[str, Any], default_seconds: int) -> int:
    minutes = teil_raw.get("duration_minutes") or teil_raw.get("time_minutes") or 0
    return int(minutes * 60) if minutes else default_seconds


def make_step(
    *,
    order: int,
    role: AgentRole,
    agent_opens: bool,
    behavior_note: str,
    content: dict[str, Any] | None = None,
    target_duration_seconds: int | None = None,
    min_turns: int = 1,
    phases: list[str] | None = None,
    question_categories: list[str] | None = None,
) -> SequenceStep:
    """Construit une étape avec les clés de contenu que prompt_builder.py
    sait afficher : behavior_note, phases, question_categories (+ le
    contenu normalisé du Teil : instructions, content_points, scenario,
    text, person_a/person_b...)."""
    step_content: dict[str, Any] = {**(content or {}), "behavior_note": behavior_note}
    if phases:
        step_content["phases"] = list(phases)
    if question_categories:
        step_content["question_categories"] = list(question_categories)
    return SequenceStep(
        order=order,
        role=role,
        agent_opens=agent_opens,
        content=step_content,
        target_duration_seconds=target_duration_seconds,
        min_turns=min_turns,
    )


class ProviderProfile:
    """Profil par défaut : ne sait rien, renvoie toujours None."""

    name = "generic"

    def build_sequence(
        self,
        teil_raw: dict[str, Any],
        *,
        level: str,
        content: dict[str, Any],
    ) -> list[SequenceStep] | None:
        return None