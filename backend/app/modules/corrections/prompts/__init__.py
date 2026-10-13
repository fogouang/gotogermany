"""
app/modules/corrections/prompts/__init__.py

Router central : reçoit les données extraites de la DB et retourne
le prompt complet prêt à envoyer à l'IA.

Mapping :
    telc    + b1      → get_telc_b1_prompt
    telc    + b2      → get_telc_b2_prompt
    goethe  + b1      → get_goethe_osd_b1_prompt
    goethe  + b2      → get_goethe_b2_prompt
    osd     + b1      → get_goethe_osd_b1_prompt  (structure identique à Goethe B1)
    osd     + b2      → get_osd_b2_prompt
    ecl     + b1/b2   → get_ecl_prompt             (ESQUISSE à valider)
    testdaf + b2/c1   → get_testdaf_prompt         (ESQUISSE à valider)
"""
from app.modules.corrections.testdaf_prompt import get_testdaf_prompt
from app.modules.corrections.ecl_prompt import get_ecl_prompt
from dataclasses import dataclass, field

from app.modules.corrections.prompts.b1.telc_b1_prompt import get_telc_b1_prompt
from app.modules.corrections.prompts.b1.goethe_osd_b1_prompt import get_goethe_osd_b1_prompt
from app.modules.corrections.prompts.b2.telc_b2_prompt import get_telc_b2_prompt
from app.modules.corrections.prompts.b2.goethe_b2_prompt import get_goethe_b2_prompt
from app.modules.corrections.prompts.b2.osd_b2_prompt import get_osd_b2_prompt


# ─────────────────────────────────────────────────────────
# Dataclass pour transporter les données d'une tâche
# ─────────────────────────────────────────────────────────

@dataclass
class TaskData:
    """Données extraites de la DB pour une tâche Schreiben."""
    text: str                           # Réponse du candidat
    instruction: str                    # Consigne de la question
    bullet_points: list[str] = field(default_factory=list)   # Points à traiter
    opinion_quote: str = ""             # Goethe B1 Teil 2 : citation du forum
    topic: str = ""                     # Goethe/ÖSD B2 Teil 1 : thème
    context_ad: str = ""                # Telc B2 : annonce ; ÖSD B2 Teil 1 : Informationsblatt ; TestDaF A2 : texte source + graphique

# ─────────────────────────────────────────────────────────
# Constantes : providers et niveaux supportés
# ─────────────────────────────────────────────────────────

SUPPORTED_PROVIDERS = {"telc", "goethe", "osd", "ecl", "testdaf"}
SUPPORTED_LEVELS    = {"b1", "b2", "c1"}

# Nombre de tâches attendues par (provider, level)
EXPECTED_TASK_COUNT = {
    ("telc",    "b1"): 1,
    ("telc",    "b2"): 1,
    ("goethe",  "b1"): 3,
    ("goethe",  "b2"): 2,
    ("osd",     "b1"): 3,
    ("osd",     "b2"): 2,
    ("ecl",     "b1"): 2,
    ("ecl",     "b2"): 2,
    ("testdaf", "b2"): 2,
    ("testdaf", "c1"): 2,
}

# Score maximum par (provider, level)
MAX_SCORES = {
    ("telc",    "b1"): 45,
    ("telc",    "b2"): 45,
    ("goethe",  "b1"): 100,
    ("goethe",  "b2"): 100,
    ("osd",     "b1"): 100,
    ("osd",     "b2"): 30,
    ("ecl",     "b1"): 25,
    ("ecl",     "b2"): 25,
    ("testdaf", "b2"): 20,
    ("testdaf", "c1"): 20,
}

def _with_points(instruction: str, points: list[str], label: str = "Leitpunkte") -> str:
    """Ajoute les points à traiter à la consigne, pour les prompts sans paramètre dédié."""
    if not points:
        return instruction
    lines = "\n".join(f"- {p}" for p in points)
    return f"{instruction}\n\n{label}:\n{lines}".strip()


def _normalize_provider(provider: str) -> str:
    """"ÖSD" / "ösd" -> "osd" ; le reste en minuscules."""
    return provider.lower().strip().replace("ö", "o")


# ─────────────────────────────────────────────────────────
# Fonction principale
# ─────────────────────────────────────────────────────────

def build_correction_prompt(
    provider: str,
    level: str,
    tasks: list[TaskData],
) -> str:
    """
    Construire le prompt de correction selon le provider et le niveau.

    Raises:
        ValueError: Provider/niveau non supporté ou nombre de tâches incorrect
    """
    provider = _normalize_provider(provider)
    level    = level.lower().strip()

    _validate(provider, level, tasks)

    key = (provider, level)

    # ── Telc B1 ─────────────────────────────────────────
    if key == ("telc", "b1"):
        t = tasks[0]
        return get_telc_b1_prompt(
            text=t.text,
            task_instruction=t.instruction,
            bullet_points=t.bullet_points,
        )

    # ── Telc B2 ─────────────────────────────────────────
    if key == ("telc", "b2"):
        t = tasks[0]
        return get_telc_b2_prompt(
            text=t.text,
            task_instruction=t.instruction,
            bullet_points=t.bullet_points,
            context_ad=t.context_ad,
        )

    # ── Goethe B1 / ÖSD B1 ──────────────────────────────
    if key in (("goethe", "b1"), ("osd", "b1")):
        t1, t2, t3 = tasks[0], tasks[1], tasks[2]
        return get_goethe_osd_b1_prompt(
            task1_text=t1.text,
            task1_instruction=t1.instruction,
            task1_bullet_points=t1.bullet_points,
            task2_text=t2.text,
            task2_instruction=t2.instruction,
            task2_opinion_quote=t2.opinion_quote,
            task3_text=t3.text,
            task3_instruction=t3.instruction,
        )

    # ── Goethe B2 ───────────────────────────────────────
    if key == ("goethe", "b2"):
        t1, t2 = tasks[0], tasks[1]
        return get_goethe_b2_prompt(
            task1_text=t1.text,
            task1_instruction=_with_points(t1.instruction, t1.bullet_points),
            task1_topic=t1.topic,
            task2_text=t2.text,
            task2_instruction=_with_points(t2.instruction, t2.bullet_points),
        )

    # ── ÖSD B2 ──────────────────────────────────────────
    if key == ("osd", "b2"):
        t1, t2 = tasks[0], tasks[1]
        # Teil 1 = Beschwerde-Mail, Teil 2 = Meinungsäußerung (ordre des sujets ÖSD B2)
        return get_osd_b2_prompt(
            task1_text=t1.text,
            task1_instruction=t1.instruction,
            task1_context=t1.context_ad,
            task1_bullet_points=t1.bullet_points,
            task2_text=t2.text,
            task2_instruction=t2.instruction,
            task2_topic=t2.topic,
            task2_statements=t2.opinion_quote,
            task2_bullet_points=t2.bullet_points,
        )

    # ── ECL B1 / B2 (esquisse) ──────────────────────────
    if provider == "ecl":
        t1, t2 = tasks[0], tasks[1]
        return get_ecl_prompt(
            level=level,
            task1_text=t1.text,
            task1_instruction=t1.instruction,
            task1_bullets=t1.bullet_points,
            task2_text=t2.text,
            task2_instruction=t2.instruction,
            task2_bullets=t2.bullet_points,
        )

    # ── TestDaF (esquisse) ──────────────────────────────
    if provider == "testdaf":
        t1, t2 = tasks[0], tasks[1]
        return get_testdaf_prompt(
            task1_text=t1.text,
            task1_instruction=t1.instruction,
            task2_text=t2.text,
            task2_instruction=t2.instruction,
            task2_source=t2.context_ad,
        )

    raise ValueError(f"Combinaison non gérée : provider={provider}, level={level}")


def get_max_score(provider: str, level: str) -> int:
    """Retourner le score maximum pour un examen donné."""
    return MAX_SCORES[(_normalize_provider(provider), level.lower())]


def get_expected_task_count(provider: str, level: str) -> int:
    """Retourner le nombre de tâches attendues pour un examen donné."""
    return EXPECTED_TASK_COUNT[(_normalize_provider(provider), level.lower())]


# ─────────────────────────────────────────────────────────
# Validation interne
# ─────────────────────────────────────────────────────────

def _validate(provider: str, level: str, tasks: list[TaskData]) -> None:
    """Valider provider, level et nombre de tâches."""

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Provider '{provider}' non supporté. "
            f"Valeurs acceptées : {SUPPORTED_PROVIDERS}"
        )

    if level not in SUPPORTED_LEVELS:
        raise ValueError(
            f"Niveau '{level}' non supporté. "
            f"Valeurs acceptées : {SUPPORTED_LEVELS}"
        )

    expected = EXPECTED_TASK_COUNT.get((provider, level))
    if expected is None:
        raise ValueError(
            f"La correction IA n'est pas disponible pour {provider.upper()} {level.upper()}."
        )
    if len(tasks) != expected:
        raise ValueError(
            f"Examen {provider.upper()} {level.upper()} attend {expected} tâche(s), "
            f"mais {len(tasks)} ont été fournies."
        )

    for i, task in enumerate(tasks, start=1):
        if not task.text or not task.text.strip():
            raise ValueError(f"Le texte de la tâche {i} est vide.")
        if not task.instruction or not task.instruction.strip():
            raise ValueError(f"La consigne de la tâche {i} est vide.")