"""
sprechen_agent.orchestrator
=============================
Ties the raw subject JSON (already in DB, provider-specific shape) to
a live SessionState, and drives it forward one step at a time.

Two responsibilities that don't belong in mapping.py because they
need `provider` context, which mapping.py deliberately doesn't take:
  1. scoring_system selection (provider -> which of the 3 grading
     styles applies)
  2. presenter theme resolution (when the AI plays Kandidat B, which
     of possibly several nested themes/images does it actually use)

service.py calls create_session() once, then advance() every time a
turn boundary is detected (by live_client.py) or a step's target
duration elapses.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from . import mapping
from .session_state import (
    AgentRole,
    ScoringSystem,
    SequenceStep,
    SessionState,
    SessionStatus,
    TeilConfig,
    TranscriptEntry,
)

PROVIDER_SCORING_SYSTEM: dict[str, ScoringSystem] = {
    "goethe": ScoringSystem.LETTER_TIER,
    "telc": ScoringSystem.POINT_TIER,
    "oesd": ScoringSystem.CONTINUOUS,
}
DEFAULT_SCORING_SYSTEM = ScoringSystem.CONTINUOUS


# ---------------------------------------------------------------------------
# Presenter theme resolution — the provider-shape-specific part
# ---------------------------------------------------------------------------

def _resolve_presenter_content(kandidat_b_raw: dict[str, Any]) -> dict[str, Any]:
    """kandidat_b's raw data comes in at least 3 shapes across the
    samples we've seen:
      - Goethe B2: {"thema1": {...}, "thema2": {...}}  -> pick one
      - ÖSD B2:    {"bilder": [{...}, {...}, {...}]}    -> pick one image
      - Flat:      {"title": ..., "leitpunkte": [...]}  -> use directly

    Selection is deterministic (first option), not random — keeps
    sessions reproducible for debugging/support without needing to
    replay exact randomness.
    """
    theme_keys = sorted(k for k in kandidat_b_raw if k.startswith("thema"))
    if theme_keys:
        chosen = kandidat_b_raw[theme_keys[0]]
        payload = mapping.content_payload(chosen)
        payload["title"] = chosen.get("title")
        return payload

    if "bilder" in kandidat_b_raw and kandidat_b_raw["bilder"]:
        bild = kandidat_b_raw["bilder"][0]
        title = bild.get("titel", "")
        return {
            "instructions": f'Describe and interpret the image titled "{title}".',
            "content_points": [],
            "scenario": title,
            "title": title,
        }

    # already flat
    payload = mapping.content_payload(kandidat_b_raw)
    payload["title"] = kandidat_b_raw.get("title")
    return payload


def _finalize_presenter_steps(
    sequence: list[SequenceStep], teil_raw: dict[str, Any]
) -> list[SequenceStep]:
    """mapping.build_sequence() gives PRESENTER steps a naive content
    payload built straight off kandidat_b's raw dict, which is wrong
    whenever that dict is nested (thema1/thema2, bilder). Overwrite
    with the properly resolved content here.
    """
    kandidat_b_raw = teil_raw.get("kandidat_b", {})
    if not kandidat_b_raw:
        return sequence

    resolved = _resolve_presenter_content(kandidat_b_raw)
    for step in sequence:
        if step.role == AgentRole.PRESENTER:
            step.content = {**step.content, **resolved}
    return sequence


# ---------------------------------------------------------------------------
# Sprachliche Mittel normalization — flat list, nested dict, or absent
# (Goethe B1 keeps it at subject level, not per-Teil)
# ---------------------------------------------------------------------------

def _flatten_sprachliche_mittel(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, dict):
        flattened: list[str] = []
        for sub in value.values():
            flattened.extend(_flatten_sprachliche_mittel(sub))
        return flattened
    return []


def _resolve_sprachliche_mittel(teil_raw: dict[str, Any], subject_raw: dict[str, Any]) -> list[str]:
    # Most formats keep it inline on the Teil itself.
    if "sprachliche_mittel" in teil_raw:
        return _flatten_sprachliche_mittel(teil_raw["sprachliche_mittel"])

    # Goethe B1-style: a subject-level reference dict, keyed loosely
    # by "teil1" / "teil2_folien" / "teil3" etc. Best-effort match by
    # teil_number; fall back to the whole reference if no clean match
    # rather than silently returning nothing.
    reference = subject_raw.get("sprachliche_mittel_reference")
    if not reference:
        return []

    teil_number = teil_raw.get("teil_number")
    for key, value in reference.items():
        if key.startswith(f"teil{teil_number}"):
            return _flatten_sprachliche_mittel(value)

    return _flatten_sprachliche_mittel(reference)


# ---------------------------------------------------------------------------
# TeilConfig construction
# ---------------------------------------------------------------------------

def build_teil_configs(subject_raw: dict[str, Any], provider: str) -> list[TeilConfig]:
    scoring_system = PROVIDER_SCORING_SYSTEM.get(provider, DEFAULT_SCORING_SYSTEM)
    teile_raw = subject_raw.get("teile", [])

    configs: list[TeilConfig] = []
    for teil_raw in teile_raw:
        sequence = mapping.build_sequence(teil_raw)
        sequence = _finalize_presenter_steps(sequence, teil_raw)

        configs.append(
            TeilConfig(
                teil_number=teil_raw.get("teil_number", len(configs) + 1),
                name=teil_raw.get("name", ""),
                format_type=teil_raw.get("format_type", ""),
                instructions=teil_raw.get("instructions", ""),
                duration_minutes=teil_raw.get("duration_minutes") or teil_raw.get("time_minutes") or 0,
                preparation_minutes=teil_raw.get("preparation_minutes", 0) or 0,
                content_points=mapping.extract_content_points(teil_raw),
                sprachliche_mittel=_resolve_sprachliche_mittel(teil_raw, subject_raw),
                scoring_system=scoring_system,
                scoring_criteria_raw=teil_raw.get("scoring_criteria", {}),
                sequence=sequence,
            )
        )
    return configs


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------

def create_session(
    *,
    student_id: UUID,
    subject_id: UUID,
    subject_raw: dict[str, Any],
    provider: str,
    level: str,
) -> SessionState:
    teile = build_teil_configs(subject_raw, provider)
    return SessionState(
        student_id=student_id,
        subject_id=subject_id,
        provider=provider,
        level=level,
        cefr_target=level,
        pass_threshold_percent=subject_raw.get("pass_threshold_percent", 60.0),
        teile=teile,
        status=SessionStatus.PENDING,
    )


def start_session(session: SessionState) -> SessionState:
    session.status = SessionStatus.ACTIVE
    session.started_at = datetime.now(timezone.utc)
    session.updated_at = session.started_at
    session.current_step_started_at = session.started_at
    session.current_step_turn_count = 0
    return session


# Safety cap: even if min_turns hasn't been reached, force-advance a
# conversational step once elapsed time is this multiple of its
# target_duration_seconds — prevents a chatty exchange from running
# indefinitely if the model keeps the conversation going past budget.
STEP_TIME_SAFETY_MULTIPLIER = 2.0


def record_step_turn(session: SessionState) -> None:
    """Call once per turn_complete signal from live_client.py — every
    time either the agent or the student finishes speaking."""
    session.current_step_turn_count += 1
    session.updated_at = datetime.now(timezone.utc)


def is_step_complete(session: SessionState) -> bool:
    """Whether the CURRENT step has had enough turns to actually move
    the sequence forward. False means: reopen a fresh Live segment for
    the same step (still needed for the cost/segmentation strategy)
    without advancing current_step_index/current_teil_index."""
    step = session.current_step()
    if session.current_step_turn_count >= step.min_turns:
        return True

    if step.target_duration_seconds and session.current_step_started_at:
        elapsed = (datetime.now(timezone.utc) - session.current_step_started_at).total_seconds()
        if elapsed >= step.target_duration_seconds * STEP_TIME_SAFETY_MULTIPLIER:
            return True

    return False


@dataclass
class StepTransition:
    """What service.py needs to know after advance() to decide what
    to tell the frontend and whether live_client.py must reconnect."""
    teil_changed: bool
    session_ended: bool
    # Per the validated cost strategy: every step change closes the
    # current Live segment and opens a fresh one, carrying only the
    # text transcript forward — never raw audio history.
    requires_new_live_segment: bool
    new_teil: TeilConfig | None = None
    new_step: SequenceStep | None = None


def advance(session: SessionState) -> StepTransition:
    """Called only once is_step_complete(session) is True — moves the
    sequence position forward and resets the per-step turn/time
    tracking for whatever step comes next. Mutates session in place."""
    current_teil = session.current_teil()
    current_teil.sequence[session.current_step_index].completed = True

    if session.current_step_index < len(current_teil.sequence) - 1:
        session.current_step_index += 1
        session.current_step_turn_count = 0
        session.current_step_started_at = datetime.now(timezone.utc)
        session.updated_at = session.current_step_started_at
        return StepTransition(
            teil_changed=False,
            session_ended=False,
            requires_new_live_segment=True,
            new_step=session.current_step(),
        )

    if session.is_last_teil():
        session.status = SessionStatus.AWAITING_GRADING
        session.ended_at = datetime.now(timezone.utc)
        session.updated_at = session.ended_at
        return StepTransition(
            teil_changed=False,
            session_ended=True,
            requires_new_live_segment=False,
        )

    session.current_teil_index += 1
    session.current_step_index = 0
    session.current_step_turn_count = 0
    session.current_step_started_at = datetime.now(timezone.utc)
    session.status = SessionStatus.BETWEEN_SEGMENTS
    session.updated_at = session.current_step_started_at
    return StepTransition(
        teil_changed=True,
        session_ended=False,
        requires_new_live_segment=True,
        new_teil=session.current_teil(),
        new_step=session.current_step(),
    )


def is_agent_turn_next(session: SessionState) -> bool:
    """Whether the agent should speak next in the CURRENT step. Falls
    back to step.agent_opens when the step has no transcript yet (the
    very first turn); past that, alternates based on who spoke last
    within this step — required now that a single conversational step
    can span several back-and-forth turns, where agent_opens alone
    would keep pointing at the same speaker forever.

    Shared by service.py (decides whether to call
    LiveSegment.trigger_agent_turn() on a freshly opened segment) and
    router.py (decides whether to send AgentSpeakingEvent or
    StudentTurnEvent to the frontend) — same question, two consumers.
    """
    step = session.current_step()
    teil_number = session.current_teil().teil_number
    step_entries = [
        e for e in session.transcript
        if e.teil_number == teil_number and e.step_order == step.order
    ]
    if not step_entries:
        return step.agent_opens
    return step_entries[-1].speaker == "student"


def record_turn(session: SessionState, *, speaker: str, text: str) -> None:
    """Appends one transcript line. Called by service.py as text
    arrives from live_client.py (Gemini Live streams text alongside
    audio), and again for the AI's own utterances so grading.py gets
    a complete record of both sides."""
    session.transcript.append(
        TranscriptEntry(
            teil_number=session.current_teil().teil_number,
            step_order=session.current_step().order,
            speaker=speaker,
            text=text,
        )
    )
    session.updated_at = datetime.now(timezone.utc)


def mark_abandoned(session: SessionState) -> None:
    session.status = SessionStatus.ABANDONED
    session.ended_at = datetime.now(timezone.utc)
    session.updated_at = session.ended_at