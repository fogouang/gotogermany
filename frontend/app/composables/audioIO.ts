/**
 * audioIO.ts
 * ============
 * The real `SprechenAudioIO` implementation for the browser —
 * getUserMedia + AudioWorklet for capture, a scheduled playback
 * queue for the incoming audio.
 *
 * NOT unit-testable in this environment: AudioContext, AudioWorklet,
 * and getUserMedia don't exist outside a real browser.
 *
 * MODIF : taux d'échantillonnage désormais paramétrables. Par défaut,
 * on garde 16kHz capture / 24kHz lecture — ce qui correspond aux
 * besoins de Gemini Live pour l'agent IA (entrée et sortie ne sont PAS
 * le même flux : la voix de l'utilisateur en entrée, la voix générée
 * par Gemini en sortie, chacune à son propre taux). Pour live_session
 * (voix humaine à humaine, même flux capté et rejoué), il faut passer
 * des taux IDENTIQUES en capture et lecture, sinon la voix rejouée est
 * accélérée/suraiguë (effet "voix de tchip").
 *
 * MODIF : sortie audio externe optionnelle (setOutputTarget). Utilisée
 * par l'agent IA pour jouer la voix dans l'avatar 3D (lip-sync).
 * Sans sortie externe, lecture habituelle sur un contexte dédié.
 *
 * MODIF : anti-écho optionnel (muteMicWhilePlaying). Agent IA
 * uniquement : le micro envoie du silence tant que la voix de l'agent
 * est encore jouée, pour ne pas capter la fin de sa phrase.
 */

import type { SprechenAudioIO } from './useSprechenSession';

/** Sortie audio fournie par un tiers (ex. l'avatar 3D de l'examinatrice). */
export interface AudioOutputTarget {
  ctx: AudioContext;
  node: AudioNode;
}

// Étend SprechenAudioIO avec un accès au flux brut, pour permettre un
// vrai mute (track.enabled = false) sans arrêter toute la capture —
// utilisé par live_session, ignoré sans risque par l'agent IA qui garde
// son typage SprechenAudioIO plus étroit (surplus de méthode inoffensif).
export interface BrowserAudioIO extends SprechenAudioIO {
  getLocalStream(): MediaStream | null;
  /**
   * Fournit une sortie audio externe, interrogée à chaque chunk.
   * Le getter peut renvoyer null (avatar pas encore prêt) : la lecture
   * se fait alors sur le contexte interne. null pour retirer la sortie.
   */
  setOutputTarget(getter: (() => AudioOutputTarget | null) | null): void;
}

const DEFAULT_CAPTURE_SAMPLE_RATE = 16000;
const DEFAULT_PLAYBACK_SAMPLE_RATE = 24000;
const WORKLET_MODULE_URL = '/pcm-capture-processor.js'; // must be in Nuxt's public/

// Marge après la fin de la voix de l'agent (réverbération de la pièce)
const ECHO_TAIL_SECONDS = 0.35;

export interface CreateAudioIOOptions {
  captureSampleRate?: number;
  playbackSampleRate?: number;
  /**
   * Agent IA uniquement : envoie du silence tant que la voix de l'agent
   * est encore jouée (fin de file + résonance), pour que le micro ne
   * capte pas la fin de sa phrase. Désactivé par défaut (live_session :
   * les deux personnes doivent pouvoir parler en même temps).
   */
  muteMicWhilePlaying?: boolean;
}

export function createBrowserAudioIO(options: CreateAudioIOOptions = {}): BrowserAudioIO {
  const CAPTURE_SAMPLE_RATE = options.captureSampleRate ?? DEFAULT_CAPTURE_SAMPLE_RATE;
  const PLAYBACK_SAMPLE_RATE = options.playbackSampleRate ?? DEFAULT_PLAYBACK_SAMPLE_RATE;
  const MUTE_MIC_WHILE_PLAYING = options.muteMicWhilePlaying ?? false;

  let captureContext: AudioContext | null = null;
  let micStream: MediaStream | null = null;
  let workletNode: AudioWorkletNode | null = null;

  // Contexte interne, utilisé quand aucune sortie externe n'est prête
  let playbackContext: AudioContext | null = null;
  let nextPlaybackStartTime = 0;

  let outputProvider: (() => AudioOutputTarget | null) | null = null;
  let currentTarget: (AudioOutputTarget & { external: boolean }) | null = null;
  const activeSources = new Set<AudioBufferSourceNode>();

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
      if (MUTE_MIC_WHILE_PLAYING && isPlaybackActive()) {
        // Silence de même taille : le flux reste continu pour Gemini
        onChunk(new Uint8Array(event.data.byteLength));
        return;
      }
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
    }
    return playbackContext;
  }

  /**
   * Choisit où jouer le prochain chunk. On ne bascule vers la sortie
   * externe que quand la file en cours est vide, sinon deux contextes
   * joueraient la voix en même temps.
   */
  function getPlaybackTarget(): AudioOutputTarget & { external: boolean } {
    const external = outputProvider?.() ?? null;

    // Sortie externe disparue (avatar démonté) : retour au contexte interne
    if (currentTarget?.external && (!external || currentTarget.ctx.state === 'closed')) {
      currentTarget = null;
    }

    const queueDrained =
      !currentTarget || nextPlaybackStartTime <= currentTarget.ctx.currentTime;

    if (external && !currentTarget?.external && queueDrained) {
      currentTarget = { ...external, external: true };
      nextPlaybackStartTime = external.ctx.currentTime;
    } else if (!currentTarget) {
      const ctx = ensurePlaybackContext();
      currentTarget = { ctx, node: ctx.destination, external: false };
      nextPlaybackStartTime = ctx.currentTime;
    }

    if (currentTarget.ctx.state === 'suspended') {
      void currentTarget.ctx.resume();
    }
    return currentTarget;
  }

  function playChunk(bytes: Uint8Array): void {
    const { ctx, node } = getPlaybackTarget();

    // PCM16 -> Float32 for the Web Audio API
    const pcm16 = new Int16Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 2);
    const float32 = new Float32Array(pcm16.length);
    for (let i = 0; i < pcm16.length; i++) {
      float32[i] = pcm16[i]! / (pcm16[i]! < 0 ? 0x8000 : 0x7fff);
    }

    // Toujours au taux de la source : le contexte cible (ex. avatar à
    // 48kHz) rééchantillonne lui-même.
    const buffer = ctx.createBuffer(1, float32.length, PLAYBACK_SAMPLE_RATE);
    buffer.copyToChannel(float32, 0);

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(node);
    activeSources.add(source);
    source.onended = () => activeSources.delete(source);

    // Schedule back-to-back rather than firing immediately, so
    // consecutive chunks don't overlap or gap — a simple streaming
    // playback queue without needing to buffer whole utterances.
    const startAt = Math.max(nextPlaybackStartTime, ctx.currentTime);
    source.start(startAt);
    nextPlaybackStartTime = startAt + buffer.duration;
  }

  function stopPlayback(): void {
    // On coupe les sons en cours sans jamais fermer un contexte externe :
    // c'est son propriétaire (l'avatar) qui le libère.
    activeSources.forEach((source) => {
      try {
        source.stop();
      } catch {
        // déjà terminé
      }
    });
    activeSources.clear();

    if (playbackContext && playbackContext.state !== 'closed') {
      void playbackContext.close();
    }
    playbackContext = null;
    currentTarget = null;
    nextPlaybackStartTime = 0;
  }

  /** Vrai tant que la voix de l'agent sort encore des haut-parleurs. */
  function isPlaybackActive(): boolean {
    if (!currentTarget) return false;
    return nextPlaybackStartTime + ECHO_TAIL_SECONDS > currentTarget.ctx.currentTime;
  }

  function getLocalStream(): MediaStream | null {
    return micStream;
  }

  function setOutputTarget(getter: (() => AudioOutputTarget | null) | null): void {
    outputProvider = getter;
  }

  return {
    startCapture,
    stopCapture,
    playChunk,
    stopPlayback,
    getLocalStream,
    setOutputTarget,
  };
}