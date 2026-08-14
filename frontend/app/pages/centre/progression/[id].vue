<!-- pages/centre/progression/[id].vue -->
<template>
  <div class="max-w-5xl mx-auto">
    <Button
      icon="pi pi-arrow-left"
      label="Retour à la progression"
      text
      size="small"
      class="mb-4"
      @click="router.push('/centre/progression')"
    />

    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div v-else-if="detail" class="space-y-6">
      <!-- En-tête étudiant — dégradé + avatar initiales -->
      <div class="rounded-2xl border border-gray-200 bg-white overflow-hidden">
        <div
          class="flex flex-wrap items-center gap-4 px-6 py-6 text-white bg-linear-to-br from-emerald-600 to-emerald-700"
        >
          <div
            class="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/20 text-lg font-black shrink-0"
          >
            {{ initials }}
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-2xl font-black tracking-tight">
              {{ detail.student_name }}
            </h1>
            <p class="text-sm opacity-90">{{ detail.branch_name }}</p>
          </div>
          <span
            v-if="detail.score_history.length >= 2"
            class="ml-auto inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1.5 text-sm font-semibold shrink-0"
          >
            <i :class="trend >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'"></i>
            {{ trend >= 0 ? "+" : "" }}{{ trend.toFixed(0) }} pts depuis le
            début
          </span>
        </div>

        <div class="grid divide-gray-100 sm:grid-cols-3 sm:divide-x">
          <div
            v-for="s in headerStats"
            :key="s.label"
            class="flex items-center gap-3 px-6 py-5"
          >
            <span
              class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 shrink-0"
            >
              <i :class="['pi', s.icon]"></i>
            </span>
            <div>
              <p class="text-2xl font-black leading-none text-gray-900">
                {{ s.value }}
              </p>
              <p class="mt-1 text-xs text-gray-400">{{ s.label }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Courbe d'évolution -->
      <div class="rounded-2xl border border-gray-200 bg-white p-6">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-lg font-bold text-gray-900 tracking-tight">
            Évolution des scores
          </h2>
          <span class="text-xs text-gray-400">sur 100 points</span>
        </div>
        <Sparkline v-if="sparklinePoints.length" :points="sparklinePoints" />
        <p v-else class="mt-4 text-sm text-gray-500">
          Pas encore assez de données.
        </p>
      </div>

      <!-- Détail par examen — accordéon -->
      <div class="space-y-4">
        <h2 class="text-lg font-bold text-gray-900 tracking-tight">
          Détail par examen
        </h2>

        <div
          v-if="detail.exams.length === 0"
          class="rounded-2xl border border-dashed border-gray-200 bg-white p-10 text-center text-sm text-gray-500"
        >
          Aucune session complétée pour l'instant.
        </div>

        <article
          v-for="exam in examsWithCounts"
          :key="exam.exam_id"
          class="rounded-2xl border border-gray-200 bg-white overflow-hidden"
        >
          <button
            class="flex w-full items-center gap-4 p-5 text-left"
            @click="openExam = openExam === exam.exam_id ? null : exam.exam_id"
          >
            <div class="min-w-0 flex-1">
              <p class="truncate text-base font-bold text-gray-900">
                {{ exam.exam_name }}
              </p>
              <p class="mt-0.5 text-xs text-gray-400">
                {{ exam.total_sessions }} session(s)
                <span v-if="exam.last_session_at">
                  · dernière le {{ formatDate(exam.last_session_at) }}
                </span>
              </p>
              <div class="mt-2">
                <QuestionCounts :correct="exam.correct" :wrong="exam.wrong" />
              </div>
              <ScoreLine :score="exam.average_score" />
            </div>
            <span
              class="text-xl font-black shrink-0"
              :class="scoreTone(exam.average_score)"
            >
              {{ nf(exam.average_score, "/100") }}
            </span>
            <i
              class="pi pi-chevron-down shrink-0 text-gray-400 transition-transform"
              :class="{ 'rotate-180': openExam === exam.exam_id }"
            ></i>
          </button>

          <div
            v-if="openExam === exam.exam_id"
            class="grid gap-4 border-t border-gray-100 bg-gray-50 p-5 sm:grid-cols-2"
          >
            <div
              v-for="subject in exam.subjectsWithCounts"
              :key="subject.subject_id"
              class="rounded-xl border border-gray-200 bg-white p-4"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="truncate text-sm font-semibold text-gray-900">
                  {{ subject.subject_name }}
                </p>
                <span
                  class="text-sm font-bold"
                  :class="scoreTone(subject.average_score)"
                >
                  {{ nf(subject.average_score, "/100") }}
                </span>
              </div>
              <ScoreLine :score="subject.average_score" />
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <QuestionCounts
                  :correct="subject.correct"
                  :wrong="subject.wrong"
                />
                <span
                  v-if="subject.correct + subject.wrong > 0"
                  class="text-xs text-gray-400"
                >
                  {{ subject.correct + subject.wrong }} questions posées
                </span>
              </div>
            </div>
            <p
              v-if="exam.subjectsWithCounts.length === 0"
              class="text-sm text-gray-500"
            >
              Aucune matière évaluée.
            </p>
          </div>
        </article>
      </div>

      <!-- Commentaires des enseignants — lecture seule, directeur uniquement -->
      <div
        v-if="authStore.isDirector"
        class="rounded-2xl border border-gray-200 bg-white p-5 space-y-3"
      >
        <h3 class="text-sm font-semibold text-gray-700">
          Commentaires des enseignants ({{ comments.length }})
        </h3>

        <div v-if="loadingComments" class="flex justify-center py-6">
          <i class="pi pi-spin pi-spinner text-xl text-emerald-600"></i>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="c in comments"
            :key="c.id"
            class="bg-gray-50 rounded-lg px-4 py-3"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-semibold text-gray-700">{{
                c.teacher_name
              }}</span>
              <span class="text-xs text-gray-400">{{
                formatDate(c.created_at)
              }}</span>
            </div>
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ c.comment }}
            </p>
          </div>
          <p v-if="comments.length === 0" class="text-sm text-gray-400">
            Aucun commentaire d'enseignant pour l'instant.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import type {
  StudentDetailedProgressResponse,
  TeacherCommentResponse,
} from "#shared/api";

const route = useRoute();
const router = useRouter();
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
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function nf(v: number | null, suffix = "") {
  return v !== null && v !== undefined ? `${Math.round(v)}${suffix}` : "—";
}

function scoreTone(score: number | null) {
  if (score === null) return "text-gray-400";
  if (score >= 80) return "text-emerald-600";
  if (score >= 60) return "text-amber-600";
  return "text-red-600";
}

const initials = computed(() => {
  if (!detail.value) return "??";
  return detail.value.student_name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
});

const headerStats = computed(() => {
  if (!detail.value) return [];
  return [
    {
      icon: "pi-calendar",
      value: String(detail.value.total_sessions),
      label: "sessions passées",
    },
    {
      icon: "pi-th-large",
      value: nf(detail.value.overall_average_score, "/100"),
      label: "score moyen global",
    },
    {
      icon: "pi-sparkles",
      value: String(detail.value.ai_credits_remaining),
      label: "crédits IA restants",
    },
  ];
});

const trend = computed(() => {
  if (!detail.value || detail.value.score_history.length < 2) return 0;
  const h = detail.value.score_history;
  return h[h.length - 1]!.score - h[0]!.score;
});

const sparklinePoints = computed(() => {
  if (!detail.value) return [];
  return detail.value.score_history.map((p) => ({
    label: new Date(p.date).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
    }),
    score: p.score,
  }));
});

const examsWithCounts = computed(() => {
  if (!detail.value) return [];
  return detail.value.exams.map((exam) => {
    const subjectsWithCounts = exam.subjects.map((subject) => {
      const correct = subject.modules.reduce(
        (a, m) => a + (m.questions_correct ?? 0),
        0,
      );
      const wrong = subject.modules.reduce(
        (a, m) => a + (m.questions_incorrect ?? 0),
        0,
      );
      return { ...subject, correct, wrong };
    });
    return {
      ...exam,
      subjectsWithCounts,
      correct: subjectsWithCounts.reduce((a, s) => a + s.correct, 0),
      wrong: subjectsWithCounts.reduce((a, s) => a + s.wrong, 0),
    };
  });
});

async function loadDetail() {
  loading.value = true;
  const studentId = route.params.id as string;
  const result = await centerStaffStore.fetchStudentProgressDetail(studentId);
  if (result.success && result.detail) {
    detail.value = result.detail;
    openExam.value = result.detail.exams[0]?.exam_id ?? null;
  } else {
    errorMessage.value = result.error || "Erreur de chargement.";
  }
  loading.value = false;

  if (authStore.isDirector) {
    loadingComments.value = true;
    const commentsResult =
      await trainingSessionsStore.fetchCommentsForDirector(studentId);
    if (commentsResult.success) {
      comments.value = commentsResult.comments ?? [];
    }
    loadingComments.value = false;
  }
}

onMounted(loadDetail);
</script>
