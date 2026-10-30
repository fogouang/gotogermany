<!-- components/start-deutsch/StartDeutschPlayer.vue -->
<!--
  Lecteur Start Deutsch, même présentation et même déroulé que le lecteur des B :
  plein écran, en-tête, onglets des modules, un Teil par écran.
  Les modules se passent l'un après l'autre, chacun avec son temps officiel :
  on ne revient pas sur un module terminé, un écran de transition annonce le suivant.
  - Entraînement (subjectId) : à la fin, correction IA du Schreiben puis résultat.
  - Devoir (assignmentId) : pas de Sprechen, pas d'IA, écran « Devoir rendu ».
-->
<template>
  <div class="flex h-screen flex-col overflow-hidden bg-canvas">
    <!-- ── Chargement ── -->
    <div
      v-if="!initialized || store.loading"
      class="flex flex-1 items-center justify-center"
    >
      <div class="text-center">
        <i class="pi pi-spin pi-spinner text-3xl text-primary" />
        <p class="mt-4 text-sm text-muted">{{ t("session.loading") }}</p>
      </div>
    </div>

    <!-- ── Devoir rendu ── -->
    <div
      v-else-if="submitted"
      class="flex flex-1 items-center justify-center p-4"
    >
      <div
        class="w-full max-w-md rounded-card border border-line bg-card p-8 text-center shadow-soft"
      >
        <span
          class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600"
        >
          <i class="pi pi-check-circle text-3xl" />
        </span>
        <h1 class="text-xl font-bold text-ink">
          {{ t("student_assignments.submitted_title") }}
        </h1>
        <p class="mt-2 text-sm text-muted">
          {{
            autoGraded
              ? t("student_assignments.submitted_auto")
              : t("student_assignments.submitted_teacher")
          }}
        </p>
        <Button
          :label="t('student_assignments.sheet.view')"
          icon="pi pi-file"
          class="mt-6 w-full"
          @click="
            navigateTo(
              localePath({
                path: '/dashboard/devoirs',
                query: { releve: assignmentId },
              }),
            )
          "
        />
        <Button
          :label="t('student_assignments.back')"
          icon="pi pi-arrow-left"
          text
          class="mt-2 w-full"
          @click="leave"
        />
      </div>
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="store.error && !store.sessionId"
      class="flex flex-1 items-center justify-center p-4"
    >
      <div
        class="w-full max-w-md rounded-card border border-line bg-card p-8 text-center shadow-soft"
      >
        <span
          class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-red-500/10 text-red-600"
        >
          <i class="pi pi-exclamation-triangle text-2xl" />
        </span>
        <h1 class="text-lg font-bold text-ink">{{ t("session.error") }}</h1>
        <p class="mt-2 text-sm text-muted">{{ store.error }}</p>
        <Button
          :label="t('start_deutsch.result.back')"
          icon="pi pi-arrow-left"
          outlined
          class="mt-6 w-full"
          @click="leave"
        />
      </div>
    </div>

    <!-- ── Entre deux modules ── -->
    <div
      v-else-if="phase === 'transition'"
      class="flex flex-1 items-center justify-center overflow-y-auto px-4 py-10"
    >
      <div
        class="w-full max-w-lg rounded-card border border-line bg-card p-6 text-center shadow-soft sm:p-8"
      >
        <div
          class="mx-auto mb-4 flex size-14 items-center justify-center rounded-full bg-emerald-500/10"
        >
          <i class="pi pi-check text-xl text-emerald-600" />
        </div>
        <h2 class="text-xl font-bold text-ink">
          {{
            t("session.player.transition_done", {
              name: moduleLabel(currentModule?.slug),
            })
          }}
        </h2>
        <p v-if="moduleQuestions.length" class="mt-1 text-sm text-muted">
          {{
            t("session.player.answered", {
              answered: moduleAnswered,
              total: moduleQuestions.length,
            })
          }}
        </p>

        <div
          v-if="nextModule"
          class="mt-6 rounded-leaf border border-line bg-card-2 p-4 text-left"
        >
          <p class="text-xs font-semibold uppercase tracking-wide text-faint">
            {{ t("session.player.transition_next") }}
          </p>
          <p class="mt-1 flex items-center gap-2 font-semibold text-ink">
            <i class="pi text-sm text-primary" :class="moduleIcon(nextModule.slug)" />
            {{ moduleLabel(nextModule.slug) }}
          </p>
          <p class="mt-0.5 text-sm text-muted">
            <i class="pi pi-clock mr-1 text-xs" />
            {{ t("session.player.intro_minutes", { n: minutesOf(nextModule) }) }}
          </p>
        </div>

        <Button
          class="mt-6 w-full"
          :label="t('session.player.transition_start')"
          icon="pi pi-play"
          @click="startModule(moduleIndex + 1)"
        />
      </div>
    </div>

    <!-- ── Lecteur ── -->
    <template v-else-if="currentModule && currentTeil">
      <SessionHeader
        class="shrink-0"
        :exam-name="store.subjectTitle"
        :subject-number="store.subjectNumber ?? 0"
        :module-name="moduleLabel(currentModule.slug)"
        :teil-label="`Teil ${currentTeil.teil_number}`"
        :step-index="stepIndex"
        :step-count="currentModule.teile?.length ?? 0"
        :steps="headerSteps"
        :answered="moduleAnswered"
        :total="moduleQuestions.length"
        :time-remaining="timeRemaining"
        :can-font-down="fontStep > 0"
        :can-font-up="fontStep < FONT_SCALES.length - 1"
        @goto="goToStep"
        @font="(delta) => setFontStep(fontStep + delta)"
        @exit="exitDialogVisible = true"
      />

      <!-- Modules : seul celui en cours est ouvert -->
      <div class="shrink-0 border-b border-line bg-card">
        <div class="mx-auto flex max-w-7xl overflow-x-auto px-4">
          <button
            v-for="(mod, mi) in modules"
            :key="mod.id"
            type="button"
            :disabled="mi !== moduleIndex"
            class="whitespace-nowrap border-b-2 px-5 py-3 text-sm font-medium transition-colors disabled:cursor-not-allowed"
            :class="tabClass(mi)"
          >
            <i class="pi mr-2" :class="tabIcon(mod.slug, mi)" />
            {{ moduleLabel(mod.slug) }}
          </button>
        </div>
      </div>

      <div ref="scrollArea" class="min-h-0 flex-1 overflow-y-auto">
        <div class="mx-auto max-w-7xl space-y-5 px-4 py-6">
          <!-- Consigne et audio du Teil -->
          <div class="rounded-card border border-line bg-card p-4 shadow-soft sm:p-5">
            <p class="text-xs font-bold uppercase tracking-wide text-faint">
              {{ moduleLabel(currentModule.slug) }} · Teil {{ currentTeil.teil_number }}
            </p>
            <p
              v-if="currentTeil.instructions"
              class="mt-1.5 whitespace-pre-line text-sm leading-relaxed text-ink"
            >
              {{ currentTeil.instructions }}
            </p>
            <audio
              v-if="currentTeil.audio_file"
              :key="currentTeil.id"
              class="mt-3 w-full"
              controls
              preload="metadata"
              :src="`${assetsBaseUrl}/${currentTeil.audio_file}`"
            />
          </div>

          <!-- Liste commune (images ou annonces) affichée une fois -->
          <PoolMatchingBlock
            v-if="isPoolTeil"
            :teil="currentTeil"
            :questions="teilQuestions"
            :answers="store.answers"
            :assets-base-url="assetsBaseUrl"
            :level="store.level"
            :subject-number="store.subjectNumber"
            @answer="(qid, value) => store.setAnswer(qid, value)"
          />

          <!-- Texte commun à gauche (fixe), questions à droite -->
          <div
            v-else
            :class="
              sharedText ? 'lg:grid lg:grid-cols-2 lg:items-start lg:gap-6' : ''
            "
          >
            <div
              v-if="sharedText"
              class="mb-5 whitespace-pre-line rounded-card border border-line bg-card p-5 text-[15px] leading-relaxed text-ink shadow-soft lg:sticky lg:top-4 lg:mb-0 lg:max-h-[calc(100dvh-12rem)] lg:overflow-y-auto"
            >
              {{ sharedText }}
            </div>

            <!-- Sans texte commun (Hören, panneaux) : questions sur deux colonnes -->
            <div
              :class="
                !sharedText && teilQuestions.length > 1
                  ? 'grid items-start gap-4 lg:grid-cols-2'
                  : 'space-y-4'
              "
            >
              <div
                v-for="q in teilQuestions"
                :id="`question-${q.id}`"
                :key="q.id"
                class="flex items-start gap-3"
              >
                <span
                  v-if="teilQuestions.length > 1"
                  class="mt-4 inline-flex h-6 min-w-6 shrink-0 items-center justify-center rounded-full border px-1.5 text-[11px] font-bold tabular-nums"
                  :class="
                    store.isAnswered(q.id)
                      ? 'border-primary bg-primary text-white'
                      : 'border-line bg-card-2 text-ink'
                  "
                  >{{ q.question_number }}</span
                >
                <div class="min-w-0 flex-1">
                  <QuestionRenderer
                    :question="q"
                    :teil="teilForQuestions"
                    :assets-base-url="assetsBaseUrl"
                    :level="store.level"
                    :subject-number="store.subjectNumber"
                    :model-value="store.answers[q.id]?.user_answer ?? null"
                    @update:model-value="(v) => store.setAnswer(q.id, v)"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- PDF Schreiben (entraînement) : visible quand les deux tâches sont faites -->
          <SchreibenDownloadButton
            v-if="!isAssignment && currentModule.slug === 'schreiben'"
            :subject-title="store.subjectTitle"
            :level="store.level"
            :student-name="authStore.userName"
            :teile="currentModule.teile ?? []"
            :answers="store.answers"
            :time-expired="timeRemaining === 0"
          />
        </div>
      </div>

      <SessionFooter
        class="shrink-0"
        :can-prev="stepIndex > 0"
        :is-last-step="isLastStep"
        :finish-label="
          isLastModule ? t('session.submit') : t('session.player.finish_module')
        "
        :answered="moduleAnswered"
        :total="moduleQuestions.length"
        @prev="goToStep(stepIndex - 1)"
        @next="goToStep(stepIndex + 1)"
        @finish="submitDialogVisible = true"
        @sheet="sheetVisible = true"
      />
    </template>

    <!-- ══════════ Feuille de réponses (module en cours) ══════════ -->
    <SessionAnswerSheet
      v-model:visible="sheetVisible"
      :groups="sheetGroups"
      @go="
        (idx) => {
          goToStep(idx);
          sheetVisible = false;
        }
      "
    />

    <!-- ══════════ Quitter ══════════ -->
    <Dialog
      v-model:visible="exitDialogVisible"
      :header="t('session.exit_title')"
      modal
      :style="{ width: '26rem', maxWidth: '95vw' }"
    >
      <Message v-if="isAssignment" severity="info" :closable="false">{{
        t("student_assignments.exit_warning")
      }}</Message>
      <template #footer>
        <Button
          :label="t('session.cancel')"
          text
          severity="secondary"
          @click="exitDialogVisible = false"
        />
        <Button :label="t('session.quit')" severity="warn" @click="leave" />
      </template>
    </Dialog>

    <!-- ══════════ Terminer le module / rendre ══════════ -->
    <Dialog
      v-model:visible="submitDialogVisible"
      :header="
        isLastModule
          ? t('session.submit_title')
          : t('session.player.finish_module_title')
      "
      modal
      :style="{ width: '26rem', maxWidth: '95vw' }"
    >
      <p v-if="moduleQuestions.length" class="mb-3 text-sm text-ink">
        {{
          t("session.player.answered", {
            answered: moduleAnswered,
            total: moduleQuestions.length,
          })
        }}
      </p>
      <Message v-if="moduleUnanswered > 0" severity="warn" :closable="false">
        {{ t("session.player.unanswered", { n: moduleUnanswered }, moduleUnanswered) }}
      </Message>
      <p v-if="!isLastModule" class="mt-3 text-sm text-muted">
        {{ t("session.player.finish_module_text") }}
      </p>
      <Message
        v-if="submitError"
        severity="error"
        :closable="false"
        class="mt-3"
        >{{ submitError }}</Message
      >
      <template #footer>
        <Button
          :label="t('session.continue')"
          text
          severity="secondary"
          @click="submitDialogVisible = false"
        />
        <Button
          :label="
            isLastModule ? t('session.submit') : t('session.player.finish_module')
          "
          severity="success"
          :loading="store.isSubmitting || correcting"
          @click="confirmFinish"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import QuestionRenderer from "~/components/start-deutsch/QuestionRenderer.vue";
import PoolMatchingBlock from "~/components/start-deutsch/PoolMatchingBlock.vue";
import SchreibenDownloadButton from "~/components/start-deutsch/SchreibenDownloadButton.vue";
import SessionHeader from "~/components/session/SessionHeader.vue";
import SessionFooter from "~/components/session/SessionFooter.vue";
import SessionAnswerSheet from "~/components/session/SessionAnswerSheet.vue";

const props = defineProps<{
  /** Entraînement : sujet du catalogue */
  subjectId?: string;
  /** Devoir : copie créée par le module des devoirs */
  assignmentId?: string;
}>();

const { t } = useI18n();
const localePath = useLocalePath();
const store = useStartDeutschSessionStore();
const authStore = useAuthStore();
const notify = useNotify();
const config = useRuntimeConfig();

const isAssignment = computed(() => !!props.assignmentId);

const assetsBaseUrl = computed(
  () => `${config.public.apiBaseUrl || "http://localhost:8001"}/start-deutsch`,
);

// ── Libellés ──
const MODULE_LABELS: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
};
const MODULE_ICONS: Record<string, string> = {
  lesen: "pi-book",
  hoeren: "pi-volume-up",
  schreiben: "pi-pencil",
  sprechen: "pi-microphone",
};
const moduleLabel = (slug?: string) => MODULE_LABELS[slug ?? ""] ?? slug ?? "";
const moduleIcon = (slug?: string) => MODULE_ICONS[slug ?? ""] ?? "pi-file";

// Le Sprechen s'affiche (consultation) mais ne se note pas ici
const isGraded = (slug?: string) => slug !== "sprechen";

// ── Durées officielles (Start Deutsch 1 / Goethe-Zertifikat A2) ──
const MODULE_DURATIONS_MINUTES: Record<string, Record<string, number>> = {
  A1: { lesen: 25, hoeren: 20, schreiben: 20, sprechen: 15 },
  A2: { lesen: 30, hoeren: 30, schreiben: 30, sprechen: 15 },
};
const minutesOf = (mod: any) => MODULE_DURATIONS_MINUTES[store.level]?.[mod?.slug] ?? 20;

// ── Modules : en devoir, pas de Sprechen ──
const modules = computed<any[]>(() =>
  isAssignment.value
    ? store.modules.filter((m: any) => m.slug !== "sprechen")
    : store.modules,
);

// ── Déroulé : un module après l'autre, un Teil par écran ──
type Phase = "running" | "transition";
const phase = ref<Phase>("running");
const moduleIndex = ref(0);
const stepIndex = ref(0);

const currentModule = computed<any>(() => modules.value[moduleIndex.value] ?? null);
const nextModule = computed<any>(() => modules.value[moduleIndex.value + 1] ?? null);
const isLastModule = computed(() => moduleIndex.value >= modules.value.length - 1);

const teile = computed<any[]>(() => currentModule.value?.teile ?? []);
const currentTeil = computed<any>(() => teile.value[stepIndex.value] ?? null);
const isLastStep = computed(() => stepIndex.value >= teile.value.length - 1);

const teilQuestions = computed<any[]>(() => currentTeil.value?.questions ?? []);

const POOL_FORMATS = new Set(["image_day_matching", "matching_with_distractor"]);
const isPoolTeil = computed(() => POOL_FORMATS.has(currentTeil.value?.format_type));

// Texte commun du Teil, affiché une seule fois à gauche
const sharedText = computed<string>(() => currentTeil.value?.shared_content?.text ?? "");
const teilForQuestions = computed(() =>
  sharedText.value
    ? {
        ...currentTeil.value,
        shared_content: { ...currentTeil.value.shared_content, text: undefined },
      }
    : currentTeil.value,
);

const scrollArea = ref<HTMLElement | null>(null);

function goToStep(idx: number) {
  if (idx < 0 || idx >= teile.value.length) return;
  stepIndex.value = idx;
  scrollArea.value?.scrollTo({ top: 0 });
}

// ── Onglets des modules ──
function tabClass(mi: number) {
  if (mi === moduleIndex.value) return "border-primary text-primary";
  if (mi < moduleIndex.value) return "border-transparent text-emerald-600 opacity-70";
  return "border-transparent text-faint";
}

function tabIcon(slug: string, mi: number) {
  if (mi < moduleIndex.value) return "pi-check-circle";
  if (mi > moduleIndex.value) return "pi-lock";
  return moduleIcon(slug);
}

// ── Réponses ──
const questionsOfModule = (m: any): any[] =>
  isGraded(m?.slug) ? (m?.teile ?? []).flatMap((tl: any) => tl.questions ?? []) : [];

const moduleQuestions = computed(() => questionsOfModule(currentModule.value));
const moduleAnswered = computed(
  () => moduleQuestions.value.filter((q) => store.isAnswered(q.id)).length,
);
const moduleUnanswered = computed(
  () => moduleQuestions.value.length - moduleAnswered.value,
);

const headerSteps = computed(() =>
  teile.value.map((tl: any) => {
    const qs = isGraded(currentModule.value?.slug) ? tl.questions ?? [] : [];
    return {
      label: `Teil ${tl.teil_number}`,
      answered: qs.filter((q: any) => store.isAnswered(q.id)).length,
      total: qs.length,
    };
  }),
);

const sheetGroups = computed(() =>
  teile.value
    .map((tl: any, idx: number) => ({
      stepIndex: idx,
      current: idx === stepIndex.value,
      label: `${moduleLabel(currentModule.value?.slug)} · Teil ${tl.teil_number}`,
      questions: isGraded(currentModule.value?.slug)
        ? (tl.questions ?? []).map((q: any) => ({
            id: q.id,
            number: q.question_number,
            answered: store.isAnswered(q.id),
          }))
        : [],
    }))
    .filter((g: any) => g.questions.length > 0),
);

// ── Taille du texte ──
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
    if (Number.isInteger(v) && v >= 0 && v < FONT_SCALES.length) fontStep.value = v;
  } catch {
    /* ignore */
  }
}

// ── Chrono du module en cours, basé sur l'heure réelle ──
const timeRemaining = ref(0);
let deadline = 0;
let timerInterval: ReturnType<typeof setInterval> | null = null;
const warned = new Set<string>();

function stopTimer() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;
}

function startTimer() {
  stopTimer();
  timerInterval = setInterval(() => {
    timeRemaining.value = Math.max(0, Math.round((deadline - Date.now()) / 1000));
    warnIfLowTime();
    if (timeRemaining.value <= 0) onTimeUp();
  }, 1000);
}

function warnIfLowTime() {
  const key = `${moduleIndex.value}`;
  for (const seuil of [300, 60]) {
    if (timeRemaining.value <= seuil && !warned.has(`${key}-${seuil}`)) {
      warned.add(`${key}-${seuil}`);
      const n = Math.ceil(timeRemaining.value / 60);
      notify.warn(t("toast.time_left", { n }, n), t("toast.time_left_detail"));
      break;
    }
  }
}

function startModule(mi: number) {
  const mod = modules.value[mi];
  if (!mod) return;
  moduleIndex.value = mi;
  stepIndex.value = 0;
  deadline = Date.now() + minutesOf(mod) * 60_000;
  timeRemaining.value = minutesOf(mod) * 60;
  phase.value = "running";
  startTimer();
}

// Schreiben : PDF automatique à la fin du temps (entraînement), une seule fois
let schreibenPdfDone = false;
function downloadSchreibenIfNeeded() {
  const mod = currentModule.value;
  if (isAssignment.value || mod?.slug !== "schreiben" || schreibenPdfDone) return;
  schreibenPdfDone = true;
  useSchreibenPdf().download({
    subjectTitle: store.subjectTitle,
    level: store.level,
    studentName: authStore.userName,
    teile: mod.teile ?? [],
    answers: store.answers,
  });
}

function onTimeUp() {
  stopTimer();
  downloadSchreibenIfNeeded();
  submitDialogVisible.value = false;
  if (isLastModule.value) {
    notify.info(t("toast.time_up"), t("toast.time_up_detail"));
    handleSubmit();
    return;
  }
  notify.info(t("session.player.time_up_module"), t("session.player.time_up_module_detail"));
  phase.value = "transition";
}

// ── Fin de module / remise ──
const exitDialogVisible = ref(false);
const submitDialogVisible = ref(false);
const sheetVisible = ref(false);
const submitError = ref("");
const correcting = ref(false);
const submitted = ref(false);
const autoGraded = ref(false);

function confirmFinish() {
  if (isLastModule.value) {
    handleSubmit();
    return;
  }
  submitDialogVisible.value = false;
  stopTimer();
  phase.value = "transition";
}

async function handleSubmit() {
  if (store.isSubmitting || correcting.value || submitted.value) return;
  submitError.value = "";

  const result = await store.submitSession();
  if (!result.success) {
    submitError.value = result.error || "";
    submitDialogVisible.value = true;
    return;
  }
  stopTimer();

  // Devoir : corrigé par l'enseignant, l'élève ne voit que l'écran de remise
  if (isAssignment.value) {
    submitDialogVisible.value = false;
    autoGraded.value = store.status === "COMPLETED";
    submitted.value = true;
    store.resetSession();
    return;
  }

  // Entraînement : correction IA de chaque Schreiben répondu, puis résultat
  correcting.value = true;
  const freeTextTeile = store.modules
    .flatMap((m: any) => m.teile ?? [])
    .filter((teil: any) => teil.format_type === "free_text");
  for (const teil of freeTextTeile) {
    const question = teil.questions?.[0];
    const text = question ? store.answers[question.id]?.user_answer?.text : undefined;
    if (question && text?.trim()) await store.correctSchreiben(teil.id, text);
  }
  correcting.value = false;

  submitDialogVisible.value = false;
  navigateTo({
    path: localePath(`/dashboard/start-deutsch/${store.subjectId}/result`),
    query: { sessionId: String(store.sessionId) },
  });
}

function leave() {
  stopTimer();
  if (isAssignment.value) {
    store.resetSession();
    navigateTo(localePath("/dashboard/devoirs"));
  } else {
    navigateTo(localePath("/dashboard/start-deutsch"));
  }
}

// ── Chargement ──
const initialized = ref(false);

onMounted(async () => {
  restoreFontStep();
  applyFontScale();

  if (props.assignmentId) {
    await store.startAssignment(props.assignmentId);
  } else if (
    props.subjectId &&
    (store.sessionId === null || store.subjectId !== props.subjectId || store.assignmentId)
  ) {
    await store.startSession(props.subjectId);
  }

  initialized.value = true;
  if (modules.value.length) startModule(0);
});

onBeforeUnmount(() => {
  stopTimer();
  if (import.meta.client) document.documentElement.style.fontSize = "";
});
</script>