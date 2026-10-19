<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useSprechenSession } from "~/composables/useSprechenSession";
import { createBrowserAudioIO } from "~/composables/audioIO";
import ThemeChoicePanel from "~/components/sprechen/ThemeChoicePanel.vue";
import ExaminerTile from "~/components/sprechen/ExaminerTile.vue";
import CandidateTile from "~/components/sprechen/CandidateTile.vue";
import TranscriptPanel from "~/components/sprechen/TranscriptPanel.vue";
import CallControls from "~/components/sprechen/CallControls.vue";
import ExaminerAvatar from "~/components/sprechen/ExaminerAvatar.vue";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const route = useRoute();
const localePath = useLocalePath();
const runtimeConfig = useRuntimeConfig();

const subjectId = route.params.subjectId as string;
const wsBaseUrl = runtimeConfig.public.sprechenWsBaseUrl as string;
const audioIO = createBrowserAudioIO({ muteMicWhilePlaying: true });

const {
  status,
  totalTeile,
  currentTeil,
  preparationInfo,
  micState,
  transcript,
  gradingResult,
  errorMessage,
  errorCode,
  connect,
  sendReadyToStart,
  abandonSession,
  disconnect,
} = useSprechenSession({ subjectId, wsBaseUrl, audioIO });

const isCallTheme = computed(
  () =>
    ["idle", "connecting", "preparing", "active", "error"].includes(
      status.value,
    ) ||
    (status.value === "ended" && !gradingResult.value),
);

// Pendant la préparation, currentTeil est encore l'ANCIEN Teil :
// on affiche celui qu'on prépare.
const headerTeilName = computed(() =>
  status.value === "preparing"
    ? (preparationInfo.value?.teil_name ?? "")
    : (currentTeil.value?.teil_name ?? preparationInfo.value?.teil_name ?? ""),
);
const headerTeilNumber = computed(() =>
  status.value === "preparing"
    ? (preparationInfo.value?.teil_number ?? null)
    : (currentTeil.value?.teil_number ??
      preparationInfo.value?.teil_number ??
      null),
);

// ── Interface d'appel ──
// Une seule scène pour la préparation et l'échange : l'avatar 3D se
// charge pendant la préparation et n'est jamais remonté entre deux Teile.
const isStage = computed(
  () =>
    (status.value === "preparing" && !!preparationInfo.value) ||
    (status.value === "active" && !!currentTeil.value),
);

// Teil affiché dans le panneau de consignes
const panelTeil = computed(() =>
  status.value === "preparing" ? preparationInfo.value : currentTeil.value,
);

const callState = computed<"preparing" | "agent" | "student" | "waiting">(
  () => {
    if (status.value === "preparing") return "preparing";
    if (micState.value === "agent_speaking") return "agent";
    if (micState.value === "student_turn") return "student";
    return "waiting";
  },
);

const authStore = useAuthStore();

// Message d'erreur affiché : les causes connues sont traduites
const errorText = computed(() =>
  errorCode.value === "insufficient_credits"
    ? t("sprechen_subject.insufficient_credits")
    : errorMessage.value || t("sprechen_subject.connection_error"),
);

// Les crédits sont débités au premier "Commencer" : on rafraîchit le
// solde affiché dès que l'oral démarre vraiment.
let creditsRefreshed = false;
watch(status, (value) => {
  if (value === "active" && !creditsRefreshed) {
    creditsRefreshed = true;
    void authStore.fetchUser();
  }
});

const showTranscript = ref(true);

const cameraEnabled = ref(false);

// Tuile de l'examinatrice : expose la sortie audio de l'avatar 3D
// (branchement de la voix pour le lip-sync à faire dans audioIO).
const examinerRef = ref<{
  getAudioOutput: () => { ctx: AudioContext; node: AudioNode } | null;
  resume: () => Promise<void> | undefined;
} | null>(null);

// La voix de l'examinatrice passe par l'avatar 3D dès qu'il est prêt
// (lip-sync). Avant ça, audioIO joue sur son contexte habituel.
audioIO.setOutputTarget(() => {
  const out = examinerRef.value?.getAudioOutput() ?? null;
  // Contexte de l'avatar en pause (pas encore débloqué par un clic) :
  // on garde la lecture habituelle plutôt que de jouer dans le vide.
  return out && out.ctx.state === "running" ? out : null;
});

// Chaque clic dans la page débloque l'audio de l'avatar s'il est en pause
function unlockAvatarAudio() {
  try {
    void Promise.resolve(examinerRef.value?.resume()).catch(() => {});
  } catch {
    // avatar pas prêt
  }
}
onMounted(() => window.addEventListener("pointerdown", unlockAvatarAudio));
onUnmounted(() => window.removeEventListener("pointerdown", unlockAvatarAudio));

function startNow() {
  // L'envoi au backend passe en premier : rien ne doit pouvoir le bloquer
  sendReadyToStart();

  // Geste utilisateur : on en profite pour débloquer l'audio de l'avatar
  try {
    void Promise.resolve(examinerRef.value?.resume()).catch(() => {});
  } catch {
    // avatar pas prêt : audioIO relancera le contexte au premier son
  }
}
const groupedTranscript = computed(() => {
  const groups: { speaker: "student" | "agent"; text: string }[] = [];
  for (const line of transcript.value) {
    const last = groups[groups.length - 1];
    if (last && last.speaker === line.speaker) {
      last.text = `${last.text} ${line.text}`.replace(/\s+/g, " ").trim();
    } else {
      groups.push({ speaker: line.speaker, text: line.text.trim() });
    }
  }
  return groups;
});

// Seuil d'alerte visuelle (rien n'est coupé côté backend)
const TIMER_ALERT_THRESHOLD_SECONDS = 30;

const formatClock = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
};

// ── Préparation : temps écoulé (affichage principal, sans limite)
// + repère du temps officiel (preparation_minutes), jamais imposé ──
const prepSecondsElapsed = ref(0);
const prepSecondsLeft = ref(0);
let prepIntervalId: ReturnType<typeof setInterval> | null = null;

const officialPrepSeconds = computed(
  () => (preparationInfo.value?.preparation_minutes ?? 0) * 60,
);

watch(preparationInfo, (info) => {
  if (prepIntervalId) clearInterval(prepIntervalId);
  prepIntervalId = null;
  if (!info) return;
  prepSecondsElapsed.value = 0;
  prepSecondsLeft.value = (info.preparation_minutes ?? 0) * 60;
  prepIntervalId = setInterval(() => {
    prepSecondsElapsed.value += 1;
    if (prepSecondsLeft.value > 0) prepSecondsLeft.value -= 1;
  }, 1000);
});

const prepElapsedLabel = computed(() => formatClock(prepSecondsElapsed.value));
const prepCountdownLabel = computed(() => formatClock(prepSecondsLeft.value));
const prepTimerIsAlert = computed(
  () =>
    prepSecondsLeft.value > 0 &&
    prepSecondsLeft.value <= TIMER_ALERT_THRESHOLD_SECONDS,
);

// ── Compte à rebours du Teil actif (alerte seulement : le backend
// enchaîne lui-même sur le Teil suivant) ──
const teilSecondsLeft = ref(0);
let teilIntervalId: ReturnType<typeof setInterval> | null = null;

watch(currentTeil, (teil) => {
  if (teilIntervalId) clearInterval(teilIntervalId);
  teilIntervalId = null;
  if (!teil) return;
  teilSecondsLeft.value = (teil.duration_minutes || 0) * 60;
  teilIntervalId = setInterval(() => {
    if (teilSecondsLeft.value > 0) teilSecondsLeft.value -= 1;
  }, 1000);
});

const teilCountdownLabel = computed(() => formatClock(teilSecondsLeft.value));
const teilTimerIsAlert = computed(
  () =>
    teilSecondsLeft.value > 0 &&
    teilSecondsLeft.value <= TIMER_ALERT_THRESHOLD_SECONDS,
);

// ── Étapes décoratives pendant la notation ──
const gradingSteps = [
  { key: "listening", labelKey: "sprechen_subject.grading_step_listening" },
  { key: "vocab", labelKey: "sprechen_subject.grading_step_vocab" },
  {
    key: "pronunciation",
    labelKey: "sprechen_subject.grading_step_pronunciation",
  },
  { key: "tips", labelKey: "sprechen_subject.grading_step_tips" },
];
const gradingStepIndex = ref(0);
let gradingIntervalId: ReturnType<typeof setInterval> | null = null;

watch(status, (value) => {
  if (value === "ended" && !gradingResult.value) {
    gradingStepIndex.value = 0;
    gradingIntervalId = setInterval(() => {
      if (gradingStepIndex.value < gradingSteps.length - 1)
        gradingStepIndex.value += 1;
    }, 2500);
  } else if (gradingIntervalId) {
    clearInterval(gradingIntervalId);
    gradingIntervalId = null;
  }

  // currentTeil n'est pas remis à null en fin de session : on arrête ici
  if (value !== "active" && teilIntervalId) {
    clearInterval(teilIntervalId);
    teilIntervalId = null;
  }
  if (value !== "preparing" && prepIntervalId) {
    clearInterval(prepIntervalId);
    prepIntervalId = null;
  }
});

function gradingStepStateClass(i: number) {
  if (i < gradingStepIndex.value) return "bg-emerald-500/10";
  if (i === gradingStepIndex.value) return "bg-primary/10";
  return "";
}

const scorePercent = computed(() => {
  if (!gradingResult.value || !gradingResult.value.total_max_score) return 0;
  return Math.round(
    (gradingResult.value.total_score / gradingResult.value.total_max_score) *
      100,
  );
});

// ── Navigation ──
const goToList = () => navigateTo(localePath("/dashboard/sprechen"));

function confirmLeave() {
  if (
    status.value === "active" &&
    !window.confirm(t("sprechen_subject.confirm_leave"))
  )
    return;
  abandonSession();
  goToList();
}

const redo = () => {
  disconnect();
  connect();
};

onMounted(() => connect());
onUnmounted(() => {
  audioIO.setOutputTarget(null);
  disconnect();
  if (prepIntervalId) clearInterval(prepIntervalId);
  if (teilIntervalId) clearInterval(teilIntervalId);
  if (gradingIntervalId) clearInterval(gradingIntervalId);
});

useHead({ title: t("sprechen_subject.page_title") });
</script>

<template>
  <div>
    <!-- Pendant l'appel, l'écran sort du layout (sinon son en-tête passe par-dessus) -->
    <Teleport to="body" :disabled="!isCallTheme">
      <div
        class="flex flex-col bg-canvas text-ink"
        :class="
          isCallTheme
            ? 'fixed inset-0 z-100 overflow-hidden'
            : 'h-screen overflow-hidden'
        "
      >
        <div class="relative flex min-h-0 flex-1 flex-col">
          <!-- Connexion -->
          <div
            v-if="status === 'connecting' || status === 'idle'"
            class="flex flex-1 items-center justify-center"
          >
            <div class="flex flex-col items-center gap-5">
              <div class="relative grid size-28 place-items-center">
                <span
                  class="absolute inset-0 animate-pulse rounded-full bg-primary/15 blur-xl"
                />
                <span
                  class="relative grid size-16 place-items-center rounded-full border border-line bg-card shadow-soft"
                >
                  <i class="pi pi-spin pi-spinner text-xl text-primary" />
                </span>
              </div>
              <p class="text-sm font-medium tracking-wide text-muted">
                {{ t("sprechen_subject.connecting") }}
              </p>
            </div>
          </div>

          <!-- Erreur -->
          <div
            v-else-if="status === 'error'"
            class="flex flex-1 items-center justify-center"
          >
            <div class="max-w-lg space-y-4 px-6 text-center">
              <span
                class="mx-auto grid size-14 place-items-center rounded-full border border-red-400/25 bg-red-500/10"
              >
                <i class="pi pi-exclamation-circle text-2xl text-red-500" />
              </span>
              <p class="font-medium text-ink">
                {{ errorText }}
              </p>
              <Button
                :label="t('sprechen_subject.back')"
                icon="pi pi-arrow-left"
                outlined
                severity="secondary"
                @click="goToList"
              />
            </div>
          </div>

          <!-- Session : préparation / échange / notation / résultat -->
          <template v-else>
            <!-- Barre d'appel -->
            <header
              v-if="isCallTheme"
              class="flex shrink-0 items-center gap-3 border-b border-line bg-card/80 px-4 py-3 backdrop-blur-md"
            >
              <button
                type="button"
                :aria-label="t('sprechen_subject.back')"
                class="grid size-9 shrink-0 place-items-center rounded-leaf text-muted transition-colors hover:bg-card-2 hover:text-ink"
                @click="confirmLeave"
              >
                <i class="pi pi-arrow-left text-sm" />
              </button>

              <div class="flex min-w-0 flex-1 items-center gap-2.5">
                <span
                  class="size-2 shrink-0 rounded-full"
                  :class="
                    status === 'active'
                      ? 'animate-pulse bg-red-500 shadow-[0_0_0_4px_rgb(239_68_68/0.25)]'
                      : 'bg-faint'
                  "
                />
                <h1 class="truncate text-sm font-bold text-ink">
                  {{ headerTeilName }}
                </h1>
              </div>

              <span
                v-if="isStage"
                class="hidden shrink-0 items-center gap-1.5 rounded-full bg-card-2 px-2.5 py-1 text-xs font-semibold text-muted sm:inline-flex"
              >
                <i class="pi pi-shield text-[0.65rem]" />
                {{ t("sprechen_subject.call.exam_mode") }}
              </span>
              <span
                v-if="headerTeilNumber"
                class="shrink-0 rounded-full bg-card-2 px-2.5 py-1 text-xs font-semibold text-muted"
              >
                Teil {{ headerTeilNumber }} / {{ totalTeile }}
              </span>
            </header>

            <!-- ═══════════════ Scène : préparation + échange ═══════════════ -->
            <div
              v-if="isStage"
              class="grid min-h-0 flex-1 grid-rows-[auto_minmax(0,1fr)] md:grid-cols-[320px_minmax(0,1fr)] md:grid-rows-1"
            >
              <!-- Consignes -->
              <aside
                v-if="panelTeil"
                class="flex max-h-52 flex-col gap-5 overflow-y-auto border-b border-line bg-card/70 p-5 backdrop-blur md:max-h-none md:border-b-0 md:border-r md:p-6"
              >
                <div>
                  <span
                    class="text-xs font-semibold uppercase tracking-wide text-faint"
                  >
                    Teil {{ panelTeil.teil_number }}
                  </span>
                  <h2 class="mt-1 text-lg font-semibold text-ink">
                    {{ panelTeil.teil_name }}
                  </h2>
                </div>

                <p class="text-sm leading-relaxed text-muted">
                  {{ panelTeil.instructions }}
                </p>

                <div
                  v-if="panelTeil.scenario"
                  class="rounded-leaf border border-primary/20 bg-primary/10 px-4 py-3"
                >
                  <p
                    class="mb-1 text-[11px] font-semibold uppercase tracking-wide text-primary"
                  >
                    {{ t("sprechen_subject.scenario_label") }}
                  </p>
                  <p class="text-sm leading-relaxed text-ink">
                    {{ panelTeil.scenario }}
                  </p>
                </div>

                <div
                  v-if="panelTeil.stimulus_people?.length"
                  class="overflow-hidden rounded-card border border-line bg-card-2"
                >
                  <div class="border-b border-line px-4 py-2">
                    <p
                      class="text-[11px] font-semibold uppercase tracking-wide text-faint"
                    >
                      {{ t("sprechen_subject.stimulus_people_label") }}
                    </p>
                  </div>
                  <div class="divide-y divide-line">
                    <div
                      v-for="person in panelTeil.stimulus_people"
                      :key="person.name"
                      class="px-4 py-3"
                    >
                      <p class="text-sm font-semibold text-ink">
                        {{ person.name }}
                      </p>
                      <p class="mt-1.5 text-sm italic leading-relaxed text-ink">
                        „{{ person.opinion }}“
                      </p>
                    </div>
                  </div>
                </div>

                <div
                  v-if="panelTeil.stimulus_text"
                  class="overflow-hidden rounded-card border border-line bg-card-2"
                >
                  <div class="border-b border-line px-4 py-2">
                    <p
                      class="text-[11px] font-semibold uppercase tracking-wide text-faint"
                    >
                      {{ t("sprechen_subject.reading_text_label") }}
                    </p>
                  </div>
                  <p
                    class="max-h-80 overflow-y-auto whitespace-pre-line px-4 py-3 text-sm leading-relaxed text-ink"
                  >
                    {{ panelTeil.stimulus_text }}
                  </p>
                </div>

                <ThemeChoicePanel
                  v-if="panelTeil.themes"
                  :themes="panelTeil.themes"
                />
                <div
                  v-if="
                    panelTeil.content_points.length &&
                    (status === 'active' || !panelTeil.themes)
                  "
                  class="overflow-hidden rounded-card border border-line bg-card-2"
                >
                  <div class="border-b border-line px-4 py-2">
                    <p
                      class="text-[11px] font-semibold uppercase tracking-wide text-faint"
                    >
                      {{ t("sprechen_subject.points_to_cover") }}
                    </p>
                  </div>
                  <ul class="space-y-1.5 px-4 py-3">
                    <li
                      v-for="point in panelTeil.content_points"
                      :key="point"
                      class="flex gap-2 text-sm text-ink"
                    >
                      <i
                        class="pi pi-circle-fill mt-2 shrink-0 text-[5px] text-primary"
                      />
                      <span>{{ point }}</span>
                    </li>
                  </ul>
                </div>
              </aside>

              <!-- Scène d'appel -->
              <section class="flex min-h-0 flex-col">
                <div class="flex min-h-0 flex-1 flex-col gap-4 p-4 lg:flex-row">
                  <div class="relative min-h-0 flex-1">
                    <ExaminerTile
                      ref="examinerRef"
                      avatar-url="/avatars/brunette.glb"
                      :speaking="micState === 'agent_speaking'"
                      :listening="micState === 'student_turn'"
                    />

                    <!-- Vignette candidat -->
                    <div
                      class="absolute bottom-3 right-3 z-10 h-32 w-24 sm:h-40 sm:w-32"
                    >
                      <CandidateTile
                        class="size-full"
                        :mic-active="status === 'active'"
                        :speaking="micState === 'student_turn'"
                        :camera-enabled="cameraEnabled"
                        @camera-error="cameraEnabled = false"
                      />
                    </div>

                    <!-- Préparation : carte posée sur la scène -->
                    <div
                      v-if="status === 'preparing'"
                      class="absolute inset-0 z-20 grid place-items-center rounded-card bg-canvas/55 p-4 backdrop-blur-sm"
                    >
                      <div
                        class="flex w-full max-w-sm flex-col items-center gap-5 rounded-card border border-line bg-card p-6 shadow-soft"
                      >
                        <div class="flex flex-col items-center gap-1.5">
                          <span
                            class="text-3xl font-semibold tabular-nums text-ink"
                          >
                            {{ prepElapsedLabel }}
                          </span>
                          <span
                            class="text-xs uppercase tracking-wide text-faint"
                          >
                            {{ t("sprechen_subject.preparing") }}
                          </span>
                        </div>

                        <!-- Repère : temps officiel de préparation (jamais imposé) -->
                        <span
                          v-if="officialPrepSeconds > 0"
                          class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold transition-colors"
                          :class="
                            prepSecondsLeft === 0
                              ? 'border-line bg-card-2 text-muted'
                              : prepTimerIsAlert
                                ? 'animate-pulse border-red-400/40 bg-red-500/15 text-red-600'
                                : 'border-primary/25 bg-primary/10 text-primary'
                          "
                        >
                          <i class="pi pi-clock text-[11px]" />
                          {{
                            prepSecondsLeft > 0
                              ? t("sprechen_subject.official_prep_left", {
                                  time: prepCountdownLabel,
                                })
                              : t("sprechen_subject.official_prep_over")
                          }}
                        </span>

                        <p
                          class="text-center text-sm leading-relaxed text-muted"
                        >
                          {{ t("sprechen_subject.preparation_no_limit") }}
                        </p>
                        <Button
                          :label="t('sprechen_subject.start_now')"
                          icon="pi pi-play"
                          class="w-full"
                          @click="startNow"
                        />
                      </div>
                    </div>
                  </div>

                  <TranscriptPanel
                    v-if="status === 'active' && showTranscript"
                    :lines="groupedTranscript"
                    class="h-44 shrink-0 lg:h-auto lg:w-80"
                  />
                </div>

                <CallControls
                  :state="callState"
                  :timer-label="status === 'active' ? teilCountdownLabel : null"
                  :timer-alert="teilTimerIsAlert"
                  :transcript-available="status === 'active'"
                  :transcript-visible="showTranscript"
                  :camera-enabled="cameraEnabled"
                  @toggle-transcript="showTranscript = !showTranscript"
                  @toggle-camera="cameraEnabled = !cameraEnabled"
                />
              </section>
            </div>

            <!-- ═══════════════ Notation en cours ═══════════════ -->
            <div
              v-else-if="status === 'ended' && !gradingResult"
              class="flex flex-1 items-center justify-center p-6"
            >
              <div
                class="w-full max-w-sm rounded-card bg-card p-7 text-center text-ink shadow-soft"
              >
                <div
                  class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10"
                >
                  <i class="pi pi-comments text-2xl text-primary"></i>
                </div>
                <h3 class="mb-1 text-base font-semibold text-ink">
                  {{ t("sprechen_subject.grading_modal_title") }}
                </h3>
                <p class="mb-5 text-sm text-muted">
                  {{ t("sprechen_subject.grading_modal_subtitle") }}
                </p>

                <div class="flex flex-col gap-2 text-left">
                  <div
                    v-for="(step, i) in gradingSteps"
                    :key="step.key"
                    class="flex items-center gap-2.5 rounded-leaf px-3 py-2.5 transition-colors"
                    :class="gradingStepStateClass(i)"
                  >
                    <i
                      :class="[
                        'shrink-0 text-lg',
                        i < gradingStepIndex
                          ? 'pi pi-check-circle text-emerald-600'
                          : '',
                        i === gradingStepIndex
                          ? 'pi pi-spin pi-spinner text-primary'
                          : '',
                        i > gradingStepIndex ? 'pi pi-circle text-faint' : '',
                      ]"
                    ></i>
                    <span
                      class="text-sm"
                      :class="
                        i <= gradingStepIndex
                          ? 'font-medium text-ink'
                          : 'text-faint'
                      "
                    >
                      {{ t(step.labelKey) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- ═══════════════ Résultat ═══════════════ -->
            <div
              v-else-if="status === 'ended' && gradingResult"
              class="flex-1 overflow-y-auto"
            >
              <div class="mx-auto max-w-2xl space-y-5 px-4 py-8">
                <!-- En-tête -->
                <div
                  class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
                >
                  <div
                    :class="[
                      'h-1.5',
                      gradingResult.passed ? 'bg-emerald-500' : 'bg-amber-500',
                    ]"
                  ></div>
                  <div
                    class="flex items-center justify-between gap-4 px-6 py-5"
                  >
                    <div>
                      <p
                        class="mb-1 text-xs font-semibold uppercase tracking-wider text-muted"
                      >
                        {{ gradingResult.provider.toUpperCase() }} ·
                        {{ gradingResult.level.toUpperCase() }} · Sprechen
                      </p>
                      <h1 class="text-2xl font-bold text-ink">
                        {{
                          gradingResult.passed
                            ? t("sprechen_subject.passed")
                            : t("sprechen_subject.not_passed")
                        }}
                      </h1>
                      <p class="mt-1 text-sm tabular-nums text-muted">
                        {{ gradingResult.total_score }} /
                        {{ gradingResult.total_max_score }}
                        {{ t("sprechen_subject.points") }}
                      </p>
                    </div>
                    <p
                      :class="[
                        'shrink-0 text-3xl font-extrabold tabular-nums',
                        gradingResult.passed
                          ? 'text-emerald-600'
                          : 'text-amber-600',
                      ]"
                    >
                      {{ scorePercent }}%
                    </p>
                  </div>
                </div>

                <!-- Évolution -->
                <div
                  v-if="gradingResult.score_delta_percent !== null"
                  class="flex items-center justify-between rounded-card border border-line bg-card px-5 py-4"
                >
                  <div>
                    <p class="mb-0.5 text-xs text-muted">
                      {{ t("sprechen_subject.score_delta_since_last") }}
                    </p>
                    <p class="text-lg font-semibold tabular-nums text-ink">
                      {{ Math.round(gradingResult.previous_score_percent!) }}%
                    </p>
                  </div>
                  <span
                    class="flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold tabular-nums"
                    :class="
                      gradingResult.score_delta_percent >= 0
                        ? 'bg-emerald-500/10 text-emerald-700'
                        : 'bg-amber-500/10 text-amber-700'
                    "
                  >
                    <i
                      :class="
                        gradingResult.score_delta_percent >= 0
                          ? 'pi pi-arrow-up'
                          : 'pi pi-arrow-down'
                      "
                    ></i>
                    {{ gradingResult.score_delta_percent >= 0 ? "+" : ""
                    }}{{ Math.round(gradingResult.score_delta_percent) }}%
                  </span>
                </div>

                <!-- Détail par Teil -->
                <div
                  class="overflow-hidden rounded-card border border-line bg-card"
                >
                  <div class="border-b border-line px-5 py-4">
                    <h2 class="text-sm font-semibold text-ink">
                      {{ t("sprechen_subject.detail_by_teil") }}
                    </h2>
                  </div>
                  <div class="divide-y divide-line">
                    <div
                      v-for="teil in gradingResult.teile"
                      :key="teil.teil_number"
                      class="space-y-3 px-5 py-4"
                    >
                      <div class="flex items-center justify-between gap-3">
                        <span class="text-sm font-semibold text-ink"
                          >Teil {{ teil.teil_number }} ·
                          {{ teil.teil_name }}</span
                        >
                        <span
                          class="shrink-0 text-xs font-semibold tabular-nums text-muted"
                        >
                          {{ teil.teil_score }} / {{ teil.teil_max_score }}
                        </span>
                      </div>

                      <div
                        v-for="c in teil.criteria"
                        :key="c.criterion_name"
                        class="rounded-leaf border border-line bg-card-2 p-3.5"
                      >
                        <div class="mb-2 flex items-center justify-between">
                          <span class="text-sm font-medium text-ink">{{
                            c.criterion_name
                          }}</span>
                          <span
                            class="text-xs font-semibold tabular-nums"
                            :class="
                              c.max_score && c.score / c.max_score >= 0.75
                                ? 'text-emerald-600'
                                : 'text-amber-600'
                            "
                          >
                            {{ c.score }} / {{ c.max_score }}
                          </span>
                        </div>

                        <div
                          v-if="c.issue"
                          class="mb-2 flex gap-2 rounded-leaf bg-amber-500/10 px-3 py-2"
                        >
                          <i
                            class="pi pi-exclamation-circle mt-0.5 shrink-0 text-xs text-amber-600"
                          ></i>
                          <p class="text-xs leading-relaxed text-ink">
                            <span class="font-semibold"
                              >{{
                                t("sprechen_subject.criterion_issue_label")
                              }}
                              :</span
                            >
                            {{ c.issue }}
                          </p>
                        </div>

                        <div
                          v-if="c.model_phrase"
                          class="mb-2 flex gap-2 rounded-leaf bg-primary/10 px-3 py-2"
                        >
                          <i
                            class="pi pi-comment mt-0.5 shrink-0 text-xs text-primary"
                          ></i>
                          <p class="text-xs italic leading-relaxed text-ink">
                            <span class="font-semibold not-italic"
                              >{{
                                t(
                                  "sprechen_subject.criterion_model_phrase_label",
                                )
                              }}
                              :</span
                            >
                            „{{ c.model_phrase }}“
                          </p>
                        </div>

                        <div v-if="c.tip" class="flex gap-2 px-1">
                          <i
                            class="pi pi-lightbulb mt-0.5 shrink-0 text-xs text-faint"
                          ></i>
                          <p class="text-xs leading-relaxed text-muted">
                            <span class="font-semibold"
                              >{{
                                t("sprechen_subject.criterion_tip_label")
                              }}
                              :</span
                            >
                            {{ c.tip }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Points forts / à améliorer -->
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div v-if="gradingResult.strengths.length">
                    <p
                      class="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-emerald-600"
                    >
                      <i class="pi pi-check-circle" />{{
                        t("sprechen_subject.strengths")
                      }}
                    </p>
                    <ul class="space-y-1.5">
                      <li
                        v-for="(s, i) in gradingResult.strengths"
                        :key="i"
                        class="flex items-start gap-2 rounded-leaf bg-emerald-500/10 px-3 py-2 text-sm text-ink"
                      >
                        <i
                          class="pi pi-check mt-0.5 shrink-0 text-xs text-emerald-600"
                        /><span>{{ s }}</span>
                      </li>
                    </ul>
                  </div>
                  <div v-if="gradingResult.improvement_areas.length">
                    <p
                      class="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-amber-600"
                    >
                      <i class="pi pi-exclamation-circle" />{{
                        t("sprechen_subject.to_improve")
                      }}
                    </p>
                    <ul class="space-y-1.5">
                      <li
                        v-for="(a, i) in gradingResult.improvement_areas"
                        :key="i"
                        class="flex items-start gap-2 rounded-leaf bg-amber-500/10 px-3 py-2 text-sm text-ink"
                      >
                        <i
                          class="pi pi-arrow-right mt-0.5 shrink-0 text-xs text-amber-600"
                        /><span>{{ a }}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex flex-col gap-3 pb-8 sm:flex-row">
                  <Button
                    :label="t('sprechen_subject.redo')"
                    icon="pi pi-refresh"
                    outlined
                    severity="secondary"
                    class="flex-1"
                    @click="redo"
                  />
                  <Button
                    :label="t('sprechen_subject.choose_another')"
                    icon="pi pi-list"
                    class="flex-1"
                    @click="goToList"
                  />
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </Teleport>
  </div>
</template>
