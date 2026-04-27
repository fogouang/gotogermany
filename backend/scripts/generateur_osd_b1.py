"""
Générateur d'examen Goethe-ÖSD B1 complet
==========================================
- Gemini API  → génération du contenu (4 modules)
- edge-tts    → audio pour Hören (gratuit, voix allemande)
- Sortie      → examen_YYYYMMDD_HHMMSS.json + audio/horen_teil_X.mp3

Usage:
    python generate_exam.py --api-key VOTRE_CLE_GEMINI
    python generate_exam.py --api-key VOTRE_CLE_GEMINI --no-audio
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

# ─── Prompts par module ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es un expert certifié en création d'examens de langue allemande Goethe-ÖSD Zertifikat B1.
Tu génères des examens authentiques, calibrés CECRL B1, avec des textes variés sur des sujets quotidiens.
Réponds UNIQUEMENT en JSON valide. Pas de texte avant ni après. Pas de balises markdown.
Tous les textes, questions et réponses sont en ALLEMAND.
"""

def prompt_lesen() -> str:
    return """Génère le module LESEN complet d'un examen Goethe-ÖSD B1.

Structure EXACTE (5 Teile) :

Teil 1 — Richtig/Falsch
- 1 texte blog/email personnel (~200 mots, sujet quotidien)
- 6 questions Richtig/Falsch (numéros 1-6)

Teil 2 — QCM a/b/c
- 2 textes de presse (~150 mots chacun, sujets différents)
- 3 questions QCM par texte (numéros 7-12)

Teil 3 — Zuordnung (situations → annonces)
- 10 annonces courtes (a-j, ressources pour apprendre l'allemand ou services)
- 7 situations (numéros 13-19), dont 1 sans annonce correspondante (réponse = "0")

Teil 4 — Ja/Nein (pour un Verbot ou une opinion)
- 7 commentaires de lecteurs (~50 mots chacun) sur un sujet de société
- Pour chaque commentaire : est la personne POUR (ja) ou CONTRE (nein) ?
- (numéros 20-26)

Teil 5 — QCM a/b/c
- 1 texte officiel (règlement, mode d'emploi, ~150 mots)
- 4 questions QCM (numéros 27-30)

Retourne ce JSON :
{
  "slug": "lesen",
  "name": "Lesen",
  "time_limit_minutes": 65,
  "max_score": 100,
  "raw_items": 30,
  "teile": [
    {
      "teil_number": 1,
      "name": "...",
      "format_type": "richtig_falsch",
      "instructions": "...",
      "time_minutes": 10,
      "max_score": 6,
      "stimulus_text": "...",
      "questions": [
        {"number": 1, "statement": "...", "answer": "richtig|falsch"}
      ]
    },
    {
      "teil_number": 2,
      "format_type": "qcm_abc",
      "instructions": "...",
      "time_minutes": 20,
      "max_score": 6,
      "texts": [
        {
          "stimulus_text": "...",
          "questions": [
            {"number": 7, "stem": "...", "options": {"a": "...", "b": "...", "c": "..."}, "answer": "a|b|c"}
          ]
        }
      ]
    },
    {
      "teil_number": 3,
      "format_type": "matching",
      "instructions": "...",
      "time_minutes": 10,
      "max_score": 7,
      "anzeigen": {"a": "...", "b": "...", "c": "...", "d": "...", "e": "...", "f": "...", "g": "...", "h": "...", "i": "...", "j": "..."},
      "questions": [
        {"number": 13, "situation": "...", "answer": "a-j|0"}
      ]
    },
    {
      "teil_number": 4,
      "format_type": "ja_nein",
      "instructions": "...",
      "time_minutes": 15,
      "max_score": 7,
      "topic": "...",
      "questions": [
        {"number": 20, "author": "...", "text": "...", "answer": "ja|nein"}
      ]
    },
    {
      "teil_number": 5,
      "format_type": "qcm_abc",
      "instructions": "...",
      "time_minutes": 10,
      "max_score": 4,
      "stimulus_text": "...",
      "questions": [
        {"number": 27, "stem": "...", "options": {"a": "...", "b": "...", "c": "..."}, "answer": "a|b|c"}
      ]
    }
  ]
}"""

def prompt_horen() -> str:
    return """Génère le module HÖREN complet d'un examen Goethe-ÖSD B1.

Structure EXACTE (4 Teile) :

Teil 1 — 5 courts enregistrements (répondeur, annonce radio, etc.)
- Chaque enregistrement : 1 question Richtig/Falsch + 1 question QCM a/b/c
- Total 10 questions (numéros 1-10)
- Fournis la TRANSCRIPTION complète de chaque enregistrement (~60 mots chacun)

Teil 2 — 1 enregistrement long (visite guidée, conférence, ~250 mots)
- 5 questions QCM a/b/c (numéros 11-15)
- Fournis la TRANSCRIPTION complète

Teil 3 — 1 conversation entre deux personnes (~300 mots)
- 7 questions Richtig/Falsch (numéros 16-22)
- Fournis la TRANSCRIPTION complète

Teil 4 — 1 discussion radio (modérateur + 2 invités, ~400 mots)
- 8 questions Zuordnung : qui dit quoi ? (a=Moderator, b=Gast1, c=Gast2)
- (numéros 23-30)
- Fournis la TRANSCRIPTION complète avec indication du locuteur

Retourne ce JSON :
{
  "slug": "horen",
  "name": "Hören",
  "time_limit_minutes": 40,
  "max_score": 100,
  "raw_items": 30,
  "teile": [
    {
      "teil_number": 1,
      "format_type": "mixed_richtig_falsch_qcm",
      "instructions": "...",
      "time_minutes": 10,
      "max_score": 10,
      "audios": [
        {
          "audio_number": 1,
          "audio_type": "Anrufbeantworter|Radio|Bahnhof|...",
          "transcription": "...",
          "questions": [
            {"number": 1, "type": "richtig_falsch", "statement": "...", "answer": "richtig|falsch"},
            {"number": 2, "type": "qcm_abc", "stem": "...", "options": {"a": "...", "b": "...", "c": "..."}, "answer": "a|b|c"}
          ]
        }
      ]
    },
    {
      "teil_number": 2,
      "format_type": "qcm_abc",
      "instructions": "...",
      "time_minutes": 8,
      "max_score": 5,
      "transcription": "...",
      "context": "...",
      "questions": [
        {"number": 11, "stem": "...", "options": {"a": "...", "b": "...", "c": "..."}, "answer": "a|b|c"}
      ]
    },
    {
      "teil_number": 3,
      "format_type": "richtig_falsch",
      "instructions": "...",
      "time_minutes": 8,
      "max_score": 7,
      "transcription": "...",
      "context": "...",
      "questions": [
        {"number": 16, "statement": "...", "answer": "richtig|falsch"}
      ]
    },
    {
      "teil_number": 4,
      "format_type": "zuordnung_speaker",
      "instructions": "...",
      "time_minutes": 10,
      "max_score": 8,
      "speakers": {"a": "Moderator", "b": "...", "c": "..."},
      "transcription": "...",
      "questions": [
        {"number": 23, "statement": "...", "answer": "a|b|c"}
      ]
    }
  ]
}"""

def prompt_schreiben() -> str:
    return """Génère le module SCHREIBEN complet d'un examen Goethe-ÖSD B1.

Structure EXACTE (3 Aufgaben) :

Aufgabe 1 — E-Mail personnelle (~80 mots)
- Scénario + 3 points à traiter obligatoirement
- Scoring : Erfüllung(10) + Kohärenz(10) + Wortschatz(10) + Strukturen(10) = 40 pts

Aufgabe 2 — Diskussionsbeitrag/Meinungsäußerung (~80 mots)  
- Un commentaire stimulus d'un autre utilisateur à réagir
- Scoring : Erfüllung(10) + Kohärenz(10) + Wortschatz(10) + Strukturen(10) = 40 pts

Aufgabe 3 — E-Mail formelle courte (~40 mots)
- Scénario formel (excuse, demande, etc.)
- Scoring : Erfüllung(4) + Kohärenz(4) + Wortschatz(6) + Strukturen(6) = 20 pts

Retourne ce JSON :
{
  "slug": "schreiben",
  "name": "Schreiben",
  "time_limit_minutes": 60,
  "max_score": 100,
  "raw_items": 3,
  "teile": [
    {
      "teil_number": 1,
      "name": "Persönliche E-Mail",
      "format_type": "free_text",
      "instructions": "...",
      "time_minutes": 20,
      "max_score": 40,
      "text_type": "E-Mail",
      "word_count_target": 80,
      "scenario": "...",
      "prompts": ["...", "...", "..."],
      "scoring_criteria": {
        "Erfüllung": {"max": 10, "description": "..."},
        "Kohärenz": {"max": 10, "description": "..."},
        "Wortschatz": {"max": 10, "description": "..."},
        "Strukturen": {"max": 10, "description": "..."}
      },
      "musterlösung": "..."
    },
    {
      "teil_number": 2,
      "name": "Meinungsäußerung",
      "format_type": "free_text",
      "instructions": "...",
      "time_minutes": 25,
      "max_score": 40,
      "text_type": "Diskussionsbeitrag",
      "word_count_target": 80,
      "stimulus": "...",
      "stimulus_author": "...",
      "task": "...",
      "scoring_criteria": {
        "Erfüllung": {"max": 10, "description": "..."},
        "Kohärenz": {"max": 10, "description": "..."},
        "Wortschatz": {"max": 10, "description": "..."},
        "Strukturen": {"max": 10, "description": "..."}
      },
      "musterlösung": "..."
    },
    {
      "teil_number": 3,
      "name": "Formelle E-Mail",
      "format_type": "free_text",
      "instructions": "...",
      "time_minutes": 15,
      "max_score": 20,
      "text_type": "E-Mail",
      "register": "formell",
      "word_count_target": 40,
      "scenario": "...",
      "scoring_criteria": {
        "Erfüllung": {"max": 4, "description": "..."},
        "Kohärenz": {"max": 4, "description": "..."},
        "Wortschatz": {"max": 6, "description": "..."},
        "Strukturen": {"max": 6, "description": "..."}
      },
      "musterlösung": "..."
    }
  ]
}"""

def prompt_sprechen() -> str:
    return """Génère le module SPRECHEN complet d'un examen Goethe-ÖSD B1.

Structure EXACTE (3 Teile) :

Teil 1 — Gemeinsam etwas planen (~3 min, 2 candidats)
- Scénario de planification commune
- 4-5 points de discussion obligatoires
- Max 32 pts

Teil 2 — Thema präsentieren (~3 min, monologue)
- 2 thèmes au choix (Thema 1 ou Thema 2)
- Chaque thème : 5 diapositives avec titres
- Structure : Einleitung → Erfahrung → Heimatland → Vor-/Nachteile → Abschluss
- Max 36 pts

Teil 3 — Feedback + Frage stellen (~2 min)
- Réagir à la présentation du partenaire
- Poser une question, répondre aux questions
- Max 32 pts

Retourne ce JSON :
{
  "slug": "sprechen",
  "name": "Sprechen",
  "time_limit_minutes": 15,
  "max_score": 100,
  "raw_items": 3,
  "preparation_minutes": 15,
  "teile": [
    {
      "teil_number": 1,
      "name": "Gemeinsam etwas planen",
      "format_type": "oral_interaction",
      "instructions": "...",
      "time_minutes": 3,
      "max_score": 32,
      "scenario": "...",
      "prompts": ["...", "...", "...", "..."],
      "scoring_criteria": {
        "Erfüllung": {"Sprachfunktionen": 8, "Inhalt": 8},
        "Wortschatz": 8,
        "Strukturen": 8
      }
    },
    {
      "teil_number": 2,
      "name": "Ein Thema präsentieren",
      "format_type": "oral_monologue",
      "instructions": "...",
      "time_minutes": 3,
      "max_score": 36,
      "themes": {
        "thema1": {
          "title": "...",
          "slides": ["Folie 1: ...", "Folie 2: ...", "Folie 3: ...", "Folie 4: ...", "Folie 5: ..."]
        },
        "thema2": {
          "title": "...",
          "slides": ["Folie 1: ...", "Folie 2: ...", "Folie 3: ...", "Folie 4: ...", "Folie 5: ..."]
        }
      },
      "scoring_criteria": {
        "Erfüllung": {"Vollständigkeit": 12},
        "Kohärenz": 12,
        "Wortschatz": 6,
        "Strukturen": 6
      }
    },
    {
      "teil_number": 3,
      "name": "Über ein Thema sprechen",
      "format_type": "oral_feedback",
      "instructions": "...",
      "time_minutes": 2,
      "max_score": 32,
      "tasks": ["...", "...", "...", "..."],
      "scoring_criteria": {
        "Erfüllung": {"Sprachfunktionen": 8, "Inhalt": 8},
        "Aussprache": 16
      }
    }
  ]
}"""


# ─── Génération Gemini ────────────────────────────────────────────────────────

def call_gemini(client: genai.Client, prompt: str) -> dict:
    """Appel Gemini avec nettoyage JSON."""
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


def prompt_lesen_teil(teil_number: int) -> str:
    """Génère un prompt pour un seul Teil du Lesen."""
    specs = {
        1: ("richtig_falsch", "1 texte blog/email personnel (~200 mots), 6 questions Richtig/Falsch (numéros 1-6)",
            '{"teil_number":1,"name":"...","format_type":"richtig_falsch","instructions":"...","time_minutes":10,"max_score":6,"stimulus_text":"...","questions":[{"number":1,"statement":"...","answer":"richtig"}]}'),
        2: ("qcm_abc", "2 textes de presse (~150 mots chacun), 3 questions QCM a/b/c par texte (numéros 7-12)",
            '{"teil_number":2,"format_type":"qcm_abc","instructions":"...","time_minutes":20,"max_score":6,"texts":[{"stimulus_text":"...","questions":[{"number":7,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"b"}]}]}'),
        3: ("matching", "10 annonces (a-j), 7 situations (numéros 13-19), 1 sans correspondance (réponse=0)",
            '{"teil_number":3,"format_type":"matching","instructions":"...","time_minutes":10,"max_score":7,"anzeigen":{"a":"...","b":"...","c":"...","d":"...","e":"...","f":"...","g":"...","h":"...","i":"...","j":"..."},"questions":[{"number":13,"situation":"...","answer":"d"}]}'),
        4: ("ja_nein", "7 commentaires de lecteurs (~50 mots) sur un sujet de société, Ja/Nein (numéros 20-26)",
            '{"teil_number":4,"format_type":"ja_nein","instructions":"...","time_minutes":15,"max_score":7,"topic":"...","questions":[{"number":20,"author":"...","text":"...","answer":"ja"}]}'),
        5: ("qcm_abc", "1 texte officiel (règlement ~150 mots), 4 questions QCM (numéros 27-30)",
            '{"teil_number":5,"format_type":"qcm_abc","instructions":"...","time_minutes":10,"max_score":4,"stimulus_text":"...","questions":[{"number":27,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"c"}]}'),
    }
    fmt, desc, example = specs[teil_number]
    return f"""Génère le Teil {teil_number} du module LESEN (Goethe-ÖSD B1).
Description : {desc}
Format : {fmt}
Tous les textes et questions en ALLEMAND, niveau B1 CECRL.
Retourne UNIQUEMENT ce JSON (complète tous les "...") :
{example}"""


def prompt_horen_teil1_batch(batch: int) -> str:
    """Hören Teil 1 en 2 batches : batch=1 → audios 1-3, batch=2 → audios 4-5."""
    if batch == 1:
        template = '{"audios":[{"audio_number":1,"audio_type":"Anrufbeantworter","transcription":"...~60 mots...","questions":[{"number":1,"type":"richtig_falsch","statement":"...","answer":"richtig"},{"number":2,"type":"qcm_abc","stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"b"}]},{"audio_number":2,"audio_type":"Anrufbeantworter","transcription":"...~60 mots...","questions":[{"number":3,"type":"richtig_falsch","statement":"...","answer":"falsch"},{"number":4,"type":"qcm_abc","stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"a"}]},{"audio_number":3,"audio_type":"Radio Durchsage","transcription":"...~60 mots...","questions":[{"number":5,"type":"richtig_falsch","statement":"...","answer":"richtig"},{"number":6,"type":"qcm_abc","stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"c"}]}]}'
        return f"""Génère les audios 1, 2 et 3 du Teil 1 Hören (Goethe-ÖSD B1).
Audio 1 = message Anrufbeantworter, Audio 2 = message Anrufbeantworter, Audio 3 = annonce Radio.
Chaque transcription ~60 mots, en ALLEMAND naturel B1.
Retourne UNIQUEMENT ce JSON (remplace tous les "...") :
{template}"""
    else:
        template = '{"audios":[{"audio_number":4,"audio_type":"Bahnhof Durchsage","transcription":"...~60 mots...","questions":[{"number":7,"type":"richtig_falsch","statement":"...","answer":"falsch"},{"number":8,"type":"qcm_abc","stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"b"}]},{"audio_number":5,"audio_type":"Wetterbericht","transcription":"...~60 mots...","questions":[{"number":9,"type":"richtig_falsch","statement":"...","answer":"richtig"},{"number":10,"type":"qcm_abc","stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"a"}]}]}'
        return f"""Génère les audios 4 et 5 du Teil 1 Hören (Goethe-ÖSD B1).
Audio 4 = annonce Bahnhof, Audio 5 = Wetterbericht.
Chaque transcription ~60 mots, en ALLEMAND naturel B1.
Retourne UNIQUEMENT ce JSON (remplace tous les "...") :
{template}"""


def prompt_horen_teil(teil_number: int) -> str:
    """Génère un prompt pour Hören Teil 2, 3 ou 4."""
    specs = {
        2: '{"teil_number":2,"format_type":"qcm_abc","instructions":"...","time_minutes":8,"max_score":5,"context":"Führung durch ein Museum","transcription":"...texte ~250 mots...","questions":[{"number":11,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"c"},{"number":12,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"a"},{"number":13,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"b"},{"number":14,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"c"},{"number":15,"stem":"...","options":{"a":"...","b":"...","c":"..."},"answer":"a"}]}',
        3: '{"teil_number":3,"format_type":"richtig_falsch","instructions":"...","time_minutes":8,"max_score":7,"context":"Gespräch an einer Bushaltestelle","transcription":"...conversation ~300 mots...","questions":[{"number":16,"statement":"...","answer":"richtig"},{"number":17,"statement":"...","answer":"falsch"},{"number":18,"statement":"...","answer":"richtig"},{"number":19,"statement":"...","answer":"falsch"},{"number":20,"statement":"...","answer":"richtig"},{"number":21,"statement":"...","answer":"falsch"},{"number":22,"statement":"...","answer":"richtig"}]}',
        4: '{"teil_number":4,"format_type":"zuordnung_speaker","instructions":"...","time_minutes":10,"max_score":8,"speakers":{"a":"Moderator","b":"Gast 1 Name","c":"Gast 2 Name"},"transcription":"...discussion ~400 mots avec [Moderator]:, [Gast1]:, [Gast2]:...","questions":[{"number":23,"statement":"...","answer":"b"},{"number":24,"statement":"...","answer":"c"},{"number":25,"statement":"...","answer":"a"},{"number":26,"statement":"...","answer":"b"},{"number":27,"statement":"...","answer":"c"},{"number":28,"statement":"...","answer":"b"},{"number":29,"statement":"...","answer":"a"},{"number":30,"statement":"...","answer":"c"}]}',
    }
    template = specs[teil_number]
    return f"""Génère le Teil {teil_number} du module HÖREN (Goethe-ÖSD B1).
Tous les textes et transcriptions en ALLEMAND naturel B1.
Retourne UNIQUEMENT ce JSON (remplace tous les "...") :
{template}"""


def generate_module_by_teil(client: genai.Client, module_name: str) -> dict:
    """Génère Lesen ou Hören Teil par Teil."""
    print(f"  🤖 Génération {module_name} (Teil par Teil)...")
    teile = []

    if module_name == "Lesen":
        slug, time_min, raw = "lesen", 65, 30
        for i in range(1, 6):
            print(f"     → Teil {i}/5...")
            try:
                teil_data = call_gemini(client, prompt_lesen_teil(i))
                teile.append(teil_data)
                print(f"        ✅ OK")
            except Exception as e:
                print(f"        ❌ Erreur : {e}")
                teile.append({"teil_number": i, "error": str(e)})
    else:
        slug, time_min, raw = "horen", 40, 30
        # Teil 1 : 2 batches fusionnés
        print(f"     → Teil 1/4 (batch 1/2)...")
        try:
            b1 = call_gemini(client, prompt_horen_teil1_batch(1))
            print(f"        ✅ batch 1 OK")
        except Exception as e:
            print(f"        ❌ batch 1 : {e}")
            b1 = {"audios": []}
        print(f"     → Teil 1/4 (batch 2/2)...")
        try:
            b2 = call_gemini(client, prompt_horen_teil1_batch(2))
            print(f"        ✅ batch 2 OK")
        except Exception as e:
            print(f"        ❌ batch 2 : {e}")
            b2 = {"audios": []}
        teile.append({
            "teil_number": 1,
            "format_type": "mixed_richtig_falsch_qcm",
            "instructions": "Sie hören fünf kurze Texte. Jeden Text hören Sie zweimal.",
            "time_minutes": 10,
            "max_score": 10,
            "audios": b1.get("audios", []) + b2.get("audios", [])
        })
        # Teile 2, 3, 4
        for i in range(2, 5):
            print(f"     → Teil {i}/4...")
            try:
                teil_data = call_gemini(client, prompt_horen_teil(i))
                teile.append(teil_data)
                print(f"        ✅ OK")
            except Exception as e:
                print(f"        ❌ Erreur : {e}")
                teile.append({"teil_number": i, "error": str(e)})

    return {
        "slug": slug,
        "name": module_name,
        "time_limit_minutes": time_min,
        "max_score": 100,
        "raw_items": raw,
        "teile": teile
    }


def generate_module(client: genai.Client, module_name: str, prompt: str) -> dict:
    print(f"  🤖 Génération {module_name}...")
    return call_gemini(client, prompt)


# ─── Extraction des transcriptions Hören ─────────────────────────────────────

def extract_horen_transcriptions(horen: dict) -> list[dict]:
    """
    Extrait toutes les transcriptions du module Hören.
    Retourne une liste de {teil, label, text} pour le TTS.
    """
    scripts = []
    for teil in horen.get("teile", []):
        t = teil["teil_number"]
        if t == 1:
            for audio in teil.get("audios", []):
                n = audio.get("audio_number", "?")
                text = audio.get("transcription", "")
                if text:
                    scripts.append({
                        "teil": t,
                        "label": f"teil1_audio{n}",
                        "text": text,
                        "audio_type": audio.get("audio_type", "")
                    })
        else:
            text = teil.get("transcription", "")
            if text:
                scripts.append({
                    "teil": t,
                    "label": f"teil{t}",
                    "text": text,
                    "context": teil.get("context", "")
                })
    return scripts


# ─── TTS avec edge-tts (gratuit) ──────────────────────────────────────────────

async def text_to_audio(text: str, output_path: str, voice: str = "de-DE-KatjaNeural"):
    """Convertit du texte en audio MP3 via edge-tts (gratuit, pas de limite)."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def generate_all_audio(scripts: list[dict], audio_dir: Path) -> dict:
    """Génère tous les fichiers audio et retourne un mapping label → fichier."""
    audio_dir.mkdir(parents=True, exist_ok=True)
    mapping = {}
    for item in scripts:
        label = item["label"]
        filename = f"horen_{label}.mp3"
        filepath = audio_dir / filename
        print(f"  🔊 TTS → {filename}")
        try:
            await text_to_audio(item["text"], str(filepath))
            mapping[label] = str(filepath)
            print(f"     ✅ OK ({filepath.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"     ⚠  Erreur TTS : {e}")
            mapping[label] = None
    return mapping


# ─── Assemblage final ─────────────────────────────────────────────────────────

def attach_audio_refs(horen: dict, audio_mapping: dict) -> dict:
    """Attache les références audio dans le JSON Hören."""
    for teil in horen.get("teile", []):
        t = teil["teil_number"]
        if t == 1:
            for audio in teil.get("audios", []):
                n = audio.get("audio_number", "?")
                label = f"teil1_audio{n}"
                audio["audio_file"] = audio_mapping.get(label)
        else:
            label = f"teil{t}"
            teil["audio_file"] = audio_mapping.get(label)
    return horen


def build_full_exam(modules: list[dict], timestamp: str) -> dict:
    return {
        "exam_id": f"goethe_osd_b1_{timestamp}",
        "name": "Goethe-ÖSD Zertifikat B1",
        "slug": "goethe_osd_b1",
        "cefr_code": "B1",
        "version": "generated",
        "generated_at": timestamp,
        "scoring_model": "per_module_100",
        "pass_threshold": 60,
        "modules": modules
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main_async(api_key: str, output_dir: Path, no_audio: bool):
    client = genai.Client(api_key=api_key)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_dir = output_dir / f"audio_{timestamp}"

    generated_modules = []

    # Lesen et Hören : Teil par Teil (évite troncature JSON)
    for name in ["Lesen", "Hören"]:
        module_data = generate_module_by_teil(client, name)
        generated_modules.append(module_data)
        ok = sum(1 for t in module_data.get("teile", []) if "error" not in t)
        print(f"  ✅ {name} généré ({ok}/{len(module_data.get('teile', []))} Teile OK)")

    # Schreiben et Sprechen : en un seul appel
    for name, prompt in [("Schreiben", prompt_schreiben()), ("Sprechen", prompt_sprechen())]:
        try:
            module_data = generate_module(client, name, prompt)
            generated_modules.append(module_data)
            print(f"  ✅ {name} généré ({len(module_data.get('teile', []))} Teile)")
        except Exception as e:
            print(f"  ❌ Erreur {name} : {e}")
            generated_modules.append({"slug": name.lower(), "error": str(e)})

    # TTS pour Hören
    horen_data = next((m for m in generated_modules if m.get("slug") == "horen"), None)

    if horen_data and not no_audio:
        print("\n🔊 Génération audio (edge-tts)...")
        scripts = extract_horen_transcriptions(horen_data)
        print(f"   {len(scripts)} transcriptions trouvées")
        audio_mapping = await generate_all_audio(scripts, audio_dir)
        horen_data = attach_audio_refs(horen_data, audio_mapping)
        # Remplacer dans la liste
        for i, m in enumerate(generated_modules):
            if m.get("slug") == "horen":
                generated_modules[i] = horen_data
    elif no_audio:
        print("\n⏭  Audio ignoré (--no-audio)")

    # Export JSON final
    exam = build_full_exam(generated_modules, timestamp)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"examen_b1_{timestamp}.json"
    json_path.write_text(json.dumps(exam, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ Examen généré → {json_path}")
    if not no_audio and horen_data:
        print(f"✅ Fichiers audio  → {audio_dir}/")

    return str(json_path)


def main():
    parser = argparse.ArgumentParser(description="Générateur d'examen B1 complet")
    parser.add_argument("--api-key", required=True, help="Clé API Gemini")
    parser.add_argument("--output", default="./output", help="Dossier de sortie")
    parser.add_argument("--no-audio", action="store_true", help="Ne pas générer les fichiers audio")
    args = parser.parse_args()

    asyncio.run(main_async(
        api_key=args.api_key,
        output_dir=Path(args.output),
        no_audio=args.no_audio
    ))


if __name__ == "__main__":
    main()