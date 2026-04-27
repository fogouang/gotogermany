<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Loading -->
    <div
      v-if="sessionStore.loading"
      class="flex items-center justify-center flex-1"
    >
      <div class="text-center">
        <ProgressSpinner style="width: 60px; height: 60px" />
        <p class="mt-4 text-gray-600 text-sm">Chargement de la session...</p>
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
            <h2 class="text-xl font-bold mb-2">Erreur</h2>
            <p class="text-gray-600 mb-4">{{ sessionStore.error }}</p>
            <Button
              label="Retour aux examens"
              @click="navigateTo('/dashboard/examens')"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Session active -->
    <template v-else-if="sessionStore.sessionId && currentModule">
      <!-- Header -->
      <SessionHeader
        :exam-name="sessionStore.examName"
        :subject-info="`Sujet ${sessionStore.subjectNumber}`"
        :module-name="currentModule.name"
        :current-teil-index="currentTeilIndex"
        :teile="currentModule.teile"
        :time-remaining="sessionStore.timeRemaining"
        @exit="exitDialogVisible = true"
      />

      <!-- Tabs modules -->
      <div class="bg-white border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 flex gap-0 overflow-x-auto">
          <button
            v-for="(mod, mi) in sessionStore.modules"
            :key="mod.id"
            :class="[
              'px-5 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
              mi === currentModuleIndex
                ? 'border-teal-600 text-teal-700'
                : 'border-transparent text-gray-500 hover:text-gray-700',
            ]"
            @click="goToModule(mi)"
          >
            <i :class="['pi mr-2', getModuleIcon(mod.slug)]"></i>
            {{ mod.name }}
          </button>
        </div>
      </div>

      <!-- Vue du Teil courant -->
      <div class="flex-1 overflow-auto">
        <component
          :is="currentView"
          :teil="currentTeil"
          :questions="currentTeilQuestions"
          :answers="sessionStore.answers"
          @answer="onAnswer"
        />
      </div>

      <!-- Footer navigation -->
      <SessionFooter
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
      header="Quitter l'examen ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <Message severity="warn" :closable="false" class="mb-4">
        Vos réponses en cours seront perdues.
      </Message>
      <template #footer>
        <Button label="Annuler" text @click="exitDialogVisible = false" />
        <Button label="Quitter" severity="danger" @click="exitSession" />
      </template>
    </Dialog>

    <!-- Dialog soumettre -->
    <Dialog
      v-model:visible="submitDialogVisible"
      header="Terminer l'examen ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <p class="mb-2">
        Vous avez répondu à
        <strong>{{ sessionStore.answeredQuestions }}</strong>
        question(s) sur
        <strong>{{ sessionStore.totalQuestions }}</strong
        >.
      </p>
      <Message
        v-if="sessionStore.answeredQuestions < sessionStore.totalQuestions"
        severity="warn"
        :closable="false"
        class="mb-2"
      >
        Certaines questions sont sans réponse.
      </Message>
      <template #footer>
        <Button label="Continuer" text @click="submitDialogVisible = false" />
        <Button
          label="Soumettre"
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

definePageMeta({ layout: false, middleware: "auth" });

const route = useRoute();
const session = useSession();
const sessionStore = useSessionStore();

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
  if (slug.includes("lesen")) return LesenView;
  if (slug.includes("horen") || slug.includes("hören")) return HorenView;
  if (slug.includes("schreiben")) return SchreibenView;
  if (slug.includes("sprechen")) return SprechenView;
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

const handleSubmit = async () => {
  submitDialogVisible.value = false;
  stopTimer();
  const result = await sessionStore.submitSession();
  if (result.success) {
    const slug = route.params.slug as string;
    navigateTo({
      path: `/dashboard/examens/${slug}/result`,
      query: { sessionId: sessionStore.sessionId },
    });
  }
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

onMounted(async () => {
  const examId = route.query.examId as string;
  const subjectId = route.query.subjectId as string | undefined;

  console.log("=== SESSION PAGE MOUNTED ===");
  console.log("examId:", examId);
  console.log("subjectId:", subjectId);
  console.log("store loading before:", sessionStore.loading);
  console.log("store sessionId before:", sessionStore.sessionId);

  if (!examId) {
    navigateTo("/dashboard/examens");
    return;
  }

  const result = await session.startSession(examId, subjectId);
  console.log("startSession result:", result);
  console.log("store modules after:", sessionStore.modules.length);
  console.log("store sessionId after:", sessionStore.sessionId);
  console.log("store error:", sessionStore.error);

  if (result.success) startTimer();
});

onUnmounted(() => stopTimer());

onBeforeRouteLeave(() => {
  if (sessionStore.sessionId && !sessionStore.isSubmitting) {
    return confirm("Quitter ? Votre progression ne sera pas sauvegardée.");
  }
});
</script>
