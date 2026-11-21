"""
testdaf_sprechen.transcription
=================================
Transcription d'un enregistrement d'élève avec Gemini (appel classique
generateContent, pas Live) : l'audio est envoyé en ligne, Gemini renvoie
le texte allemand tel que prononcé, sans correction.

Le nom du modèle bouge vite chez Google : à revérifier si l'appel
renvoie une erreur 404 "model not found".
"""

from __future__ import annotations

import base64

import httpx

GEMINI_REST_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TRANSCRIPTION_MODEL = "gemini-2.5-flash"
TRANSCRIPTION_TIMEOUT_SECONDS = 60.0

_PROMPT = (
    "Transcribe this German speech recording exactly as spoken, word for word. "
    "Do NOT correct grammar, vocabulary or pronunciation mistakes, do NOT translate, "
    "do NOT summarize, do NOT add any comment. Keep hesitations only if they are "
    "real words. If the recording contains no understandable speech, answer with "
    "exactly: [keine Sprache]"
)


class TranscriptionError(Exception):
    pass


def _clean_mime(mime_type: str | None) -> str:
    # "audio/webm;codecs=opus" -> "audio/webm"
    return (mime_type or "audio/webm").split(";")[0].strip() or "audio/webm"


async def transcribe(audio_bytes: bytes, mime_type: str | None, *, api_key: str) -> str:
    if not audio_bytes:
        return "[keine Sprache]"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": _clean_mime(mime_type),
                            "data": base64.b64encode(audio_bytes).decode("ascii"),
                        }
                    },
                    {"text": _PROMPT},
                ],
            }
        ],
        "generationConfig": {"temperature": 0},
    }

    async with httpx.AsyncClient(timeout=TRANSCRIPTION_TIMEOUT_SECONDS) as client:
        response = await client.post(
            GEMINI_REST_URL.format(model=TRANSCRIPTION_MODEL),
            params={"key": api_key},
            json=payload,
        )
    if response.status_code != 200:
        raise TranscriptionError(f"Gemini {response.status_code}: {response.text[:300]}")

    data = response.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as exc:
        raise TranscriptionError(f"Réponse Gemini inattendue : {data!r}"[:300]) from exc
    return " ".join(p.get("text", "") for p in parts).strip() or "[keine Sprache]"