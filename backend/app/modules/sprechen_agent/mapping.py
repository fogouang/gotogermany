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
    # "oral_monologue" is deliberately NOT listed here — a standalone
    # monologue Teil (no kandidat split, not merged via ablauf_schema —
    # both of those bypass _build_single_role_sequence entirely and
    # never consult this table) is handled as its own special case
    # right at the top of _build_single_role_sequence() instead, since
    # it needs a 2-step sequence (presentation, then a follow-up
    # question), not a single step. Every official structure verified
    # so far (telc B2 Teil 1 "Präsentation", Goethe B1 Teil 2+3, Goethe
    # B2 Teil 1 "Kurzvortrag") has the partner/examiner ask 1-2
    # questions right after the presentation — there is no case where
    # a real exam leaves a presentation completely unanswered.
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
    for key in ("leitpunkte", "prompts", "tasks", "leitfragen", "topics"):
        value = data.get(key)
        if value:
            return list(value)

    # Goethe-style slide-by-slide presentation structure (each theme's
    # "folien": [{"nummer":1,"titel":"...","konsigne":"..."}, ...]) —
    # was previously dropped entirely (no key above matched), leaving
    # the AI presenting Kandidat B with nothing but a bare title and no
    # structure to follow. Each slide's own instruction becomes one
    # content point, its title kept as a short label.
    folien = data.get("folien")
    if folien:
        points = []
        for i, slide in enumerate(folien):
            label = slide.get("titel") or f"Folie {slide.get('nummer', i + 1)}"
            points.append(f'{label}: {slide.get("konsigne", "")}')
        return points

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
        # Free-text reading stimulus (telc B2 oral_interaction/
        # oral_discussion "Diskussion" Teile: a full magazine article
        # under "text") — previously silently dropped, reaching
        # neither the agent's prompt nor the frontend prep screen,
        # even though the real exam hands the student this exact text.
        "text": teil_raw.get("text"),
    }
    for key in ("person_a", "person_b", "person1", "person2"):
        if key in teil_raw:
            payload[key] = teil_raw[key]

    if not payload["content_points"] and "themes" in teil_raw:
        payload["themes"] = teil_raw["themes"]

    return payload


def _resolve_stimulus_people(teil_raw: dict[str, Any]) -> list[dict[str, str]] | None:
    """Normalizes the two-stimulus-person pattern used by oral_thema
    (telc: person_a/person_b) and oral_meinungsaustausch (ÖSD:
    person1/person2) into one provider-agnostic shape:
    [{"name": ..., "opinion": ...}, {"name": ..., "opinion": ...}].

    Exists so TeilConfig (and therefore the frontend preparation
    screen) can show the actual reading stimulus — until now this data
    only ever reached the agent's own prompt (prompt_builder.py's
    _format_stimulus_people, kept separate and untouched), never the
    student, even though the real exam hands the student this exact
    text/card during the 20-min Vorbereitungszeit.
    """
    for first_key, second_key in (("person_a", "person_b"), ("person1", "person2")):
        first, second = teil_raw.get(first_key), teil_raw.get(second_key)
        if first and second:
            return [
                {
                    "name": p.get("name", "?"),
                    "opinion": p.get("meinung") or p.get("position") or "",
                }
                for p in (first, second)
            ]
    return None


# Public alias — orchestrator.py needs this directly when populating
# TeilConfig.stimulus_people for the frontend preparation screen.
resolve_stimulus_people = _resolve_stimulus_people


def _has_two_candidate_split(teil_raw: dict[str, Any]) -> bool:
    # Scoped to oral_monologue: this is the only format where the AI
    # genuinely needs to present as Kandidat B in a full alternating
    # sequence. bildbeschreibung also carries kandidat_a/kandidat_b
    # (each candidate's own separate set of images to choose from,
    # not two speakers alternating a presentation+feedback pattern) —
    # matching on key presence alone previously misrouted it into the
    # 6-step alternating template it was never meant to use.
    return (
        teil_raw.get("format_type") == "oral_monologue"
        and ("kandidat_a" in teil_raw or "kandidat_b" in teil_raw)
    )


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
    if not isinstance(kandidat_b_data, dict):
        # e.g. Goethe B2-style: kandidat_b is a LIST of alternative
        # themes ([{"title":..., "leitpunkte":[...]}, ...]) rather than
        # a dict keyed thema1/thema2 — _content_payload() below needs a
        # dict and would crash otherwise (AttributeError: 'list' object
        # has no attribute 'get'). This naive payload is only a
        # placeholder anyway — orchestrator._finalize_presenter_steps()
        # overwrites it right after with the properly resolved theme
        # (orchestrator._resolve_presenter_content() handles the list
        # shape explicitly), so an empty dict here is harmless.
        kandidat_b_data = {}

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
    duration_minutes = teil_raw.get("duration_minutes") or teil_raw.get("time_minutes") or 0

    if format_type == "oral_monologue":
        # A standalone monologue reaching this function is, by
        # construction, neither part of a kandidat_a/kandidat_b split
        # nor merged via ablauf_schema (both bypass this function
        # entirely) — so it's a genuinely lone presentation, and every
        # verified official structure (telc B2 Teil 1, Goethe B1
        # Teil 2+3, Goethe B2 Teil 1) has the partner/examiner ask 1-2
        # questions right after it. Two steps: presentation, then a
        # real follow-up question — not the single silent-only step
        # used before.
        return [
            SequenceStep(
                order=1, role=AgentRole.SILENT_LISTENER, agent_opens=False,
                content={
                    "behavior_note": ROLE_DEFAULT_NOTES[AgentRole.SILENT_LISTENER],
                    **_content_payload(teil_raw),
                },
                target_duration_seconds=(duration_minutes * 60) or None,
                min_turns=1,  # the student's presentation is genuinely one turn
            ),
            SequenceStep(
                order=2, role=AgentRole.EXAMINER, agent_opens=True,
                content={"behavior_note": ROLE_DEFAULT_NOTES[AgentRole.EXAMINER]},
                target_duration_seconds=45,
                min_turns=2,  # agent's question, then the student's answer
            ),
        ]

    behavior = FORMAT_TYPE_BEHAVIOR.get(format_type, DEFAULT_BEHAVIOR)

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