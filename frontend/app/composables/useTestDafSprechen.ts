/**
 * composables/useTestDafSprechen.ts
 * ===================================
 * Sprechen TestDaF en mode enregistré, fidèle au TestDaF digital.
 * Tout le déroulé vit ici ; la page ne fait que l'affichage.
 *
 * Pour chaque tâche : graphique à regarder, déclaration audio du
 * camarade, préparation imposée, question de l'interlocuteur, puis
 * enregistrement coupé à la fin du temps de parole. Les 7 tâches
 * s'enchaînent sans pause, comme à l'examen.
 *
 * Appels API : TestdafSprechenService (client généré), configuré via
 * authStore._ensureApiConfig() comme le reste de l'app.
 * Backend : app/modules/testdaf_sprechen.
 */

import { computed, ref } from "vue";
import { OpenAPI, TestdafSprechenService } from "#shared/api";
import type { GradingResponse, TestDafTaskOut } from "#shared/api";
import { createBrowserAudioIO } from "~/composables/audioIO";

export type TestDafStage =
  | "intro"
  | "starting"
  | "running"
  | "grading"
  | "result"
  | "error";
export type TestDafPhase =
  | "grafik"
  | "listen"
  | "prep"
  | "question"
  | "speaking";
export type TestDafErrorCode =
  | "mic"
  | "insufficient_credits"
  | "start"
  | "finish";

// Taux d'échantillonnage des trames PCM16 fournies par audioIO : le même
// que pour l'oral Gemini (live_client.GEMINI_INPUT_SAMPLE_RATE).
const CAPTURE_SAMPLE_RATE = 16000;
const QUESTION_AUDIO_MAX_SECONDS = 30;

// PCM16 mono -> WAV (format lu directement par Gemini, contrairement au webm)
function buildWav(chunks: Uint8Array[], sampleRate: number): Blob {
  const dataLength = chunks.reduce((sum, c) => sum + c.byteLength, 0);
  const buffer = new ArrayBuffer(44 + dataLength);
  const view = new DataView(buffer);
  const writeString = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i++)
      view.setUint8(offset + i, value.charCodeAt(i));
  };
  writeString(0, "RIFF");
  view.setUint32(4, 36 + dataLength, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, dataLength, true);
  let offset = 44;
  for (const chunk of chunks) {
    new Uint8Array(buffer, offset, chunk.byteLength).set(chunk);
    offset += chunk.byteLength;
  }
  return new Blob([buffer], { type: "audio/wav" });
}

export function useTestDafSprechen(subjectId: string) {
  const authStore = useAuthStore();
  const tokenCookie = useCookie("access_token");
  const audioIO = createBrowserAudioIO({ muteMicWhilePlaying: false });

  // ── État exposé ──
  const stage = ref<TestDafStage>("intro");
  const errorCode = ref<TestDafErrorCode | null>(null);
  const sessionId = ref<string | null>(null);
  const tasks = ref<TestDafTaskOut[]>([]);
  const taskIndex = ref(0);
  const phase = ref<TestDafPhase>("prep");
  const secondsLeft = ref(0);
  const phaseTotal = ref(0);
  const textVisible = ref(true);
  const uploadWarning = ref(false);
  const result = ref<GradingResponse | null>(null);

  const currentTask = computed(() => tasks.value[taskIndex.value] ?? null);
  const showCountdown = computed(() =>
    ["grafik", "prep", "speaking"].includes(phase.value),
  );
  const progressPercent = computed(() =>
    phaseTotal.value
      ? Math.round(
          ((phaseTotal.value - secondsLeft.value) / phaseTotal.value) * 100,
        )
      : 0,
  );

  // ── État interne ──
  let aborted = false;
  let stopRequested = false;
  let currentAudio: HTMLAudioElement | null = null;
  let capturedChunks: Uint8Array[] = [];
  const uploads: Promise<void>[] = [];

  const token = () => tokenCookie.value ?? undefined;

  // ── Outils de déroulé ──
  const tick = () => new Promise((resolve) => setTimeout(resolve, 200));

  async function countdown(
    seconds: number,
    onTick?: () => void,
    stopEarly?: () => boolean,
  ) {
    phaseTotal.value = seconds;
    const end = Date.now() + seconds * 1000;
    while (!aborted) {
      secondsLeft.value = Math.max(0, Math.ceil((end - Date.now()) / 1000));
      onTick?.();
      if (secondsLeft.value <= 0 || stopEarly?.()) return;
      await tick();
    }
  }

  function playUrl(url: string, maxSeconds: number): Promise<void> {
    return new Promise((resolve) => {
      const audio = new Audio(url);
      currentAudio = audio;
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolve();
      };
      const timer = setTimeout(done, maxSeconds * 1000);
      audio.onended = done;
      audio.onerror = done;
      audio.play().catch(done);
    });
  }

  async function uploadRecording(teilNumber: number, wav: Blob) {
    const send = () =>
      TestdafSprechenService.uploadTestdafRecordingApiV1TestdafSprechenSessionsSessionIdTasksTeilNumberRecordingPost(
        sessionId.value!,
        teilNumber,
        // Le générateur type les fichiers en string (OpenAPI 3.1 de FastAPI) ;
        // le client généré envoie bien le Blob tel quel dans le FormData.
        { file: wav as unknown as string },
        token(),
      );
    try {
      await send();
    } catch {
      try {
        await send(); // une nouvelle tentative
      } catch {
        uploadWarning.value = true;
      }
    }
  }

  // ── Déroulé d'une tâche ──
  async function runTask(task: TestDafTaskOut) {
    const taskStart = Date.now();
    const hideAfter = task.stimulus_hidden_after_seconds ?? null;
    textVisible.value = !!task.stimulus_text;
    const updateText = () => {
      if (hideAfter != null && (Date.now() - taskStart) / 1000 >= hideAfter)
        textVisible.value = false;
    };

    // 1. Graphique à regarder (il reste affiché ensuite)
    if (task.grafik && task.grafik_seconds) {
      phase.value = "grafik";
      await countdown(task.grafik_seconds, updateText);
    }

    // 2. Déclaration du camarade (tâches 4 et 6)
    const statementUrls = task.statement_audio_urls ?? [];
    if (statementUrls.length && !aborted) {
      phase.value = "listen";
      phaseTotal.value = 0;
      for (const url of statementUrls) {
        if (aborted) return;
        await playUrl(url, (task.listen_seconds ?? 60) + 15);
      }
    }

    // 3. Préparation imposée
    if (aborted) return;
    phase.value = "prep";
    await countdown(task.prep_seconds, updateText);
    if (hideAfter != null) textVisible.value = false;

    // 4. Question de l'interlocuteur
    if (task.question_audio_url && !aborted) {
      phase.value = "question";
      phaseTotal.value = 0;
      await playUrl(task.question_audio_url, QUESTION_AUDIO_MAX_SECONDS);
    }

    // 5. Enregistrement, coupé à la fin du temps de parole
    if (aborted) return;
    phase.value = "speaking";
    stopRequested = false;
    capturedChunks = [];
    await audioIO.startCapture((chunk) =>
      capturedChunks.push(new Uint8Array(chunk)),
    );
    await countdown(task.speak_seconds, undefined, () => stopRequested);
    audioIO.stopCapture();
    if (aborted) return;

    uploads.push(
      uploadRecording(
        task.teil_number,
        buildWav(capturedChunks, CAPTURE_SAMPLE_RATE),
      ),
    );
  }

  async function runExam() {
    for (let i = 0; i < tasks.value.length; i++) {
      if (aborted) return;
      taskIndex.value = i;
      await runTask(tasks.value[i]!);
    }
    if (aborted) return;

    stage.value = "grading";
    await Promise.allSettled(uploads);
    try {
      authStore._ensureApiConfig();
      result.value =
        await TestdafSprechenService.finishTestdafSessionApiV1TestdafSprechenSessionsSessionIdFinishPost(
          sessionId.value!,
          token(),
        );
      stage.value = "result";
    } catch {
      errorCode.value = "finish";
      stage.value = "error";
    }
    void authStore.fetchUser();
  }

  // ── Actions ──
  async function start() {
    stage.value = "starting";
    errorCode.value = null;

    // Micro vérifié AVANT de débiter les crédits
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch {
      errorCode.value = "mic";
      stage.value = "error";
      return;
    }

    try {
      authStore._ensureApiConfig();
      const response =
        await TestdafSprechenService.startTestdafSessionApiV1TestdafSprechenSessionsPost(
          { subject_id: subjectId },
          token(),
        );
      sessionId.value = response.session_id;
      tasks.value = response.tasks;
    } catch (error: any) {
      // Affiche la vraie cause dans la console du navigateur (F12 > Console)
      console.error("TestDaF start error:", error);
      errorCode.value =
        error?.status === 402 ? "insufficient_credits" : "start";
      stage.value = "error";
      return;
    }

    void authStore.fetchUser(); // solde de crédits à jour
    stage.value = "running";
    void runExam();
  }

  function finishSpeakingEarly() {
    stopRequested = true;
  }

  function stopEverything() {
    aborted = true;
    currentAudio?.pause();
    currentAudio = null;
    audioIO.stopCapture();
  }

  /** Abandon : crédits rendus côté serveur. keepalive=true quand la page
   * se ferme (le client généré ne sait pas faire de requête keepalive,
   * d'où le fetch direct dans ce seul cas). */
  function abandon(keepalive = false) {
    const id = sessionId.value;
    if (!id || stage.value !== "running") {
      stopEverything();
      return;
    }
    stopEverything();
    if (keepalive) {
      void fetch(
        `${OpenAPI.BASE}/api/v1/testdaf-sprechen/sessions/${id}/abandon`,
        {
          method: "POST",
          headers: tokenCookie.value
            ? { Authorization: `Bearer ${tokenCookie.value}` }
            : undefined,
          keepalive: true,
        },
      ).catch(() => {});
      return;
    }
    authStore._ensureApiConfig();
    void TestdafSprechenService.abandonTestdafSessionApiV1TestdafSprechenSessionsSessionIdAbandonPost(
      id,
      token(),
    ).catch(() => {});
  }

  return {
    // état
    stage,
    errorCode,
    tasks,
    taskIndex,
    currentTask,
    phase,
    secondsLeft,
    showCountdown,
    progressPercent,
    textVisible,
    uploadWarning,
    result,
    // actions
    start,
    finishSpeakingEarly,
    abandon,
  };
}
