"""
sprechen_agent.grading
=========================
Post-session grading. One Claude call per session (not per Teil) —
the full transcript is small enough that a single call is both
cheaper and lets Claude judge fluency/coherence across the whole exam
rather than in disconnected fragments.

Reads SessionState.transcript + each TeilConfig's scoring_criteria_raw
(kept exactly as imported from the subject JSON, in whichever of the
3 provider styles) and produces a GradingResult ready for
repository.py to persist.

NOTE: like live_client.py, the actual Claude API call in
call_claude_grading() can't be exercised end-to-end in this
environment (no API key available here). The prompt construction and
response-parsing logic are unit-tested against a synthetic response
instead. compute_teil_max_score(), however, IS fully verified — it
was checked by hand against every real scoring_criteria sample shared
in this conversation (Goethe B1 Teile 1-3, telc B1 Teil 1) and
reproduces every officially-documented max_score exactly.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from .session_state import (
    GradingResult,
    ScoringSystem,
    SessionState,
    TeilConfig,
    TeilGrading,
    CriterionScore,
)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
# Matches the primary model already used for Schreiben correction —
# swap via config if that pins to something more specific in prod.
GRADING_MODEL = "claude-sonnet-4-6"
GRADING_MAX_TOKENS = 2000


# ---------------------------------------------------------------------------
# Max-score computation — scoring_system-aware, validated against every
# real sample shared: Goethe (compound sub-criteria are additive, simple
# ones use "max" directly), telc (A/B/C/D tiers are mutually exclusive,
# take the highest), ÖSD (always has an explicit "max").
# ---------------------------------------------------------------------------

def _extract_criterion_max(value: Any, scoring_system: ScoringSystem) -> float:
    if not isinstance(value, dict):
        return float(value) if isinstance(value, (int, float)) else 0.0

    if "max" in value:
        return float(value["max"])

    numeric_leaves = [v for v in value.values() if isinstance(v, (int, float))]
    if not numeric_leaves:
        return 0.0

    if scoring_system == ScoringSystem.POINT_TIER:
        # A/B/C/D tiers are mutually exclusive — the max attainable is
        # whichever tier is worth the most (normally "A").
        return float(max(numeric_leaves))

    # LETTER_TIER (Goethe): sub-criteria points are additive
    # (e.g. Erfuellung = Sprachfunktionen + Inhalt).
    return float(sum(numeric_leaves))


def compute_teil_max_score(teil: TeilConfig) -> float:
    return sum(
        _extract_criterion_max(v, teil.scoring_system)
        for v in teil.scoring_criteria_raw.values()
    )


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_SCORING_SYSTEM_INSTRUCTIONS: dict[ScoringSystem, str] = {
    ScoringSystem.LETTER_TIER: (
        "Goethe-style grading: each criterion below lists either a single "
        '"max" point value, or several named sub-components that ADD UP to '
        "the criterion's total (e.g. Erfuellung = Sprachfunktionen + Inhalt). "
        "Score each sub-component independently based on the transcript, "
        "then report the criterion's total as their sum."
    ),
    ScoringSystem.POINT_TIER: (
        "telc-style grading: each criterion lists point values for tiers "
        "A/B/C/D (A = best). Decide which single tier the performance "
        "matches for that criterion, and report that tier's point value "
        "as the score — never a value between two tiers."
    ),
    ScoringSystem.CONTINUOUS: (
        'ÖSD-style grading: each criterion has a "max" score and a short '
        "description of what it covers. Assign any score from 0 up to "
        "max based on how well the transcript meets that description — "
        "this one allows free-form scores, not fixed tiers."
    ),
}


def _format_transcript(session: SessionState) -> str:
    lines = []
    for entry in session.transcript:
        speaker = "Kandidat (Student)" if entry.speaker == "student" else "Agent"
        lines.append(f"[Teil {entry.teil_number}] {speaker}: {entry.text}")
    return "\n".join(lines) if lines else "(no transcript recorded)"


def _format_teil_criteria(teil: TeilConfig) -> str:
    system_note = _SCORING_SYSTEM_INSTRUCTIONS[teil.scoring_system]
    max_score = compute_teil_max_score(teil)
    criteria_json = json.dumps(teil.scoring_criteria_raw, ensure_ascii=False, indent=2)
    return (
        f"--- Teil {teil.teil_number}: {teil.name} (format: {teil.format_type}) ---\n"
        f"Grading system: {teil.scoring_system.value}\n"
        f"{system_note}\n"
        f"Maximum score for this Teil: {max_score}\n"
        f"Raw criteria:\n{criteria_json}"
    )


def build_grading_prompt(session: SessionState) -> str:
    teile_blocks = "\n\n".join(_format_teil_criteria(t) for t in session.teile)

    return f"""\
You are grading a German language Sprechen (oral) exam for the \
{session.provider.upper()} {session.level} certification.

The candidate is always the speaker labeled "Kandidat (Student)" in the \
transcript below. Turns labeled "Agent" are the AI examiner/partner — \
never grade the Agent's speech, it exists only to prompt the candidate.

FULL TRANSCRIPT:
{_format_transcript(session)}

GRADING CRITERIA BY TEIL:
{teile_blocks}

Grade the candidate's performance on every criterion of every Teil listed \
above, following each Teil's specific grading system instructions. Then \
identify 2-4 concrete strengths and 2-4 concrete areas for improvement, \
grounded in specific things the candidate actually said.

Respond with ONLY a JSON object, no markdown fences, no preamble, matching \
exactly this shape:
{{
  "teile": [
    {{
      "teil_number": <int>,
      "criteria": [
        {{
          "criterion_name": <str>,
          "score": <float>,
          "max_score": <float>,
          "issue": <str or null>,
          "model_phrase": <str or null>,
          "tip": <str or null>
        }}
      ]
    }}
  ],
  "strengths": [<str>, ...],
  "improvement_areas": [<str>, ...]
}}

For each criterion:
- "issue": one short sentence naming the concrete gap you observed, grounded \
  in what the candidate actually said (or didn't say). Use null only if the \
  score is at or near max and there is genuinely nothing to flag.
- "model_phrase": a short German sentence or phrase the candidate could have \
  used instead, illustrating the fix. Use null if not applicable (e.g. a \
  pronunciation-only issue).
- "tip": one short, actionable practice suggestion (e.g. "Prepare a 30-60 \
  second self-introduction you can always reuse"). Use null only alongside \
  a null issue.
"""


# ---------------------------------------------------------------------------
# Claude call + response parsing
# ---------------------------------------------------------------------------

def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else stripped
        if stripped.endswith("```"):
            stripped = stripped.rsplit("```", 1)[0]
    return stripped.strip()


def parse_grading_response(raw_text: str, session: SessionState) -> GradingResult:
    """Turns Claude's raw JSON text into a validated GradingResult,
    filling in max_score totals and the pass/fail decision. Separated
    from call_claude_grading() so it can be unit-tested against a
    synthetic response without a real API call."""
    data = json.loads(_strip_code_fences(raw_text))

    teile_by_number = {t.teil_number: t for t in session.teile}
    teil_gradings: list[TeilGrading] = []
    total_score = 0.0
    total_max_score = 0.0

    for teil_data in data["teile"]:
        teil_number = teil_data["teil_number"]
        teil = teile_by_number.get(teil_number)
        teil_name = teil.name if teil else f"Teil {teil_number}"

        criteria = [
            CriterionScore(
                criterion_name=c["criterion_name"],
                score=float(c["score"]),
                max_score=float(c["max_score"]),
                issue=c.get("issue"),
                model_phrase=c.get("model_phrase"),
                tip=c.get("tip"),
            )
            for c in teil_data["criteria"]
        ]
        teil_score = sum(c.score for c in criteria)
        teil_max = sum(c.max_score for c in criteria)

        teil_gradings.append(
            TeilGrading(
                teil_number=teil_number,
                criteria=criteria,
                teil_score=teil_score,
                teil_max_score=teil_max,
            )
        )
        total_score += teil_score
        total_max_score += teil_max

    percent = (total_score / total_max_score * 100) if total_max_score else 0.0

    return GradingResult(
        session_id=session.session_id,
        provider=session.provider,
        level=session.level,
        teile=teil_gradings,
        total_score=total_score,
        total_max_score=total_max_score,
        pass_threshold_percent=session.pass_threshold_percent,
        passed=percent >= session.pass_threshold_percent,
        strengths=data.get("strengths", []),
        improvement_areas=data.get("improvement_areas", []),
    )


async def call_claude_grading(session: SessionState, *, anthropic_api_key: str) -> GradingResult:
    """The actual network call. Thin on purpose — build_grading_prompt()
    and parse_grading_response() hold all the logic worth testing without
    a live key."""
    prompt = build_grading_prompt(session)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": anthropic_api_key,
                "anthropic-version": ANTHROPIC_API_VERSION,
                "content-type": "application/json",
            },
            json={
                "model": GRADING_MODEL,
                "max_tokens": GRADING_MAX_TOKENS,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        payload = response.json()

    raw_text = payload["content"][0]["text"]
    return parse_grading_response(raw_text, session)