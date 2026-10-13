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
        :subject-info="`${t('session.subject')} ${sessionStore.subjectNumber}`"
        :module-name="currentModule.name"
        :current-teil-index="currentTeilIndex"
        :teile="currentModule.teile"
        :time-remaining="sessionStore.timeRemaining"
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
        :is-first-teil="isFirstTeil"
        :is-last-teil="isLastTeil && isLastModule"
        :answered-in-teil="answeredInCurrentTeil"
        :total-in-teil="currentTeilQuestions.length"
        @prev="prevTeil"
        @next="nextTeil"
        @submit="submitDialogVisible = true"
      />
    </template>

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
        {{ t("session.answered") }}
        <strong>{{ sessionStore.answeredQuestions }}</strong>
        {{ t("session.questions_of") }}
        <strong>{{ sessionStore.totalQuestions }}</strong
        >.
      </p>
      <Message
        v-if="sessionStore.answeredQuestions < sessionStore.totalQuestions"
        severity="warn"
        :closable="false"
      >
        {{ t("session.unanswered_warning") }}
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
import SprechenView from "~/components/session/SprechenView.vue";
import SessionHeader from "~/components/session/SessionHeader.vue";
import SessionFooter from "~/components/session/SessionFooter.vue";

definePageMeta({ layout: false });

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

const answeredInCurrentTeil = computed(
  () =>
    currentTeilQuestions.value.filter((q) => sessionStore.answers[q.id]).length,
);

const isFirstTeil = computed(
  () => currentModuleIndex.value === 0 && currentTeilIndex.value === 0,
);
const isLastTeil = computed(
  () =>
    currentTeilIndex.value === (currentModule.value?.teile?.length ?? 1) - 1,
);
const isLastModule = computed(
  () => currentModuleIndex.value === sessionStore.modules.length - 1,
);

const slugOf = () => currentModule.value?.slug?.toLowerCase() || "";
const isSchreibenModule = computed(
  () => slugOf().includes("schreib") || slugOf().includes("schriftlich"),
);

const currentView = computed(() => {
  const slug = slugOf();
  if (slug.includes("lese")) return LesenView;
  if (slug.includes("hor") || slug.includes("hoer") || slug.includes("hör"))
    return HorenView;
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return SchreibenView;
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return SprechenView;
  return LesenView;
});

// Alertes de temps : 5 min puis 1 min, une seule fois par module
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
      break; // une seule alerte par seconde, même si deux seuils sont franchis
    }
  }
}

// Réponse non synchronisée : au plus une alerte toutes les 30 s
let lastSaveWarning = 0;
function warnSaveFailed() {
  if (Date.now() - lastSaveWarning < 30_000) return;
  lastSaveWarning = Date.now();
  notify.warn(t("toast.save_failed"), t("toast.save_failed_detail"));
}

const getModuleIcon = (slug: string) => {
  const icons: Record<string, string> = {
    horen: "pi-volume-up",
    lesen: "pi-book",
    schreiben: "pi-pencil",
    sprechen: "pi-microphone",
  };
  for (const key in icons)
    if (slug.toLowerCase().includes(key)) return icons[key];
  return "pi-file";
};

const goToModule = (index: number) => {
  sessionStore.switchToModule(index);
  currentModuleIndex.value = index;
  currentTeilIndex.value = 0;
};

const nextTeil = () => {
  const mod = currentModule.value;
  if (!mod) return;
  if (currentTeilIndex.value < mod.teile.length - 1) {
    currentTeilIndex.value++;
  } else if (currentModuleIndex.value < sessionStore.modules.length - 1) {
    goToModule(currentModuleIndex.value + 1);
  }
};

const prevTeil = () => {
  if (currentTeilIndex.value > 0) {
    currentTeilIndex.value--;
  } else if (currentModuleIndex.value > 0) {
    sessionStore.switchToModule(currentModuleIndex.value - 1);
    currentModuleIndex.value--;
    const prevModule = sessionStore.modules[currentModuleIndex.value];
    currentTeilIndex.value = (prevModule?.teile?.length ?? 1) - 1;
  }
};

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
  currentModuleIndex.value = 0;
  currentTeilIndex.value = 0;
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

onMounted(load);
onBeforeUnmount(stopTimer);
</script>
