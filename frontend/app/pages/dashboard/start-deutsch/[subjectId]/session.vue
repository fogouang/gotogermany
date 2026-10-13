<!-- pages/dashboard/start-deutsch/[subjectId]/session.vue -->
<template>
  <div class="pb-10">
    <!-- ── Chargement ── -->
    <div v-if="store.loading" class="space-y-4 px-4 pt-6">
      <div class="h-16 animate-pulse rounded-card bg-card-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <template v-else>
      <SessionHeader
        :exam-name="store.subjectTitle"
        :subject-number="store.subjectNumber ?? 0"
        :module-name="currentModuleLabel"
        :teil-label="teilLabel"
        :step-index="currentTeilIndexInModule"
        :step-count="store.currentModule?.teile?.length ?? 0"
        :answered="answeredInModule"
        :total="questionsInCurrentModule.length"
        :time-remaining="timeRemainingForCurrentModule"
        :can-font-down="fontStep > 0"
        :can-font-up="fontStep < FONT_SCALES.length - 1"
        @font="(delta) => setFontStep(fontStep + delta)"
        @exit="handleExit"
      />

      <div class="space-y-6 px-4 pt-6">
        <!-- Onglets modules -->
        <div class="flex gap-2 overflow-x-auto">
          <button
            v-for="(mod, index) in store.modules"
            :key="mod.id"
            type="button"
            class="shrink-0 rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
            :class="
              store.currentModuleIndex === index
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-line bg-card text-muted hover:border-primary/30 hover:text-ink'
            "
            @click="store.switchToModule(index)"
          >
            {{ moduleLabel(mod.slug) }}
          </button>
        </div>

        <!-- Progression, numérotée par module (ex. Lesen : question 3 sur 15) -->
        <div>
          <p class="text-sm font-semibold text-muted">
            {{
              t("start_deutsch.session.progress", {
                current: currentQuestionIndexInModule + 1,
                total: questionsInCurrentModule.length,
              })
            }}
          </p>
          <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-card-2">
            <div
              class="h-full rounded-full bg-primary transition-[width] duration-300"
              :style="{ width: `${moduleProgressPercent}%` }"
            />
          </div>
        </div>

        <!-- Consigne + audio du Teil courant -->
        <div
          v-if="store.currentTeil"
          class="rounded-card border border-line bg-card p-4 shadow-soft"
        >
          <p class="mb-1 text-xs font-bold uppercase tracking-wide text-faint">
            Teil {{ store.currentTeil.teil_number }}
          </p>
          <p v-if="store.currentTeil.instructions" class="text-sm text-muted">
            {{ store.currentTeil.instructions }}
          </p>
          <audio
            v-if="store.currentTeil.audio_file"
            class="mt-3 w-full"
            controls
            :src="resolveAudioUrl(store.currentTeil.audio_file)"
          />
        </div>

        <!-- Question courante -->
        <QuestionRenderer
          v-if="store.currentQuestion && store.currentTeil"
          :question="store.currentQuestion"
          :teil="store.currentTeil"
          :assets-base-url="assetsBaseUrl"
          :level="store.level"
          :subject-number="store.subjectNumber"
          :used-labels="usedLabelsInCurrentTeil"
          :model-value="store.currentAnswer?.user_answer ?? null"
          @update:model-value="onAnswer"
        />

        <!-- Navigation -->
        <div class="flex items-center justify-between gap-3">
          <Button
            :label="t('start_deutsch.session.previous')"
            icon="pi pi-arrow-left"
            outlined
            :disabled="store.isFirstQuestion"
            @click="store.previousQuestion"
          />
          <Button
            v-if="!store.isLastQuestion"
            :label="t('start_deutsch.session.next')"
            icon="pi pi-arrow-right"
            icon-pos="right"
            @click="store.nextQuestion"
          />
          <Button
            v-else
            :label="t('start_deutsch.session.submit')"
            icon="pi pi-check"
            icon-pos="right"
            :loading="store.isSubmitting"
            @click="handleSubmit"
          />
        </div>

        <!-- PDF Schreiben : seulement sur ce module -->
        <SchreibenDownloadButton
          v-if="store.currentModule?.slug === 'schreiben'"
          :subject-title="store.subjectTitle"
          :level="store.level"
          :student-name="authStore.userName"
          :teile="store.currentModule?.teile ?? []"
          :answers="store.answers"
          :time-expired="timeRemainingForCurrentModule === 0"
        />

        <!-- Navigateur de questions du module courant -->
        <div class="flex flex-wrap justify-center gap-1.5 pt-2">
          <button
            v-for="q in questionsInCurrentModule"
            :key="q.id"
            type="button"
            class="size-2.5 rounded-full transition-colors"
            :class="
              q.id === store.currentQuestion?.id
                ? 'bg-primary'
                : store.isAnswered(q.id)
                  ? 'bg-primary/40'
                  : 'border border-line bg-card-2'
            "
            @click="goToQuestionById(q.id)"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import QuestionRenderer from "~/components/start-deutsch/QuestionRenderer.vue";
import SchreibenDownloadButton from "~/components/start-deutsch/SchreibenDownloadButton.vue";
import SessionHeader from "~/components/session/SessionHeader.vue";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const store = useStartDeutschSessionStore();
const authStore = useAuthStore();
const config = useRuntimeConfig();

const assetsBaseUrl = computed(
  () => `${config.public.apiBaseUrl || "http://localhost:8001"}/start-deutsch`,
);

function resolveAudioUrl(audioFile: string) {
  return `${assetsBaseUrl.value}/${audioFile}`;
}

const moduleLabels: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
};

function moduleLabel(slug: string) {
  return moduleLabels[slug] ?? slug;
}

const currentModuleLabel = computed(() =>
  moduleLabel(store.currentModule?.slug ?? ""),
);

const teilLabel = computed(() =>
  store.currentTeil ? `Teil ${store.currentTeil.teil_number}` : "",
);

// ── Numérotation par module ──
// Le store garde la liste globale des questions ; la page la refiltre
// sur le module actif sans toucher au store.
const questionsInCurrentModule = computed(() =>
  (store.currentModule?.teile ?? []).flatMap(
    (teil: any) => teil.questions ?? [],
  ),
);

const currentQuestionIndexInModule = computed(() =>
  questionsInCurrentModule.value.findIndex(
    (q: any) => q.id === store.currentQuestion?.id,
  ),
);

const answeredInModule = computed(
  () =>
    questionsInCurrentModule.value.filter((q: any) => store.isAnswered(q.id))
      .length,
);

const moduleProgressPercent = computed(() => {
  const total = questionsInCurrentModule.value.length;
  if (!total) return 0;
  return ((currentQuestionIndexInModule.value + 1) / total) * 100;
});

const currentTeilIndexInModule = computed(() =>
  (store.currentModule?.teile ?? []).findIndex(
    (teil: any) => teil.id === store.currentTeil?.id,
  ),
);

function goToQuestionById(questionId: string) {
  const globalIndex = store.questions.findIndex(
    (q: any) => q.id === questionId,
  );
  if (globalIndex !== -1) store.goToQuestion(globalIndex);
}

// ── Taille du texte : même réglage que le lecteur principal ──
const FONT_SCALES = [0.9, 1, 1.1, 1.25, 1.4];
const FONT_KEY = "gtg_exam_font";
const fontStep = ref(1);

function setFontStep(step: number) {
  fontStep.value = Math.min(Math.max(step, 0), FONT_SCALES.length - 1);
  try {
    localStorage.setItem(FONT_KEY, String(fontStep.value));
  } catch {
    /* stockage indisponible */
  }
}

function applyFontScale() {
  if (import.meta.client) {
    document.documentElement.style.fontSize = `${(FONT_SCALES[fontStep.value] ?? 1) * 100}%`;
  }
}

watch(fontStep, applyFontScale);

function restoreFontStep() {
  try {
    const raw = localStorage.getItem(FONT_KEY);
    if (raw === null) return;
    const v = Number(raw);
    if (Number.isInteger(v) && v >= 0 && v < FONT_SCALES.length)
      fontStep.value = v;
  } catch {
    /* ignore */
  }
}

// ── Minuteur par module ──
// Durées officielles Goethe (Start Deutsch 1 / Goethe-Zertifikat A2), côté
// front uniquement. Changer d'onglet met en pause le module quitté.
const MODULE_DURATIONS_MINUTES: Record<string, Record<string, number>> = {
  A1: { lesen: 25, hoeren: 20, schreiben: 20, sprechen: 15 },
  A2: { lesen: 30, hoeren: 30, schreiben: 30, sprechen: 15 },
};

const secondsRemainingByModule = reactive<Record<number, number>>({});
let timerInterval: ReturnType<typeof setInterval> | null = null;

function initModuleTimers() {
  store.modules.forEach((mod: any, index: number) => {
    if (secondsRemainingByModule[index] === undefined) {
      const minutes = MODULE_DURATIONS_MINUTES[store.level]?.[mod.slug] ?? 20;
      secondsRemainingByModule[index] = minutes * 60;
    }
  });
}

const timeRemainingForCurrentModule = computed(
  () => secondsRemainingByModule[store.currentModuleIndex] ?? 0,
);

function startTimerLoop() {
  timerInterval = setInterval(() => {
    const idx = store.currentModuleIndex;
    const current = secondsRemainingByModule[idx];
    if (current !== undefined && current > 0) {
      secondsRemainingByModule[idx] = current - 1;
    }
  }, 1000);
}

// PDF Schreiben automatique quand le temps est écoulé : géré par
// SchreibenDownloadButton (prop time-expired), une seule fois.
const schreibenAutoDownloaded = ref(false);

function onModuleTimeUp(moduleIndex: number) {
  const mod = store.modules[moduleIndex];
  if (mod?.slug !== "schreiben" || schreibenAutoDownloaded.value) return;

  schreibenAutoDownloaded.value = true;
  const { download } = useSchreibenPdf();
  download({
    subjectTitle: store.subjectTitle,
    level: store.level,
    studentName: authStore.userName,
    teile: mod.teile ?? [],
    answers: store.answers,
  });
}

function handleExit() {
  navigateTo(localePath("/dashboard/start-deutsch"));
}

// image_day_matching : lettres déjà choisies par les autres questions du Teil
const usedLabelsInCurrentTeil = computed(() => {
  const teil = store.currentTeil;
  if (!teil) return [];
  return (teil.questions ?? [])
    .filter((q: any) => q.id !== store.currentQuestion?.id)
    .map((q: any) => store.answers[q.id]?.user_answer?.answer)
    .filter((label: any): label is string => !!label);
});

function onAnswer(value: Record<string, any>) {
  if (!store.currentQuestion) return;
  store.setAnswer(store.currentQuestion.id, value);
}

async function handleSubmit() {
  const result = await store.submitSession();
  if (!result.success) return;

  // Correction IA de chaque Teil free_text répondu : pas déclenchée par le
  // serveur à la soumission, on l'appelle ici avant d'aller au résultat
  const freeTextTeile = store.modules
    .flatMap((m: any) => m.teile ?? [])
    .filter((teil: any) => teil.format_type === "free_text");

  for (const teil of freeTextTeile) {
    const question = teil.questions?.[0];
    const text = question
      ? store.answers[question.id]?.user_answer?.text
      : undefined;
    if (question && text) await store.correctSchreiben(teil.id, text);
  }

  if (timerInterval) clearInterval(timerInterval);
  navigateTo({
    path: localePath(
      `/dashboard/start-deutsch/${route.params.subjectId}/result`,
    ),
    query: { sessionId: String(store.sessionId) },
  });
}

onMounted(async () => {
  restoreFontStep();
  applyFontScale();

  const subjectId = route.params.subjectId as string;
  if (store.sessionId === null || store.subjectId !== subjectId) {
    await store.startSession(subjectId);
  }
  initModuleTimers();
  startTimerLoop();
});

onBeforeUnmount(() => {
  if (timerInterval) clearInterval(timerInterval);
  if (import.meta.client) document.documentElement.style.fontSize = "";
});
</script>
