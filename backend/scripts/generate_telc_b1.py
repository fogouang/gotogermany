"""
Générateur d'examen TELC Deutsch B1 / Zertifikat Deutsch
=========================================================
- Gemini API  → génération du contenu (5 modules)
- edge-tts    → audio pour Hörverstehen (gratuit, voix allemande)
- Sortie      → telc_b1_YYYYMMDD_HHMMSS.json + audio/horen_teil_X.mp3

Différences clés vs Goethe-ÖSD B1 :
- Lesen : 3 Teile (zuordnung_titre, qcm_abc, selektives_matching)
- Sprachbausteine : module supplémentaire (gap_fill + word_bank)
- Hörverstehen : 3 Teile, Teil 1 joué 1 SEULE fois, tout Richtig/Falsch
- Schriftlicher Ausdruck : 1 seule tâche email avec 4 Leitpunkte
- Mündlicher Ausdruck : Kennenlernen + Thema + Planen

Usage:
    python generate_telc_b1.py --api-key VOTRE_CLE_GEMINI
    python generate_telc_b1.py --api-key VOTRE_CLE_GEMINI --no-audio
"""

import json
import asyncio
import argparse
import re
import os
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types

# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es un expert certifié en création d'examens de langue allemande TELC Deutsch B1 / Zertifikat Deutsch.
Tu génères des examens authentiques, calibrés CECRL B1, avec des textes variés sur des sujets quotidiens.
Réponds UNIQUEMENT en JSON valide. Pas de texte avant ni après. Pas de balises markdown.
Tous les textes, questions et réponses sont en ALLEMAND.
"""

# ─── Prompts Leseverstehen ────────────────────────────────────────────────────

def prompt_lesen_teil1() -> str:
    return """Génère le Teil 1 du module LESEVERSTEHEN (TELC Deutsch B1).

TELC Lesen Teil 1 — Globalverstehen (Zuordnung Überschriften)
- 5 textes courts (~80 mots chacun) sur des sujets variés du quotidien
- 10 titres possibles (a-j), dont 5 correspondent aux textes et 5 sont des distracteurs
- L'étudiant doit associer chaque texte au bon titre
- Questions numéros 1-5
- 25 points total (5 pts par bonne réponse)

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 1,
  "name": "Globalverstehen",
  "format_type": "zuordnung_titre",
  "instructions": "Lesen Sie die Überschriften a–j und die Texte 1–5. Finden Sie für jeden Text die passende Überschrift. Sie können jede Überschrift nur einmal benutzen. Markieren Sie Ihre Lösungen für die Aufgaben 1–5 auf dem Antwortbogen.",
  "time_minutes": 15,
  "max_score": 25,
  "titres": {
    "a": "...",
    "b": "...",
    "c": "...",
    "d": "...",
    "e": "...",
    "f": "...",
    "g": "...",
    "h": "...",
    "i": "...",
    "j": "..."
  },
  "questions": [
    {
      "number": 1,
      "stimulus_text": "...(texte ~80 mots)...",
      "answer": "c"
    },
    {
      "number": 2,
      "stimulus_text": "...",
      "answer": "f"
    },
    {
      "number": 3,
      "stimulus_text": "...",
      "answer": "a"
    },
    {
      "number": 4,
      "stimulus_text": "...",
      "answer": "h"
    },
    {
      "number": 5,
      "stimulus_text": "...",
      "answer": "d"
    }
  ]
}"""


def prompt_lesen_teil2() -> str:
    return """Génère le Teil 2 du module LESEVERSTEHEN (TELC Deutsch B1).

TELC Lesen Teil 2 — Detailverstehen
- 1 texte long (~300 mots) sur un sujet de société (entreprise sociale, projet communautaire, etc.)
- 5 questions QCM a/b/c (numéros 6-10)
- 25 points total (5 pts par bonne réponse)

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 2,
  "name": "Detailverstehen",
  "format_type": "qcm_abc",
  "instructions": "Lesen Sie den Text und die Aufgaben 6–10. Welche Lösung (a, b oder c) ist jeweils richtig? Markieren Sie Ihre Lösungen für die Aufgaben 6–10 auf dem Antwortbogen.",
  "time_minutes": 20,
  "max_score": 25,
  "stimulus_text": "...(texte ~300 mots)...",
  "source": "aus einem deutschen Online-Magazin",
  "questions": [
    {
      "number": 6,
      "stem": "In diesem Text geht es darum, dass ...",
      "options": {"a": "...", "b": "...", "c": "..."},
      "answer": "b"
    },
    {
      "number": 7,
      "stem": "...",
      "options": {"a": "...", "b": "...", "c": "..."},
      "answer": "a"
    },
    {
      "number": 8,
      "stem": "...",
      "options": {"a": "...", "b": "...", "c": "..."},
      "answer": "c"
    },
    {
      "number": 9,
      "stem": "...",
      "options": {"a": "...", "b": "...", "c": "..."},
      "answer": "b"
    },
    {
      "number": 10,
      "stem": "...",
      "options": {"a": "...", "b": "...", "c": "..."},
      "answer": "a"
    }
  ]
}"""


def prompt_lesen_teil3() -> str:
    return """Génère le Teil 3 du module LESEVERSTEHEN (TELC Deutsch B1).

TELC Lesen Teil 3 — Selektives Verstehen (Zuordnung situations/annonces)
- 10 situations d'étudiants cherchant des offres/services spécifiques (numéros 11-20)
- 12 annonces courtes (a-l) provenant de médias germanophones
- L'étudiant associe chaque situation à l'annonce correspondante
- Certaines situations n'ont PAS d'annonce correspondante (réponse = "x")
- Chaque annonce ne peut être utilisée qu'une fois
- 25 points total

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 3,
  "name": "Selektives Verstehen",
  "format_type": "selektives_matching",
  "instructions": "Lesen Sie die Situationen 11–20 und die Anzeigen a–l. Finden Sie für jede Situation die passende Anzeige. Sie können jede Anzeige nur einmal benutzen. Wenn Sie zu einer Situation keine Anzeige finden, markieren Sie ein x. Markieren Sie Ihre Lösungen für die Aufgaben 11–20 auf dem Antwortbogen.",
  "time_minutes": 20,
  "max_score": 25,
  "context": "Touristen suchen passende Angebote in einer deutschsprachigen Stadt.",
  "anzeigen": {
    "a": "...(annonce courte)...",
    "b": "...",
    "c": "...",
    "d": "...",
    "e": "...",
    "f": "...",
    "g": "...",
    "h": "...",
    "i": "...",
    "j": "...",
    "k": "...",
    "l": "..."
  },
  "questions": [
    {"number": 11, "situation": "...", "answer": "c"},
    {"number": 12, "situation": "...", "answer": "a"},
    {"number": 13, "situation": "...", "answer": "f"},
    {"number": 14, "situation": "...", "answer": "x"},
    {"number": 15, "situation": "...", "answer": "h"},
    {"number": 16, "situation": "...", "answer": "i"},
    {"number": 17, "situation": "...", "answer": "k"},
    {"number": 18, "situation": "...", "answer": "l"},
    {"number": 19, "situation": "...", "answer": "x"},
    {"number": 20, "situation": "...", "answer": "g"}
  ]
}"""


# ─── Prompts Sprachbausteine ──────────────────────────────────────────────────

def prompt_sprachbausteine_teil1() -> str:
    return """Génère le Teil 1 du module SPRACHBAUSTEINE (TELC Deutsch B1).

TELC Sprachbausteine Teil 1 — Grammatik (QCM à trous)
- 1 texte cohérent (~200 mots, lettre/email personnel)
- 10 lacunes numérotées dans le texte (numéros 21-30)
- Pour chaque lacune : 3 options a/b/c dont 1 seule est grammaticalement correcte
- Teste : articles, prépositions, conjonctions, pronoms, formes verbales
- 15 points total

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 1,
  "name": "Grammatik",
  "format_type": "qcm_gap_fill",
  "instructions": "Lesen Sie den Text und schließen Sie die Lücken 21–30. Welche Lösung (a, b oder c) ist jeweils richtig? Markieren Sie Ihre Lösungen für die Aufgaben 21–30 auf dem Antwortbogen.",
  "time_minutes": 15,
  "max_score": 15,
  "text_with_gaps": "Liebe Maria,\n\nich schreibe dir _21_ meiner neuen Wohnung. Ich bin jetzt _22_ drei Wochen hier und fühle mich schon ganz wohl. Die Wohnung _23_ sehr hell und modern. _24_ habe ich sogar einen kleinen Balkon...(texte ~200 mots avec exactement 10 lacunes marquées _21_ à _30_)...\n\nLiebe Grüße\nThomas",
  "questions": [
    {"number": 21, "options": {"a": "aus", "b": "von", "c": "bei"}, "answer": "b"},
    {"number": 22, "options": {"a": "seit", "b": "vor", "c": "nach"}, "answer": "a"},
    {"number": 23, "options": {"a": "bin", "b": "hat", "c": "ist"}, "answer": "c"},
    {"number": 24, "options": {"a": "Außerdem", "b": "Trotzdem", "c": "Deshalb"}, "answer": "a"},
    {"number": 25, "options": {"a": "weil", "b": "dass", "c": "wenn"}, "answer": "c"},
    {"number": 26, "options": {"a": "in", "b": "an", "c": "auf"}, "answer": "b"},
    {"number": 27, "options": {"a": "gelernt", "b": "lernen", "c": "lernte"}, "answer": "a"},
    {"number": 28, "options": {"a": "dem", "b": "den", "c": "die"}, "answer": "c"},
    {"number": 29, "options": {"a": "meine", "b": "meinen", "c": "meiner"}, "answer": "b"},
    {"number": 30, "options": {"a": "dir", "b": "Ihnen", "c": "euch"}, "answer": "a"}
  ]
}"""


def prompt_sprachbausteine_teil2() -> str:
    return """Génère le Teil 2 du module SPRACHBAUSTEINE (TELC Deutsch B1).

TELC Sprachbausteine Teil 2 — Lexik (Word Bank à trous)
- 1 texte cohérent (~200 mots, lettre formelle/demande d'information)
- 10 lacunes numérotées dans le texte (numéros 31-40)
- 1 liste de 15 mots candidats (a-o) dont 10 correspondent aux lacunes
- 5 mots sont des distracteurs non utilisés
- Teste le vocabulaire et les expressions idiomatiques B1
- 15 points total

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 2,
  "name": "Lexik",
  "format_type": "word_bank_gap_fill",
  "instructions": "Lesen Sie den Text und schließen Sie die Lücken 31–40. Benutzen Sie die Wörter a–o. Jedes Wort passt nur einmal. Markieren Sie Ihre Lösungen für die Aufgaben 31–40 auf dem Antwortbogen.",
  "time_minutes": 15,
  "max_score": 15,
  "text_with_gaps": "Sehr geehrte Damen und Herren,\n\nich interessiere mich _31_ Ihr Angebot und hätte _32_ noch einige Fragen...(texte ~200 mots avec exactement 10 lacunes marquées _31_ à _40_)...\n\nMit freundlichen Grüßen\nAnna Müller",
  "word_bank": {
    "a": "BESONDERS",
    "b": "DA",
    "c": "DAFÜR",
    "d": "DAMALS",
    "e": "DAMIT",
    "f": "DANKBAR",
    "g": "DESHALB",
    "h": "FÜR",
    "i": "GERNE",
    "j": "KÖNNTEN",
    "k": "MIT",
    "l": "MÜSSTEN",
    "m": "SCHLIESSLICH",
    "n": "WANN",
    "o": "WENN"
  },
  "questions": [
    {"number": 31, "answer": "h"},
    {"number": 32, "answer": "i"},
    {"number": 33, "answer": "a"},
    {"number": 34, "answer": "b"},
    {"number": 35, "answer": "o"},
    {"number": 36, "answer": "l"},
    {"number": 37, "answer": "m"},
    {"number": 38, "answer": "g"},
    {"number": 39, "answer": "e"},
    {"number": 40, "answer": "f"}
  ]
}"""


# ─── Prompts Hörverstehen ─────────────────────────────────────────────────────

def prompt_horen_teil1_telc() -> str:
    return """Génère le Teil 1 du module HÖRVERSTEHEN (TELC Deutsch B1).

TELC Hören Teil 1 — Globalverstehen
ATTENTION : chaque audio est joué UNE SEULE FOIS (pas de réécoute !)
- 5 courts enregistrements (~50 mots chacun) : conversations, annonces, messages
- 1 question Richtig/Falsch par enregistrement (numéros 41-45)
- 25 points total (5 pts par bonne réponse)
- Fournis la transcription complète de chaque enregistrement

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 1,
  "name": "Globalverstehen",
  "format_type": "richtig_falsch",
  "instructions": "Sie hören nun fünf kurze Texte. Dazu sollen Sie fünf Aufgaben lösen. Sie hören diese Texte nur einmal. Entscheiden Sie beim Hören, ob die Aussagen 41-45 richtig oder falsch sind.",
  "time_minutes": 8,
  "max_score": 25,
  "max_plays": 1,
  "audios": [
    {
      "audio_number": 1,
      "audio_type": "Gespräch",
      "transcription": "...(~50 mots, dialogue naturel B1)...",
      "questions": [
        {"number": 41, "statement": "...", "answer": "richtig"}
      ]
    },
    {
      "audio_number": 2,
      "audio_type": "Ansage",
      "transcription": "...",
      "questions": [
        {"number": 42, "statement": "...", "answer": "falsch"}
      ]
    },
    {
      "audio_number": 3,
      "audio_type": "Gespräch",
      "transcription": "...",
      "questions": [
        {"number": 43, "statement": "...", "answer": "richtig"}
      ]
    },
    {
      "audio_number": 4,
      "audio_type": "Nachricht",
      "transcription": "...",
      "questions": [
        {"number": 44, "statement": "...", "answer": "falsch"}
      ]
    },
    {
      "audio_number": 5,
      "audio_type": "Gespräch",
      "transcription": "...",
      "questions": [
        {"number": 45, "statement": "...", "answer": "richtig"}
      ]
    }
  ]
}"""


def prompt_horen_teil2_telc() -> str:
    return """Génère le Teil 2 du module HÖRVERSTEHEN (TELC Deutsch B1).

TELC Hören Teil 2 — Detailverstehen
- 1 conversation longue (~300 mots) entre deux personnes sur un sujet quotidien
- Joué DEUX FOIS
- 10 questions Richtig/Falsch (numéros 46-55)
- 25 points total

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 2,
  "name": "Detailverstehen",
  "format_type": "richtig_falsch",
  "instructions": "Sie hören nun ein Gespräch. Dazu sollen Sie zehn Aufgaben lösen. Sie hören das Gespräch zweimal. Entscheiden Sie beim Hören, ob die Aussagen 46-55 richtig oder falsch sind. Lesen Sie jetzt die Aufgaben 46-55. Sie haben dazu eine Minute Zeit.",
  "time_minutes": 12,
  "max_score": 25,
  "max_plays": 2,
  "context": "Ein Journalist spricht mit einer Vereinsvertreterin über das 100-jährige Jubiläum des Sportvereins.",
  "transcription": "...(conversation ~300 mots avec 2 locuteurs clairement identifiés, couvrant exactement les 10 statements à évaluer)...",
  "questions": [
    {"number": 46, "statement": "...", "answer": "richtig"},
    {"number": 47, "statement": "...", "answer": "richtig"},
    {"number": 48, "statement": "...", "answer": "falsch"},
    {"number": 49, "statement": "...", "answer": "falsch"},
    {"number": 50, "statement": "...", "answer": "falsch"},
    {"number": 51, "statement": "...", "answer": "richtig"},
    {"number": 52, "statement": "...", "answer": "richtig"},
    {"number": 53, "statement": "...", "answer": "falsch"},
    {"number": 54, "statement": "...", "answer": "falsch"},
    {"number": 55, "statement": "...", "answer": "richtig"}
  ]
}"""


def prompt_horen_teil3_telc() -> str:
    return """Génère le Teil 3 du module HÖRVERSTEHEN (TELC Deutsch B1).

TELC Hören Teil 3 — Selektives Verstehen
- 5 courts enregistrements (~40 mots chacun) : annonces publiques, publicités, météo, info pratique
- Joué DEUX FOIS
- 1 question Richtig/Falsch par enregistrement (numéros 56-60)
- 25 points total

Retourne UNIQUEMENT ce JSON :
{
  "teil_number": 3,
  "name": "Selektives Verstehen",
  "format_type": "richtig_falsch",
  "instructions": "Sie hören nun fünf kurze Texte. Dazu sollen Sie fünf Aufgaben lösen. Sie hören jeden Text zweimal. Entscheiden Sie beim Hören, ob die Aussagen 56-60 richtig oder falsch sind.",
  "time_minutes": 10,
  "max_score": 25,
  "max_plays": 2,
  "audios": [
    {
      "audio_number": 1,
      "audio_type": "Wegbeschreibung",
      "transcription": "...(~40 mots, annonce publique ou info pratique)...",
      "questions": [
        {"number": 56, "statement": "...", "answer": "richtig"}
      ]
    },
    {
      "audio_number": 2,
      "audio_type": "Kinoprogramm",
      "transcription": "...",
      "questions": [
        {"number": 57, "statement": "...", "answer": "falsch"}
      ]
    },
    {
      "audio_number": 3,
      "audio_type": "Wetterbericht",
      "transcription": "...",
      "questions": [
        {"number": 58, "statement": "...", "answer": "richtig"}
      ]
    },
    {
      "audio_number": 4,
      "audio_type": "Zugdurchsage",
      "transcription": "...",
      "questions": [
        {"number": 59, "statement": "...", "answer": "falsch"}
      ]
    },
    {
      "audio_number": 5,
      "audio_type": "Werbung",
      "transcription": "...",
      "questions": [
        {"number": 60, "statement": "...", "answer": "richtig"}
      ]
    }
  ]
}"""


# ─── Prompt Schriftlicher Ausdruck ────────────────────────────────────────────

def prompt_schreiben_telc() -> str:
    return """Génère le module SCHRIFTLICHER AUSDRUCK (TELC Deutsch B1).

TELC Schriftlicher Ausdruck — 1 seule tâche (email)
- L'étudiant reçoit un email d'un ami/contact et doit répondre
- 4 Leitpunkte obligatoires à traiter dans la réponse
- Email informelle ou semi-formelle (~80 mots)
- 30 minutes
- Scoring : Aufgabenbewältigung(A/B/C/D) + Kommunikative Gestaltung(A/B/C/D) + Formale Richtigkeit(A/B/C/D)
- 45 points total (chaque critère multiplié par 3 en centrale)

Retourne UNIQUEMENT ce JSON :
{
  "slug": "schreiben",
  "name": "Schriftlicher Ausdruck",
  "time_limit_minutes": 30,
  "max_score": 45,
  "raw_items": 1,
  "teile": [
    {
      "teil_number": 1,
      "name": "E-Mail schreiben",
      "format_type": "free_text",
      "instructions": "Sie haben von einer Freundin/einem Freund folgende E-Mail erhalten. Antworten Sie auf die E-Mail. Schreiben Sie etwas zu allen vier Punkten: ...",
      "time_minutes": 30,
      "max_score": 45,
      "text_type": "E-Mail",
      "word_count_target": 80,
      "stimulus_email": {
        "sender": "Marianne",
        "subject": "...",
        "body": "...(email reçu ~80 mots avec une question générale qui génère 4 points de réponse naturels)..."
      },
      "scenario": "Antworten Sie auf die E-Mail Ihrer Freundin/Ihres Freundes.",
      "prompts": [
        "...(point 1 à traiter)...",
        "...(point 2 à traiter)...",
        "...(point 3 à traiter)...",
        "...(point 4 à traiter)..."
      ],
      "register": "informell",
      "scoring_criteria": {
        "Aufgabenbewältigung": {
          "A": "Alle vier Leitpunkte werden inhaltlich angemessen bearbeitet.",
          "B": "Drei Leitpunkte werden inhaltlich angemessen bearbeitet.",
          "C": "Zwei Leitpunkte werden inhaltlich angemessen bearbeitet.",
          "D": "Nur ein oder kein Leitpunkt wird inhaltlich angemessen bearbeitet."
        },
        "Kommunikative_Gestaltung": {
          "description": "Wortschatz, Kohäsion, Register, Textlogik"
        },
        "Formale_Richtigkeit": {
          "description": "Grammatik, Morphologie, Syntax, Orthografie"
        }
      },
      "musterlösung": "...(exemple de réponse correcte ~80 mots)..."
    }
  ]
}"""


# ─── Prompt Mündlicher Ausdruck ───────────────────────────────────────────────

def prompt_sprechen_telc() -> str:
    return """Génère le module MÜNDLICHER AUSDRUCK (TELC Deutsch B1).

TELC Mündlicher Ausdruck — 3 Teile (~15 min pour 2 candidats)

Teil 1 — Einander kennenlernen (~3 min)
- Liste de topics de conversation pour que les 2 candidats se présentent
- Pas de planification, juste des sujets de discussion

Teil 2 — Über ein Thema sprechen (~6 min)
- Candidat A reçoit une opinion sur un thème
- Candidat B reçoit une opinion CONTRAIRE sur le même thème
- Ils présentent leur opinion puis discutent ensemble

Teil 3 — Gemeinsam etwas planen (~6 min)
- Les 2 candidats doivent planifier quelque chose ensemble
- Liste de points à aborder

Scoring total : 75 points
- Teil 1 : max 15 pts (Ausdrucksfähigkeit 4+Aufgabenbewältigung 4+Formale Richtigkeit 4+Aussprache 3)
- Teil 2+3 : max 30 pts chacun (×2 critères)

Retourne UNIQUEMENT ce JSON :
{
  "slug": "sprechen",
  "name": "Mündlicher Ausdruck",
  "time_limit_minutes": 15,
  "max_score": 75,
  "preparation_minutes": 20,
  "raw_items": 3,
  "teile": [
    {
      "teil_number": 1,
      "name": "Einander kennenlernen",
      "format_type": "oral_kennenlernen",
      "instructions": "Unterhalten Sie sich mit Ihrer Partnerin bzw. Ihrem Partner über folgende Themen:",
      "time_minutes": 3,
      "max_score": 15,
      "topics": [
        "Name",
        "Woher sie oder er kommt",
        "Wie sie oder er wohnt",
        "Familie",
        "Wo sie oder er Deutsch gelernt hat",
        "Was sie oder er macht (Schule, Studium, Beruf)",
        "Hobbys und Freizeit"
      ]
    },
    {
      "teil_number": 2,
      "name": "Über ein Thema sprechen",
      "format_type": "oral_thema",
      "instructions": "Sie haben in einer Zeitschrift etwas zum Thema gelesen. Berichten Sie Ihrer Gesprächspartnerin/Ihrem Gesprächspartner darüber. Unterhalten Sie sich dann über das Thema.",
      "time_minutes": 6,
      "max_score": 30,
      "topic": "...(thème de société B1 : Gruppenreisen / Homeoffice / Soziale Medien / ...)...",
      "opinion_a": {
        "person": "...(nom, âge, profession)...",
        "text": "...(opinion PRO ~50 mots en allemand)..."
      },
      "opinion_b": {
        "person": "...(nom, âge, profession)...",
        "text": "...(opinion CONTRE ~50 mots en allemand)..."
      }
    },
    {
      "teil_number": 3,
      "name": "Gemeinsam etwas planen",
      "format_type": "oral_interaction",
      "instructions": "Sie haben zwei Wochen Urlaub gemacht und möchten vor dem Ende eine Abschiedsfeier organisieren. Planen Sie gemeinsam mit Ihrem Partner.",
      "time_minutes": 6,
      "max_score": 30,
      "scenario": "...(scénario de planification commune)...",
      "prompts": [
        "Wann?",
        "Wo?",
        "Essen und Getränke",
        "Wer bezahlt wofür?",
        "Musik / Unterhaltung?"
      ]
    }
  ]
}"""


# ─── Gemini caller ────────────────────────────────────────────────────────────

def call_gemini(client: genai.Client, prompt: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=16000,
        ),
        contents=prompt
    )
    raw = response.text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


# ─── Génération modules ───────────────────────────────────────────────────────

def generate_leseverstehen(client: genai.Client) -> dict:
    print("  📖 Génération LESEVERSTEHEN (3 Teile)...")
    teile = []
    for i, (name, prompt_fn) in enumerate([
        ("Teil 1 Globalverstehen", prompt_lesen_teil1),
        ("Teil 2 Detailverstehen", prompt_lesen_teil2),
        ("Teil 3 Selektives Verstehen", prompt_lesen_teil3),
    ], 1):
        print(f"     → {name}...")
        try:
            teil = call_gemini(client, prompt_fn())
            teile.append(teil)
            print(f"        ✅ OK")
        except Exception as e:
            print(f"        ❌ Erreur : {e}")
            teile.append({"teil_number": i, "error": str(e)})

    return {
        "slug": "lesen",
        "name": "Leseverstehen",
        "time_limit_minutes": 90,
        "max_score": 75,
        "raw_items": 20,
        "note": "Inclut aussi Sprachbausteine dans le même bloc de 90 min",
        "teile": teile
    }


def generate_sprachbausteine(client: genai.Client) -> dict:
    print("  📝 Génération SPRACHBAUSTEINE (2 Teile)...")
    teile = []
    for i, (name, prompt_fn) in enumerate([
        ("Teil 1 Grammatik", prompt_sprachbausteine_teil1),
        ("Teil 2 Lexik", prompt_sprachbausteine_teil2),
    ], 1):
        print(f"     → {name}...")
        try:
            teil = call_gemini(client, prompt_fn())
            teile.append(teil)
            print(f"        ✅ OK")
        except Exception as e:
            print(f"        ❌ Erreur : {e}")
            teile.append({"teil_number": i, "error": str(e)})

    return {
        "slug": "sprachbausteine",
        "name": "Sprachbausteine",
        "time_limit_minutes": 0,
        "max_score": 30,
        "raw_items": 20,
        "note": "Intégré dans le bloc Leseverstehen (90 min partagées)",
        "teile": teile
    }


def generate_horverstehen(client: genai.Client) -> dict:
    print("  🎧 Génération HÖRVERSTEHEN (3 Teile)...")
    teile = []
    for i, (name, prompt_fn) in enumerate([
        ("Teil 1 Globalverstehen (1 écoute !)", prompt_horen_teil1_telc),
        ("Teil 2 Detailverstehen (2 écoutes)", prompt_horen_teil2_telc),
        ("Teil 3 Selektives Verstehen (2 écoutes)", prompt_horen_teil3_telc),
    ], 1):
        print(f"     → {name}...")
        try:
            teil = call_gemini(client, prompt_fn())
            teile.append(teil)
            print(f"        ✅ OK")
        except Exception as e:
            print(f"        ❌ Erreur : {e}")
            teile.append({"teil_number": i, "error": str(e)})

    return {
        "slug": "horen",
        "name": "Hörverstehen",
        "time_limit_minutes": 30,
        "max_score": 75,
        "raw_items": 20,
        "teile": teile
    }


def generate_schreiben(client: genai.Client) -> dict:
    print("  ✍️  Génération SCHRIFTLICHER AUSDRUCK...")
    try:
        data = call_gemini(client, prompt_schreiben_telc())
        print("     ✅ OK")
        return data
    except Exception as e:
        print(f"     ❌ Erreur : {e}")
        return {"slug": "schreiben", "error": str(e)}


def generate_sprechen(client: genai.Client) -> dict:
    print("  🎤 Génération MÜNDLICHER AUSDRUCK...")
    try:
        data = call_gemini(client, prompt_sprechen_telc())
        print("     ✅ OK")
        return data
    except Exception as e:
        print(f"     ❌ Erreur : {e}")
        return {"slug": "sprechen", "error": str(e)}


# ─── Audio TTS ────────────────────────────────────────────────────────────────

def extract_horen_transcriptions(horen: dict) -> list[dict]:
    scripts = []
    for teil in horen.get("teile", []):
        t = teil["teil_number"]
        max_plays = teil.get("max_plays", 2)

        if "audios" in teil:
            # Teil 1 et Teil 3 : multi-audios
            for audio in teil.get("audios", []):
                n = audio.get("audio_number", "?")
                text = audio.get("transcription", "")
                if text:
                    scripts.append({
                        "teil": t,
                        "label": f"teil{t}_audio{n}",
                        "text": text,
                        "max_plays": max_plays,
                        "audio_type": audio.get("audio_type", "")
                    })
        elif "transcription" in teil:
            # Teil 2 : 1 seul audio long
            text = teil.get("transcription", "")
            if text:
                scripts.append({
                    "teil": t,
                    "label": f"teil{t}",
                    "text": text,
                    "max_plays": max_plays,
                    "context": teil.get("context", "")
                })
    return scripts


async def text_to_audio(text: str, output_path: str, voice: str = "de-DE-KatjaNeural"):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def generate_all_audio(scripts: list[dict], audio_dir: Path) -> dict:
    audio_dir.mkdir(parents=True, exist_ok=True)
    mapping = {}
    for item in scripts:
        label = item["label"]
        filename = f"horen_{label}.mp3"
        filepath = audio_dir / filename
        print(f"  🔊 TTS → {filename} (max {item['max_plays']}x écoute)")
        try:
            await text_to_audio(item["text"], str(filepath))
            mapping[label] = str(filepath)
            print(f"     ✅ OK ({filepath.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"     ⚠  Erreur TTS : {e}")
            mapping[label] = None
    return mapping


def attach_audio_refs(horen: dict, audio_mapping: dict) -> dict:
    for teil in horen.get("teile", []):
        t = teil["teil_number"]
        if "audios" in teil:
            for audio in teil.get("audios", []):
                n = audio.get("audio_number", "?")
                label = f"teil{t}_audio{n}"
                audio["audio_file"] = audio_mapping.get(label)
        elif "transcription" in teil:
            label = f"teil{t}"
            teil["audio_file"] = audio_mapping.get(label)
    return horen


# ─── Assemblage ───────────────────────────────────────────────────────────────

def build_full_exam(modules: list[dict], timestamp: str) -> dict:
    return {
        "exam_id": f"telc_b1_{timestamp}",
        "name": "TELC Deutsch B1 / Zertifikat Deutsch",
        "slug": "telc_b1",
        "provider": "telc",
        "cefr_code": "B1",
        "version": "generated",
        "generated_at": timestamp,
        "scoring_model": "per_module_weighted",
        "pass_threshold": 60,
        "scoring_details": {
            "written_total": 225,
            "oral_total": 75,
            "grand_total": 300,
            "written_pass": 135,
            "oral_pass": 45,
            "modules": {
                "Leseverstehen": "75 pts (25%)",
                "Sprachbausteine": "30 pts (10%)",
                "Hoerverstehen": "75 pts (25%)",
                "Schriftlicher Ausdruck": "45 pts (15%)",
                "Muendlicher Ausdruck": "75 pts (25%)"
            }
        },
        "modules": modules
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main_async(api_key: str, output_dir: Path, no_audio: bool):
    client = genai.Client(api_key=api_key)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_dir = output_dir / f"audio_telc_{timestamp}"

    print("\n🇩🇪 Génération TELC Deutsch B1 / Zertifikat Deutsch")
    print("=" * 55)

    generated_modules = []

    # 1. Leseverstehen
    lesen = generate_leseverstehen(client)
    generated_modules.append(lesen)

    # 2. Sprachbausteine (module unique TELC)
    sprachbausteine = generate_sprachbausteine(client)
    generated_modules.append(sprachbausteine)

    # 3. Hörverstehen
    horen = generate_horverstehen(client)
    generated_modules.append(horen)

    # 4. Schriftlicher Ausdruck
    schreiben = generate_schreiben(client)
    generated_modules.append(schreiben)

    # 5. Mündlicher Ausdruck
    sprechen = generate_sprechen(client)
    generated_modules.append(sprechen)

    # TTS pour Hörverstehen
    if not no_audio:
        print("\n🔊 Génération audio (edge-tts)...")
        horen_data = next((m for m in generated_modules if m.get("slug") == "horen"), None)
        if horen_data:
            scripts = extract_horen_transcriptions(horen_data)
            print(f"   {len(scripts)} transcriptions trouvées")
            for s in scripts:
                plays = s.get('max_plays', 2)
                note = "⚠ UNE SEULE ÉCOUTE" if plays == 1 else f"{plays} écoutes"
                print(f"   → {s['label']} [{note}]")
            audio_mapping = await generate_all_audio(scripts, audio_dir)
            horen_data = attach_audio_refs(horen_data, audio_mapping)
            for i, m in enumerate(generated_modules):
                if m.get("slug") == "horen":
                    generated_modules[i] = horen_data
    else:
        print("\n⏭  Audio ignoré (--no-audio)")

    # Export JSON final
    exam = build_full_exam(generated_modules, timestamp)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"telc_b1_{timestamp}.json"
    json_path.write_text(json.dumps(exam, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ Examen TELC B1 généré → {json_path}")
    if not no_audio:
        print(f"✅ Fichiers audio → {audio_dir}/")
    print("\n📊 Résumé scoring :")
    print("   Leseverstehen     : 75 pts (25%)")
    print("   Sprachbausteine   : 30 pts (10%)")
    print("   Hörverstehen      : 75 pts (25%)")
    print("   Schriftl. Ausdr.  : 45 pts (15%)")
    print("   Mündl. Ausdr.     : 75 pts (25%)")
    print("   Total             : 300 pts")
    print("   Seuil écrit       : 135/225 (60%)")
    print("   Seuil oral        : 45/75  (60%)")

    return str(json_path)


def main():
    parser = argparse.ArgumentParser(
        description="Générateur d'examen TELC Deutsch B1 complet"
    )
    parser.add_argument("--api-key", required=True, help="Clé API Gemini")
    parser.add_argument("--output", default="./output", help="Dossier de sortie")
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Ne pas générer les fichiers audio (utile pour tester)"
    )
    args = parser.parse_args()

    asyncio.run(main_async(
        api_key=args.api_key,
        output_dir=Path(args.output),
        no_audio=args.no_audio
    ))


if __name__ == "__main__":
    main()
    
#uv run python scripts/generate_telc_b1.py --api-key AIzaSyDeXASIB2de6_U5eyZY8eOmIN_LDDpznFw