<script setup lang="ts">
/**
 * pages/dashboard/sprechen/testdaf/[subjectId].vue
 * ==================================================
 * Affichage du Sprechen TestDaF en mode enregistré. Tout le déroulé
 * (chronos, audio, enregistrement, API) est dans useTestDafSprechen.
 */
import { useTestDafSprechen } from "~/composables/useTestDafSprechen";

definePageMeta({ layout: "dashboard" });

// Forme du graphique (le client généré le type en objet libre)
interface Grafik {
  type: string;
  title?: string;
  unit?: string;
  x_label?: string;
  y_label?: string;
  labels: string[];
  series: { name: string; values: number[] }[];
  note?: string;
}

const { t } = useI18n();
const route = useRoute();
const localePath = useLocalePath();

const subjectId = route.params.subjectId as string;

const {
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
  start,
  finishSpeakingEarly,
  abandon,
} = useTestDafSprechen(subjectId);

const errorText = computed(() => {
  switch (errorCode.value) {
    case "mic":
      return t("testdaf_sprechen.mic_error");
    case "insufficient_credits":
      return t("sprechen_subject.insufficient_credits");
    case "finish":
      return t("testdaf_sprechen.finish_error");
    default:
      return t("testdaf_sprechen.start_error");
  }
});

const phaseLabel = computed(() => {
  switch (phase.value) {
    case "grafik":
      return t("testdaf_sprechen.phase_grafik");
    case "listen":
      return t("testdaf_sprechen.phase_listen");
    case "prep":
      return t("testdaf_sprechen.phase_prep");
    case "question":
      return (
        currentTask.value?.interlocutor ?? t("testdaf_sprechen.phase_question")
      );
    case "speaking":
      return t("testdaf_sprechen.phase_speaking");
  }
  return "";
});

const formatClock = (seconds: number) =>
  `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, "0")}`;

// ── Graphique ──
const grafik = computed(
  () => (currentTask.value?.grafik ?? null) as Grafik | null,
);
const grafikMax = computed(() =>
  grafik.value
    ? Math.max(1, ...grafik.value.series.flatMap((s) => s.values))
    : 1,
);
const seriesColors = [
  "bg-primary",
  "bg-sky-500",
  "bg-emerald-500",
  "bg-rose-500",
];

// ── Résultat ──
const scorePercent = computed(() =>
  result.value?.total_max_score
    ? Math.round(
        (result.value.total_score / result.value.total_max_score) * 100,
      )
    : 0,
);

// ── Navigation ──
const goToList = () => navigateTo(localePath("/dashboard/sprechen"));

function confirmLeave() {
  if (
    stage.value === "running" &&
    !window.confirm(t("sprechen_subject.confirm_leave"))
  )
    return;
  abandon();
  goToList();
}

const redo = () => window.location.reload();

onBeforeUnmount(() => abandon(true));

useHead({ title: t("testdaf_sprechen.page_title") });
</script>

<template>
  <div class="space-y-5 pb-10">
    <!-- Barre du haut -->
    <div class="flex items-center gap-3">
      <button
        type="button"
        class="inline-flex items-center gap-2 text-sm font-medium text-muted transition-colors hover:text-ink"
        @click="confirmLeave"
      >
        <i class="pi pi-arrow-left text-xs" />
        {{ t("testdaf_sprechen.exit") }}
      </button>
      <span
        class="ml-auto rounded-full bg-card-2 px-3 py-1 text-xs font-semibold text-muted"
      >
        TestDaF · Sprechen
      </span>
      <span
        v-if="stage === 'running' && tasks.length"
        class="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary"
      >
        {{
          t("testdaf_sprechen.task_of", {
            n: taskIndex + 1,
            total: tasks.length,
          })
        }}
      </span>
    </div>

    <!-- ═══════════ Introduction ═══════════ -->
    <div
      v-if="stage === 'intro' || stage === 'starting'"
      class="mx-auto max-w-xl rounded-card border border-line bg-card p-7 shadow-soft"
    >
      <span
        class="mb-4 grid size-12 place-items-center rounded-leaf bg-primary/10 text-primary"
      >
        <i class="pi pi-microphone text-xl" />
      </span>
      <h1 class="text-xl font-bold text-ink">
        {{ t("testdaf_sprechen.intro_title") }}
      </h1>
      <p class="mt-2 text-sm leading-relaxed text-muted">
        {{ t("testdaf_sprechen.intro_text") }}
      </p>
      <ul class="mt-4 space-y-2 text-sm text-ink">
        <li class="flex gap-2">
          <i class="pi pi-clock mt-0.5 text-primary" />{{
            t("testdaf_sprechen.intro_point_timers")
          }}
        </li>
        <li class="flex gap-2">
          <i class="pi pi-volume-up mt-0.5 text-primary" />{{
            t("testdaf_sprechen.intro_point_audio")
          }}
        </li>
        <li class="flex gap-2">
          <i class="pi pi-forward mt-0.5 text-primary" />{{
            t("testdaf_sprechen.intro_point_chain")
          }}
        </li>
      </ul>
      <Button
        class="mt-6 w-full"
        :label="t('testdaf_sprechen.start')"
        icon="pi pi-play"
        :loading="stage === 'starting'"
        @click="start"
      />
    </div>

    <!-- ═══════════ Erreur ═══════════ -->
    <div
      v-else-if="stage === 'error'"
      class="mx-auto max-w-lg rounded-card border border-line bg-card p-7 text-center"
    >
      <i class="pi pi-exclamation-circle mb-3 block text-3xl text-red-500" />
      <p class="mb-5 font-medium text-ink">{{ errorText }}</p>
      <Button
        :label="t('testdaf_sprechen.exit')"
        outlined
        severity="secondary"
        @click="goToList"
      />
    </div>

    <!-- ═══════════ Épreuve ═══════════ -->
    <div
      v-else-if="stage === 'running' && currentTask"
      class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]"
    >
      <!-- Tâche -->
      <section class="space-y-4 rounded-card border border-line bg-card p-5">
        <div class="flex items-center gap-3">
          <span
            class="grid size-9 shrink-0 place-items-center rounded-leaf bg-primary/10 text-sm font-bold text-primary"
          >
            {{ currentTask.teil_number }}
          </span>
          <h2 class="font-semibold text-ink">{{ currentTask.name }}</h2>
        </div>

        <div
          v-if="currentTask.situation"
          class="rounded-leaf border border-primary/20 bg-primary/10 px-4 py-3"
        >
          <p
            class="mb-1 text-[11px] font-semibold uppercase tracking-wide text-primary"
          >
            {{ t("testdaf_sprechen.situation_label") }}
          </p>
          <p class="text-sm leading-relaxed text-ink">
            {{ currentTask.situation }}
          </p>
        </div>

        <div v-if="currentTask.instructions">
          <p
            class="mb-1 text-[11px] font-semibold uppercase tracking-wide text-faint"
          >
            {{ t("testdaf_sprechen.task_label") }}
          </p>
          <p class="text-sm font-medium leading-relaxed text-ink">
            {{ currentTask.instructions }}
          </p>
        </div>

        <!-- Texte (masqué après le temps de lecture si prévu) -->
        <div
          v-if="currentTask.stimulus_text"
          class="overflow-hidden rounded-card border border-line bg-card-2"
        >
          <div class="border-b border-line px-4 py-2">
            <p
              class="text-[11px] font-semibold uppercase tracking-wide text-faint"
            >
              {{ t("testdaf_sprechen.text_label") }}
            </p>
          </div>
          <p
            v-if="textVisible"
            class="max-h-96 overflow-y-auto whitespace-pre-line px-4 py-3 text-sm leading-relaxed text-ink"
          >
            {{ currentTask.stimulus_text }}
          </p>
          <p v-else class="px-4 py-6 text-center text-sm italic text-muted">
            {{ t("testdaf_sprechen.text_hidden") }}
          </p>
        </div>

        <!-- Graphique -->
        <div
          v-if="grafik"
          class="rounded-card border border-line bg-card-2 p-4"
        >
          <p
            class="mb-1 text-[11px] font-semibold uppercase tracking-wide text-faint"
          >
            {{ t("testdaf_sprechen.chart_label") }}
          </p>
          <p class="mb-3 text-sm font-semibold text-ink">{{ grafik.title }}</p>
          <div class="flex h-48 items-end gap-6 border-b border-line px-2">
            <div
              v-for="(label, li) in grafik.labels"
              :key="label"
              class="flex h-full flex-1 items-end justify-center gap-1.5"
            >
              <div
                v-for="(serie, si) in grafik.series"
                :key="serie.name"
                class="flex h-full w-7 flex-col items-center justify-end"
              >
                <span
                  class="mb-1 text-[10px] font-semibold tabular-nums text-ink"
                >
                  {{ serie.values[li] }}{{ grafik.unit }}
                </span>
                <div
                  class="w-full rounded-t"
                  :class="seriesColors[si % seriesColors.length]"
                  :style="{
                    height: `${((serie.values[li] ?? 0) / grafikMax) * 80}%`,
                  }"
                />
              </div>
            </div>
          </div>
          <div class="mt-2 flex gap-6 px-2">
            <span
              v-for="label in grafik.labels"
              :key="label"
              class="flex-1 text-center text-xs text-muted"
            >
              {{ label }}
            </span>
          </div>
          <div class="mt-3 flex flex-wrap gap-4 text-xs text-muted">
            <span
              v-for="(serie, si) in grafik.series"
              :key="serie.name"
              class="inline-flex items-center gap-1.5"
            >
              <span
                class="size-2.5 rounded-sm"
                :class="seriesColors[si % seriesColors.length]"
              />
              {{ serie.name }}
            </span>
            <span v-if="grafik.x_label" class="ml-auto">{{
              grafik.x_label
            }}</span>
          </div>
        </div>

        <!-- Plan de présentation (diapositive) -->
        <div
          v-if="currentTask.gliederung?.length"
          class="rounded-card border border-line bg-card-2 p-5"
        >
          <p
            class="mb-1 text-[11px] font-semibold uppercase tracking-wide text-faint"
          >
            {{ t("testdaf_sprechen.slide_label") }}
          </p>
          <p class="mb-3 text-base font-bold text-ink">
            {{ currentTask.gliederung_title }}
          </p>
          <ul class="space-y-2">
            <li
              v-for="point in currentTask.gliederung"
              :key="point"
              class="flex gap-2 text-sm text-ink"
            >
              <span class="mt-2 size-1.5 shrink-0 rounded-full bg-primary" />{{
                point
              }}
            </li>
          </ul>
        </div>
      </section>

      <!-- Phase en cours -->
      <aside
        class="h-fit space-y-4 rounded-card border border-line bg-card p-5 lg:sticky lg:top-4"
      >
        <div class="flex items-center gap-2">
          <span
            class="size-2.5 rounded-full"
            :class="
              phase === 'speaking' ? 'animate-pulse bg-red-500' : 'bg-primary'
            "
          />
          <p class="text-sm font-semibold text-ink">{{ phaseLabel }}</p>
        </div>

        <p
          v-if="showCountdown"
          class="text-4xl font-bold tabular-nums text-ink"
        >
          {{ formatClock(secondsLeft) }}
        </p>
        <p v-else class="flex items-center gap-2 text-sm text-muted">
          <i class="pi pi-volume-up text-primary" />{{
            t("testdaf_sprechen.listening_hint")
          }}
        </p>

        <div
          v-if="showCountdown"
          class="h-1.5 overflow-hidden rounded-full bg-card-2"
        >
          <div
            class="h-full rounded-full transition-all duration-200"
            :class="phase === 'speaking' ? 'bg-red-500' : 'bg-primary'"
            :style="{ width: `${progressPercent}%` }"
          />
        </div>

        <p v-if="phase === 'prep'" class="text-xs leading-relaxed text-muted">
          {{ t("testdaf_sprechen.prep_hint") }}
        </p>

        <template v-if="phase === 'speaking'">
          <p class="text-xs leading-relaxed text-muted">
            {{ t("testdaf_sprechen.speaking_hint") }}
          </p>
          <Button
            class="w-full"
            :label="t('testdaf_sprechen.done_button')"
            icon="pi pi-check"
            severity="secondary"
            outlined
            @click="finishSpeakingEarly"
          />
        </template>

        <p
          v-if="uploadWarning"
          class="rounded-leaf bg-amber-500/10 px-3 py-2 text-xs text-amber-700"
        >
          {{ t("testdaf_sprechen.upload_warning") }}
        </p>
      </aside>
    </div>

    <!-- ═══════════ Correction en cours ═══════════ -->
    <div
      v-else-if="stage === 'grading'"
      class="mx-auto max-w-sm rounded-card bg-card p-7 text-center shadow-soft"
    >
      <span
        class="mx-auto mb-4 grid size-14 place-items-center rounded-full bg-primary/10"
      >
        <i class="pi pi-spin pi-spinner text-2xl text-primary" />
      </span>
      <h3 class="mb-1 text-base font-semibold text-ink">
        {{ t("testdaf_sprechen.grading_title") }}
      </h3>
      <p class="text-sm text-muted">
        {{ t("testdaf_sprechen.grading_subtitle") }}
      </p>
    </div>

    <!-- ═══════════ Résultat ═══════════ -->
    <div
      v-else-if="stage === 'result' && result"
      class="mx-auto max-w-2xl space-y-5"
    >
      <div
        class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <div
          :class="['h-1.5', result.passed ? 'bg-emerald-500' : 'bg-amber-500']"
        />
        <div class="flex items-center justify-between gap-4 px-6 py-5">
          <div>
            <p
              class="mb-1 text-xs font-semibold uppercase tracking-wider text-muted"
            >
              TestDaF · {{ result.level }} · Sprechen
            </p>
            <h1 class="text-2xl font-bold text-ink">
              {{ result.level_estimate }}
            </h1>
            <p class="mt-1 text-sm tabular-nums text-muted">
              {{ result.total_score }} / {{ result.total_max_score }}
              {{ t("sprechen_subject.points") }} ·
              {{ t("testdaf_sprechen.level_label") }}
            </p>
          </div>
          <p
            :class="[
              'shrink-0 text-3xl font-extrabold tabular-nums',
              result.passed ? 'text-emerald-600' : 'text-amber-600',
            ]"
          >
            {{ scorePercent }}%
          </p>
        </div>
      </div>

      <div class="overflow-hidden rounded-card border border-line bg-card">
        <div class="divide-y divide-line">
          <div
            v-for="teil in result.teile"
            :key="teil.teil_number"
            class="space-y-3 px-5 py-4"
          >
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-semibold text-ink">
                {{
                  t("testdaf_sprechen.task_short", { n: teil.teil_number })
                }}
                · {{ teil.teil_name }}
              </span>
              <span
                class="shrink-0 text-xs font-semibold tabular-nums text-muted"
              >
                {{ teil.teil_score }} / {{ teil.teil_max_score }}
              </span>
            </div>
            <template v-for="c in teil.criteria" :key="c.criterion_name">
              <div
                v-if="c.issue"
                class="flex gap-2 rounded-leaf bg-amber-500/10 px-3 py-2"
              >
                <i
                  class="pi pi-exclamation-circle mt-0.5 shrink-0 text-xs text-amber-600"
                />
                <p class="text-xs leading-relaxed text-ink">
                  <span class="font-semibold"
                    >{{ t("sprechen_subject.criterion_issue_label") }} :</span
                  >
                  {{ c.issue }}
                </p>
              </div>
              <div
                v-if="c.model_phrase"
                class="flex gap-2 rounded-leaf bg-primary/10 px-3 py-2"
              >
                <i class="pi pi-comment mt-0.5 shrink-0 text-xs text-primary" />
                <p class="text-xs italic leading-relaxed text-ink">
                  <span class="font-semibold not-italic"
                    >{{
                      t("sprechen_subject.criterion_model_phrase_label")
                    }}
                    :</span
                  >
                  „{{ c.model_phrase }}“
                </p>
              </div>
              <div v-if="c.tip" class="flex gap-2 px-1">
                <i class="pi pi-lightbulb mt-0.5 shrink-0 text-xs text-faint" />
                <p class="text-xs leading-relaxed text-muted">
                  <span class="font-semibold"
                    >{{ t("sprechen_subject.criterion_tip_label") }} :</span
                  >
                  {{ c.tip }}
                </p>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div v-if="result.strengths.length">
          <p
            class="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-emerald-600"
          >
            <i class="pi pi-check-circle" />{{
              t("sprechen_subject.strengths")
            }}
          </p>
          <ul class="space-y-1.5">
            <li
              v-for="(s, i) in result.strengths"
              :key="i"
              class="rounded-leaf bg-emerald-500/10 px-3 py-2 text-sm text-ink"
            >
              {{ s }}
            </li>
          </ul>
        </div>
        <div v-if="result.improvement_areas.length">
          <p
            class="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-amber-600"
          >
            <i class="pi pi-exclamation-circle" />{{
              t("sprechen_subject.to_improve")
            }}
          </p>
          <ul class="space-y-1.5">
            <li
              v-for="(a, i) in result.improvement_areas"
              :key="i"
              class="rounded-leaf bg-amber-500/10 px-3 py-2 text-sm text-ink"
            >
              {{ a }}
            </li>
          </ul>
        </div>
      </div>

      <div class="flex flex-col gap-3 sm:flex-row">
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
