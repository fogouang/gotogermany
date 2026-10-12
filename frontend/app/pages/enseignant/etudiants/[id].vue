<!-- pages/enseignant/etudiants/[id].vue -->
<template>
  <div class="space-y-5">
    <NuxtLink
      :to="localePath('/enseignant/etudiants')"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("teacher.student_detail.back") }}
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
      <!-- ══ En-tête élève ══ -->
      <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <div class="flex flex-wrap items-center gap-4 border-b border-line px-5 py-5 sm:px-6">
          <span
            class="flex size-14 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-lg font-bold text-primary"
          >
            {{ initials }}
          </span>
          <div class="min-w-0 flex-1">
            <h1 class="truncate text-xl font-bold text-ink">{{ detail.student_name }}</h1>
            <p v-if="detail.branch_name" class="flex items-center gap-1.5 text-sm text-muted">
              <i class="pi pi-map-marker text-xs" />
              {{ detail.branch_name }}
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span
              v-if="detail.score_history.length >= 2"
              class="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-semibold"
              :class="trend >= 0 ? 'bg-emerald-500/10 text-emerald-600' : 'bg-red-500/10 text-red-600'"
            >
              <i :class="trend >= 0 ? 'pi pi-arrow-up-right' : 'pi pi-arrow-down-right'" class="text-xs" />
              {{ t("centre.progress.trend", { points: `${trend >= 0 ? "+" : ""}${Math.round(trend)}` }) }}
            </span>
            <Button
              :label="t('teacher.classes.launch_live')"
              icon="pi pi-microphone"
              size="small"
              @click="goToLaunchLive"
            />
          </div>
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

      <div class="grid items-start gap-5 lg:grid-cols-3">
        <!-- ══ Colonne principale ══ -->
        <div class="space-y-5 lg:col-span-2">
          <!-- Évolution -->
          <section class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
            <div class="mb-4 flex items-center justify-between gap-3">
              <h2 class="font-semibold text-ink">{{ t("centre.progress.evolution") }}</h2>
              <span class="text-xs text-muted">{{ t("centre.progress.out_of_100") }}</span>
            </div>
            <ScoreEvolutionChart v-if="detail.score_history.length" :data="detail.score_history" />
            <p v-else class="text-sm text-muted">{{ t("centre.progress.not_enough_data") }}</p>
          </section>

          <!-- Détail par examen -->
          <section class="space-y-3">
            <h2 class="font-semibold text-ink">{{ t("centre.progress.by_exam") }}</h2>

            <div
              v-if="detail.exams.length === 0"
              class="rounded-card border border-dashed border-line bg-card p-10 text-center text-sm text-muted"
            >
              {{ t("centre.progress.no_completed") }}
            </div>

            <article
              v-for="exam in detail.exams"
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
                </div>
                <span class="shrink-0 text-xl font-bold" :class="scoreTone(exam.average_score)">
                  {{ nf(exam.average_score, "/100") }}
                </span>
                <i
                  class="pi pi-chevron-down shrink-0 text-muted transition-transform"
                  :class="{ 'rotate-180': openExam === exam.exam_id }"
                />
              </button>

              <div v-if="openExam === exam.exam_id" class="space-y-4 border-t border-line bg-card-2/40 p-5">
                <div
                  v-for="subject in exam.subjects"
                  :key="subject.subject_id"
                  class="rounded-leaf border border-line bg-card p-4"
                >
                  <div class="flex flex-wrap items-center justify-between gap-3">
                    <p class="min-w-0 truncate text-sm font-semibold text-ink">{{ subject.subject_name }}</p>
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-bold" :class="scoreTone(subject.average_score)">
                        {{ nf(subject.average_score, "/100") }}
                      </span>
                      <Button
                        v-if="subject.last_session_id"
                        :label="t('teacher.student_detail.see_detail')"
                        icon="pi pi-list-check"
                        text
                        size="small"
                        @click="openResultDialog(subject.last_session_id)"
                      />
                    </div>
                  </div>

                  <!-- Modules -->
                  <div class="mt-3 space-y-2">
                    <div
                      v-for="mod in subject.modules"
                      :key="mod.module_name"
                      class="flex flex-wrap items-center justify-between gap-2 rounded-leaf bg-card-2 px-3 py-2 text-sm"
                    >
                      <span class="font-medium text-ink">{{ mod.module_name }}</span>
                      <div class="flex items-center gap-3">
                        <span class="text-xs text-muted">
                          {{
                            t("teacher.student_detail.module_counts", {
                              correct: mod.questions_correct,
                              wrong: mod.questions_incorrect,
                              total: mod.questions_total,
                            })
                          }}
                        </span>
                        <span class="w-10 text-right font-semibold" :class="scoreTone(mod.average_score)">
                          {{ nf(mod.average_score) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <p v-if="exam.subjects.length === 0" class="text-sm text-muted">
                  {{ t("centre.progress.no_subject") }}
                </p>
              </div>
            </article>
          </section>
        </div>

        <!-- ══ Commentaires ══ -->
        <section class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft lg:sticky lg:top-0">
          <h2 class="font-semibold text-ink">
            {{ t("centre.progress.comments_title") }}
            <span class="font-normal text-muted">· {{ comments.length }}</span>
          </h2>

          <div class="space-y-2">
            <Textarea
              v-model="newComment"
              rows="3"
              autoResize
              class="w-full"
              :placeholder="t('teacher.student_detail.comment_placeholder')"
            />
            <div class="flex items-center justify-between gap-3">
              <p v-if="commentError" class="text-xs text-red-600">{{ commentError }}</p>
              <Button
                :label="t('teacher.student_detail.publish')"
                icon="pi pi-send"
                size="small"
                class="ml-auto"
                :loading="postingComment"
                :disabled="!newComment.trim()"
                @click="handlePostComment"
              />
            </div>
          </div>

          <div class="max-h-128 space-y-2 overflow-y-auto">
            <div v-for="c in comments" :key="c.id" class="rounded-leaf bg-card-2 px-4 py-3">
              <div class="mb-1 flex items-center justify-between gap-3">
                <span class="truncate text-xs font-semibold text-ink">{{ c.teacher_name }}</span>
                <span class="shrink-0 text-xs text-muted">{{ formatDate(c.created_at) }}</span>
              </div>
              <p class="whitespace-pre-wrap text-sm text-ink">{{ c.comment }}</p>
            </div>
            <p v-if="comments.length === 0" class="text-sm text-muted">
              {{ t("centre.progress.no_comments") }}
            </p>
          </div>
        </section>
      </div>
    </template>

    <!-- ══ Détail question par question ══ -->
    <Dialog
      v-model:visible="showResultDialog"
      :header="t('teacher.student_detail.result_title')"
      modal
      :style="{ width: '95vw', maxWidth: '48rem' }"
    >
      <div v-if="loadingResult" class="space-y-3">
        <div v-for="n in 3" :key="n" class="h-20 animate-pulse rounded-leaf bg-card-2" />
      </div>

      <div v-else-if="sessionResult" class="space-y-4">
        <div v-for="mod in sessionResult.modules" :key="mod.slug" class="rounded-leaf border border-line p-4">
          <div class="mb-3 flex items-center justify-between gap-3">
            <p class="text-sm font-semibold text-ink">{{ mod.name }}</p>
            <span class="text-xs text-muted">
              {{ t("teacher.student_detail.correct_count", { correct: mod.questions_correct, total: mod.questions_total }) }}
            </span>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <template v-for="teil in mod.teile" :key="teil.teil_number">
              <span
                v-for="ans in teil.answers"
                :key="ans.question_id"
                class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="
                  ans.is_correct === null
                    ? 'bg-card-2 text-muted'
                    : ans.is_correct
                      ? 'bg-emerald-500/10 text-emerald-600'
                      : 'bg-red-500/10 text-red-600'
                "
              >
                <i
                  class="text-[9px]"
                  :class="ans.is_correct === null ? 'pi pi-minus' : ans.is_correct ? 'pi pi-check' : 'pi pi-times'"
                />
                {{ t("teacher.student_detail.question", { n: ans.question_number }) }}
              </span>
            </template>
          </div>
        </div>
      </div>

      <p v-else class="text-sm text-muted">{{ t("common.load_error") }}</p>

      <template #footer>
        <Button :label="t('common.close')" text @click="showResultDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { StudentDetailedProgressResponse, TeacherCommentResponse } from "#shared/api";
import ScoreEvolutionChart from "~/components/centre/ScoreEvolutionChart.vue";

definePageMeta({ layout: "enseignant", watermark: "Fortschritt" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const teacherPortalStore = useTeacherPortalStore();

const studentId = route.params.id as string;

const loading = ref(true);
const detail = ref<StudentDetailedProgressResponse | null>(null);
const errorMessage = ref<string | null>(null);
const openExam = ref<string | null>(null);

const comments = ref<TeacherCommentResponse[]>([]);
const newComment = ref("");
const postingComment = ref(false);
const commentError = ref<string | null>(null);

const showResultDialog = ref(false);
const loadingResult = ref(false);
const sessionResult = ref<any>(null);

// ── Utilitaires ──
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
  if (score >= 60) return "text-emerald-600";
  if (score >= 45) return "text-amber-600";
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
    { icon: "pi pi-calendar", value: String(detail.value.total_sessions), label: t("centre.progress.stat_sessions") },
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

function goToLaunchLive() {
  navigateTo({ path: localePath("/enseignant/live/nouveau"), query: { student_id: studentId } });
}

// ── Chargement ──
async function loadDetail() {
  loading.value = true;
  const [result, commentsResult] = await Promise.all([
    teacherPortalStore.fetchStudentProgress(studentId),
    teacherPortalStore.fetchComments(studentId),
  ]);

  if (result.success && result.detail) {
    detail.value = result.detail;
    openExam.value = result.detail.exams[0]?.exam_id ?? null;
  } else {
    errorMessage.value = result.error || t("common.load_error");
  }

  if (commentsResult.success) comments.value = commentsResult.comments ?? [];
  loading.value = false;
}

// ── Commentaires ──
async function handlePostComment() {
  if (!newComment.value.trim()) return;
  postingComment.value = true;
  commentError.value = null;

  const result = await teacherPortalStore.addComment(studentId, { comment: newComment.value.trim() });

  postingComment.value = false;

  if (result.success && result.comment) {
    comments.value.unshift(result.comment);
    newComment.value = "";
  } else {
    commentError.value = result.error || t("teacher.student_detail.publish_error");
  }
}

// ── Détail d'une session ──
async function openResultDialog(sessionId: string) {
  showResultDialog.value = true;
  loadingResult.value = true;
  sessionResult.value = null;

  const result = await teacherPortalStore.fetchSessionResult(studentId, sessionId);
  if (result.success) sessionResult.value = result.result;
  loadingResult.value = false;
}

onMounted(loadDetail);
</script>