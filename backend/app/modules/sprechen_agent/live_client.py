"""
sprechen_agent.live_client
=============================
One Live "segment" = one WebSocket connection to a real-time voice
provider, opened fresh for each sequence step (per the validated cost
strategy: no audio history carried across steps, only the text
transcript via prompt_builder.py's recap).

Gemini Live is primary (far cheaper per the pricing comparison already
done). OpenAI Realtime is fallback only, triggered by a failed
pre-flight health check or a failed setup handshake — never mid-
conversation, per the earlier reliability discussion.

IMPORTANT — cannot be network-tested in this environment (no access to
generativelanguage.googleapis.com / api.openai.com from this sandbox).
This file is syntax-validated and its message construction / event
parsing logic is unit-tested against mocked WebSocket objects, but the
real wire protocol should be re-verified against current provider docs
at integration time — these protocols evolve independently of this
design and model IDs in particular go stale fast:
  - Gemini Live:      https://ai.google.dev/api/live
  - OpenAI Realtime:  https://developers.openai.com/api/docs/guides/realtime-websocket

Useful independent validation found while researching this: Gemini
Live audio-only sessions are capped around 15 minutes (10 min per
WebSocket connection) without context-window compression — which
lines up with, and reinforces, the per-step segmentation strategy
already decided on cost grounds alone.
"""

from __future__ import annotations

import asyncio
import base64
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Literal

import websockets

GEMINI_WS_URL = (
    "wss://generativelanguage.googleapis.com/ws/"
    "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
)
# Confirmed current as of July 2026 — the previous model
# (gemini-live-2.5-flash-native-audio) is deprecated and shut down,
# which is exactly what produced the "1008 policy violation ... is
# not found for API version v1beta, or is not supported for
# bidiGenerateContent" error. Google's official migration guidance
# points here. Re-verify at future integration/maintenance time —
# this model line moves fast.
GEMINI_MODEL = "gemini-3.1-flash-live-preview"

OPENAI_WS_URL = "wss://api.openai.com/v1/realtime"
# Same caveat — check current model catalog before deploying.
OPENAI_MODEL = "gpt-realtime-2.1"

DEFAULT_HANDSHAKE_TIMEOUT_SECONDS = 5.0
HEALTH_CHECK_TIMEOUT_SECONDS = 2.0

# Both providers expect raw PCM16 audio; only the sample rate differs.
GEMINI_INPUT_SAMPLE_RATE = 16000
OPENAI_INPUT_SAMPLE_RATE = 24000


class LiveConnectionError(Exception):
    """Raised on a failed handshake with either provider — the signal
    open_segment() uses to decide whether to fall back."""


@dataclass
class LiveServerEvent:
    type: Literal["text_delta", "audio_delta", "turn_complete", "interrupted", "error"]
    speaker: Literal["student", "agent"] | None = None
    text: str | None = None
    audio_bytes: bytes | None = None
    error_message: str | None = None


class LiveSegment(ABC):
    provider: str

    @abstractmethod
    async def send_audio_chunk(self, pcm16_bytes: bytes) -> None:
        """Stream one chunk of raw PCM16 mic audio to the provider."""

    @abstractmethod
    async def trigger_agent_turn(self) -> None:
        """Explicitly prompts the agent to speak first, with no prior
        student audio. Both providers wait for input before responding
        by default (confirmed in Gemini's Live API best-practices docs:
        "Live API expects user input before it responds") — without
        this, a fresh segment where the agent is supposed to open
        (step.agent_opens / orchestrator.is_agent_turn_next) would just
        sit silently forever."""

    @abstractmethod
    def events(self) -> AsyncIterator[LiveServerEvent]:
        """Yields server events as they arrive — audio to play back,
        transcript deltas to feed orchestrator.record_turn(), and
        turn/interruption signals service.py uses to decide when to
        call orchestrator.advance()."""

    @abstractmethod
    async def close(self) -> None:
        """Closes the underlying WebSocket. Always call this before
        opening the next segment — never leave a Live connection open
        past the step it belongs to; that's exactly the audio-history
        rebilling growth the segmentation strategy exists to avoid."""


# ---------------------------------------------------------------------------
# Gemini Live
# ---------------------------------------------------------------------------

class GeminiLiveSegment(LiveSegment):
    provider = "gemini"

    def __init__(self, websocket) -> None:
        self._ws = websocket

    @classmethod
    async def open(
        cls,
        system_prompt: str,
        *,
        api_key: str,
        timeout_seconds: float = DEFAULT_HANDSHAKE_TIMEOUT_SECONDS,
    ) -> "GeminiLiveSegment":
        url = f"{GEMINI_WS_URL}?key={api_key}"
        try:
            ws = await asyncio.wait_for(websockets.connect(url), timeout=timeout_seconds)
        except Exception as exc:  # noqa: BLE001 — any connect failure -> caller falls back
            raise LiveConnectionError(f"Gemini Live connect failed: {exc}") from exc

        setup_message = {
            "setup": {
                "model": f"models/{GEMINI_MODEL}",
                "generationConfig": {"responseModalities": ["AUDIO"]},
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                # Get text transcripts of both sides without a separate
                # STT pass — cheap relative to the audio tokens anyway.
                "outputAudioTranscription": {},
                "inputAudioTranscription": {},
            }
        }
        await ws.send(json.dumps(setup_message))

        try:
            first_raw = await asyncio.wait_for(ws.recv(), timeout=timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            await ws.close()
            raise LiveConnectionError(f"Gemini Live setup handshake timed out: {exc}") from exc

        first = json.loads(first_raw)
        if "setupComplete" not in first:
            await ws.close()
            raise LiveConnectionError(f"Gemini Live setup failed: unexpected first message {first!r}")

        return cls(ws)

    async def send_audio_chunk(self, pcm16_bytes: bytes) -> None:
        message = {
            "realtimeInput": {
                "audio": {
                    "data": base64.b64encode(pcm16_bytes).decode("ascii"),
                    "mimeType": f"audio/pcm;rate={GEMINI_INPUT_SAMPLE_RATE}",
                }
            }
        }
        await self._ws.send(json.dumps(message))

    async def trigger_agent_turn(self) -> None:
        # Sends a minimal synthetic user turn so the model has
        # something to react to and proceeds to speak per its system
        # instructions (which already tell it to open — see
        # prompt_builder's OPENING_RULE). Empty text alone isn't
        # reliably enough to prompt a response, so a short neutral
        # cue is sent instead.
        message = {
            "clientContent": {
                "turns": [{"role": "user", "parts": [{"text": "(Bitte beginne jetzt.)"}]}],
                "turnComplete": True,
            }
        }
        await self._ws.send(json.dumps(message))

    async def events(self) -> AsyncIterator[LiveServerEvent]:
        async for raw in self._ws:
            msg = json.loads(raw)
            server_content = msg.get("serverContent")
            if server_content is None:
                continue

            model_turn = server_content.get("modelTurn")
            if model_turn:
                for part in model_turn.get("parts", []):
                    inline = part.get("inlineData")
                    if inline and inline.get("data"):
                        yield LiveServerEvent(
                            type="audio_delta", audio_bytes=base64.b64decode(inline["data"])
                        )

            output_transcript = server_content.get("outputTranscription", {}).get("text")
            if output_transcript:
                yield LiveServerEvent(type="text_delta", speaker="agent", text=output_transcript)

            input_transcript = server_content.get("inputTranscription", {}).get("text")
            if input_transcript:
                yield LiveServerEvent(type="text_delta", speaker="student", text=input_transcript)

            if server_content.get("interrupted"):
                yield LiveServerEvent(type="interrupted")
            if server_content.get("turnComplete"):
                yield LiveServerEvent(type="turn_complete")

    async def close(self) -> None:
        await self._ws.close()


# ---------------------------------------------------------------------------
# OpenAI Realtime — fallback only
# ---------------------------------------------------------------------------

class OpenAIRealtimeSegment(LiveSegment):
    provider = "openai"

    def __init__(self, websocket) -> None:
        self._ws = websocket

    @classmethod
    async def open(
        cls,
        system_prompt: str,
        *,
        api_key: str,
        timeout_seconds: float = DEFAULT_HANDSHAKE_TIMEOUT_SECONDS,
    ) -> "OpenAIRealtimeSegment":
        url = f"{OPENAI_WS_URL}?model={OPENAI_MODEL}"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            # NOTE: `additional_headers` is the current `websockets` lib
            # kwarg (v12+). Older pins use `extra_headers` — check your
            # installed version if this raises a TypeError.
            ws = await asyncio.wait_for(
                websockets.connect(url, additional_headers=headers), timeout=timeout_seconds
            )
        except Exception as exc:  # noqa: BLE001
            raise LiveConnectionError(f"OpenAI Realtime connect failed: {exc}") from exc

        try:
            created_raw = await asyncio.wait_for(ws.recv(), timeout=timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            await ws.close()
            raise LiveConnectionError(f"OpenAI Realtime handshake timed out: {exc}") from exc

        created = json.loads(created_raw)
        if created.get("type") != "session.created":
            await ws.close()
            raise LiveConnectionError(
                f"OpenAI Realtime handshake failed: unexpected first event {created!r}"
            )

        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": system_prompt,
                "turn_detection": {"type": "server_vad", "silence_duration_ms": 500},
                "input_audio_transcription": {"model": "whisper-1"},
            },
        }))

        return cls(ws)

    async def send_audio_chunk(self, pcm16_bytes: bytes) -> None:
        await self._ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(pcm16_bytes).decode("ascii"),
        }))

    async def trigger_agent_turn(self) -> None:
        # OpenAI Realtime has a purpose-built event for this — no
        # synthetic user turn needed, unlike Gemini.
        await self._ws.send(json.dumps({"type": "response.create"}))

    async def events(self) -> AsyncIterator[LiveServerEvent]:
        async for raw in self._ws:
            event = json.loads(raw)
            etype = event.get("type", "")

            if etype == "response.audio.delta":
                yield LiveServerEvent(type="audio_delta", audio_bytes=base64.b64decode(event["delta"]))
            elif etype == "response.audio_transcript.delta":
                yield LiveServerEvent(type="text_delta", speaker="agent", text=event.get("delta", ""))
            elif etype == "conversation.item.input_audio_transcription.completed":
                yield LiveServerEvent(type="text_delta", speaker="student", text=event.get("transcript", ""))
            elif etype == "response.done":
                yield LiveServerEvent(type="turn_complete")
            elif etype == "input_audio_buffer.speech_started":
                yield LiveServerEvent(type="interrupted")
            elif etype == "error":
                yield LiveServerEvent(type="error", error_message=str(event.get("error")))

    async def close(self) -> None:
        await self._ws.close()


# ---------------------------------------------------------------------------
# Facade — health check + fallback, per the validated reliability strategy
# ---------------------------------------------------------------------------

async def _gemini_reachable(api_key: str, timeout_seconds: float = HEALTH_CHECK_TIMEOUT_SECONDS) -> bool:
    """Cheap pre-flight probe, done BEFORE committing to Gemini for this
    segment — never discovered mid-conversation. Opens and immediately
    closes a connection. Not a full guarantee the segment stays healthy,
    but catches the common case (saturated/unreachable endpoint) cited
    as the original motivation for the fallback."""
    url = f"{GEMINI_WS_URL}?key={api_key}"
    try:
        ws = await asyncio.wait_for(websockets.connect(url), timeout=timeout_seconds)
        await ws.close()
        return True
    except Exception:  # noqa: BLE001 — any failure means "not healthy"
        return False


async def open_segment(
    system_prompt: str,
    *,
    gemini_api_key: str,
    openai_api_key: str,
    preferred_provider: str = "gemini",
) -> LiveSegment:
    gemini_error: Exception | None = None

    if preferred_provider == "gemini" and await _gemini_reachable(gemini_api_key):
        try:
            return await GeminiLiveSegment.open(system_prompt, api_key=gemini_api_key)
        except LiveConnectionError as exc:
            gemini_error = exc  # fall through to OpenAI below, if configured

    if not openai_api_key:
        # No OpenAI fallback configured — surface the real Gemini
        # failure instead of a confusing "invalid_api_key: ''" from a
        # provider we never intended to use.
        raise gemini_error or LiveConnectionError(
            "Gemini Live unreachable and no OpenAI fallback key configured."
        )

    return await OpenAIRealtimeSegment.open(system_prompt, api_key=openai_api_key)