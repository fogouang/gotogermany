<template>
  <div class="h-screen bg-white flex flex-col overflow-hidden">
    <!-- Loading -->
    <!-- Avant initialized → toujours spinner -->
    <div
      v-if="!initialized || sessionStore.loading"
      class="flex items-center justify-center flex-1"
    >
      <div class="text-center">
        <ProgressSpinner style="width: 60px; height: 60px" />
        <p class="mt-4 text-gray-600 text-sm">{{ t("session.loading") }}</p>
      </div>
    </div>

    <!-- Erreur -->
    <div
      v-else-if="sessionStore.error"
      class="flex items-center justify-center flex-1"
    >
      <Card class="max-w-md">
        <template #content>
          <div class="text-center">
            <i
              class="pi pi-exclamation-triangle text-5xl text-red-500 mb-4"
            ></i>
            <h2 class="text-xl font-bold mb-2">{{ t("session.error") }}</h2>
            <p class="text-gray-600 mb-4">{{ sessionStore.error }}</p>
            <Button
              :label="t('session.back_to_exams')"
              @click="navigateTo('/dashboard/examens')"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Session active -->
    <template v-else-if="sessionStore.sessionId && currentModule">
      <!-- Header — sticky, ne scroll jamais -->
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

      <!-- Tabs modules — sticky, ne scroll jamais -->
      <div class="shrink-0 bg-white border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 flex gap-0 overflow-x-auto">
          <button
            v-for="(mod, mi) in sessionStore.modules"
            :key="mod.id"
            :class="[
              'px-5 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
              mi === currentModuleIndex
                ? 'border-primary-600 text-primary-700'
                : 'border-transparent text-gray-500 hover:text-gray-700',
            ]"
            @click="goToModule(mi)"
          >
            <i :class="['pi mr-2', getModuleIcon(mod.slug)]"></i>
            {{ mod.name }}
          </button>
        </div>
      </div>

      <!-- Vue du Teil courant — seule zone scrollable -->
      <div class="flex-1 overflow-y-auto min-h-0">
        <component
          :is="currentView"
          :key="`${currentModuleIndex}-${currentTeilIndex}`"
          :teil="currentTeil"
          :questions="currentTeilQuestions"
          :answers="sessionStore.answers"
          :session-id="sessionStore.sessionId"
          :exam-name="sessionStore.examName"
          @answer="onAnswer"
        />
      </div>

      <!-- Footer navigation — sticky, ne scroll jamais -->
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

    <!-- Dialog quitter -->
    <Dialog
      v-model:visible="exitDialogVisible"
      :header="t('session.exit_title')"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <Message severity="warn" :closable="false" class="mb-4">
        {{ t("session.exit_warning") }}
      </Message>
      <template #footer>
        <Button
          :label="t('session.cancel')"
          text
          @click="exitDialogVisible = false"
        />
        <Button
          :label="t('session.quit')"
          severity="warn"
          @click="exitSession"
        />
      </template>
    </Dialog>

    <!-- Dialog soumettre -->
    <Dialog
      v-model:visible="submitDialogVisible"
      :header="t('session.submit_title')"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <p class="mb-2">
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
        class="mb-2"
      >
        {{ t("session.unanswered_warning") }}
      </Message>
      <template #footer>
        <Button
          :label="t('session.continue')"
          text
          @click="submitDialogVisible = false"
        />
        <Button
          :label="t('session.submit')"
          severity="success"
          :loading="sessionStore.isSubmitting || correctionStore.loading"
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
import { useCorrectionStore } from "~/stores/correction";

definePageMeta({ layout: false, middleware: "auth" });

const route = useRoute();
const session = useSession();
const sessionStore = useSessionStore();
const { t } = useI18n();

const currentModuleIndex = ref(0);
const currentTeilIndex = ref(0);
const exitDialogVisible = ref(false);
const submitDialogVisible = ref(false);

let timerInterval: ReturnType<typeof setInterval> | null = null;

// ── Computed ──────────────────────────────────────────

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

// Vue à afficher selon le slug du module
const currentView = computed(() => {
  const slug = currentModule.value?.slug?.toLowerCase() || "";
  if (slug.includes("lese")) return LesenView;
  if (slug.includes("hor") || slug.includes("hoer") || slug.includes("hör")) return HorenView;
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

// ── Actions ───────────────────────────────────────────

const getModuleIcon = (slug: string) => {
  const icons: Record<string, string> = {
    horen: "pi-volume-up",
    lesen: "pi-book",
    schreiben: "pi-pencil",
    sprechen: "pi-microphone",
  };
  for (const key in icons) {
    if (slug.toLowerCase().includes(key)) return icons[key];
  }
  return "pi-file";
};

const goToModule = (index: number) => {
  currentModuleIndex.value = index;
  currentTeilIndex.value = 0;
};

const nextTeil = () => {
  const module = currentModule.value;
  if (!module) return;

  if (currentTeilIndex.value < module.teile.length - 1) {
    currentTeilIndex.value++;
  } else if (currentModuleIndex.value < sessionStore.modules.length - 1) {
    currentModuleIndex.value++;
    currentTeilIndex.value = 0;
  }
};

const prevTeil = () => {
  if (currentTeilIndex.value > 0) {
    currentTeilIndex.value--;
  } else if (currentModuleIndex.value > 0) {
    currentModuleIndex.value--;
    const prevModule = sessionStore.modules[currentModuleIndex.value];
    currentTeilIndex.value = (prevModule?.teile?.length ?? 1) - 1;
  }
};

const onAnswer = async (questionId: string, value: any) => {
  await session.saveAnswer(questionId, value);
};

const exitSession = () => {
  stopTimer();
  sessionStore.resetSession();
  navigateTo("/dashboard/examens");
};

const correctionStore = useCorrectionStore();

const hasSchreibenModule = computed(() =>
  sessionStore.modules.some(
    (m) =>
      m.slug?.toLowerCase().includes("schreib") ||
      m.slug?.toLowerCase().includes("schriftlich"),
  ),
);

const handleSubmit = async () => {
  submitDialogVisible.value = false;
  stopTimer();

  const result = await sessionStore.submitSession();
  if (!result.success) return;

  const sessionId = sessionStore.sessionId;

  console.log(
    "DEBUG hasSchreibenModule:",
    hasSchreibenModule.value,
    "sessionId:",
    sessionId,
    "modules:",
    sessionStore.modules,
  );

  if (hasSchreibenModule.value && sessionId) {
    try {
      await correctionStore.correct(sessionId);
    } catch (err) {
      console.error("Erreur correction Schreiben:", err);
    }
    console.log("DEBUG correctionStore.error:", correctionStore.error);
  }

  const slug = route.params.slug as string;
  const moduleSlug = route.query.moduleSlug as string | undefined;
  const moduleSlugs = route.query.moduleSlugs as string | undefined;
  navigateTo({
    path: `/dashboard/examens/${slug}/result`,
    query: {
      sessionId,
      ...(moduleSlug ? { moduleSlug } : {}),
      ...(moduleSlugs ? { moduleSlugs } : {}),
    },
  });
};
// ── Timer ─────────────────────────────────────────────

const startTimer = () => {
  timerInterval = setInterval(() => {
    sessionStore.decrementTimer();
    if (sessionStore.timeRemaining === 0) {
      stopTimer();
      handleSubmit();
    }
  }, 1000);
};

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
};

// ── Lifecycle ─────────────────────────────────────────

const initialized = ref(false);

const loadSession = async () => {
  initialized.value = false;
  stopTimer();
  sessionStore.resetSession(); // vide l'ancien état avant de recharger

  const examId = route.query.examId as string;
  const subjectId = route.query.subjectId as string | undefined;
  const moduleSlug = route.query.moduleSlug as string | undefined;
  const moduleSlugs = route.query.moduleSlugs as string | undefined;

  if (!examId) {
    navigateTo("/dashboard/examens");
    return;
  }

  const result = await session.startSession(examId, subjectId);

  if (result.success && (moduleSlug || moduleSlugs)) {
    const targetSlugs = moduleSlugs
      ? moduleSlugs.split(",").map((s) => s.trim().toLowerCase())
      : [moduleSlug!.toLowerCase()];

    sessionStore.modules = sessionStore.modules.filter((m) =>
      targetSlugs.some((slug) => m.slug.toLowerCase().includes(slug)),
    );
    sessionStore.questions = sessionStore.questions.filter((q) =>
      sessionStore.modules.some((m) =>
        m.teile?.some((t: any) => t.id === q.teil_id),
      ),
    );
    const combinedMinutes = sessionStore.modules.reduce(
      (sum: number, m: any) => sum + (m.time_limit_minutes || 0),
      0,
    );
    sessionStore.timeRemaining = (combinedMinutes || 30) * 60;
  }

  currentModuleIndex.value = 0;
  currentTeilIndex.value = 0;
  initialized.value = true;
  startTimer();
};

onMounted(loadSession);

// ✅ Recharge la session si l'utilisateur navigue vers un autre sujet/module
// SANS rechargement complet de page (query change, même route).
watch(
  () => [
    route.query.subjectId,
    route.query.examId,
    route.query.moduleSlug,
    route.query.moduleSlugs,
  ],
  () => {
    loadSession();
  },
);
</script>
