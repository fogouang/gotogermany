/**
 * useLiveVideo.ts
 * ================
 * Capture et lecture vidéo pour live_session, sur le même principe que
 * l'audio (relais via le backend, pas de WebRTC/ICE — voir la décision
 * prise après avoir vu une appli concurrente planter avec des erreurs
 * ICE en prod).
 *
 * Volontairement séparé de l'audio PCM16 déjà en place (audioIO.ts) :
 * MediaRecorder ici capture UNIQUEMENT la vidéo (audio: false), pour ne
 * pas dupliquer/entrer en conflit avec le pipeline audio existant, qui
 * reste la seule source de son.
 *
 * Capture : MediaRecorder produit des chunks WebM/VP8 compressés toutes
 * les ~500ms, envoyés tels quels (ArrayBuffer) par le composable appelant.
 *
 * Lecture : les chunks reçus sont ajoutés à un SourceBuffer MediaSource,
 * qui alimente une balise <video> en flux continu — pas de re-création
 * d'URL blob à chaque chunk (ça casserait la lecture).
 */

// Basse résolution, priorité à la fiabilité — cf. décision prise pour
// la V1. À ajuster si besoin une fois testé en conditions réelles.
const VIDEO_WIDTH = 320;
const VIDEO_HEIGHT = 240;
const VIDEO_FRAMERATE = 15;
const VIDEO_BITRATE = 150_000; // ~150 kbps, volontairement bas
const CHUNK_INTERVAL_MS = 500;
const MIME_TYPE = "video/webm;codecs=vp8";

export interface LiveVideoCapture {
  startCapture(onChunk: (bytes: ArrayBuffer) => void): Promise<void>;
  stopCapture(): void;
  /** Flux vidéo local, pour un aperçu "vous" côté candidat/examinateur. */
  getLocalStream(): MediaStream | null;
}

export function createLiveVideoCapture(): LiveVideoCapture {
  let stream: MediaStream | null = null;
  let recorder: MediaRecorder | null = null;

  async function startCapture(onChunk: (bytes: ArrayBuffer) => void): Promise<void> {
    if (recorder) return; // déjà en capture — no-op

    if (!MediaRecorder.isTypeSupported(MIME_TYPE)) {
      throw new Error(`Format vidéo non supporté par ce navigateur : ${MIME_TYPE}`);
    }

    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: VIDEO_WIDTH },
        height: { ideal: VIDEO_HEIGHT },
        frameRate: { ideal: VIDEO_FRAMERATE },
      },
      audio: false, // le son passe par le pipeline PCM16 séparé, jamais ici
    });

    recorder = new MediaRecorder(stream, {
      mimeType: MIME_TYPE,
      videoBitsPerSecond: VIDEO_BITRATE,
    });

    recorder.ondataavailable = async (event: BlobEvent) => {
      if (event.data.size === 0) return;
      const buffer = await event.data.arrayBuffer();
      onChunk(buffer);
    };

    recorder.start(CHUNK_INTERVAL_MS);
  }

  function stopCapture(): void {
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
    recorder = null;

    stream?.getTracks().forEach((track) => track.stop());
    stream = null;
  }

  function getLocalStream(): MediaStream | null {
    return stream;
  }

  return { startCapture, stopCapture, getLocalStream };
}

// ─── Lecture du flux entrant (côté pair) ───────────────────────────────

export interface LiveVideoPlayback {
  /** Attache la lecture à une balise <video> fournie par le composant. */
  attach(videoEl: HTMLVideoElement): void;
  /** Ajoute un chunk vidéo reçu du pair au flux en cours de lecture. */
  pushChunk(bytes: ArrayBuffer): void;
  stop(): void;
}

export function createLiveVideoPlayback(): LiveVideoPlayback {
  let mediaSource: MediaSource | null = null;
  let sourceBuffer: SourceBuffer | null = null;
  let videoElement: HTMLVideoElement | null = null;
  // Chunks arrivés avant que le SourceBuffer soit prêt (sourceopen async)
  // — mis en attente puis vidés dès que possible, pour ne rien perdre.
  const pendingChunks: ArrayBuffer[] = [];

  function attach(videoEl: HTMLVideoElement): void {
    videoElement = videoEl;
    mediaSource = new MediaSource();
    videoEl.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener("sourceopen", () => {
      if (!mediaSource) return;
      sourceBuffer = mediaSource.addSourceBuffer(MIME_TYPE);
      sourceBuffer.addEventListener("updateend", flushPending);
      flushPending();
      void videoEl.play().catch(() => {
        // L'autoplay peut être bloqué tant que l'utilisateur n'a pas
        // interagi avec la page — pas fatal, la vidéo démarrera au
        // premier clic/interaction si le navigateur l'exige.
      });
    });
  }

  function flushPending(): void {
    if (!sourceBuffer || sourceBuffer.updating) return;
    const next = pendingChunks.shift();
    if (next) {
      try {
        sourceBuffer.appendBuffer(next);
      } catch (err) {
        console.error("Erreur ajout chunk vidéo:", err);
      }
    }
  }

  function pushChunk(bytes: ArrayBuffer): void {
    pendingChunks.push(bytes);
    flushPending();
  }

  function stop(): void {
    if (videoElement) {
      videoElement.pause();
      videoElement.removeAttribute("src");
      videoElement.load();
    }
    if (mediaSource && mediaSource.readyState === "open") {
      try {
        mediaSource.endOfStream();
      } catch {
        // ignore — peut déjà être dans un état incompatible
      }
    }
    mediaSource = null;
    sourceBuffer = null;
    videoElement = null;
    pendingChunks.length = 0;
  }

  return { attach, pushChunk, stop };
}