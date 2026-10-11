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
    # Esquisses : notes libres 0..max par critère (cf. mapping.py, oral_semidirect)
    "ecl": ScoringSystem.CONTINUOUS,
    "testdaf": ScoringSystem.CONTINUOUS,
}
DEFAULT_SCORING_SYSTEM = ScoringSystem.CONTINUOUS


# ---------------------------------------------------------------------------
# Presenter theme resolution — the provider-shape-specific part
# ---------------------------------------------------------------------------

def _resolve_presenter_content(kandidat_b_raw: dict[str, Any] | list[Any]) -> dict[str, Any]:
    """kandidat_b's raw data comes in at least 4 shapes across the
    samples we've seen:
      - Goethe B1: {"thema1": {...}, "thema2": {...}}   -> pick one
      - Goethe B2: [{"title": ..., "leitpunkte": [...]}, {...}]
                                                          -> pick one (LIST, not dict)
      - ÖSD B2:    {"bilder": [{...}, {...}, {...}]}    -> pick one image
      - Flat:      {"title": ..., "leitpunkte": [...]}  -> use directly

    Selection is deterministic (first option), not random — keeps
    sessions reproducible for debugging/support without needing to
    replay exact randomness.
    """
    if isinstance(kandidat_b_raw, list):
        # Goethe B2-style: a list of alternative themes rather than a
        # dict keyed thema1/thema2. Once we pick one, it's the same
        # flat {"title":..., "leitpunkte":[...]} shape as the "already
        # flat" branch below, so just fall through to it.
        kandidat_b_raw = kandidat_b_raw[0] if kandidat_b_raw else {}

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
# ablauf_schema-only alternating pairs — some Goethe-style subjects (17 in
# the current catalog) encode the Kandidat A/B alternation ONLY via a
# subject-level "ablauf_schema" string, spanning two teil_numbers, with NO
# kandidat_a/kandidat_b split on the Teile themselves (unlike other Goethe
# subjects where the split IS present per-Teil — those already work via
# mapping.py's normal detection). Retrofitting every existing subject's
# data was judged impractical, so this is detected structurally instead:
# an oral_monologue Teil immediately followed by an oral_feedback Teil,
# under a subject that has an ablauf_schema key — never by parsing the
# schema text itself, which stays fragile free text for humans to read.
# ---------------------------------------------------------------------------

def _teil_minutes(teil_raw: dict[str, Any]) -> int:
    # Mirrors the fallback build_teil_configs() already applies to
    # every non-merged Teil — most subjects use "time_minutes", not
    # "duration_minutes". The merge below previously read only
    # "duration_minutes" and silently produced 0.
    return teil_raw.get("duration_minutes") or teil_raw.get("time_minutes") or 0


def _merge_monologue_feedback_pair(
    monologue_teil: dict[str, Any], feedback_teil: dict[str, Any], subject_raw: dict[str, Any]
) -> dict[str, Any]:
    """Combines the two source Teile into one synthetic Teil carrying
    a kandidat_a/kandidat_b split, so mapping.py's existing alternating-
    sequence builder picks it up unchanged — no new sequence logic
    needed, just the right shape of input data."""
    themes = monologue_teil.get("themes", {})
    theme_keys = sorted(themes.keys())
    # Kandidat A (the real student) picks freely at runtime, whatever
    # they say. Kandidat B (the AI) is deterministically assigned the
    # LAST theme in the shared pool as a stable default — with only
    # two themes this just means "the other one" without needing to
    # know in advance which one the student will actually choose.
    kandidat_b_key = theme_keys[-1] if theme_keys else None
    kandidat_b = {kandidat_b_key: themes[kandidat_b_key]} if kandidat_b_key else {}

    merged_scoring: dict[str, Any] = dict(monologue_teil.get("scoring_criteria", {}))
    for key, value in feedback_teil.get("scoring_criteria", {}).items():
        existing = merged_scoring.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged_scoring[key] = {**existing, **value}  # merge sub-criteria, don't overwrite
        else:
            merged_scoring[key] = value

    # sprachliche_mittel: prefer whatever either source Teil carries
    # inline. When NEITHER does (Goethe B1-style subjects keep it at
    # subject level instead, under sprachliche_mittel_reference), pull
    # and combine both merged-away Teil numbers' reference blocks
    # directly here — _resolve_sprachliche_mittel()'s normal per-Teil
    # lookup only ever matches a single teil_number by prefix, and this
    # merged Teil represents two (e.g. "teil2_folien" + "teil3").
    merged_sprachliche_mittel = (
        monologue_teil.get("sprachliche_mittel") or feedback_teil.get("sprachliche_mittel")
    )
    if not merged_sprachliche_mittel:
        reference = subject_raw.get("sprachliche_mittel_reference") or {}
        combined: list[str] = []
        for number in (monologue_teil.get("teil_number"), feedback_teil.get("teil_number")):
            for key, value in reference.items():
                if key.startswith(f"teil{number}"):
                    combined.extend(_flatten_sprachliche_mittel(value))
        merged_sprachliche_mittel = combined or None

    merged: dict[str, Any] = {
        "teil_number": monologue_teil["teil_number"],
        "name": f'{monologue_teil.get("name", "")} + {feedback_teil.get("name", "")}',
        "format_type": monologue_teil.get("format_type", "oral_monologue"),
        "instructions": monologue_teil.get("instructions", ""),
        "duration_minutes": _teil_minutes(monologue_teil) + _teil_minutes(feedback_teil),
        "max_score": (monologue_teil.get("max_score") or 0) + (feedback_teil.get("max_score") or 0),
        "themes": themes,
        "kandidat_a": {},  # presence alone is enough to trigger mapping.py's alternating detector
        "kandidat_b": kandidat_b,
        "scoring_criteria": merged_scoring,
    }
    # Only set the key when there's something real to put there —
    # leaving it absent (rather than None) lets _resolve_sprachliche_mittel()
    # correctly detect "this Teil has no inline sprachliche_mittel" in
    # case this merge logic itself ever needs revisiting; here we've
    # already done the combining above, so this is just the write-out.
    if merged_sprachliche_mittel:
        merged["sprachliche_mittel"] = merged_sprachliche_mittel

    return merged


def _merge_alternating_teil_pairs(
    teile_raw: list[dict[str, Any]], subject_raw: dict[str, Any]
) -> list[dict[str, Any]]:
    if "ablauf_schema" not in subject_raw:
        return teile_raw

    merged: list[dict[str, Any]] = []
    i = 0
    while i < len(teile_raw):
        current = teile_raw[i]
        nxt = teile_raw[i + 1] if i + 1 < len(teile_raw) else None

        is_mergeable_pair = (
            nxt is not None
            and current.get("format_type") == "oral_monologue"
            and nxt.get("format_type") == "oral_feedback"
            and "kandidat_a" not in current  # only the no-split shape needs this — the other Goethe subjects already work as-is
        )

        if is_mergeable_pair:
            merged.append(_merge_monologue_feedback_pair(current, nxt, subject_raw))
            i += 2
        else:
            merged.append(current)
            i += 1

    return merged


# ---------------------------------------------------------------------------
# TeilConfig construction
# ---------------------------------------------------------------------------

def _resolve_available_themes(teil_raw: dict[str, Any]) -> dict[str, Any] | None:
    """Surfaces free-choice presentation topics to the frontend, no
    matter which of the two observed shapes they're stored in:
      - top-level "themes": {"thema1": {...}, "thema2": {...}}
        (telc B2 Teil 1, single-role oral_monologue)
      - nested under "kandidat_a": {"thema1": {...}, "thema2": {...}}
        (Goethe B1/B2, two-candidate oral_monologue — kandidat_a is
        always the real student's own set of choices, regardless of
        which role they end up playing in the sequence)
    Returns None when the Teil has no theme choice at all (a single
    fixed scenario/prompt list instead)."""
    if "themes" in teil_raw:
        return teil_raw["themes"]

    kandidat_a = teil_raw.get("kandidat_a")
    if isinstance(kandidat_a, dict) and any(k.startswith("thema") for k in kandidat_a):
        return kandidat_a

    if isinstance(kandidat_a, list) and kandidat_a:
        # Goethe B2-style: kandidat_a is a list of alternative themes
        # ([{"title":..., "leitpunkte":[...]}, ...]) instead of a dict
        # keyed thema1/thema2. Without this the student's own two
        # theme choices never reached the frontend "choose a topic"
        # panel at all (isinstance(..., dict) was False, so this whole
        # branch was skipped and None was returned). Normalize to the
        # same thema1/thema2-keyed shape the frontend already expects.
        return {f"thema{i + 1}": theme for i, theme in enumerate(kandidat_a)}

    return None


def build_teil_configs(subject_raw: dict[str, Any], provider: str) -> list[TeilConfig]:
    scoring_system = PROVIDER_SCORING_SYSTEM.get(provider, DEFAULT_SCORING_SYSTEM)
    teile_raw = _merge_alternating_teil_pairs(subject_raw.get("teile", []), subject_raw)

    configs: list[TeilConfig] = []
    for teil_raw in teile_raw:
        sequence = mapping.build_sequence(teil_raw)
        sequence = _finalize_presenter_steps(sequence, teil_raw)

        # scenario/stimulus_people: same normalization mapping.py
        # already applies when building the agent's own prompt content
        # (mapping.content_payload), just also surfaced here so the
        # frontend preparation screen can show it to the student. For
        # two-candidate alternating Teile this is naturally None/empty
        # (teil_raw itself carries no scenario/person_a at top level
        # in that shape) — harmless, nothing to show there.
        content = mapping.content_payload(teil_raw)

        configs.append(
            TeilConfig(
                teil_number=teil_raw.get("teil_number", len(configs) + 1),
                name=teil_raw.get("name", ""),
                format_type=teil_raw.get("format_type", ""),
                instructions=teil_raw.get("instructions", ""),
                duration_minutes=teil_raw.get("duration_minutes") or teil_raw.get("time_minutes") or 0,
                preparation_minutes=teil_raw.get("preparation_minutes", 0) or 0,
                content_points=mapping.extract_content_points(teil_raw),
                themes=_resolve_available_themes(teil_raw),
                scenario=content.get("scenario"),
                stimulus_people=mapping.resolve_stimulus_people(teil_raw),
                stimulus_text=content.get("text"),
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
    without advancing current_step_index/current_teil_index.

    Bug fix: min_turns alone used to be sufficient — a step (and for
    single-step Teile, the whole Teil) would advance the instant enough
    turns happened, often in well under a minute of real conversation,
    regardless of the "programmed" duration_minutes/target_duration_seconds
    it was supposed to run for. There was a ceiling (STEP_TIME_SAFETY_
    MULTIPLIER, below) but never a floor, so nothing ever held a step
    open for its allotted time. Fixed by requiring BOTH conditions
    below target_duration_seconds*SAFETY_MULTIPLIER: enough turns AND
    enough elapsed time. Steps with no target_duration_seconds keep the
    old turns-only behavior (nothing to hold against)."""
    step = session.current_step()
    turns_reached = session.current_step_turn_count >= step.min_turns

    elapsed: float | None = None
    if session.current_step_started_at:
        elapsed = (datetime.now(timezone.utc) - session.current_step_started_at).total_seconds()

    if step.target_duration_seconds and elapsed is not None:
        # Ceiling — unchanged: force-advance regardless of turns once a
        # chatty exchange has run way past its budget.
        if elapsed >= step.target_duration_seconds * STEP_TIME_SAFETY_MULTIPLIER:
            return True
        # Floor — new: don't let min_turns alone end the step before
        # its own allotted time has actually passed.
        if elapsed < step.target_duration_seconds:
            return False

    return turns_reached


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