"""
sprechen_agent.providers.goethe
==================================
Goethe-Zertifikat B1 et B2, épreuve orale (Sprechen).

Structure officielle suivie (Modellsatz / Übungssatz Goethe-Institut) :
  B1  Teil 1    Gemeinsam etwas planen (~3 min) : 4 Leitpunkte, décision
                commune à la fin.
      Teil 2+3  Ein Thema präsentieren (~3 min, 5 Folien) puis Über ein
                Thema sprechen (~2 min) : le partenaire fait un retour et
                pose une question, puis l'examinateur pose une question.
                Ensuite l'autre candidat présente, et on inverse.
                (Les deux Teile sont fusionnés en un seul par
                orchestrator._merge_alternating_teil_pairs.)
  B2  Teil 1    Vortrag halten (~4 min par candidat) : introduction,
                développement, conclusion. Le partenaire pose des
                questions (pas de retour prévu sur la feuille officielle),
                l'examinateur aussi.
      Teil 2    Diskussion führen (~5 min) : positions et arguments,
                réactions, et à la fin chacun dit s'il est dafür ou dagegen.

Dispatch sur le format_type et la présence d'un split kandidat_a /
kandidat_b, pas sur le numéro de Teil : un Teil non reconnu renvoie
None et garde la logique générique de mapping.py.
"""

from __future__ import annotations

from typing import Any

from ..session_state import AgentRole, SequenceStep
from .base import PARTNER_RULES, ProviderProfile, make_step, normalize_level, teil_seconds

# ---------------------------------------------------------------------------
# Durées cibles (secondes)
# ---------------------------------------------------------------------------
# Plancher de temps de la présentation de l'élève : sous ce seuil, une
# simple pause de l'élève ne fait pas passer à l'étape suivante. Gardé
# volontairement sous la durée officielle (3 min en B1, 4 min en B2) :
# si l'élève finit plus tôt, il ne reste pas bloqué trop longtemps.
B1_STUDENT_PRESENTATION_SECONDS = 120
B2_STUDENT_TALK_SECONDS = 150

# Présentation de l'IA (raccourcie pour le coût, comme validé pour telc)
AI_PRESENTATION_SECONDS = 120

DEFAULT_TEIL_SECONDS = 300

SAME_FORM_RULE = (
    "Use the same form (du or Sie) as the student; if unclear, use Sie. Never mix them."
)

# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

B1_PLANNING_PHASES = [
    (
        "Open: restate in one sentence what you have to plan together, then make a "
        "first concrete proposal for the first planning point."
    ),
    (
        "Go through EVERY planning point listed below, one after the other (including "
        "an open point of your own if there is one). For each: propose something, ask "
        "for the student's opinion, react, and agree on a decision before moving on."
    ),
    (
        "Do not just agree: at least once, raise a doubt or a practical problem and "
        "negotiate a compromise ('Das ist zwar eine gute Idee, aber ...')."
    ),
    "At the end, summarize the decisions you made together in one or two sentences.",
]

B2_DISCUSSION_PHASES = [
    (
        "Open: say the question in your own words, state your position (dafür or "
        "dagegen) with a first reason, and ask the student for their position. By "
        "default take the side OPPOSITE to the student's. If you turn out to agree, "
        "keep your side but bring up its limits and drawbacks so the debate stays alive."
    ),
    (
        "Exchange arguments: react to each argument of the student (agree partly or "
        "object, with a reason), using the hint questions below as a source of ideas."
    ),
    "Bring in at least one argument the student has not raised yet, and ask them to respond to it.",
    (
        "Close: summarize together who is dafür and who is dagegen ('Zusammenfassend "
        "...', 'Nach dieser Diskussion bin ich immer noch der Meinung, dass ...') and "
        "ask the student for their final position. Never skip this phase."
    ),
]

PHASE_PACING_NOTE = (
    "Move through the phases in order, one at a time; each phase usually needs at least "
    "one real exchange. Use the conversation so far and the elapsed time to know where you "
    "are, and pace yourself so the last phase happens before the time runs out."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_candidate_split(teil_raw: dict[str, Any]) -> bool:
    return "kandidat_a" in teil_raw or "kandidat_b" in teil_raw


# ---------------------------------------------------------------------------
# B1
# ---------------------------------------------------------------------------


def _b1_planning(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=teil_seconds(teil_raw, 180),
            min_turns=6,
            phases=B1_PLANNING_PHASES,
            behavior_note=(
                "You are the exam PARTNER (the other candidate). You plan something together "
                "as equals: propose your own concrete ideas, do not just wait for the "
                "student, and do not accept every proposal. Simple B1 sentences and everyday "
                "words. " + SAME_FORM_RULE + " " + PHASE_PACING_NOTE + " " + PARTNER_RULES
            ),
        ),
    ]


def _b1_presentation(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    """Teil 2 + Teil 3 fusionnés : l'élève présente, retour + question du
    partenaire, question de l'examinateur, puis l'IA présente et répond
    au retour et à la question de l'élève."""
    return [
        # 1. L'élève présente son thème (5 Folien)
        make_step(
            order=1,
            role=AgentRole.SILENT_LISTENER,
            agent_opens=False,
            content=content,
            target_duration_seconds=B1_STUDENT_PRESENTATION_SECONDS,
            min_turns=1,
            behavior_note=(
                "The student presents their topic following the five slides "
                "(about 3 minutes). Stay silent."
            ),
        ),
        # 2. Partenaire : retour + une question
        make_step(
            order=2,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "You are the exam PARTNER (the other candidate). The student has just "
                "finished their presentation. Give a short, friendly feedback in one or two "
                "sentences (what you liked, what was new or interesting for you), then ask "
                "exactly ONE question about their presentation. Then listen to the answer "
                "and do not ask anything else. Simple B1 sentences. " + SAME_FORM_RULE
            ),
        ),
        # 3. Examinateur : une question
        make_step(
            order=3,
            role=AgentRole.EXAMINER,
            agent_opens=True,
            content=content,
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "You now speak as the EXAMINER, no longer as the partner. Ask the student "
                "exactly ONE short question about their presentation, different from the "
                "questions already asked (see the list below). Use 'Sie'. Then listen. Do "
                "not comment on the answer and do not ask anything else."
            ),
        ),
        # 4. L'IA présente son propre thème (contenu résolu par l'orchestrateur)
        make_step(
            order=4,
            role=AgentRole.PRESENTER,
            agent_opens=True,
            content=content,
            target_duration_seconds=AI_PRESENTATION_SECONDS,
            min_turns=1,
            behavior_note=(
                "Now it is YOUR turn to present, as the other candidate (about 2 minutes). "
                "Follow the five slides listed below, in order: introduce the topic and the "
                "structure, a personal experience, the situation in your home country with "
                "examples, advantages and disadvantages with your opinion, then end and "
                "thank the listeners. Talk as if the experiences were your own; inventing "
                "them is part of your role and is allowed. Keep the details precise and "
                "consistent: the student will ask you about them. Simple B1 sentences."
            ),
        ),
        # 5. L'élève fait son retour et pose sa question, l'IA répond
        make_step(
            order=5,
            role=AgentRole.PARTNER,
            agent_opens=False,
            content=content,
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "The student now gives feedback on your presentation and asks you a "
                "question. Thank them briefly for the feedback, then answer their question "
                "directly and concretely in 2 or 3 sentences, consistent with what you said "
                "in your presentation. Do not ask the student questions. If they stay "
                "silent, invite them once to ask a question. " + SAME_FORM_RULE
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# B2
# ---------------------------------------------------------------------------


def _b2_talk(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        # 1. L'élève fait son exposé (~4 min)
        make_step(
            order=1,
            role=AgentRole.SILENT_LISTENER,
            agent_opens=False,
            content=content,
            target_duration_seconds=B2_STUDENT_TALK_SECONDS,
            min_turns=1,
            behavior_note=(
                "The student gives a short talk on the topic they chose (about 4 minutes), "
                "with an introduction, a main part and a conclusion. Stay silent."
            ),
        ),
        # 2. Partenaire : une question (pas de retour sur la feuille officielle B2)
        make_step(
            order=2,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "You are the exam PARTNER (the other candidate). The student has just "
                "finished their talk. Ask exactly ONE relevant, open question about what "
                "they said (for example to go deeper into one point or an argument). Then "
                "listen to the answer and do not ask anything else. " + SAME_FORM_RULE
            ),
        ),
        # 3. Examinateur : une question
        make_step(
            order=3,
            role=AgentRole.EXAMINER,
            agent_opens=True,
            content=content,
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "You now speak as the EXAMINER, no longer as the partner. Ask the student "
                "exactly ONE short question about their talk, different from the questions "
                "already asked (see the list below). Use 'Sie'. Then listen. Do not comment "
                "on the answer and do not ask anything else."
            ),
        ),
        # 4. L'IA fait son exposé (contenu résolu par l'orchestrateur)
        make_step(
            order=4,
            role=AgentRole.PRESENTER,
            agent_opens=True,
            content=content,
            target_duration_seconds=AI_PRESENTATION_SECONDS,
            min_turns=1,
            behavior_note=(
                "Now it is YOUR turn to give a short talk, as the other candidate (about 2 "
                "minutes). Structure it with an introduction, a main part covering the "
                "points listed below in order, and a conclusion with your evaluation. B2 "
                "language: varied vocabulary, subordinate clauses. Personal examples are "
                "part of your role and are allowed; keep them consistent, the student will "
                "ask you about them. End with: 'Haben Sie Fragen?' (or 'Hast du Fragen?' "
                "if you use du)."
            ),
        ),
        # 5. L'élève pose sa question, l'IA répond
        make_step(
            order=5,
            role=AgentRole.PARTNER,
            agent_opens=False,
            content=content,
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "The student now asks you a question about your talk. Answer it directly "
                "and concretely in 2 to 4 sentences, consistent with what you said in your "
                "talk. Do not ask the student questions. If they stay silent, invite them "
                "once to ask a question. " + SAME_FORM_RULE
            ),
        ),
    ]


def _b2_discussion(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    hints = [str(h) for h in (teil_raw.get("hints") or []) if h]
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=teil_seconds(teil_raw, DEFAULT_TEIL_SECONDS),
            min_turns=6,
            phases=B2_DISCUSSION_PHASES,
            question_categories=hints or None,
            behavior_note=(
                "You are the exam PARTNER in a debate club discussion about the question "
                "below. This is a debate, NOT a planning task. Take a clear position and "
                "defend it with reasons, but stay fair and collaborative: the goal is a real "
                "exchange, not winning. Each of you should speak about half of the time. B2 "
                "language: varied vocabulary, subordinate clauses. "
                + SAME_FORM_RULE
                + " "
                + PHASE_PACING_NOTE
                + " "
                + PARTNER_RULES
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# Profil
# ---------------------------------------------------------------------------


class GoetheProfile(ProviderProfile):
    name = "goethe"

    def build_sequence(
        self,
        teil_raw: dict[str, Any],
        *,
        level: str,
        content: dict[str, Any],
    ) -> list[SequenceStep] | None:
        lvl = normalize_level(level)
        format_type = teil_raw.get("format_type")

        if lvl == "B1":
            if format_type == "oral_interaction":
                return _b1_planning(teil_raw, content)
            if format_type == "oral_monologue" and _has_candidate_split(teil_raw):
                return _b1_presentation(teil_raw, content)
            return None

        if lvl == "B2":
            if format_type == "oral_monologue" and _has_candidate_split(teil_raw):
                return _b2_talk(teil_raw, content)
            if format_type == "oral_discussion":
                return _b2_discussion(teil_raw, content)
            return None

        return None