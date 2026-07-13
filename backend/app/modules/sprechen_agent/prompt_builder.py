"""
sprechen_agent.prompt_builder
================================
Turns the current SessionState into the system prompt for the next
Gemini Live segment. Called by live_client.py every time
orchestrator.advance() reports requires_new_live_segment=True.

Deliberately a pure function: (SessionState) -> str. No I/O, no side
effects, easy to unit test and to tweak wording without touching
orchestration logic.
"""

from __future__ import annotations

from typing import Any

from .session_state import AgentRole, SessionState, TranscriptEntry

# How many prior transcript lines from the CURRENT Teil to recap when
# opening a new segment. Kept short on purpose — this is text, not
# audio, so it's cheap, but an unbounded recap would still bloat the
# prompt pointlessly on long Teile.
TRANSCRIPT_RECAP_MAX_ENTRIES = 8

_ROLE_LABELS: dict[AgentRole, str] = {
    AgentRole.PARTNER: "conversation partner",
    AgentRole.EXAMINER: "examiner",
    AgentRole.SILENT_LISTENER: "silent listener",
    AgentRole.PRESENTER: "presenter (Kandidat B)",
    AgentRole.ASSIGNED_POSITION: "debate partner with an assigned position",
}


def _format_transcript_recap(entries: list[TranscriptEntry]) -> str:
    if not entries:
        return "(This is the first exchange of this Teil — no prior context.)"

    recent = entries[-TRANSCRIPT_RECAP_MAX_ENTRIES:]
    lines = []
    for entry in recent:
        speaker_label = "Student" if entry.speaker == "student" else "You (agent)"
        lines.append(f"- {speaker_label}: {entry.text}")
    return "\n".join(lines)


def _format_content_points(points: list[str]) -> str:
    if not points:
        return "(none specified)"
    return "\n".join(f"- {p}" for p in points)


def _format_sprachliche_mittel(phrases: list[str]) -> str:
    if not phrases:
        return "(none provided for this Teil)"
    return "\n".join(f'- "{p}"' for p in phrases)


def _format_stimulus_people(content: dict[str, Any]) -> str:
    """Formats the two stimulus people from oral_thema (telc:
    person_a/person_b) or oral_meinungsaustausch (ÖSD: person1/
    person2) — same concept, different provider key names."""
    pairs = [
        (content.get("person_a"), content.get("person_b")),
        (content.get("person1"), content.get("person2")),
    ]
    for first, second in pairs:
        if first and second:
            lines = []
            for person in (first, second):
                name = person.get("name", "?")
                opinion = person.get("meinung") or person.get("position") or ""
                lines.append(f'- {name}: "{opinion}"')
            return "\n".join(lines)
    return ""


def _opening_instruction(agent_opens: bool, role: AgentRole) -> str:
    if agent_opens:
        return "You have the initiative — start speaking first, right now."
    return "The student has the initiative — wait for them to speak first. Do not start."


def build_system_prompt(session: SessionState, *, exam_name: str = "") -> str:
    """The full system prompt for the segment about to open. Call this
    right before live_client.py opens a new Gemini Live connection —
    never mid-segment."""
    teil = session.current_teil()
    step = session.current_step()

    role_label = _ROLE_LABELS.get(step.role, step.role.value)
    behavior_note = step.content.get("behavior_note", "")

    # Content block: PRESENTER steps carry their own resolved
    # instructions/content_points/title (set by orchestrator.py);
    # everything else falls back to the Teil's own data.
    instructions = step.content.get("instructions") or teil.instructions
    content_points = step.content.get("content_points") or teil.content_points
    scenario_or_title = step.content.get("title") or step.content.get("scenario")
    stimulus_people = _format_stimulus_people(step.content)

    recap = _format_transcript_recap(
        [e for e in session.transcript if e.teil_number == teil.teil_number]
    )

    target_seconds = step.target_duration_seconds
    duration_line = (
        f"Target duration for this turn: roughly {target_seconds} seconds."
        if target_seconds
        else f"General time budget for this Teil: {teil.duration_minutes} minutes."
    )

    exam_label = f"{exam_name} — " if exam_name else ""

    return f"""\
You are a German language {role_label} for {exam_label}{session.provider.upper()} \
{session.level} — {teil.name} (Teil {teil.teil_number}).

ROLE FOR THIS TURN: {role_label}
{behavior_note}

CEFR TARGET LEVEL: {session.cefr_target}
Match your own vocabulary and sentence complexity to this level. Never speak
above it, even if the correct answer would use more advanced grammar.

SUBJECT CONTEXT:
{instructions}
{f"Topic/scenario: {scenario_or_title}" if scenario_or_title else ""}
{f"Two given viewpoints to report and react to:\n{stimulus_people}" if stimulus_people else ""}

CONTENT POINTS TO COVER OR ADDRESS:
{_format_content_points(content_points)}

REFERENCE VOCABULARY FOR THIS TEIL (use naturally, never recite verbatim):
{_format_sprachliche_mittel(teil.sprachliche_mittel)}

{duration_line}

CONVERSATION SO FAR IN THIS TEIL (text-only recap — no audio history
is being carried over from prior turns, so use this to stay coherent):
{recap}

OPENING RULE: {_opening_instruction(step.agent_opens, step.role)}

STRICT RULES:
- Stay in character at all times. Never break character to give feedback,
  correct a mistake, or explain what you're doing.
- Never invent content that isn't grounded in the subject context above.
- Never announce or hint at moving to the next Teil or step — the backend
  system handles all transitions; you only ever handle the current turn.
- If the student is silent for more than 5 seconds, gently prompt them once.
- Speak only in German, at the target CEFR level, unless the student
  addresses you in another language first.
"""