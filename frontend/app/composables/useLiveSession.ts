/**
 * useLiveSession.ts
 * ==================
 * Owns the WebSocket connection to the live_session audio-bridge
 * endpoint (examinateur réel, pas d'IA) and the client-side state
 * machine that mirrors LiveSessionStatus on the backend.
 *
 * Unlike useSprechenSession, there is no turn-taking state
 * (agent_speaking / student_turn) — audio flows both ways
 * continuously once the session is "live", exactly like a normal
 * phone call. Capture starts when we enter "live" and stops when we
 * leave it.
 *
 * Audio capture/playback is deliberately NOT implemented here — it's
 * injected via the same shape as SprechenAudioIO (audioIO.ts), so the
 * existing mic/playback implementation is reused as-is. That's also
 * what keeps this file testable without a real browser/microphone.
 *
 * Two roles connect to two different endpoints (student vs examiner)
 * but share the same message shapes and state machine — role is
 * passed in and only changes which URL we connect to and whether
 * sendReadyToStart() is meaningful.
 */

import { ref, shallowRef, type Ref } from "vue";
import type {
  LiveSessionOutboundEvent,
  PreparationStartedEvent,
} from "#shared/liveSessionWebSocketTypes"; // ADJUST if the real path differs
import type { LiveVideoCapture, LiveVideoPlayback } from "./useLiveVideo";

// Préfixe d'un octet sur chaque message binaire, pour distinguer audio et
// vidéo dans le même flux WebSocket — le backend relaie ces messages sans
// jamais les interpréter, la distinction ne compte que côté client.
const MESSAGE_TYPE_AUDIO = 0;
const MESSAGE_TYPE_VIDEO = 1;

function withTypePrefix(type: number, bytes: Uint8Array): Uint8Array {
  const out = new Uint8Array(bytes.length + 1);
  out[0] = type;
  out.set(bytes, 1);
  return out;
}

// Combien de temps sans dépasser le seuil avant de considérer que la
// personne a arrêté de parler — évite un indicateur qui clignote entre
// deux paquets PCM16 consécutifs plutôt que de suivre le rythme naturel
// de la parole.
const SPEAKING_DECAY_MS = 400;

// Amplitude RMS (0-1, PCM16 normalisé) au-dessus de laquelle on considère
// qu'il y a de la voix plutôt que du bruit de fond/silence. À ajuster à
// l'oreille si trop sensible ou pas assez.
const SPEAKING_RMS_THRESHOLD = 0.02;

// Porte de bruit : sous ce seuil (nettement plus bas que le seuil de
// parole), on ne transmet PAS le paquet du tout — coupe le bruit de fond
// ambiant continu (souffle du micro, bruit électrique) qui autrement
// serait envoyé en permanence même dans un environnement calme. Volontairement
// bas pour ne jamais couper le début d'un mot prononcé doucement.
const NOISE_GATE_RMS_THRESHOLD = 0.006;

/** Calcule le niveau RMS (0-1) d'un chunk audio PCM16 brut. */
function pcm16RmsLevel(bytes: Uint8Array): number {
  const pcm16 = new Int16Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 2);
  if (pcm16.length === 0) return 0;
  let sumSquares = 0;
  for (let i = 0; i < pcm16.length; i++) {
    const normalized = pcm16[i]! / 0x8000;
    sumSquares += normalized * normalized;
  }
  return Math.sqrt(sumSquares / pcm16.length);
}

export interface LiveSessionAudioIO {
  /** Starts streaming mic audio; onChunk is called with each PCM16
   * frame ready to send. Must be idempotent-safe to call while
   * already capturing (no-op or restart, implementation's choice). */
  startCapture(onChunk: (bytes: Uint8Array) => void): Promise<void>;
  stopCapture(): void;
  /** Queues one PCM16 chunk of peer audio for playback. */
  playChunk(bytes: Uint8Array): void;
  stopPlayback(): void;
}

export type LiveSessionRole = "student" | "examiner";

export type LiveSessionConnectionStatus =
  | "idle"
  | "connecting"
  | "preparing" // student only in practice — examiner sits in "connecting" until live_started
  | "live"
  | "ended"
  | "error";

export interface UseLiveSessionOptions {
  liveSessionId: string;
  role: LiveSessionRole;
  wsBaseUrl: string; // e.g. "wss://api.example.com/api/v1/live-session"
  audioIO: LiveSessionAudioIO;
  /** Token d'accès à passer en query param — un WebSocket natif ne peut
   * pas fixer de header Authorization, et le cookie access_token n'est
   * pas garanti d'atteindre le domaine du backend (voir
   * get_current_user_ws côté serveur). */
  accessToken: string;
  /** Optionnels — si absents, la session reste audio seul (comportement
   * inchangé). Fournis, la vidéo bidirectionnelle s'active en même
   * temps que l'audio, sur le même WebSocket. */
  videoCapture?: LiveVideoCapture;
  videoPlayback?: LiveVideoPlayback;
  /** Injectable for testing — defaults to the real `WebSocket` global. */
  createWebSocket?: (url: string) => WebSocket;
}

export function useLiveSession(options: UseLiveSessionOptions) {
  const status: Ref<LiveSessionConnectionStatus> = ref("idle");
  const preparationInfo: Ref<PreparationStartedEvent | null> = shallowRef(null);
  const peerLeft = ref(false);
  const errorMessage = ref<string | null>(null);

  // Indicateurs "qui parle en ce moment" — dérivés du niveau du flux audio,
  // purement côté client (le backend ne fait que relayer des octets bruts,
  // il n'a aucune notion de tour de parole dans ce mode).
  const localSpeaking = ref(false);
  const peerSpeaking = ref(false);
  let localSpeakingTimer: ReturnType<typeof setTimeout> | null = null;
  let peerSpeakingTimer: ReturnType<typeof setTimeout> | null = null;

  function markSpeaking(
    flag: Ref<boolean>,
    timerHolder: "local" | "peer",
  ): void {
    flag.value = true;
    const existing = timerHolder === "local" ? localSpeakingTimer : peerSpeakingTimer;
    if (existing) clearTimeout(existing);
    const timer = setTimeout(() => {
      flag.value = false;
    }, SPEAKING_DECAY_MS);
    if (timerHolder === "local") localSpeakingTimer = timer;
    else peerSpeakingTimer = timer;
  }

  function resetSpeakingIndicators(): void {
    if (localSpeakingTimer) clearTimeout(localSpeakingTimer);
    if (peerSpeakingTimer) clearTimeout(peerSpeakingTimer);
    localSpeakingTimer = null;
    peerSpeakingTimer = null;
    localSpeaking.value = false;
    peerSpeaking.value = false;
  }

  const createWs =
    options.createWebSocket ?? ((url: string) => new WebSocket(url));
  let ws: WebSocket | null = null;

  // Set only when a 'peer_left' or a clean local end_session actually
  // happened — lets onclose distinguish a deliberate end from a dropped
  // connection, same reasoning as useSprechenSession's sessionEndedCleanly.
  let sessionEndedCleanly = false;

  function handleTextMessage(raw: string): void {
    let msg: LiveSessionOutboundEvent;
    try {
      msg = JSON.parse(raw);
    } catch {
      return; // malformed frame — ignore rather than crash the session
    }

    switch (msg.type) {
      case "preparation_started":
        preparationInfo.value = msg;
        status.value = "preparing";
        break;

      case "live_started":
        preparationInfo.value = null;
        status.value = "live";
        options.audioIO.startCapture((chunk) => {
          const level = pcm16RmsLevel(chunk);
          if (level > SPEAKING_RMS_THRESHOLD) {
            markSpeaking(localSpeaking, "local");
          }
          // Porte de bruit : on ignore silencieusement les paquets sous
          // le seuil de bruit de fond, pour ne jamais les transmettre.
          if (level < NOISE_GATE_RMS_THRESHOLD) return;
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(withTypePrefix(MESSAGE_TYPE_AUDIO, chunk) as BufferSource);
          }
        }).catch((err) => {
          console.error("Mic capture failed:", err);
          status.value = "error";
          errorMessage.value =
            "Impossible d'accéder au microphone. Vérifiez les permissions.";
        });

        if (options.videoCapture) {
          options.videoCapture.startCapture((chunk) => {
            if (ws && ws.readyState === WebSocket.OPEN) {
              const prefixed = withTypePrefix(MESSAGE_TYPE_VIDEO, new Uint8Array(chunk));
              ws.send(prefixed as BufferSource);
            }
          }).catch((err) => {
            // La vidéo est optionnelle — un échec caméra ne doit jamais
            // faire tomber la session audio, qui reste l'essentiel.
            console.error("Video capture failed:", err);
          });
        }
        break;

      case "peer_left":
        peerLeft.value = true;
        sessionEndedCleanly = true;
        status.value = "ended";
        resetSpeakingIndicators();
        options.audioIO.stopCapture();
        options.audioIO.stopPlayback();
        options.videoCapture?.stopCapture();
        options.videoPlayback?.stop();
        break;
    }
  }

  function handleBinaryMessage(data: ArrayBuffer): void {
    // Seule la session "live" doit traiter l'audio/vidéo entrant —
    // pendant la prépa côté candidat, rien n'est censé arriver, mais on
    // reste défensif plutôt que de crasher sur un flux inattendu.
    if (status.value !== "live") return;
    if (data.byteLength < 1) return;

    const messageType = new Uint8Array(data, 0, 1)[0];
    const payload = data.slice(1);

    if (messageType === MESSAGE_TYPE_VIDEO) {
      options.videoPlayback?.pushChunk(payload);
      return;
    }

    // Par défaut (ou type audio explicite) : chemin audio existant.
    const bytes = new Uint8Array(payload);
    if (pcm16RmsLevel(bytes) > SPEAKING_RMS_THRESHOLD) {
      markSpeaking(peerSpeaking, "peer");
    }
    options.audioIO.playChunk(bytes);
  }

  function connect(): void {
    if (ws) return; // already connecting/connected — connect() is idempotent
    status.value = "connecting";
    errorMessage.value = null;
    peerLeft.value = false;
    sessionEndedCleanly = false;

    const socket = createWs(
      `${options.wsBaseUrl}/ws/${options.liveSessionId}/${options.role}?token=${encodeURIComponent(options.accessToken)}`,
    );
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
      options.videoCapture?.stopCapture();
      options.videoPlayback?.stop();
      resetSpeakingIndicators();
      if (!sessionEndedCleanly) {
        status.value = "error";
        errorMessage.value =
          errorMessage.value ?? `Connexion interrompue (code ${event.code}).`;
      }
      ws = null;
    };

    ws = socket;
  }

  /** Étudiant uniquement — envoyé quand la prépa 20min/3 Teile est
   * terminée (bouton ou minuteur local à écoulement). No-op pour un
   * examinateur ou si on n'est pas en "preparing". */
  function sendReadyToStart(): void {
    if (options.role !== "student") return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    if (status.value !== "preparing") return;
    ws.send(JSON.stringify({ type: "ready_to_start" }));
  }

  /** Les deux rôles peuvent terminer la session explicitement. */
  function endSession(): void {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    sessionEndedCleanly = true;
    ws.send(JSON.stringify({ type: "end_session" }));
  }

  function disconnect(): void {
    options.audioIO.stopCapture();
    options.audioIO.stopPlayback();
    options.videoCapture?.stopCapture();
    options.videoPlayback?.stop();
    resetSpeakingIndicators();
    ws?.close();
    ws = null;
  }

  return {
    // state
    status,
    preparationInfo,
    peerLeft,
    errorMessage,
    localSpeaking,
    peerSpeaking,
    // actions
    connect,
    sendReadyToStart,
    endSession,
    disconnect,
  };
}