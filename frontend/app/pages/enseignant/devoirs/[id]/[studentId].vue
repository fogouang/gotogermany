<!-- pages/enseignant/devoirs/[id]/[studentId].vue -->
<template>
  <div class="space-y-5">
    <NuxtLink
      :to="localePath(`/enseignant/devoirs/${assignmentId}`)"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("teacher.assignments.grading.back") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-4">
      <div class="h-32 animate-pulse rounded-card bg-card-2" />
      <div class="h-80 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage || !row"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage || t("teacher.assignments.detail.not_found") }}
    </div>

    <template v-else>
      <!-- ══ En-tête : élève, statut, note ══ -->
      <section
        class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6"
      >
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex min-w-0 flex-1 items-center gap-3">
            <span
              class="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
            >
              {{ initials(row.student_name) }}
            </span>
            <div class="min-w-0">
              <h1 class="truncate text-xl font-bold text-ink">
                {{ row.student_name }}
              </h1>
              <div class="mt-1 flex flex-wrap items-center gap-1.5">
                <span
                  class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="stateBadge.class"
                >
                  {{ stateBadge.label }}
                </span>
                <span
                  v-if="row.is_late"
                  class="rounded-full bg-red-500/10 px-2 py-0.5 text-[11px] font-semibold text-red-600"
                >
                  {{ t("teacher.assignments.detail.late") }}
                </span>
                <span v-if="row.submitted_at" class="text-xs text-muted">
                  {{
                    t("teacher.assignments.detail.submitted_on", {
                      date: formatDateTime(row.submitted_at),
                    })
                  }}
                </span>
              </div>
            </div>
          </div>

          <div class="text-right">
            <p class="text-3xl font-bold" :class="scoreTone(row.final_score)">
              {{
                row.final_score !== null
                  ? `${Math.round(row.final_score)}/100`
                  : "-"
              }}
            </p>
            <p class="text-xs text-muted">
              {{ t("teacher.assignments.grading.final_score") }}
            </p>
          </div>
        </div>

        <!-- Fichiers -->
        <div
          v-if="result"
          class="mt-5 flex flex-wrap gap-2 border-t border-line pt-5"
        >
          <Button
            v-if="items.length"
            :label="t('teacher.assignments.grading.download_pdf')"
            icon="pi pi-file-pdf"
            outlined
            size="small"
            :loading="downloading"
            @click="downloadPdf"
          />
          <Button
            :label="t('teacher.assignments.grading.upload_annotated')"
            icon="pi pi-upload"
            outlined
            size="small"
            :loading="uploading"
            @click="fileInput?.click()"
          />
          <Button
            v-if="row.has_annotated_file"
            :label="t('teacher.assignments.grading.download_annotated')"
            icon="pi pi-paperclip"
            text
            size="small"
            :loading="downloading"
            @click="downloadAnnotated"
          />
          <input
            ref="fileInput"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            class="hidden"
            @change="onFileChosen"
          />
        </div>
      </section>

      <Message v-if="actionError" severity="error" :closable="false">{{
        actionError
      }}</Message>

      <!-- ── Copie non rendue ── -->
      <div
        v-if="!result"
        class="rounded-card border border-line bg-card p-6 text-center text-sm text-muted shadow-soft"
      >
        {{ t("teacher.assignments.grading.not_submitted") }}
      </div>

      <template v-else>
        <!-- ══ Correction automatique ══ -->
        <section
          v-if="autoModules.length"
          class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6"
        >
          <h2 class="mb-3 font-semibold text-ink">
            {{ t("teacher.assignments.grading.auto_title") }}
          </h2>
          <ul class="divide-y divide-line">
            <li
              v-for="m in autoModules"
              :key="m.slug"
              class="flex flex-wrap items-center justify-between gap-2 py-2.5"
            >
              <span class="text-sm font-medium text-ink">{{ m.name }}</span>
              <span class="text-sm text-muted">
                {{
                  t("teacher.assignments.grading.auto_correct", {
                    correct: m.questions_correct,
                    total: m.questions_total,
                  })
                }}
                <template
                  v-if="
                    m.points_obtained !== null &&
                    m.points_obtained !== undefined
                  "
                >
                  ·
                  <span class="font-semibold text-ink"
                    >{{ formatPoints(m.points_obtained) }}/{{
                      m.max_score
                    }}</span
                  >
                </template>
              </span>
            </li>
          </ul>
        </section>

        <!-- ══ Productions à corriger ══ -->
        <section class="space-y-4">
          <h2 class="font-semibold text-ink">
            {{ t("teacher.assignments.grading.manual_title") }}
          </h2>

          <p
            v-if="items.length === 0"
            class="rounded-card border border-line bg-card p-6 text-center text-sm text-muted shadow-soft"
          >
            {{ t("teacher.assignments.grading.no_manual") }}
          </p>

          <article
            v-for="item in items"
            :key="item.answer.question_id"
            class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6"
          >
            <header
              class="mb-3 flex flex-wrap items-center justify-between gap-2"
            >
              <p class="font-semibold text-ink">
                {{ item.moduleName }} · Teil {{ item.teilNumber }}
              </p>
              <span
                class="rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-medium text-muted"
              >
                {{
                  t("teacher.assignments.grading.words", {
                    n: wordCount(item.answer),
                  })
                }}
              </span>
            </header>

            <div
              v-if="item.answer.instruction || item.answer.prompts?.length"
              class="mb-3 rounded-leaf border border-line px-4 py-3"
            >
              <p class="mb-1 text-xs font-semibold text-muted">
                {{ t("teacher.assignments.grading.task") }}
              </p>
              <p
                v-if="item.answer.instruction"
                class="whitespace-pre-wrap text-sm text-ink"
              >
                {{ item.answer.instruction }}
              </p>
              <ul
                v-if="item.answer.prompts?.length"
                class="mt-2 list-disc space-y-0.5 pl-5 text-sm text-ink"
              >
                <li v-for="(p, i) in item.answer.prompts" :key="i">{{ p }}</li>
              </ul>
            </div>

            <p class="mb-1 text-xs font-semibold text-muted">
              {{ t("teacher.assignments.grading.student_text") }}
            </p>
            <div
              class="whitespace-pre-wrap rounded-leaf bg-card-2 px-4 py-3 text-sm leading-relaxed text-ink"
              :class="{ 'italic text-muted': !answerText(item.answer) }"
            >
              {{
                answerText(item.answer) ||
                t("teacher.assignments.grading.empty_answer")
              }}
            </div>

            <div class="mt-4 grid gap-4 sm:grid-cols-[auto_1fr]">
              <div>
                <label class="mb-1 block text-xs font-semibold text-muted">
                  {{ t("teacher.assignments.grading.score") }}
                </label>
                <div class="flex items-center gap-2">
                  <InputNumber
                    v-model="scores[item.answer.question_id]"
                    :min="0"
                    :max="item.answer.points_possible"
                    :min-fraction-digits="0"
                    :max-fraction-digits="1"
                    :step="0.5"
                    placeholder="-"
                    input-class="w-20 text-center"
                  />
                  <span class="text-sm text-muted"
                    >/ {{ formatPoints(item.answer.points_possible) }}</span
                  >
                </div>
              </div>
              <div>
                <label class="mb-1 block text-xs font-semibold text-muted">
                  {{ t("teacher.assignments.grading.comment") }}
                </label>
                <Textarea
                  v-model="comments[item.answer.question_id]"
                  rows="2"
                  auto-resize
                  class="w-full"
                  :placeholder="
                    t('teacher.assignments.grading.comment_placeholder')
                  "
                />
              </div>
            </div>
          </article>
        </section>

        <!-- ══ Commentaire général et enregistrement ══ -->
        <section
          v-if="items.length"
          class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6"
        >
          <label class="mb-1 block text-xs font-semibold text-muted">
            {{ t("teacher.assignments.grading.general_comment") }}
          </label>
          <Textarea
            v-model="teacherComment"
            rows="3"
            auto-resize
            class="w-full"
            :placeholder="t('teacher.assignments.grading.general_placeholder')"
          />

          <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p
              class="text-sm"
              :class="remaining > 0 ? 'text-amber-600' : 'text-emerald-600'"
            >
              {{ t("teacher.assignments.grading.remaining", remaining) }}
            </p>
            <Button
              :label="t('teacher.assignments.grading.save')"
              icon="pi pi-check"
              :loading="saving"
              :disabled="filled.length === 0"
              @click="save"
            />
          </div>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import type {
  AnswerDetailResponse,
  SubmissionGradingResponse,
} from "#shared/api";

definePageMeta({ layout: "enseignant", watermark: "Hausaufgaben" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const toast = useToast();
const store = useAssignmentsStore();
const { download, downloading } = useApiDownload();

const assignmentId = route.params.id as string;
const studentId = route.params.studentId as string;

const loading = ref(true);
const saving = ref(false);
const uploading = ref(false);
const errorMessage = ref<string | null>(null);
const actionError = ref<string | null>(null);
const data = ref<SubmissionGradingResponse | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

const row = computed(() => data.value?.submission ?? null);
const result = computed(() => data.value?.result ?? null);

// ── Utilitaires ──
function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function formatDateTime(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatPoints(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function scoreTone(score: number | null) {
  if (score === null) return "text-muted";
  if (score >= 60) return "text-emerald-600";
  if (score >= 45) return "text-amber-600";
  return "text-red-600";
}

// Même logique que la liste des copies : état déduit des dates
type State = "not_started" | "in_progress" | "submitted" | "graded";

const state = computed<State>(() => {
  const r = row.value;
  if (r?.graded_at) return "graded";
  if (r?.submitted_at) return "submitted";
  if (r?.started_at) return "in_progress";
  return "not_started";
});

const stateBadge = computed(() => {
  const classes: Record<State, string> = {
    not_started: "bg-card-2 text-muted",
    in_progress: "bg-sky-500/10 text-sky-600",
    submitted: "bg-amber-500/15 text-amber-600",
    graded: "bg-emerald-500/10 text-emerald-600",
  };
  return {
    label: t(`teacher.assignments.detail.state.${state.value}`),
    class: classes[state.value],
  };
});

// ── Réponses ──
// Sprechen exclu des devoirs : seules les productions écrites sont notées par l'enseignant
const TEACHER_GRADED = new Set(["free_text"]);

interface GradeItem {
  answer: AnswerDetailResponse;
  moduleName: string;
  teilNumber: number;
}

const items = computed<GradeItem[]>(() => {
  const out: GradeItem[] = [];
  for (const m of result.value?.modules ?? []) {
    for (const teil of m.teile ?? []) {
      for (const answer of teil.answers ?? []) {
        if (TEACHER_GRADED.has(answer.question_type)) {
          out.push({
            answer,
            moduleName: m.name,
            teilNumber: teil.teil_number,
          });
        }
      }
    }
  }
  return out;
});

const autoModules = computed(() =>
  (result.value?.modules ?? []).filter((m) => {
    const answers = (m.teile ?? []).flatMap((teil) => teil.answers ?? []);
    return (
      answers.length > 0 &&
      !answers.some((a) => TEACHER_GRADED.has(a.question_type))
    );
  }),
);

function answerText(answer: AnswerDetailResponse): string {
  const text = (answer.user_answer as Record<string, unknown> | null)?.text;
  return typeof text === "string" ? text.trim() : "";
}

function wordCount(answer: AnswerDetailResponse): number {
  const text = answerText(answer);
  return text ? text.split(/\s+/).length : 0;
}

function teacherFeedback(
  answer: AnswerDetailResponse,
): { comment?: string | null } | null {
  const teacher = (answer.feedback as Record<string, unknown> | null)?.teacher;
  return teacher && typeof teacher === "object"
    ? (teacher as { comment?: string | null })
    : null;
}

// ── Formulaire ──
const scores = reactive<Record<string, number | null>>({});
const comments = reactive<Record<string, string>>({});
const teacherComment = ref("");

function hydrate(res: SubmissionGradingResponse) {
  data.value = res;
  teacherComment.value = res.teacher_comment ?? "";
  for (const { answer } of items.value) {
    const fromTeacher = teacherFeedback(answer);
    // Pré-rempli seulement si la note vient déjà de l'enseignant
    scores[answer.question_id] = fromTeacher
      ? (answer.score_obtained ?? null)
      : null;
    comments[answer.question_id] = fromTeacher?.comment ?? "";
  }
}

const filled = computed(() =>
  items.value.filter((i) => typeof scores[i.answer.question_id] === "number"),
);
const remaining = computed(() => items.value.length - filled.value.length);

async function save() {
  if (!filled.value.length) return;
  saving.value = true;
  actionError.value = null;
  const res = await store.grade(assignmentId, studentId, {
    answers: filled.value.map((i) => ({
      question_id: i.answer.question_id,
      score: scores[i.answer.question_id] as number,
      comment: comments[i.answer.question_id]?.trim() || null,
    })),
    teacher_comment: teacherComment.value.trim(),
  });
  saving.value = false;
  if (res.success) {
    hydrate(res.data);
    toast.add({
      severity: "success",
      summary: t(
        res.data.submission.graded_at
          ? "teacher.assignments.grading.saved_final"
          : "teacher.assignments.grading.saved_partial",
      ),
      life: 3000,
    });
  } else {
    actionError.value =
      res.error || t("teacher.assignments.grading.save_error");
  }
}

// ── Fichiers ──
const baseUrl = `/api/v1/assignments/${assignmentId}/submissions/${studentId}`;

async function downloadPdf() {
  actionError.value = null;
  const res = await download(`${baseUrl}/schreiben.pdf`, "schreiben.pdf");
  if (!res.success)
    actionError.value =
      res.error || t("teacher.assignments.detail.download_error");
}

async function downloadAnnotated() {
  actionError.value = null;
  const res = await download(`${baseUrl}/annotated`, "copie_annotee");
  if (!res.success)
    actionError.value =
      res.error || t("teacher.assignments.detail.download_error");
}

async function onFileChosen(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file) return;
  uploading.value = true;
  actionError.value = null;
  const res = await store.uploadAnnotated(assignmentId, studentId, file);
  uploading.value = false;
  if (res.success) {
    if (data.value) data.value.submission.has_annotated_file = true;
    toast.add({
      severity: "success",
      summary: t("teacher.assignments.grading.upload_done"),
      life: 3000,
    });
  } else {
    actionError.value =
      res.error || t("teacher.assignments.grading.upload_error");
  }
}

// ── Chargement ──
onMounted(async () => {
  const res = await store.fetchSubmission(assignmentId, studentId);
  if (res.success) hydrate(res.data);
  else errorMessage.value = res.error || t("common.load_error");
  loading.value = false;
});
</script>
