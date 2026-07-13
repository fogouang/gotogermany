"""
sprechen_agent.mapping
========================
The single source of truth for "given this Teil's raw data, what
should the agent do?" — turns a format_type (and the presence/absence
of a kandidat_a/kandidat_b split) into a concrete SequenceStep list.

Everything downstream (prompt_builder.py, orchestrator.py) consumes
build_sequence() and never looks at format_type directly. Adding a
new provider/format later means touching only this file.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .session_state import AgentRole, SequenceStep

# Roughly 1.5-2 min — validated cost/pedagogy tradeoff for the AI's
# own presentation when it plays Kandidat B (see prior discussion:
# shortened vs. the official 3-4 min to keep the Live segment cheap).
AI_PRESENTER_TARGET_SECONDS = 120


@dataclass(frozen=True)
class SingleRoleBehavior:
    role: AgentRole
    agent_opens: bool
    behavior_note: str
    # Minimum speaker turns (agent + student combined) before this
    # Teil is considered complete. 1 would mean "done right after the
    # agent's opening line" — wrong for anything conversational.
    min_turns: int = 1


# ---------------------------------------------------------------------------
# format_type -> behavior, for Teile with a single agent role throughout
# ---------------------------------------------------------------------------

FORMAT_TYPE_BEHAVIOR: dict[str, SingleRoleBehavior] = {
    "oral_interaction": SingleRoleBehavior(
        role=AgentRole.PARTNER,
        agent_opens=True,
        behavior_note="Propose, negotiate, and react to the student's ideas. Never correct explicitly.",
        min_turns=4,  # at least 2 full exchanges — free-flowing planning dialogue
    ),
    "oral_kennenlernen": SingleRoleBehavior(
        role=AgentRole.PARTNER,
        agent_opens=True,
        behavior_note="Informal small talk. Ask simple personal questions (name, origin, hobbies).",
        min_turns=4,
    ),
    "oral_monologue": SingleRoleBehavior(
        role=AgentRole.SILENT_LISTENER,
        agent_opens=False,
        behavior_note='Do not interrupt. Minimal backchannel only ("Mhm", "Ja").',
        min_turns=1,  # the student's whole presentation is genuinely one turn
    ),
    "oral_feedback": SingleRoleBehavior(
        role=AgentRole.EXAMINER,
        agent_opens=True,
        behavior_note="Give brief feedback on what was just presented, then ask exactly one question.",
        min_turns=2,  # agent's question, then the student's answer
    ),
    "oral_discussion": SingleRoleBehavior(
        role=AgentRole.PARTNER,
        agent_opens=True,
        behavior_note="Take a genuine position and argue it honestly, without being complacent.",
        min_turns=4,
    ),
    "oral_meinungsaustausch": SingleRoleBehavior(
        role=AgentRole.ASSIGNED_POSITION,
        agent_opens=True,
        behavior_note="Defend the assigned position from the subject data, even if it isn't your own genuine opinion.",
        min_turns=4,
    ),
    "bildbeschreibung": SingleRoleBehavior(
        role=AgentRole.SILENT_LISTENER,
        agent_opens=False,
        behavior_note="Listen to the description/interpretation, then ask one brief clarifying question.",
        min_turns=3,  # description, agent's question, student's brief answer
    ),
    "oral_thema": SingleRoleBehavior(
        role=AgentRole.PARTNER,
        agent_opens=True,
        behavior_note=(
            "Briefly report what the two stimulus people (person_a/person_b in the subject "
            "data) think about the topic — their names and opinions are given in the content "
            "block below. Then discuss the topic genuinely with the student: ask their opinion, "
            "react to it, compare it with the two given viewpoints."
        ),
        min_turns=4,  # report the stimulus, then a real back-and-forth discussion
    ),
}

# Any format_type we haven't seen yet falls back here instead of
# crashing — logged loudly elsewhere (service.py) so it gets noticed
# and a real entry gets added above.
DEFAULT_BEHAVIOR = SingleRoleBehavior(
    role=AgentRole.PARTNER,
    agent_opens=True,
    behavior_note="Generic dialogue partner — react naturally to the student.",
    min_turns=2,
)

# Role -> generic instruction, used for steps inside the alternating
# sequence where there's no single format_type to look up (the role
# changes mid-Teil).
ROLE_DEFAULT_NOTES: dict[AgentRole, str] = {
    AgentRole.SILENT_LISTENER: 'Do not interrupt. Minimal backchannel only ("Mhm", "Ja").',
    AgentRole.EXAMINER: "Give brief feedback on what was just heard, then ask exactly one question.",
    AgentRole.PRESENTER: "Deliver a short, structured presentation (intro, 2-3 points, conclusion) at the target CEFR level.",
    AgentRole.PARTNER: "React naturally, propose and negotiate.",
    AgentRole.ASSIGNED_POSITION: "Defend the assigned position, even if it isn't your own genuine opinion.",
}


# ---------------------------------------------------------------------------
# Content normalization — leitpunkte / prompts / tasks / leitfragen / hinweis
# all mean roughly the same thing across providers
# ---------------------------------------------------------------------------

def _extract_content_points(data: dict[str, Any]) -> list[str]:
    for key in ("leitpunkte", "prompts", "tasks", "leitfragen"):
        value = data.get(key)
        if value:
            return list(value)
    hinweis = data.get("hinweis")
    return [hinweis] if hinweis else []


def _content_payload(teil_raw: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "instructions": teil_raw.get("instructions", ""),
        "content_points": _extract_content_points(teil_raw),
        "scenario": (
            teil_raw.get("scenario")
            or teil_raw.get("situation")
            or teil_raw.get("thema")
            or teil_raw.get("topic")
            or teil_raw.get("diskussion_titel")
            or teil_raw.get("question")
        ),
    }
    # Stimulus people — different key names across providers for the
    # same concept (telc's oral_thema uses person_a/person_b; ÖSD's
    # oral_meinungsaustausch uses person1/person2). Passed through as-is
    # so prompt_builder.py can render whichever pair is present.
    for key in ("person_a", "person_b", "person1", "person2"):
        if key in teil_raw:
            payload[key] = teil_raw[key]
    return payload


def _has_two_candidate_split(teil_raw: dict[str, Any]) -> bool:
    return "kandidat_a" in teil_raw or "kandidat_b" in teil_raw


# ---------------------------------------------------------------------------
# Sequence builders
# ---------------------------------------------------------------------------

def _build_default_alternating_sequence(teil_raw: dict[str, Any]) -> list[SequenceStep]:
    """The 6-step pattern for any Teil with a kandidat_a/kandidat_b
    split: candidate presents -> examiner feedback+question -> candidate
    answers -> AI (Kandidat B) presents -> candidate feedback+question
    -> AI answers. Matches the official Prüferblätter pattern.

    Note: when the raw data includes an explicit ablauf_schema (free
    text, e.g. Goethe B1), we deliberately don't parse it — it
    documents the same pattern for humans reading the JSON. This fixed
    template is validated directly against the official Prüferblätter
    instead of trusting free-text parsing.
    """
    kandidat_b_data = teil_raw.get("kandidat_b", {})

    return [
        SequenceStep(
            order=1, role=AgentRole.SILENT_LISTENER, agent_opens=False,
            content={"behavior_note": ROLE_DEFAULT_NOTES[AgentRole.SILENT_LISTENER]},
        ),
        SequenceStep(
            order=2, role=AgentRole.EXAMINER, agent_opens=True,
            content={"behavior_note": ROLE_DEFAULT_NOTES[AgentRole.EXAMINER]},
            target_duration_seconds=45,
        ),
        SequenceStep(
            order=3, role=AgentRole.SILENT_LISTENER, agent_opens=False,
            content={"behavior_note": ROLE_DEFAULT_NOTES[AgentRole.SILENT_LISTENER]},
        ),
        SequenceStep(
            order=4, role=AgentRole.PRESENTER, agent_opens=True,
            content={
                "behavior_note": ROLE_DEFAULT_NOTES[AgentRole.PRESENTER],
                **_content_payload(kandidat_b_data),
            },
            target_duration_seconds=AI_PRESENTER_TARGET_SECONDS,
        ),
        SequenceStep(
            order=5, role=AgentRole.SILENT_LISTENER, agent_opens=False,
            content={"behavior_note": ROLE_DEFAULT_NOTES[AgentRole.SILENT_LISTENER]},
        ),
        SequenceStep(
            order=6, role=AgentRole.EXAMINER, agent_opens=False,
            content={"behavior_note": ROLE_DEFAULT_NOTES[AgentRole.EXAMINER]},
            target_duration_seconds=45,
        ),
    ]


def _build_single_role_sequence(teil_raw: dict[str, Any]) -> list[SequenceStep]:
    format_type = teil_raw.get("format_type", "")
    behavior = FORMAT_TYPE_BEHAVIOR.get(format_type, DEFAULT_BEHAVIOR)
    duration_minutes = teil_raw.get("duration_minutes") or 0

    return [
        SequenceStep(
            order=1,
            role=behavior.role,
            agent_opens=behavior.agent_opens,
            content={"behavior_note": behavior.behavior_note, **_content_payload(teil_raw)},
            target_duration_seconds=(duration_minutes * 60) or None,
            min_turns=behavior.min_turns,
        )
    ]


# Public aliases — orchestrator.py needs these directly when resolving
# what the AI should present as Kandidat B (theme selection happens
# there, not here; this module stays generic/provider-agnostic).
extract_content_points = _extract_content_points
content_payload = _content_payload


def build_sequence(teil_raw: dict[str, Any]) -> list[SequenceStep]:
    """Entry point: given a raw Teil dict straight from the DB-stored
    subject JSON, return the agent's sequence of sub-roles for it."""
    if _has_two_candidate_split(teil_raw):
        return _build_default_alternating_sequence(teil_raw)
    return _build_single_role_sequence(teil_raw)