<template>
  <div class="flex h-screen flex-col overflow-hidden bg-canvas">
    <!-- ── Chargement ── -->
    <div
      v-if="!initialized || sessionStore.loading"
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
          :label="t('student_assignments.back')"
          icon="pi pi-arrow-left"
          class="mt-6 w-full"
          @click="backToList"
        />
      </div>
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="sessionStore.error && !sessionStore.sessionId"
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
        <p class="mt-2 text-sm text-muted">{{ sessionStore.error }}</p>
        <Button
          :label="t('student_assignments.back')"
          icon="pi pi-arrow-left"
          outlined
          class="mt-6 w-full"
          @click="backToList"
        />
      </div>
    </div>

    <!-- ── Lecteur ── -->
    <template v-else-if="sessionStore.sessionId && currentModule">
      <SessionHeader
        class="shrink-0"
        :exam-name="sessionStore.examName"
        :subject-number="sessionStore.subjectNumber"
        :module-name="currentModule.name"
        :teil-label="teilLabel"
        :step-index="currentTeilIndex"
        :step-count="currentModule.teile?.length ?? 0"
        :answered="sessionStore.answeredQuestions"
        :total="sessionStore.totalQuestions"
        :time-remaining="sessionStore.timeRemaining"
        :can-font-down="fontStep > 0"
        :can-font-up="fontStep < FONT_SCALES.length - 1"
        @font="(delta) => setFontStep(fontStep + delta)"
        @exit="exitDialogVisible = true"
      />

      <div class="shrink-0 border-b border-line bg-card">
        <div class="mx-auto flex max-w-7xl overflow-x-auto px-4">
          <button
            v-for="(mod, mi) in sessionStore.modules"
            :key="mod.id"
            type="button"
            class="whitespace-nowrap border-b-2 px-5 py-3 text-sm font-medium transition-colors"
            :class="
              mi === currentModuleIndex
                ? 'border-primary text-primary'
                : 'border-transparent text-muted hover:text-ink'
            "
            @click="goToModule(mi)"
          >
            <i class="pi mr-2" :class="getModuleIcon(mod.slug)" />
            {{ mod.name }}
          </button>
        </div>
      </div>

      <div class="min-h-0 flex-1 overflow-y-auto">
        <component
          :is="currentView"
          :key="`${currentModuleIndex}-${currentTeilIndex}`"
          :teil="currentTeil"
          :questions="currentTeilQuestions"
          :answers="sessionStore.answers"
          :session-id="sessionStore.sessionId"
          :exam-name="sessionStore.examName"
          :time-expired="isSchreibenModule && sessionStore.timeRemaining <= 0"
          @answer="onAnswer"
        />
      </div>

      <SessionFooter
        class="shrink-0"
        :can-prev="stepIndex > 0"
        :is-last-step="stepIndex >= steps.length - 1"
        :finish-label="t('session.submit')"
        :answered="sessionStore.answeredQuestions"
        :total="sessionStore.totalQuestions"
        @prev="goToStep(stepIndex - 1)"
        @next="goToStep(stepIndex + 1)"
        @finish="submitDialogVisible = true"
        @sheet="sheetVisible = true"
      />
    </template>

    <!-- ══════════ Feuille de réponses ══════════ -->
    <SessionAnswerSheet
      v-model:visible="sheetVisible"
      :groups="sheetGroups"
      @go="(idx) => { goToStep(idx); sheetVisible = false; }"
    />

    <!-- ══════════ Quitter ══════════ -->
    <Dialog
      v-model:visible="exitDialogVisible"
      :header="t('session.exit_title')"
      modal
      :style="{ width: '26rem', maxWidth: '95vw' }"
    >
      <Message severity="info" :closable="false">{{
        t("student_assignments.exit_warning")
      }}</Message>
      <template #footer>
        <Button
          :label="t('session.cancel')"
          text
          severity="secondary"
          @click="exitDialogVisible = false"
        />
        <Button
          :label="t('session.quit')"
          severity="warn"
          @click="exitAssignment"
        />
      </template>
    </Dialog>

    <!-- ══════════ Rendre ══════════ -->
    <Dialog
      v-model:visible="submitDialogVisible"
      :header="t('session.submit_title')"
      modal
      :style="{ width: '26rem', maxWidth: '95vw' }"
    >
      <p class="mb-3 text-sm text-ink">
        {{ t("session.player.answered", { answered: sessionStore.answeredQuestions, total: sessionStore.totalQuestions }) }}
      </p>
      <Message
        v-if="unanswered > 0"
        severity="warn"
        :closable="false"
      >
        {{ t("session.player.unanswered", { n: unanswered }, unanswered) }}
      </Message>
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
          :label="t('session.submit')"
          severity="success"
          :loading="sessionStore.isSubmitting"
          @click="handleSubmit"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import LesenView from "~/components/session/LesenView.vue";
import HorenView from "~/components/session/HorenView.vue";
import SchreibenView from "~/components/session/SchreibenView.vue";
import SessionHeader from "~/components/session/SessionHeader.vue";
import SessionFooter from "~/components/session/SessionFooter.vue";
import SessionAnswerSheet from "~/components/session/SessionAnswerSheet.vue";

definePageMeta({ layout: false });

type Step = { mi: number; ti: number };

const route = useRoute();
const { t } = useI18n();

const localePath = useLocalePath();
const sessionStore = useSessionStore();
const notify = useNotify();

const assignmentId = computed(() => route.params.id as string);

const initialized = ref(false);
const submitted = ref(false);
const autoGraded = ref(false);
const submitError = ref("");
const currentModuleIndex = ref(0);
const currentTeilIndex = ref(0);
const exitDialogVisible = ref(false);
const submitDialogVisible = ref(false);
const sheetVisible = ref(false);

// ── Slugs ──
const slugText = (slug?: string) => (slug || "").toLowerCase();
const isOralSlug = (slug?: string) =>
  ["sprech", "muendlich", "mündlich"].some((p) => slugText(slug).includes(p));

// ── Lecteur ──
const currentModule = computed(
  () => sessionStore.modules[currentModuleIndex.value],
);
const currentTeil = computed(
  () => currentModule.value?.teile?.[currentTeilIndex.value],
);

const currentTeilQuestions = computed(() => {
  if (!currentTeil.value) return [];
  const teilId = currentTeil.value.id;
  return sessionStore.questions.filter((q) => q.teil_id === teilId);
});

const isSchreibenModule = computed(() => {
  const slug = slugText(currentModule.value?.slug);
  return slug.includes("schreib") || slug.includes("schriftlich");
});

const currentView = computed(() => {
  const slug = slugText(currentModule.value?.slug);
  if (slug.includes("hor") || slug.includes("hoer") || slug.includes("hör"))
    return HorenView;
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return SchreibenView;
  return LesenView; // Lesen, Leseverstehen, Sprachbausteine
});

const teilLabel = computed(() => {
  const total = currentModule.value?.teile?.length ?? 0;
  const base = t("session.player.teil", { n: currentTeilIndex.value + 1, total });
  const name = currentTeil.value?.config?.name;
  return name ? `${base} · ${name}` : base;
});

const unanswered = computed(
  () => sessionStore.totalQuestions - sessionStore.answeredQuestions,
);

// ── Étapes (tous les Teile de tous les modules) ──
const steps = computed<Step[]>(() =>
  sessionStore.modules.flatMap((m, mi) =>
    (m.teile ?? []).map((_: unknown, ti: number) => ({ mi, ti })),
  ),
);

const stepIndex = computed(() =>
  steps.value.findIndex(
    (s) => s.mi === currentModuleIndex.value && s.ti === currentTeilIndex.value,
  ),
);

function goToStep(idx: number) {
  const target = steps.value[idx];
  if (!target) return;
  if (target.mi !== currentModuleIndex.value) {
    sessionStore.switchToModule(target.mi);
    currentModuleIndex.value = target.mi;
  }
  currentTeilIndex.value = target.ti;
}

const goToModule = (index: number) => {
  sessionStore.switchToModule(index);
  currentModuleIndex.value = index;
  currentTeilIndex.value = 0;
};

const sheetGroups = computed(() =>
  steps.value.map((s, idx) => {
    const mod = sessionStore.modules[s.mi];
    const teil = mod?.teile?.[s.ti];
    const qs = sessionStore.questions
      .filter((q) => q.teil_id === teil?.id)
      .sort((a, b) => (a.question_number ?? 0) - (b.question_number ?? 0));
    return {
      stepIndex: idx,
      current: idx === stepIndex.value,
      label: `${mod?.name ?? ""} · ${t("session.player.teil", { n: s.ti + 1, total: mod?.teile?.length ?? 0 })}`,
      questions: qs.map((q, i) => ({
        id: q.id,
        number: q.question_number ?? i + 1,
        answered: !!sessionStore.answers[q.id],
      })),
    };
  }),
);

const getModuleIcon = (slug: string) => {
  const s = slugText(slug);
  if (s.includes("sprachbaustein")) return "pi-language";
  if (s.includes("lese")) return "pi-book";
  if (s.includes("hor") || s.includes("hoer") || s.includes("hör")) return "pi-volume-up";
  if (s.includes("schreib") || s.includes("schriftlich")) return "pi-pencil";
  return "pi-file";
};

// ── Taille du texte (police racine, tout est en rem) ──
const FONT_SCALES = [0.9, 1, 1.1, 1.25, 1.4];
const FONT_KEY = "gtg_exam_font";
const fontStep = ref(1);
const fontScale = computed(() => FONT_SCALES[fontStep.value] ?? 1);

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
    document.documentElement.style.fontSize = `${fontScale.value * 100}%`;
  }
}

watch(fontScale, applyFontScale);

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

// ── Alertes ──
const WARN_AT_SECONDS = [300, 60];
const warned = new Set<string>();

function warnIfLowTime() {
  const remaining = sessionStore.timeRemaining;
  if (remaining <= 0) return;
  const moduleId = currentModule.value?.id ?? "";
  for (const seuil of WARN_AT_SECONDS) {
    const key = `${moduleId}-${seuil}`;
    if (remaining <= seuil && !warned.has(key)) {
      warned.add(key);
      const n = Math.ceil(remaining / 60);
      notify.warn(t("toast.time_left", { n }, n), t("toast.time_left_detail"));
      break;
    }
  }
}

let lastSaveWarning = 0;
function warnSaveFailed() {
  if (Date.now() - lastSaveWarning < 30_000) return;
  lastSaveWarning = Date.now();
  notify.warn(t("toast.save_failed"), t("toast.save_failed_detail"));
}

const onAnswer = async (questionId: string, value: any) => {
  const res = await sessionStore.saveAnswer(questionId, value);
  if (!res?.success) warnSaveFailed();
};

// ── Minuteur unique, basé sur l'heure réelle ──
let timerInterval: ReturnType<typeof setInterval> | null = null;

const stopTimer = () => {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;
};

const startTimer = () => {
  stopTimer();
  timerInterval = setInterval(() => {
    sessionStore.tick();
    warnIfLowTime();

    if (sessionStore.timeRemaining <= 0) {
      stopTimer();
      notify.info(t("toast.time_up"), t("toast.time_up_detail"));
      handleSubmit();
    }
  }, 1000);
};

// ── Remise (sans correction IA : c'est l'enseignant qui corrige) ──
const handleSubmit = async () => {
  if (sessionStore.isSubmitting || submitted.value) return;
  submitError.value = "";
  stopTimer();

  const result = await sessionStore.submitSession();
  if (!result.success) {
    submitError.value = result.error || "";
    submitDialogVisible.value = true;
    return;
  }

  submitDialogVisible.value = false;
  autoGraded.value = sessionStore.status === "COMPLETED";
  submitted.value = true;
  sessionStore.resetSession();
};

// ── Sortie ──
const backToList = () => navigateTo(localePath("/dashboard/devoirs"));

const exitAssignment = () => {
  stopTimer();
  sessionStore.resetSession();
  backToList();
};

// ── Chargement ──
const load = async () => {
  initialized.value = false;
  submitted.value = false;
  stopTimer();
  warned.clear();

  const result = await sessionStore.startAssignment(assignmentId.value);

  if (result.success) {
    // Oral : évalué en session live avec l'enseignant, pas dans le devoir
    sessionStore.modules = sessionStore.modules.filter((m) => !isOralSlug(m.slug));
    sessionStore.questions = sessionStore.questions.filter((q) =>
      sessionStore.modules.some((m) => m.teile?.some((tl) => tl.id === q.teil_id)),
    );
  }

  currentModuleIndex.value = 0;
  currentTeilIndex.value = 0;
  if (sessionStore.modules.length) sessionStore.switchToModule(0);
  initialized.value = true;

  if (result.success) {
    const restored = Object.keys(sessionStore.answers).length;
    if (restored > 0) {
      notify.info(
        t("toast.session_resumed", { n: sessionStore.subjectNumber }),
        t("toast.session_resumed_detail", { n: restored }, restored),
      );
    }
    startTimer();
  }
};

onMounted(() => {
  restoreFontStep();
  applyFontScale();
  load();
});

onBeforeUnmount(() => {
  document.documentElement.style.fontSize = "";
  stopTimer();
});
</script>