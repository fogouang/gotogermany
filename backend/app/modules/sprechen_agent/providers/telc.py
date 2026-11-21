"""
sprechen_agent.providers.telc
================================
telc Deutsch B1 et B2, épreuve orale (Sprechen), Teil par Teil.

Structure officielle suivie :
  B1  Teil 1  Kontaktaufnahme (~3 min) : faire connaissance, puis une
              question finale de l'examinateur.
      Teil 2  Gespräch über ein Thema (~6 min) : chacun résume SON texte
              (deux avis opposés), puis débat allégé. Pas de planification.
      Teil 3  Gemeinsam eine Aufgabe lösen (~6 min) : planifier ensemble.
  B2  Teil 1  Über Erfahrungen sprechen (~5 min) : échauffement, l'élève
              présente (~90 s), l'IA lui pose des questions variées, puis
              l'IA présente à son tour et répond aux questions de l'élève.
      Teil 2  Diskussion (~5 min) : débat en 6 phases (méthode validée par
              un centre partenaire).
      Teil 3  Gemeinsam etwas planen (~5 min).

Dispatch par numéro de Teil (la structure telc est fixe), avec un
contrôle du format_type : si le format_type ne correspond pas à ce qui
est attendu pour ce Teil, on renvoie None et la logique générique de
mapping.py s'applique (aucun risque de casser un sujet atypique).
"""

from __future__ import annotations

from typing import Any, Callable

from ..session_state import AgentRole, SequenceStep
from .base import PARTNER_RULES, ProviderProfile, make_step, normalize_level, teil_seconds

# ---------------------------------------------------------------------------
# Durées cibles (secondes)
# ---------------------------------------------------------------------------

# B2 Teil 1 : total ~300 s, aligné sur les ~5 min officielles
B2_T1_WARMUP_SECONDS = 20
B2_T1_STUDENT_PRESENTATION_SECONDS = 90
B2_T1_AGENT_QUESTIONS_SECONDS = 60
B2_T1_AGENT_PRESENTATION_SECONDS = 75
B2_T1_AGENT_ANSWERS_SECONDS = 55

# B1 Teil 1 : conversation ~150 s, puis la question finale de l'examinateur
B1_T1_CONVERSATION_SECONDS = 150

DEFAULT_TEIL_SECONDS = 300

# ---------------------------------------------------------------------------
# Banques de types de questions (l'IA doit varier, jamais répéter)
# ---------------------------------------------------------------------------

# B2 Teil 1 : questions de suivi sur l'expérience présentée par l'élève
B2_FOLLOW_UP_CATEGORIES = [
    "with whom / alone (e.g. 'Waren Sie allein oder mit jemandem dort?')",
    "when and where exactly",
    "how it happened or how they got there (e.g. 'Wie sind Sie ... gekommen?')",
    "what they liked most or least (e.g. 'Was hat Ihnen am besten gefallen?')",
    "why it was important or memorable for them (e.g. 'Warum war das so wichtig für Sie?')",
    "whether they would recommend it or do it again",
    "a comparison with their expectations or with their home country",
]

# B1 Teil 1 : sujets de la Kontaktaufnahme
B1_KONTAKT_TOPICS = [
    "name",
    "where they come from (Herkunft)",
    "where and how they live (Wohnung, Stadt)",
    "family",
    "job or studies",
    "travel: whether they have been to other countries",
    "languages: which ones, for how long, why they learn German",
    "hobbies and free time",
]

# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

B2_DISCUSSION_PHASES = [
    "Opening: greet your partner, thank them, and introduce the topic of the text in one sentence.",
    (
        "Reformulate the topic: say in your own words what the text is about and which "
        "question is controversial (pro / contra). State which side you take and ask the "
        "student for their position. By default take the side OPPOSITE to the student's. "
        "If you both turn out to agree, keep your side but keep bringing up its drawbacks "
        "so the discussion stays alive."
    ),
    "Personal experience: share a short personal experience linked to the topic, then ask about the student's.",
    (
        "Point of view: give your opinion with at least one clear reason, ask for theirs, "
        "and react to their arguments (agree partly or object)."
    ),
    (
        "Advantages and disadvantages: go through concrete pros and cons "
        "('einerseits ... andererseits'), including at least one argument the student "
        "has not raised yet."
    ),
    (
        "Solution: work towards a solution or a compromise together, then close with a "
        "one-sentence summary of what you agreed on. Never skip this phase."
    ),
]

B1_THEMA_PHASES = [
    (
        "The student reports their own text first. Listen without interrupting. Then thank "
        "them in one short sentence. If they have not reported their text, ask them once "
        "what their text was about."
    ),
    (
        "Report YOUR text briefly in your own words, with indirect speech ('Sie sagt, "
        "dass ...', 'Er findet, dass ...'). Then share one short personal experience and "
        "ask: 'Wie ist das bei Ihnen?'"
    ),
    (
        "Opinion: defend the view of YOUR text in simple words (it is the opposite of the "
        "student's text). Ask for their opinion and react to it."
    ),
    "Pros and cons: name a few concrete advantages and disadvantages of both options.",
    (
        "Free exchange: ask follow-up questions about the student's experiences and compare "
        "('Bei uns ist es ähnlich / anders ...')."
    ),
    (
        "Optional light close: for example 'Es kommt darauf an ...' or which option suits "
        "which situation. No common decision is needed."
    ),
]

PLANNING_PHASES_COMMON = [
    (
        "Open: restate briefly what you have to plan together, then make a first concrete "
        "proposal for the first planning point."
    ),
    (
        "Go through EVERY planning point listed below, one after the other. For each one: "
        "propose something, ask for the student's opinion, react."
    ),
    (
        "Do not just agree: at least once, raise a doubt or a practical problem and "
        "negotiate a compromise ('Das ist zwar eine gute Idee, aber ...')."
    ),
]

B1_PLANNING_PHASES = PLANNING_PHASES_COMMON + [
    "At the end, split the tasks between you: who takes care of what ('Wer kümmert sich um was?').",
]

B2_PLANNING_PHASES = PLANNING_PHASES_COMMON + [
    "At the end, summarize the decisions in one or two sentences ('Also, wir haben beschlossen, ...').",
]

PHASE_PACING_NOTE = (
    "Move through the phases in order, one at a time; each phase usually needs at least "
    "one real exchange. Use the conversation so far and the elapsed time to know where you "
    "are, and pace yourself so the last phase happens before the time runs out."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _theme_titles(teil_raw: dict[str, Any]) -> list[str]:
    """Titres des thèmes au choix (telc B2 Teil 1), quel que soit le
    format stocké : liste de chaînes, liste de dicts ou dict thema1/thema2."""
    themes = teil_raw.get("themes")
    if isinstance(themes, dict):
        items = list(themes.values())
    elif isinstance(themes, list):
        items = themes
    else:
        return []

    titles: list[str] = []
    for item in items:
        title = (
            item.get("title") or item.get("titel") or item.get("thema")
            if isinstance(item, dict)
            else item
        )
        if title:
            titles.append(str(title))
    return titles


# ---------------------------------------------------------------------------
# telc B1
# ---------------------------------------------------------------------------


def _b1_teil1(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=B1_T1_CONVERSATION_SECONDS,
            min_turns=6,
            question_categories=B1_KONTAKT_TOPICS,
            behavior_note=(
                "You are the exam PARTNER (another candidate). You get to know each other. "
                "First turn: greet the student, say your first name, and settle whether you "
                "say 'du' or 'Sie' ('Wollen wir du sagen?'). Then keep that form for the whole "
                "conversation, never mix du and Sie. Talk through the topics listed below, one "
                "at a time: when the student asks you something, answer in 2 or 3 simple "
                "sentences with plausible, consistent personal details, then ask them about a "
                "topic not covered yet. Never come back to a topic already covered. Simple B1 "
                "sentences and everyday words. " + PARTNER_RULES
            ),
        ),
        make_step(
            order=2,
            role=AgentRole.EXAMINER,
            agent_opens=True,
            content=content,
            # Pas de durée cible : l'étape finit dès la réponse de l'élève
            target_duration_seconds=None,
            min_turns=2,
            behavior_note=(
                "You now speak as the EXAMINER, no longer as the partner. Ask the student "
                "exactly ONE short question, for example why they are taking this certificate "
                "exam or what they want to do with their German ('Weshalb machen Sie die "
                "Zertifikatsprüfung?'). Then listen. Do not comment on the answer and do not "
                "ask anything else."
            ),
        ),
    ]


def _b1_teil2(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=False,
            content=content,
            target_duration_seconds=teil_seconds(teil_raw, DEFAULT_TEIL_SECONDS),
            min_turns=6,
            phases=B1_THEMA_PHASES,
            behavior_note=(
                "You are the exam PARTNER. You and the student each read a DIFFERENT short "
                "text on the same topic, with opposite views (see the reading stimulus "
                "below). This is a light discussion, NOT a planning task: never suggest "
                "organising something together and never split tasks. Never report, quote or "
                "reveal the student's text yourself. Use the same form (du or Sie) as the "
                "student; if unclear, use Sie. Simple B1 sentences and everyday words. "
                + PHASE_PACING_NOTE
                + " "
                + PARTNER_RULES
            ),
        ),
    ]


def _b1_teil3(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=teil_seconds(teil_raw, DEFAULT_TEIL_SECONDS),
            min_turns=6,
            phases=B1_PLANNING_PHASES,
            behavior_note=(
                "You are the exam PARTNER. You plan something together as equals. Propose "
                "your own concrete ideas, do not just wait for the student, and do not accept "
                "every proposal. Use the same form (du or Sie) as the student; if unclear, use "
                "Sie. Simple B1 sentences and everyday words. "
                + PHASE_PACING_NOTE
                + " "
                + PARTNER_RULES
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# telc B2
# ---------------------------------------------------------------------------


def _b2_teil1(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    theme_titles = _theme_titles(teil_raw)

    return [
        # 1. Échauffement (non noté à l'examen)
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=B2_T1_WARMUP_SECONDS,
            min_turns=3,
            behavior_note=(
                "Short warm-up before the task, not graded. Greet the student with 'Sie', say "
                "your first name and ask ONE simple friendly question (how they are, how the "
                "preparation went). After their answer, react in one short sentence and invite "
                "them to start presenting their chosen topic ('Möchten Sie anfangen?'). Do not "
                "talk about the topics yourself yet."
            ),
        ),
        # 2. L'élève présente (~90 s)
        make_step(
            order=2,
            role=AgentRole.SILENT_LISTENER,
            agent_opens=False,
            content=content,
            target_duration_seconds=B2_T1_STUDENT_PRESENTATION_SECONDS,
            min_turns=1,
            behavior_note=(
                "The student presents a personal experience on the topic they chose "
                "(about 90 seconds). Stay silent."
            ),
        ),
        # 3. L'IA (partenaire) pose des questions de suivi variées
        make_step(
            order=3,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=B2_T1_AGENT_QUESTIONS_SECONDS,
            min_turns=4,
            question_categories=B2_FOLLOW_UP_CATEGORIES,
            behavior_note=(
                "You are the exam PARTNER (Kandidat B), not the examiner. The student just "
                "presented a personal experience. In your first turn: one short sentence "
                "reacting to it (what you found interesting), then ONE open follow-up question "
                "about their experience. In each following turn: react in one short sentence "
                "to their answer, then ask ONE new question of a type you have not used yet "
                "(see the question types below). Only ask about what the student presented. "
                "Never repeat or rephrase a question already asked. Do not present your own "
                "topic yet. Use 'Sie'. " + PARTNER_RULES
            ),
        ),
        # 4. L'IA présente son propre thème
        make_step(
            order=4,
            role=AgentRole.PRESENTER,
            agent_opens=True,
            content={**content, "content_points": theme_titles},
            target_duration_seconds=B2_T1_AGENT_PRESENTATION_SECONDS,
            min_turns=1,
            behavior_note=(
                "Now it is YOUR turn to present, as the other candidate (about 75 seconds). "
                "Choose ONE topic from the list below that is DIFFERENT from the one the "
                "student presented (see the conversation). Talk about a concrete experience "
                "as if it were your own, in the first person, mostly in the Perfekt, with "
                "this structure: opening ('Ich möchte Ihnen von ... erzählen'), what, when and "
                "where, with whom, what happened, what you liked most and why it mattered to "
                "you, short conclusion. Inventing this personal story is part of your role "
                "and is allowed. Keep your details precise and consistent: the student will "
                "ask you about them. End with: 'Haben Sie Fragen dazu?'"
            ),
        ),
        # 5. L'élève pose ses questions, l'IA répond
        make_step(
            order=5,
            role=AgentRole.PARTNER,
            agent_opens=False,
            content=content,
            target_duration_seconds=B2_T1_AGENT_ANSWERS_SECONDS,
            min_turns=4,
            behavior_note=(
                "The student now asks YOU questions about your presentation. Answer each "
                "question directly and concretely in 2 or 3 sentences, consistent with what "
                "you said in your presentation (see the conversation); inventing plausible "
                "personal details is part of your role and is allowed, but never contradict "
                "yourself. Do not ask the student "
                "about their own topic again. After answering, wait for the next question. If "
                "the student stays silent, invite them once: 'Möchten Sie noch etwas wissen?'"
            ),
        ),
    ]


def _b2_teil2(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=teil_seconds(teil_raw, DEFAULT_TEIL_SECONDS),
            min_turns=6,
            phases=B2_DISCUSSION_PHASES,
            behavior_note=(
                "You are the exam PARTNER in a discussion about the text you both read. This "
                "is a debate, NOT a planning task. Take a clear position and defend it with "
                "reasons, but stay fair and collaborative: the goal is a real exchange, not "
                "winning. Use 'Sie'. B2 language: varied vocabulary, subordinate clauses. "
                + PHASE_PACING_NOTE
                + " "
                + PARTNER_RULES
            ),
        ),
    ]


def _b2_teil3(teil_raw: dict[str, Any], content: dict[str, Any]) -> list[SequenceStep]:
    return [
        make_step(
            order=1,
            role=AgentRole.PARTNER,
            agent_opens=True,
            content=content,
            target_duration_seconds=teil_seconds(teil_raw, DEFAULT_TEIL_SECONDS),
            min_turns=6,
            phases=B2_PLANNING_PHASES,
            behavior_note=(
                "You are the exam PARTNER. You plan something together as equals. Propose "
                "your own concrete ideas, do not just wait for the student, and do not accept "
                "every proposal. Use 'Sie'. "
                + PHASE_PACING_NOTE
                + " "
                + PARTNER_RULES
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_Builder = Callable[[dict[str, Any], dict[str, Any]], list[SequenceStep]]

# niveau -> numéro de Teil -> (format_types acceptés, constructeur)
_TELC_TEILE: dict[str, dict[int, tuple[set[str], _Builder]]] = {
    "B1": {
        1: ({"oral_kennenlernen", "oral_interaction"}, _b1_teil1),
        2: ({"oral_thema"}, _b1_teil2),
        3: ({"oral_interaction"}, _b1_teil3),
    },
    "B2": {
        1: ({"oral_monologue"}, _b2_teil1),
        2: ({"oral_interaction", "oral_discussion"}, _b2_teil2),
        3: ({"oral_interaction"}, _b2_teil3),
    },
}


class TelcProfile(ProviderProfile):
    name = "telc"

    def build_sequence(
        self,
        teil_raw: dict[str, Any],
        *,
        level: str,
        content: dict[str, Any],
    ) -> list[SequenceStep] | None:
        teile = _TELC_TEILE.get(normalize_level(level))
        if not teile:
            return None

        entry = teile.get(teil_raw.get("teil_number"))
        if entry is None:
            return None

        accepted_formats, builder = entry
        if teil_raw.get("format_type") not in accepted_formats:
            return None

        return builder(teil_raw, content)