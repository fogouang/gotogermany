/**
 * useSprechenSession.ts
 * ======================
 * Owns the WebSocket connection to the Sprechen live-conversation
 * endpoint and the client-side state machine that mirrors
 * SessionState on the backend (current Teil, whose turn it is,
 * transcript, final grading).
 *
 * Audio capture/playback is deliberately NOT implemented here —
 * it's injected via the `SprechenAudioIO` interface. That's what
 * makes this file testable without a real browser/microphone (see
 * the test alongside this file); the real getUserMedia +
 * AudioWorklet implementation lives in audioIO.ts and can only be
 * exercised in an actual browser.
 */

import { ref, shallowRef, type Ref } from "vue";
import type {
  OutboundEvent,
  GradingResultMessage,
  TeilStartedEvent,
  PreparationStartedEvent,
} from "#shared/sprechenWebSocketTypes"; // ADJUST if the real path differs

export interface SprechenAudioIO {
  /** Starts streaming mic audio; onChunk is called with each PCM16
   * frame ready to send. Must be idempotent-safe to call while
   * already capturing (no-op or restart, implementation's choice). */
  startCapture(onChunk: (bytes: Uint8Array) => void): Promise<void>;
  stopCapture(): void;
  /** Queues one PCM16 chunk of agent audio for playback. */
  playChunk(bytes: Uint8Array): void;
  stopPlayback(): void;
}

export type SprechenConnectionStatus =
  | "idle"
  | "connecting"
  | "preparing"
  | "active"
  | "ended"
  | "error";

export type SprechenMicState = "agent_speaking" | "student_turn" | null;

export interface TranscriptLine {
  speaker: "student" | "agent";
  text: string;
}

export interface UseSprechenSessionOptions {
  subjectId: string;
  wsBaseUrl: string; // e.g. "wss://api.example.com/api/v1/sprechen-simulator"
  audioIO: SprechenAudioIO;
  /** Injectable for testing — defaults to the real `WebSocket` global. */
  createWebSocket?: (url: string) => WebSocket;
}

export function useSprechenSession(options: UseSprechenSessionOptions) {
  const status: Ref<SprechenConnectionStatus> = ref("idle");
  const totalTeile = ref(0);
  const currentTeil: Ref<TeilStartedEvent | null> = shallowRef(null);
  const preparationInfo: Ref<PreparationStartedEvent | null> = shallowRef(null);
  const micState: Ref<SprechenMicState> = ref(null);
  const transcript: Ref<TranscriptLine[]> = ref([]);
  const gradingResult: Ref<GradingResultMessage | null> = shallowRef(null);
  const errorMessage = ref<string | null>(null);

  const createWs =
    options.createWebSocket ?? ((url: string) => new WebSocket(url));
  let ws: WebSocket | null = null;

  // Set only when a 'session_ended' text message actually arrives —
  // lets onclose distinguish a clean server-driven end from a dropped
  // connection / backend crash, instead of treating every close as
  // "ended" and silently stranding the user on the grading spinner.
  let sessionEndedCleanly = false;

  function handleTextMessage(raw: string): void {
    let msg: OutboundEvent | GradingResultMessage;
    try {
      msg = JSON.parse(raw);
    } catch {
      return; // malformed frame — ignore rather than crash the session
    }

    switch (msg.type) {
      case "session_ready":
        totalTeile.value = msg.total_teile;
        // Do NOT jump to "active" here — the very next message decides
        // that: either preparation_started (this Teil needs prep) or
        // teil_started (goes straight live). Forcing "active" now would
        // flash the call UI for an instant before a preparation screen
        // that's actually coming.
        status.value = "connecting";
        break;

      case "preparation_started":
        preparationInfo.value = msg;
        status.value = "preparing";
        break;

      case "teil_started":
        currentTeil.value = msg;
        preparationInfo.value = null; // clear — the live segment is open now
        status.value = "active";
        break;

      case "agent_speaking":
        micState.value = "agent_speaking";
        options.audioIO.stopCapture();
        break;

      case "student_turn":
        micState.value = "student_turn";
        options.audioIO
          .startCapture((chunk) => {
            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.send(chunk as BufferSource);
            }
          })
          .catch((err) => {
            console.error("Mic capture failed:", err);
            status.value = "error";
            errorMessage.value =
              "Impossible d'accéder au microphone. Vérifiez les permissions.";
          });
        break;

      case "transcript_update":
        transcript.value.push({ speaker: msg.speaker, text: msg.text });
        break;

      case "session_ended":
        sessionEndedCleanly = true;
        status.value = "ended";
        micState.value = null;
        options.audioIO.stopCapture();
        break;

      case "grading_result":
        gradingResult.value = msg;
        break;
    }
  }

  function handleBinaryMessage(data: ArrayBuffer): void {
    options.audioIO.playChunk(new Uint8Array(data));
  }

  function connect(): void {
    if (ws) return; // already connecting/connected — connect() is idempotent
    status.value = "connecting";
    errorMessage.value = null;
    sessionEndedCleanly = false;

    const socket = createWs(`${options.wsBaseUrl}/ws/${options.subjectId}`);
    socket.binaryType = "arraybuffer";

    socket.onmessage = (event: MessageEvent) => {
      if (typeof event.data === "string") {
        handleTextMessage(event.data);
      } else {
        handleBinaryMessage(event.data as ArrayBuffer);
      }
    };

    socket.onerror = () => {
      status.value = "error";
      errorMessage.value = "Connection error";
    };

    socket.onclose = (event: CloseEvent) => {
      options.audioIO.stopCapture();
      options.audioIO.stopPlayback();
      if (!sessionEndedCleanly) {
        // closed before a clean session_ended — treat as an error
        // state so the UI doesn't sit on a stale spinner or a
        // grading screen that will never receive its result.
        status.value = "error";
        errorMessage.value =
          errorMessage.value ?? `Connexion interrompue (code ${event.code}).`;
      }
      ws = null;
    };

    ws = socket;
  }

  /** Sent once the student is done reviewing the preparation panel
   * (button click, or a local prep timer running out) — tells the
   * backend to open the Live segment for the Teil currently in
   * preparationInfo. No-op if we're not actually in "preparing". */
  function sendReadyToStart(): void {
      console.log("sendReadyToStart called", { ws: !!ws, readyState: ws?.readyState, prepInfo: preparationInfo.value });
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (!preparationInfo.value) return;
    ws.send(
      JSON.stringify({
        type: "ready_to_start",
        session_id: preparationInfo.value.session_id,
      }),
    );
  }

  function abandonSession(): void {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(
      JSON.stringify({
        type: "abandon_session",
        session_id:
          currentTeil.value?.session_id ??
          preparationInfo.value?.session_id ??
          "",
      }),
    );
  }

  function disconnect(): void {
    options.audioIO.stopCapture();
    options.audioIO.stopPlayback();
    ws?.close();
    ws = null;
  }

  return {
    // state (readonly from the consumer's perspective by convention —
    // not wrapped in readonly() to keep this file framework-light for
    // testing; enforce readonly at the component boundary if desired)
    status,
    totalTeile,
    currentTeil,
    preparationInfo,
    micState,
    transcript,
    gradingResult,
    errorMessage,
    // actions
    connect,
    sendReadyToStart,
    abandonSession,
    disconnect,
  };
}