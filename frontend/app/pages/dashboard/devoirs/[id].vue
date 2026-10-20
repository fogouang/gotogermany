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

    <!-- ── Entre deux blocs ── -->
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
              name: blockLabel(currentBlock),
            })
          }}
        </h2>
        <p class="mt-1 text-sm text-muted">
          {{
            t("session.player.answered", {
              answered: blockAnswered,
              total: blockQuestions.length,
            })
          }}
        </p>

        <div
          v-if="nextBlock"
          class="mt-6 rounded-leaf border border-line bg-card-2 p-4 text-left"
        >
          <p class="text-xs font-semibold uppercase tracking-wide text-faint">
            {{ t("session.player.transition_next") }}
          </p>
          <p class="mt-1 font-semibold text-ink">{{ blockLabel(nextBlock) }}</p>
          <p class="mt-0.5 text-sm text-muted">
            <i class="pi pi-clock mr-1 text-xs" />
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

    <!-- ── Lecteur ── -->
    <template v-else-if="sessionStore.sessionId && currentModule">
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

      <!-- Modules : seuls ceux du bloc en cours sont accessibles -->
      <div class="shrink-0 border-b border-line bg-card">
        <div class="mx-auto flex max-w-7xl overflow-x-auto px-4">
          <button
            v-for="(mod, mi) in sessionStore.modules"
            :key="mod.id"
            type="button"
            :disabled="
              moduleState(mi) === 'done' || moduleState(mi) === 'locked'
            "
            class="whitespace-nowrap border-b-2 px-5 py-3 text-sm font-medium transition-colors disabled:cursor-not-allowed"
            :class="tabClass(mi)"
            @click="goToModule(mi)"
          >
            <i class="pi mr-2" :class="tabIcon(mod.slug, mi)" />
            {{ mod.name }}
          </button>
        </div>
      </div>

      <div class="min-h-0 flex-1 overflow-y-auto">
        <component
          :is="currentView"
          :key="`${blockIndex}-${stepIndex}`"
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
        :is-last-step="isLastStep"
        :finish-label="
          isLastBlock ? t('session.submit') : t('session.player.finish_module')
        "
        :answered="blockAnswered"
        :total="blockQuestions.length"
        @prev="goToStep(stepIndex - 1)"
        @next="goToStep(stepIndex + 1)"
        @finish="submitDialogVisible = true"
        @sheet="sheetVisible = true"
      />
    </template>

    <!-- ══════════ Feuille de réponses (bloc en cours) ══════════ -->
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

    <!-- ══════════ Terminer le bloc / rendre le devoir ══════════ -->
    <Dialog
      v-model:visible="submitDialogVisible"
      :header="
        isLastBlock
          ? t('session.submit_title')
          : t('session.player.finish_module_title')
      "
      modal
      :style="{ width: '26rem', maxWidth: '95vw' }"
    >
      <p class="mb-3 text-sm text-ink">
        {{
          t("session.player.answered", {
            answered: blockAnswered,
            total: blockQuestions.length,
          })
        }}
      </p>
      <Message v-if="blockUnanswered > 0" severity="warn" :closable="false">
        {{
          t(
            "session.player.unanswered",
            { n: blockUnanswered },
            blockUnanswered,
          )
        }}
      </Message>
      <p v-if="!isLastBlock" class="mt-3 text-sm text-muted">
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
            isLastBlock
              ? t('session.submit')
              : t('session.player.finish_module')
          "
          severity="success"
          :loading="sessionStore.isSubmitting"
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
import SessionAnswerSheet from "~/components/session/SessionAnswerSheet.vue";

definePageMeta({ layout: false });

type Phase = "running" | "transition";
type Block = { key: string; moduleIndexes: number[]; minutes: number };
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
const phase = ref<Phase>("running");
const blockIndex = ref(0);
const stepIndex = ref(0);
const exitDialogVisible = ref(false);
const submitDialogVisible = ref(false);
const sheetVisible = ref(false);

// ── Slugs ──
const slugText = (slug?: string) => (slug || "").toLowerCase();
const isOralSlug = (slug?: string) =>
  ["sprech", "muendlich", "mündlich"].some((p) => slugText(slug).includes(p));
const isSchreibenSlug = (slug?: string) =>
  slugText(slug).includes("schreib") || slugText(slug).includes("schriftlich");
const isHorenSlug = (slug?: string) =>
  ["hor", "hoer", "hör"].some((p) => slugText(slug).includes(p));

// ── Blocs chronométrés (même règle que le lecteur d'examen) ──
// Un module à 0 min rejoint le bloc précédent
// (TELC : Leseverstehen + Sprachbausteine = un seul bloc de 90 min).
const blocks = computed<Block[]>(() => {
  const out: Block[] = [];
  sessionStore.modules.forEach((m: any, i: number) => {
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

const blockOfModule = (mi: number) =>
  blocks.value.findIndex((b) => b.moduleIndexes.includes(mi));

// ── Étapes (Teile) du bloc courant ──
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
  return sessionStore.questions.filter((q) => q.teil_id === teilId);
});

const isSchreibenModule = computed(() =>
  isSchreibenSlug(currentModule.value?.slug),
);

const currentView = computed(() => {
  const slug = currentModule.value?.slug;
  if (isHorenSlug(slug)) return HorenView;
  if (isSchreibenSlug(slug)) return SchreibenView;
  return LesenView; // Lesen, Leseverstehen, Sprachbausteine
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

// ── Réponses du bloc ──
const blockQuestions = computed(() => {
  const teilIds = new Set(
    steps.value.map((s) => sessionStore.modules[s.mi]?.teile?.[s.ti]?.id),
  );
  return sessionStore.questions.filter((q) => teilIds.has(q.teil_id));
});

const blockAnswered = computed(
  () => blockQuestions.value.filter((q) => !!sessionStore.answers[q.id]).length,
);
const blockUnanswered = computed(
  () => blockQuestions.value.length - blockAnswered.value,
);

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

// ── Onglets des modules ──
type ModuleState = "current" | "block" | "done" | "locked";

function moduleState(mi: number): ModuleState {
  if (mi === currentModuleIndex.value) return "current";
  const bi = blockOfModule(mi);
  if (bi === blockIndex.value) return "block";
  return bi < blockIndex.value ? "done" : "locked";
}

const tabClass = (mi: number) => {
  switch (moduleState(mi)) {
    case "current":
      return "border-primary text-primary";
    case "block":
      return "border-transparent text-muted hover:text-ink";
    case "done":
      return "border-transparent text-emerald-600 opacity-70";
    default:
      return "border-transparent text-faint";
  }
};

const getModuleIcon = (slug: string) => {
  const s = slugText(slug);
  if (s.includes("sprachbaustein")) return "pi-language";
  if (s.includes("lese")) return "pi-book";
  if (isHorenSlug(s)) return "pi-volume-up";
  if (isSchreibenSlug(s)) return "pi-pencil";
  return "pi-file";
};

const tabIcon = (slug: string, mi: number) => {
  const state = moduleState(mi);
  if (state === "done") return "pi-check-circle";
  if (state === "locked") return "pi-lock";
  return getModuleIcon(slug);
};

// ── Navigation (dans le bloc uniquement) ──

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

function goToModule(mi: number) {
  if (blockOfModule(mi) !== blockIndex.value) return;
  const idx = steps.value.findIndex((s) => s.mi === mi);
  if (idx !== -1) goToStep(idx);
}

// Heure de fin du serveur, corrigée de l'écart d'horloge du navigateur
const serverDeadline = (s: {
  block_deadline?: string | null;
  server_now: string;
}) =>
  Date.parse(s.block_deadline as string) +
  (Date.now() - Date.parse(s.server_now));

function runBlock(bi: number, deadline: number) {
  const block = blocks.value[bi];
  const firstModule = block?.moduleIndexes[0];
  if (!block || firstModule === undefined) return;

  blockIndex.value = bi;
  stepIndex.value = 0;
  sessionStore.sharedTimer = true; // le chrono est géré par la page, bloc par bloc
  sessionStore.switchToModule(firstModule);
  sessionStore.deadline = deadline;
  sessionStore.timeRemaining = Math.max(
    0,
    Math.round((deadline - Date.now()) / 1000),
  );
  phase.value = "running";
  startTimer();
}

async function startBlock(bi: number) {
  const block = blocks.value[bi];
  if (!block) return;
  // Le serveur fixe l'heure de fin et refuse tout retour en arrière
  const state = await sessionStore.advanceBlock(bi, block.minutes);
  runBlock(
    bi,
    state?.block_deadline
      ? serverDeadline(state)
      : Date.now() + block.minutes * 60_000,
  );
}

// Reprise après rechargement : bloc et temps restant donnés par le serveur
async function resumeFromServer(): Promise<boolean> {
  const state = await sessionStore.fetchBlockState();
  if (!state?.block_deadline || !blocks.value.length) return false;

  const bi = Math.min(state.current_block, blocks.value.length - 1);
  const deadline = serverDeadline(state);
  if (deadline > Date.now()) {
    runBlock(bi, deadline);
    return true;
  }

  // Le temps du bloc s'est écoulé pendant l'absence
  blockIndex.value = bi;
  if (bi >= blocks.value.length - 1) {
    handleSubmit();
  } else {
    phase.value = "transition";
  }
  return true;
}

function confirmFinish() {
  if (isLastBlock.value) {
    handleSubmit();
    return;
  }
  submitDialogVisible.value = false;
  stopTimer();
  phase.value = "transition";
}

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
    if (Number.isInteger(v) && v >= 0 && v < FONT_SCALES.length)
      fontStep.value = v;
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

const onAnswer = async (questionId: string, value: any) => {
  const res = await sessionStore.saveAnswer(questionId, value);
  if (!res?.success) warnSaveFailed();
};

// ── Chrono du bloc, basé sur l'heure réelle ──
let timerInterval: ReturnType<typeof setInterval> | null = null;

function stopTimer() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;
}

function startTimer() {
  stopTimer();
  timerInterval = setInterval(() => {
    sessionStore.tick();
    warnIfLowTime();
    if (sessionStore.timeRemaining <= 0) onTimeUp();
  }, 1000);
}

function onTimeUp() {
  stopTimer();
  if (isLastBlock.value) {
    notify.info(t("toast.time_up"), t("toast.time_up_detail"));
    handleSubmit();
    return;
  }
  notify.info(
    t("session.player.time_up_module"),
    t("session.player.time_up_module_detail"),
  );
  submitDialogVisible.value = false;
  phase.value = "transition";
}

// ── Remise (sans correction IA : c'est l'enseignant qui corrige) ──
async function handleSubmit() {
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
}

// ── Sortie ──
const backToList = () => navigateTo(localePath("/dashboard/devoirs"));

function exitAssignment() {
  stopTimer();
  sessionStore.resetSession();
  backToList();
}

// ── Chargement ──
async function load() {
  initialized.value = false;
  submitted.value = false;
  phase.value = "running";
  blockIndex.value = 0;
  stepIndex.value = 0;
  stopTimer();
  warned.clear();

  const result = await sessionStore.startAssignment(assignmentId.value);

  if (result.success) {
    // Oral : évalué en session live avec l'enseignant, pas dans le devoir
    sessionStore.modules = sessionStore.modules.filter(
      (m) => !isOralSlug(m.slug),
    );
    sessionStore.questions = sessionStore.questions.filter((q) =>
      sessionStore.modules.some((m) =>
        m.teile?.some((tl) => tl.id === q.teil_id),
      ),
    );
  }

  initialized.value = true;

  if (result.success && sessionStore.modules.length) {
    const restored = Object.keys(sessionStore.answers).length;
    if (restored > 0) {
      notify.info(
        t("toast.session_resumed", { n: sessionStore.subjectNumber }),
        t("toast.session_resumed_detail", { n: restored }, restored),
      );
    }
    // Devoir déjà commencé : reprise au bon bloc ; sinon premier bloc
    if (!(await resumeFromServer())) await startBlock(0);
  }
}

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
