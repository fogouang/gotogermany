<!-- pages/centre/progression/[id].vue -->
<template>
  <div class=" space-y-5">
    <NuxtLink
      :to="localePath('/centre/progression')"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("centre.progress.back") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-4">
      <div class="h-40 animate-pulse rounded-card bg-card-2" />
      <div class="h-56 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <template v-else-if="detail">
      <!-- ── En-tête élève ── -->
      <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <div class="flex flex-wrap items-center gap-4 border-b border-line px-6 py-5">
          <span
            class="flex size-14 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-lg font-bold text-primary"
          >
            {{ initials }}
          </span>
          <div class="min-w-0 flex-1">
            <h1 class="truncate text-xl font-bold text-ink">{{ detail.student_name }}</h1>
            <p class="flex items-center gap-1.5 text-sm text-muted">
              <i class="pi pi-map-marker text-xs" />
              {{ detail.branch_name }}
            </p>
          </div>
          <span
            v-if="detail.score_history.length >= 2"
            class="inline-flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-semibold"
            :class="trend >= 0 ? 'bg-emerald-500/10 text-emerald-600' : 'bg-red-500/10 text-red-600'"
          >
            <i :class="trend >= 0 ? 'pi pi-arrow-up-right' : 'pi pi-arrow-down-right'" class="text-xs" />
            {{ t("centre.progress.trend", { points: `${trend >= 0 ? "+" : ""}${Math.round(trend)}` }) }}
          </span>
        </div>

        <div class="grid divide-y divide-line sm:grid-cols-3 sm:divide-x sm:divide-y-0">
          <div v-for="s in headerStats" :key="s.label" class="flex items-center gap-3 px-6 py-5">
            <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary">
              <i :class="s.icon" />
            </span>
            <div class="min-w-0">
              <p class="truncate text-xl font-bold leading-none" :class="s.tone ?? 'text-ink'">{{ s.value }}</p>
              <p class="mt-1 text-xs text-muted">{{ s.label }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Courbe d'évolution ── -->
      <section class="rounded-card border border-line bg-card p-6 shadow-soft">
        <div class="flex items-center justify-between gap-3">
          <h2 class="font-semibold text-ink">{{ t("centre.progress.evolution") }}</h2>
          <span class="text-xs text-muted">{{ t("centre.progress.out_of_100") }}</span>
        </div>
        <Sparkline v-if="sparklinePoints.length" :points="sparklinePoints" />
        <p v-else class="mt-4 text-sm text-muted">{{ t("centre.progress.not_enough_data") }}</p>
      </section>

      <!-- ── Détail par examen ── -->
      <section class="space-y-3">
        <h2 class="font-semibold text-ink">{{ t("centre.progress.by_exam") }}</h2>

        <div
          v-if="detail.exams.length === 0"
          class="rounded-card border border-dashed border-line bg-card p-10 text-center text-sm text-muted"
        >
          {{ t("centre.progress.no_completed") }}
        </div>

        <article
          v-for="exam in examsWithCounts"
          :key="exam.exam_id"
          class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
        >
          <button
            type="button"
            class="flex w-full items-center gap-4 p-5 text-left"
            :aria-expanded="openExam === exam.exam_id"
            @click="openExam = openExam === exam.exam_id ? null : exam.exam_id"
          >
            <div class="min-w-0 flex-1">
              <p class="truncate font-semibold text-ink">{{ exam.exam_name }}</p>
              <p class="mt-0.5 text-xs text-muted">
                {{ t("centre.progress.sessions", exam.total_sessions) }}
                <span v-if="exam.last_session_at">
                  · {{ t("centre.progress.last_on", { date: formatDate(exam.last_session_at) }) }}
                </span>
              </p>
              <div class="mt-2">
                <QuestionCounts :correct="exam.correct" :wrong="exam.wrong" />
              </div>
              <ScoreLine :score="exam.average_score" />
            </div>
            <span class="shrink-0 text-xl font-bold" :class="scoreTone(exam.average_score)">
              {{ nf(exam.average_score, "/100") }}
            </span>
            <i
              class="pi pi-chevron-down shrink-0 text-muted transition-transform"
              :class="{ 'rotate-180': openExam === exam.exam_id }"
            />
          </button>

          <div
            v-if="openExam === exam.exam_id"
            class="grid gap-3 border-t border-line bg-card-2/50 p-5 sm:grid-cols-2"
          >
            <div
              v-for="subject in exam.subjectsWithCounts"
              :key="subject.subject_id"
              class="rounded-leaf border border-line bg-card p-4"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="truncate text-sm font-semibold text-ink">{{ subject.subject_name }}</p>
                <span class="text-sm font-bold" :class="scoreTone(subject.average_score)">
                  {{ nf(subject.average_score, "/100") }}
                </span>
              </div>
              <ScoreLine :score="subject.average_score" />
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <QuestionCounts :correct="subject.correct" :wrong="subject.wrong" />
                <span v-if="subject.correct + subject.wrong > 0" class="text-xs text-muted">
                  {{ t("centre.progress.questions", subject.correct + subject.wrong) }}
                </span>
              </div>
            </div>
            <p v-if="exam.subjectsWithCounts.length === 0" class="text-sm text-muted">
              {{ t("centre.progress.no_subject") }}
            </p>
          </div>
        </article>
      </section>

      <!-- ── Commentaires des enseignants (directeur, lecture seule) ── -->
      <section
        v-if="authStore.isDirector"
        class="space-y-3 rounded-card border border-line bg-card p-6 shadow-soft"
      >
        <h2 class="font-semibold text-ink">
          {{ t("centre.progress.comments_title") }}
          <span class="font-normal text-muted">· {{ comments.length }}</span>
        </h2>

        <div v-if="loadingComments" class="h-16 animate-pulse rounded-leaf bg-card-2" />

        <template v-else>
          <div v-for="c in comments" :key="c.id" class="rounded-leaf bg-card-2 px-4 py-3">
            <div class="mb-1 flex items-center justify-between gap-3">
              <span class="text-xs font-semibold text-ink">{{ c.teacher_name }}</span>
              <span class="text-xs text-muted">{{ formatDate(c.created_at) }}</span>
            </div>
            <p class="whitespace-pre-wrap text-sm text-ink">{{ c.comment }}</p>
          </div>
          <p v-if="comments.length === 0" class="text-sm text-muted">
            {{ t("centre.progress.no_comments") }}
          </p>
        </template>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { StudentDetailedProgressResponse, TeacherCommentResponse } from "#shared/api";

definePageMeta({ layout: "centre", watermark: "Fortschritt" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const trainingSessionsStore = useTrainingSessionsStore();

const loading = ref(true);
const detail = ref<StudentDetailedProgressResponse | null>(null);
const errorMessage = ref<string | null>(null);

const comments = ref<TeacherCommentResponse[]>([]);
const loadingComments = ref(false);

const openExam = ref<string | null>(null);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function nf(v: number | null | undefined, suffix = "") {
  return v !== null && v !== undefined ? `${Math.round(v)}${suffix}` : "-";
}

function scoreTone(score: number | null | undefined) {
  if (score === null || score === undefined) return "text-muted";
  if (score >= 80) return "text-emerald-600";
  if (score >= 60) return "text-amber-600";
  return "text-red-600";
}

const initials = computed(() =>
  (detail.value?.student_name ?? "")
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase(),
);

// Dernière session : la plus récente parmi tous les examens
const lastSessionAt = computed(() => {
  const dates = (detail.value?.exams ?? [])
    .map((e) => e.last_session_at)
    .filter((d): d is string => !!d)
    .map((d) => new Date(d).getTime());
  return dates.length ? new Date(Math.max(...dates)).toISOString() : null;
});

const headerStats = computed(() => {
  if (!detail.value) return [];
  return [
    {
      icon: "pi pi-calendar",
      value: String(detail.value.total_sessions),
      label: t("centre.progress.stat_sessions"),
    },
    {
      icon: "pi pi-chart-bar",
      value: nf(detail.value.overall_average_score, "/100"),
      label: t("centre.progress.stat_average"),
      tone: scoreTone(detail.value.overall_average_score),
    },
    {
      icon: "pi pi-clock",
      value: lastSessionAt.value ? formatDate(lastSessionAt.value) : "-",
      label: t("centre.progress.stat_last"),
    },
  ];
});

const trend = computed(() => {
  const h = detail.value?.score_history ?? [];
  if (h.length < 2) return 0;
  return h[h.length - 1]!.score - h[0]!.score;
});

const sparklinePoints = computed(() =>
  (detail.value?.score_history ?? []).map((p) => ({
    label: new Date(p.date).toLocaleDateString(locale.value, { day: "2-digit", month: "short" }),
    score: p.score,
  })),
);

const examsWithCounts = computed(() =>
  (detail.value?.exams ?? []).map((exam) => {
    const subjectsWithCounts = exam.subjects.map((subject) => {
      const correct = subject.modules.reduce((a, m) => a + (m.questions_correct ?? 0), 0);
      const wrong = subject.modules.reduce((a, m) => a + (m.questions_incorrect ?? 0), 0);
      return { ...subject, correct, wrong };
    });
    return {
      ...exam,
      subjectsWithCounts,
      correct: subjectsWithCounts.reduce((a, s) => a + s.correct, 0),
      wrong: subjectsWithCounts.reduce((a, s) => a + s.wrong, 0),
    };
  }),
);

async function loadDetail() {
  loading.value = true;
  const studentId = route.params.id as string;
  const result = await centerStaffStore.fetchStudentProgressDetail(studentId);
  if (result.success && result.detail) {
    detail.value = result.detail;
    openExam.value = result.detail.exams[0]?.exam_id ?? null;
  } else {
    errorMessage.value = result.error || t("common.load_error");
  }
  loading.value = false;

  if (authStore.isDirector) {
    loadingComments.value = true;
    const commentsResult = await trainingSessionsStore.fetchCommentsForDirector(studentId);
    if (commentsResult.success) comments.value = commentsResult.comments ?? [];
    loadingComments.value = false;
  }
}

onMounted(loadDetail);
</script>