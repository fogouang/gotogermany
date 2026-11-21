"""
testdaf_sprechen.tts
=======================
Voix de l'interlocuteur (TestDaF digital, épreuve orale).

Le JSON d'une tâche contient le texte joué à l'examen dans `audio_prompt`,
une réplique par ligne, préfixée par le locuteur :

    [Seminarteilnehmer]: Also, ich finde, bei uns hat sich ...
    [Frau Dr. Bayer]: Ja, bitte? Sie möchten sich zum Beitrag ... äußern?

Comme à l'examen :
  - toutes les répliques SAUF la dernière forment la "déclaration" jouée
    avant la préparation (tâches 4 et 6 : le camarade qui donne son avis) ;
  - la dernière réplique est la "question" de l'interlocuteur, jouée
    juste avant l'enregistrement.

Chaque réplique est synthétisée une seule fois avec edge-tts (voix
masculine ou féminine selon le locuteur), puis mise en cache sur disque
sous un nom dérivé du texte et de la voix : un même sujet ne régénère
jamais ses fichiers.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

# Dossier de cache des fichiers audio générés. À ADAPTER si tu veux les
# ranger ailleurs (volume Docker persistant de préférence).
TTS_CACHE_DIR = Path(os.getenv("TESTDAF_TTS_CACHE_DIR", "media/testdaf_tts"))

# Voix allemandes edge-tts, deux de chaque pour pouvoir distinguer deux
# locuteurs du même genre dans une même tâche.
FEMALE_VOICES = ["de-DE-KatjaNeural", "de-DE-AmalaNeural"]
MALE_VOICES = ["de-DE-ConradNeural", "de-DE-KillianNeural"]

_LINE_RE = re.compile(r"^\s*\[([^\]]+)\]\s*:\s*(.+?)\s*$")

_FEMALE_HINTS = (
    "frau", "kommilitonin", "dozentin", "tutorin", "moderatorin", "freundin",
    "seminarteilnehmerin", "studentin", "professorin", "mitarbeiterin",
)
_MALE_HINTS = (
    "herr", "kommilitone", "dozent", "tutor", "moderator", "freund",
    "seminarteilnehmer", "student", "professor", "mitarbeiter",
)
_FEMALE_NAMES = {
    "laura", "paula", "anna", "lisa", "julia", "sarah", "maria", "lena", "sophie",
    "marie", "katharina", "ingrid", "claudia", "sabine", "nina", "lea", "hannah",
}
_MALE_NAMES = {
    "timo", "tim", "christian", "jan", "lukas", "felix", "max", "paul", "jonas",
    "thomas", "michael", "stefan", "david", "daniel", "markus", "peter", "tobias",
}


@dataclass(frozen=True)
class PromptLine:
    speaker: str
    text: str


def parse_audio_prompt(audio_prompt: str | None) -> list[PromptLine]:
    """'[Timo]: Was meinst du ...' -> [PromptLine('Timo', 'Was meinst du ...')].
    Une ligne sans préfixe est rattachée au locuteur précédent."""
    lines: list[PromptLine] = []
    for raw in (audio_prompt or "").splitlines():
        if not raw.strip():
            continue
        match = _LINE_RE.match(raw)
        if match:
            lines.append(PromptLine(match.group(1).strip(), match.group(2).strip()))
        elif lines:
            last = lines[-1]
            lines[-1] = PromptLine(last.speaker, f"{last.text} {raw.strip()}")
        else:
            lines.append(PromptLine("Sprecher", raw.strip()))
    return lines


def speaker_is_female(speaker: str) -> bool:
    s = speaker.strip().lower()
    first_word = s.split()[0] if s else ""
    if first_word in _FEMALE_NAMES or any(s.startswith(h) or s.endswith(h) for h in _FEMALE_HINTS):
        return True
    if first_word in _MALE_NAMES or any(s.startswith(h) or s.endswith(h) for h in _MALE_HINTS):
        return False
    # Inconnu : un prénom allemand finissant en -a est le plus souvent féminin
    return first_word.endswith("a")


def assign_voices(lines: list[PromptLine]) -> dict[str, str]:
    """Une voix stable par locuteur dans la tâche, deux locuteurs du même
    genre reçoivent deux voix différentes."""
    voices: dict[str, str] = {}
    female_i = male_i = 0
    for line in lines:
        if line.speaker in voices:
            continue
        if speaker_is_female(line.speaker):
            voices[line.speaker] = FEMALE_VOICES[female_i % len(FEMALE_VOICES)]
            female_i += 1
        else:
            voices[line.speaker] = MALE_VOICES[male_i % len(MALE_VOICES)]
            male_i += 1
    return voices


def cache_filename(text: str, voice: str) -> str:
    digest = hashlib.sha256(f"{voice}|{text}".encode("utf-8")).hexdigest()[:32]
    return f"{digest}.mp3"


def cache_path(filename: str) -> Path | None:
    """Chemin d'un fichier du cache, ou None si le nom n'est pas valide
    (protège la route de téléchargement contre ../ et compagnie)."""
    if not re.fullmatch(r"[0-9a-f]{32}\.mp3", filename):
        return None
    return TTS_CACHE_DIR / filename


async def synthesize(text: str, voice: str) -> str:
    """Génère (si besoin) le mp3 et renvoie son nom de fichier."""
    import edge_tts  # import local : dépendance chargée seulement ici

    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = cache_filename(text, voice)
    path = TTS_CACHE_DIR / filename
    if not path.exists() or path.stat().st_size == 0:
        tmp = path.with_suffix(".tmp")
        await edge_tts.Communicate(text, voice).save(str(tmp))
        tmp.replace(path)
    return filename


async def build_task_audio(audio_prompt: str | None) -> tuple[list[str], str | None]:
    """Renvoie (fichiers de la déclaration, fichier de la question).
    La déclaration peut être vide (tâches à une seule réplique)."""
    lines = parse_audio_prompt(audio_prompt)
    if not lines:
        return [], None

    voices = assign_voices(lines)
    statement_files = [await synthesize(l.text, voices[l.speaker]) for l in lines[:-1]]
    question_file = await synthesize(lines[-1].text, voices[lines[-1].speaker])
    return statement_files, question_file