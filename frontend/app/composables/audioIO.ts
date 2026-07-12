/**
 * audioIO.ts
 * ============
 * The real `SprechenAudioIO` implementation for the browser —
 * getUserMedia + AudioWorklet for capture, a scheduled playback
 * queue for the agent's incoming audio.
 *
 * NOT unit-testable in this environment: AudioContext, AudioWorklet,
 * and getUserMedia don't exist outside a real browser. This file is
 * type-checked but not exercised by the test suite alongside
 * useSprechenSession.ts — treat it with the same caution as
 * live_client.py's Gemini/OpenAI calls on the backend (structurally
 * sound, unverified against a live environment).
 *
 * Sample rates: capture at 16kHz to match Gemini Live's expected
 * input rate; playback assumes 24kHz PCM16 for the agent's voice
 * (Gemini Live's typical output rate) — confirm both against the
 * current Gemini Live API docs before shipping, since these have
 * shifted before and aren't guaranteed stable across model versions.
 */

import type { SprechenAudioIO } from './useSprechenSession'; 

const CAPTURE_SAMPLE_RATE = 16000;
const PLAYBACK_SAMPLE_RATE = 24000;
const WORKLET_MODULE_URL = '/pcm-capture-processor.js'; // must be in Nuxt's public/

export function createBrowserAudioIO(): SprechenAudioIO {
  let captureContext: AudioContext | null = null;
  let micStream: MediaStream | null = null;
  let workletNode: AudioWorkletNode | null = null;

  let playbackContext: AudioContext | null = null;
  let nextPlaybackStartTime = 0;

  async function startCapture(onChunk: (bytes: Uint8Array) => void): Promise<void> {
    if (workletNode) return; // already capturing — no-op rather than double-attach

    micStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: CAPTURE_SAMPLE_RATE,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });

    captureContext = new AudioContext({ sampleRate: CAPTURE_SAMPLE_RATE });
    await captureContext.audioWorklet.addModule(WORKLET_MODULE_URL);

    const source = captureContext.createMediaStreamSource(micStream);
    workletNode = new AudioWorkletNode(captureContext, 'pcm-capture-processor');

    workletNode.port.onmessage = (event: MessageEvent<ArrayBuffer>) => {
      onChunk(new Uint8Array(event.data));
    };

    source.connect(workletNode);
    // Not connecting workletNode to captureContext.destination — we
    // only want the raw samples for streaming, never local echo.
  }

  function stopCapture(): void {
    workletNode?.port.close();
    workletNode?.disconnect();
    workletNode = null;

    micStream?.getTracks().forEach((track) => track.stop());
    micStream = null;

    if (captureContext && captureContext.state !== 'closed') {
      void captureContext.close();
    }
    captureContext = null;
  }

  function ensurePlaybackContext(): AudioContext {
    if (!playbackContext || playbackContext.state === 'closed') {
      playbackContext = new AudioContext({ sampleRate: PLAYBACK_SAMPLE_RATE });
      nextPlaybackStartTime = playbackContext.currentTime;
    }
    return playbackContext;
  }

  function playChunk(bytes: Uint8Array): void {
    const ctx = ensurePlaybackContext();

    // PCM16 -> Float32 for the Web Audio API
    const pcm16 = new Int16Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 2);
    const float32 = new Float32Array(pcm16.length);
    for (let i = 0; i < pcm16.length; i++) {
      float32[i] = pcm16[i]! / (pcm16[i]! < 0 ? 0x8000 : 0x7fff);
    }

    const buffer = ctx.createBuffer(1, float32.length, PLAYBACK_SAMPLE_RATE);
    buffer.copyToChannel(float32, 0);

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    // Schedule back-to-back rather than firing immediately, so
    // consecutive chunks don't overlap or gap — a simple streaming
    // playback queue without needing to buffer whole utterances.
    const startAt = Math.max(nextPlaybackStartTime, ctx.currentTime);
    source.start(startAt);
    nextPlaybackStartTime = startAt + buffer.duration;
  }

  function stopPlayback(): void {
    if (playbackContext && playbackContext.state !== 'closed') {
      void playbackContext.close();
    }
    playbackContext = null;
    nextPlaybackStartTime = 0;
  }

  return { startCapture, stopCapture, playChunk, stopPlayback };
}