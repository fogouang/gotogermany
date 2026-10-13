<template>
  <div class="h-screen bg-canvas flex flex-col overflow-hidden">
    <!-- Chargement -->
    <div
      v-if="!initialized || sessionStore.loading"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center">
        <ProgressSpinner style="width: 56px; height: 56px" strokeWidth="3" />
        <p class="mt-4 text-sm text-muted">{{ t("session.loading") }}</p>
      </div>
    </div>

    <!-- Erreur / aucun module écrit -->
    <div
      v-else-if="loadError || !sessionStore.modules.length"
      class="flex-1 flex items-center justify-center px-4"
    >
      <div
        class="bg-card border border-line rounded-card shadow-soft p-6 max-w-md w-full text-center"
      >
        <div
          class="w-12 h-12 rounded-leaf bg-red-500/10 flex items-center justify-center mx-auto mb-4"
        >
          <i class="pi pi-exclamation-triangle text-red-500 text-xl"></i>
        </div>
        <h2 class="text-lg font-bold text-ink mb-2">
          {{ t("session.error") }}
        </h2>
        <p class="text-sm text-muted mb-5">
          {{ loadError || t("session.player.no_modules") }}
        </p>
        <Button
          :label="t('session.back_to_exams')"
          @click="navigateTo(localePath('/dashboard/examens'))"
        />
      </div>
    </div>

    <!-- Avant l'épreuve -->
    <SessionIntro
      v-else-if="phase === 'intro'"
      :exam-name="sessionStore.examName"
      :subject-number="sessionStore.subjectNumber"
      :blocks="introBlocks"
      :oral-modules="oralModuleNames"
      :oral-link="sprechenLink"
      :has-audio="hasAudio"
      :resumed-count="restoredCount"
      @begin="begin"
      @exit="exitDialogVisible = true"
    />

    <!-- Entre deux blocs -->
    <div
      v-else-if="phase === 'transition'"
      class="flex-1 overflow-y-auto flex items-center justify-center px-4 py-10"
    >
      <div
        class="bg-card border border-line rounded-card shadow-soft p-6 sm:p-8 max-w-lg w-full text-center"
      >
        <div
          class="w-14 h-14 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4"
        >
          <i class="pi pi-check text-emerald-600 text-xl"></i>
        </div>
        <h2 class="text-xl font-bold text-ink">
          {{
            t("session.player.transition_done", {
              name: blockLabel(currentBlock),
            })
          }}
        </h2>
        <p class="text-sm text-muted mt-1">
          {{
            t("session.player.answered", {
              answered: blockAnswered,
              total: blockQuestions.length,
            })
          }}
        </p>

        <div
          v-if="nextBlock"
          class="mt-6 rounded-leaf bg-card-2 border border-line p-4 text-left"
        >
          <p class="text-xs font-semibold uppercase tracking-wide text-faint">
            {{ t("session.player.transition_next") }}
          </p>
          <p class="mt-1 font-semibold text-ink">{{ blockLabel(nextBlock) }}</p>
          <p class="text-sm text-muted mt-0.5">
            <i class="pi pi-clock text-xs mr-1"></i>
            {{ t("session.player.intro_minutes", { n: nextBlock.minutes }) }}
          </p>
        </div>

        <Button
          class="mt-6 w-full"
          :label="t('session.player.transition_start')"
          icon="pi pi-play"
          @click="startBlock(blockIndex + 1)"
        />
      </div>
    </div>

    <!-- Épreuve en cours -->
    <template v-else-if="currentModule">
      <SessionHeader
        class="shrink-0"
        :exam-name="sessionStore.examName"
        :subject-number="sessionStore.subjectNumber"
        :module-name="currentModule.name"
        :teil-label="teilLabel"
        :step-index="stepIndex"
        :step-count="steps.length"
        :answered="blockAnswered"
        :total="blockQuestions.length"
        :time-remaining="sessionStore.timeRemaining"
        :can-font-down="fontStep > 0"
        :can-font-up="fontStep < FONT_SCALES.length - 1"
        @font="(delta) => setFontStep(fontStep + delta)"
        @exit="exitDialogVisible = true"
      />

      <div class="flex-1 overflow-y-auto min-h-0">
        <component
          :is="currentView"
          :key="`${blockIndex}-${stepIndex}`"
          :teil="currentTeil"
          :questions="currentTeilQuestions"
          :answers="sessionStore.answers"
          :session-id="sessionStore.sessionId"
          :exam-name="sessionStore.examName"
          :time-expired="
            isSchreibenSlug(currentModule.slug) &&
            sessionStore.timeRemaining <= 0
          "
          @answer="onAnswer"
        />
      </div>

      <SessionFooter
        class="shrink-0"
        :can-prev="stepIndex > 0"
        :is-last-step="isLastStep"
        :finish-label="
          isLastBlock ? t('session.finish') : t('session.player.finish_module')
        "
        :answered="blockAnswered"
        :total="blockQuestions.length"
        @prev="goToStep(stepIndex - 1)"
        @next="goToStep(stepIndex + 1)"
        @finish="finishDialogVisible = true"
        @sheet="sheetVisible = true"
      />
    </template>

    <!-- Feuille de réponses -->
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

    <!-- Quitter -->
    <Dialog
      v-model:visible="exitDialogVisible"
      :header="t('session.exit_title')"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <Message severity="warn" :closable="false" class="mb-2">
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

    <!-- Terminer le module / l'examen -->
    <Dialog
      v-model:visible="finishDialogVisible"
      :header="
        isLastBlock
          ? t('session.submit_title')
          : t('session.player.finish_module_title')
      "
      :modal="true"
      :style="{ width: '90vw', maxWidth: '440px' }"
    >
      <p class="text-sm text-ink mb-3">
        {{
          t("session.player.answered", {
            answered: blockAnswered,
            total: blockQuestions.length,
          })
        }}
      </p>
      <Message
        v-if="blockUnanswered > 0"
        severity="warn"
        :closable="false"
        class="mb-3"
      >
        {{
          t(
            "session.player.unanswered",
            { n: blockUnanswered },
            blockUnanswered,
          )
        }}
      </Message>
      <p v-if="!isLastBlock" class="text-sm text-muted">
        {{ t("session.player.finish_module_text") }}
      </p>
      <template #footer>
        <Button
          :label="t('session.continue')"
          text
          @click="finishDialogVisible = false"
        />
        <Button
          :label="
            isLastBlock
              ? t('session.submit')
              : t('session.player.finish_module')
          "
          severity="success"
          :loading="sessionStore.isSubmitting || correctionStore.loading"
          @click="confirmFinish"
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
import SessionIntro from "~/components/session/SessionIntro.vue";
import SessionAnswerSheet from "~/components/session/SessionAnswerSheet.vue";
import { useCorrectionStore } from "~/stores/correction";

definePageMeta({ layout: false });

type Phase = "intro" | "running" | "transition";
type Block = { key: string; moduleIndexes: number[]; minutes: number };
type Step = { mi: number; ti: number };

const route = useRoute();
const sessionStore = useSessionStore();
const correctionStore = useCorrectionStore();
const { t } = useI18n();
const notify = useNotify();
const localePath = useLocalePath();

// ── Helpers de slug ───────────────────────────────────

const slugOf = (slug?: string) => (slug || "").toLowerCase();
const isOralSlug = (slug?: string) =>
  ["sprech", "muendlich", "mündlich"].some((p) => slugOf(slug).includes(p));
const isSchreibenSlug = (slug?: string) =>
  slugOf(slug).includes("schreib") || slugOf(slug).includes("schriftlich");
const isHorenSlug = (slug?: string) =>
  ["hor", "hoer", "hör"].some((p) => slugOf(slug).includes(p));

// ── État ──────────────────────────────────────────────

const initialized = ref(false);
const loadError = ref<string | null>(null);
const phase = ref<Phase>("intro");
const blockIndex = ref(0);
const stepIndex = ref(0);
const moduleMode = ref(false);
const moduleModeMinutes = ref(30);
const oralModuleNames = ref<string[]>([]);
const restoredCount = ref(0);
const tabSwitches = ref(0);

const exitDialogVisible = ref(false);
const finishDialogVisible = ref(false);
const sheetVisible = ref(false);

// ── Blocs chronométrés ────────────────────────────────
// Examen complet : un module à 0 min rejoint le bloc précédent
// (TELC : Leseverstehen + Sprachbausteine = un seul bloc de 90 min).
// Mode module seul / combinés : un seul bloc avec le temps cumulé.

const blocks = computed<Block[]>(() => {
  const mods = sessionStore.modules;
  if (!mods.length) return [];

  if (moduleMode.value) {
    return [
      {
        key: "modules",
        moduleIndexes: mods.map((_: unknown, i: number) => i),
        minutes: moduleModeMinutes.value,
      },
    ];
  }

  const out: Block[] = [];
  mods.forEach((m: any, i: number) => {
    const minutes = Number(m.time_limit_minutes) || 0;
    const last = out[out.length - 1];
    if (minutes === 0 && last) {
      last.moduleIndexes.push(i);
      return;
    }
    out.push({ key: String(m.id), moduleIndexes: [i], minutes: minutes || 30 });
  });
  return out;
});

const currentBlock = computed(() => blocks.value[blockIndex.value]);
const nextBlock = computed(() => blocks.value[blockIndex.value + 1]);
const isLastBlock = computed(() => blockIndex.value >= blocks.value.length - 1);

const blockLabel = (block?: Block) =>
  block
    ? block.moduleIndexes
        .map((mi) => sessionStore.modules[mi]?.name)
        .filter(Boolean)
        .join(" + ")
    : "";

const introBlocks = computed(() =>
  blocks.value.map((b) => ({ label: blockLabel(b), minutes: b.minutes })),
);

// ── Étapes (Teile) du bloc courant ────────────────────

const steps = computed<Step[]>(() => {
  const block = currentBlock.value;
  if (!block) return [];
  return block.moduleIndexes.flatMap((mi) =>
    (sessionStore.modules[mi]?.teile ?? []).map((_: unknown, ti: number) => ({
      mi,
      ti,
    })),
  );
});

const currentStep = computed(() => steps.value[stepIndex.value]);
const currentModuleIndex = computed(() => currentStep.value?.mi ?? 0);
const currentModule = computed(
  () => sessionStore.modules[currentModuleIndex.value],
);
const currentTeil = computed(
  () => currentModule.value?.teile?.[currentStep.value?.ti ?? 0],
);
const isLastStep = computed(() => stepIndex.value >= steps.value.length - 1);

const currentTeilQuestions = computed(() => {
  const teilId = currentTeil.value?.id;
  if (!teilId) return [];
  return sessionStore.questions.filter((q: any) => q.teil_id === teilId);
});

const teilLabel = computed(() => {
  const total = currentModule.value?.teile?.length ?? 0;
  const base = t("session.player.teil", {
    n: (currentStep.value?.ti ?? 0) + 1,
    total,
  });
  const name = currentTeil.value?.config?.name;
  return name ? `${base} · ${name}` : base;
});

// ── Réponses du bloc ──────────────────────────────────

const isAnswered = (questionId: string) => !!sessionStore.answers[questionId];

const blockQuestions = computed(() => {
  const teilIds = new Set(
    steps.value.map((s) => sessionStore.modules[s.mi]?.teile?.[s.ti]?.id),
  );
  return sessionStore.questions.filter((q: any) => teilIds.has(q.teil_id));
});

const blockAnswered = computed(
  () => blockQuestions.value.filter((q: any) => isAnswered(q.id)).length,
);
const blockUnanswered = computed(
  () => blockQuestions.value.length - blockAnswered.value,
);

const sheetGroups = computed(() =>
  steps.value.map((s, idx) => {
    const mod = sessionStore.modules[s.mi];
    const teil = mod?.teile?.[s.ti];
    const qs = sessionStore.questions
      .filter((q: any) => q.teil_id === teil?.id)
      .sort(
        (a: any, b: any) => (a.question_number ?? 0) - (b.question_number ?? 0),
      );
    return {
      stepIndex: idx,
      current: idx === stepIndex.value,
      label: `${mod?.name ?? ""} · ${t("session.player.teil", { n: s.ti + 1, total: mod?.teile?.length ?? 0 })}`,
      questions: qs.map((q: any, i: number) => ({
        id: q.id,
        number: q.question_number ?? i + 1,
        answered: isAnswered(q.id),
      })),
    };
  }),
);

// ── Vue du module ─────────────────────────────────────

const currentView = computed(() => {
  const slug = currentModule.value?.slug;
  if (isHorenSlug(slug)) return HorenView;
  if (isSchreibenSlug(slug)) return SchreibenView;
  return LesenView; // Lesen, Leseverstehen, Sprachbausteine
});

const hasAudio = computed(() =>
  sessionStore.modules.some((m: any) => isHorenSlug(m.slug)),
);

const sprechenLink = computed(() => {
  const id = route.query.subjectId as string | undefined;
  return id ? localePath(`/dashboard/sprechen/${id}`) : null;
});

// ── Taille du texte ───────────────────────────────────

const FONT_SCALES = [0.9, 1, 1.1, 1.25, 1.4];
const FONT_KEY = "gtg_exam_font";
const fontStep = ref(1);
const fontScale = computed(() => FONT_SCALES[fontStep.value] ?? 1);

function setFontStep(step: number) {
  fontStep.value = Math.min(Math.max(step, 0), FONT_SCALES.length - 1);
  try {
    localStorage.setItem(FONT_KEY, String(fontStep.value));
  } catch {
    /* stockage indisponible : on garde la valeur en mémoire */
  }
}

// Taille du texte : on agit sur la police racine (tout est en rem)
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
    if (Number.isInteger(v) && v >= 0 && v < FONT_SCALES.length)
      fontStep.value = v;
  } catch {
    /* ignore */
  }
}

// ── Plein écran / sortie d'onglet ─────────────────────

async function enterFullscreen() {
  try {
    await document.documentElement.requestFullscreen?.();
  } catch {
    /* refusé ou non supporté */
  }
}

function leaveFullscreen() {
  if (import.meta.client && document.fullscreenElement) {
    document.exitFullscreen?.().catch(() => {});
  }
}

function onVisibilityChange() {
  if (phase.value !== "running") return;
  if (document.hidden) {
    tabSwitches.value++;
    return;
  }
  notify.warn(
    t("session.player.tab_left_title"),
    t("session.player.tab_left_detail", { n: tabSwitches.value }),
  );
}

// ── Alertes ───────────────────────────────────────────

const WARN_AT_SECONDS = [300, 60];
const warned = new Set<string>();

function warnIfLowTime() {
  const remaining = sessionStore.timeRemaining;
  if (remaining <= 0) return;
  const blockKey = currentBlock.value?.key ?? "";
  for (const seuil of WARN_AT_SECONDS) {
    const key = `${blockKey}-${seuil}`;
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

// ── Chrono ────────────────────────────────────────────

let timerInterval: ReturnType<typeof setInterval> | null = null;

function startTimer() {
  stopTimer();
  timerInterval = setInterval(() => {
    sessionStore.tick();
    warnIfLowTime();
    if (sessionStore.timeRemaining <= 0) onTimeUp();
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function onTimeUp() {
  stopTimer();
  if (isLastBlock.value) {
    submit(true);
    return;
  }
  notify.info(
    t("session.player.time_up_module"),
    t("session.player.time_up_module_detail"),
  );
  phase.value = "transition";
}

// ── Navigation ────────────────────────────────────────

// Change de module dans le store sans toucher au chrono du bloc
function syncStoreModule(mi: number) {
  const remaining = sessionStore.timeRemaining;
  const deadline = sessionStore.deadline;
  sessionStore.switchToModule(mi);
  sessionStore.timeRemaining = remaining;
  sessionStore.deadline = deadline;
}

function goToStep(idx: number) {
  const target = steps.value[idx];
  if (!target) return;
  if (target.mi !== currentModuleIndex.value) syncStoreModule(target.mi);
  stepIndex.value = idx;
}

function startBlock(bi: number) {
  const block = blocks.value[bi];
  const firstModule = block?.moduleIndexes[0];
  if (!block || firstModule === undefined) return;

  blockIndex.value = bi;
  stepIndex.value = 0;
  sessionStore.sharedTimer = true; // le chrono est géré par la page, bloc par bloc
  sessionStore.switchToModule(firstModule);
  sessionStore.timeRemaining = block.minutes * 60;
  sessionStore.deadline = Date.now() + block.minutes * 60_000;
  phase.value = "running";
  startTimer();
}

async function begin(fullscreen: boolean) {
  if (fullscreen) await enterFullscreen();

  if (restoredCount.value > 0) {
    notify.info(
      t("toast.session_resumed", { n: sessionStore.subjectNumber }),
      t(
        "toast.session_resumed_detail",
        { n: restoredCount.value },
        restoredCount.value,
      ),
    );
  } else {
    notify.success(
      t("toast.session_started", { n: sessionStore.subjectNumber }),
      t("toast.session_started_detail"),
    );
  }
  startBlock(0);
}

function confirmFinish() {
  finishDialogVisible.value = false;
  if (isLastBlock.value) {
    submit(false);
    return;
  }
  stopTimer();
  phase.value = "transition";
}

// ── Réponses ──────────────────────────────────────────

const onAnswer = async (questionId: string, value: any) => {
  const res = await sessionStore.saveAnswer(questionId, value);
  if (!res?.success) warnSaveFailed();
};

// ── Sortie / soumission ───────────────────────────────

function exitSession() {
  stopTimer();
  leaveFullscreen();
  sessionStore.resetSession();
  navigateTo(localePath("/dashboard/examens"));
}

const hasSchreibenModule = computed(() =>
  sessionStore.modules.some((m: any) => isSchreibenSlug(m.slug)),
);

async function submit(auto: boolean) {
  finishDialogVisible.value = false;
  stopTimer();

  const result = await sessionStore.submitSession();
  if (!result.success) {
    notify.error(
      t("toast.error_title"),
      result.error || t("api_errors.generic"),
    );
    return;
  }

  if (auto) notify.info(t("toast.time_up"), t("toast.time_up_detail"));
  else notify.success(t("toast.submitted"), t("toast.submitted_detail"));

  const sessionId = sessionStore.sessionId;

  if (hasSchreibenModule.value && sessionId) {
    try {
      await correctionStore.correct(sessionId);
    } catch (err) {
      console.error("Erreur correction Schreiben:", err);
    }
  }

  leaveFullscreen();

  const slug = route.params.slug as string;
  const moduleSlug = route.query.moduleSlug as string | undefined;
  const moduleSlugs = route.query.moduleSlugs as string | undefined;
  navigateTo(
    localePath({
      path: `/dashboard/examens/${slug}/result`,
      query: {
        sessionId,
        ...(moduleSlug ? { moduleSlug } : {}),
        ...(moduleSlugs ? { moduleSlugs } : {}),
      },
    }),
  );
}

// ── Chargement ────────────────────────────────────────

async function loadSession() {
  initialized.value = false;
  loadError.value = null;
  stopTimer();
  warned.clear();
  phase.value = "intro";
  blockIndex.value = 0;
  stepIndex.value = 0;
  tabSwitches.value = 0;

  sessionStore.resetSession();

  const examId = route.query.examId as string;
  const subjectId = route.query.subjectId as string | undefined;
  const moduleSlug = route.query.moduleSlug as string | undefined;
  const moduleSlugs = route.query.moduleSlugs as string | undefined;

  if (!examId) {
    navigateTo(localePath("/dashboard/examens"));
    return;
  }

  // Appel direct au store : un seul chrono, celui de cette page
  const result = await sessionStore.startSession(examId, subjectId);
  if (!result.success) {
    loadError.value = sessionStore.error || t("api_errors.generic");
    notify.error(t("toast.error_title"), loadError.value);
    initialized.value = true;
    return;
  }

  // 1. Mode module seul / modules combinés
  moduleMode.value = !!(moduleSlug || moduleSlugs);
  if (moduleMode.value) {
    const targetSlugs = moduleSlugs
      ? moduleSlugs.split(",").map((s) => s.trim().toLowerCase())
      : [moduleSlug!.toLowerCase()];
    sessionStore.modules = sessionStore.modules.filter((m: any) =>
      targetSlugs.some((slug) => slugOf(m.slug).includes(slug)),
    );
  }

  // 2. Oral : passé séparément avec un examinateur, hors du lecteur
  oralModuleNames.value = sessionStore.modules
    .filter((m: any) => isOralSlug(m.slug))
    .map((m: any) => m.name);
  sessionStore.modules = sessionStore.modules.filter(
    (m: any) => !isOralSlug(m.slug),
  );
  sessionStore.questions = sessionStore.questions.filter((q: any) =>
    sessionStore.modules.some((m: any) =>
      m.teile?.some((tl: any) => tl.id === q.teil_id),
    ),
  );

  if (
    !sessionStore.modules.length &&
    oralModuleNames.value.length &&
    sprechenLink.value
  ) {
    navigateTo(sprechenLink.value);
    return;
  }

  moduleModeMinutes.value =
    sessionStore.modules.reduce(
      (sum: number, m: any) => sum + (Number(m.time_limit_minutes) || 0),
      0,
    ) || 30;

  restoredCount.value = Object.keys(sessionStore.answers).length;
  initialized.value = true;
}

onMounted(() => {
  restoreFontStep();
  applyFontScale();
  document.addEventListener("visibilitychange", onVisibilityChange);
  loadSession();
});

onBeforeUnmount(() => {
  document.documentElement.style.fontSize = "";
  stopTimer();
  document.removeEventListener("visibilitychange", onVisibilityChange);
  leaveFullscreen();
});

// Recharge si on passe à un autre sujet/module sans recharger la page
watch(
  () => [
    route.query.subjectId,
    route.query.examId,
    route.query.moduleSlug,
    route.query.moduleSlugs,
  ],
  () => loadSession(),
);
</script>
