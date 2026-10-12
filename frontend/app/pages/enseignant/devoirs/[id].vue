<!-- pages/enseignant/devoirs/[id].vue -->
<template>
  <div class="space-y-5">
    <NuxtLink
      :to="localePath('/enseignant/devoirs')"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("teacher.assignments.form.back") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-4">
      <div class="h-40 animate-pulse rounded-card bg-card-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage || !assignment"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage || t("teacher.assignments.detail.not_found") }}
    </div>

    <template v-else>
      <!-- ══ En-tête ══ -->
      <section class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <h1 class="truncate text-xl font-bold text-ink">{{ assignment.title }}</h1>
              <span
                v-if="assignment.is_cancelled"
                class="rounded-full bg-card-2 px-2.5 py-1 text-xs font-semibold text-muted"
              >
                {{ t("teacher.assignments.cancelled") }}
              </span>
            </div>
            <p class="mt-1 text-sm text-muted">
              {{ assignment.exam_name }} · {{ assignment.cefr_code }} · {{ assignment.subject_name }}
            </p>
            <p class="mt-2 flex items-center gap-1.5 text-xs" :class="dueClass">
              <i class="pi pi-clock text-[11px]" />
              {{ dueLabel }}
            </p>
          </div>

          <div class="flex flex-wrap gap-2">
            <Button
              :label="t('teacher.assignments.detail.download_zip')"
              icon="pi pi-download"
              outlined
              size="small"
              :loading="downloading"
              :disabled="!hasSubmissions"
              @click="downloadZip"
            />
            <Button
              v-if="!assignment.is_cancelled"
              :label="t('teacher.assignments.detail.cancel')"
              icon="pi pi-ban"
              severity="danger"
              text
              size="small"
              @click="confirmCancel"
            />
          </div>
        </div>

        <!-- Cibles -->
        <div v-if="assignment.targets?.length" class="mt-4 flex flex-wrap gap-1.5">
          <span
            v-for="target in assignment.targets"
            :key="`${target.type}-${target.id}`"
            class="inline-flex items-center gap-1 rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-medium text-muted"
          >
            <i :class="target.type === 'class' ? 'pi pi-users' : 'pi pi-user'" class="text-[10px]" />
            {{ target.name }}
          </span>
        </div>

        <!-- Consignes -->
        <div v-if="assignment.instructions" class="mt-4 rounded-leaf bg-card-2 px-4 py-3">
          <p class="mb-1 text-xs font-semibold text-muted">{{ t("teacher.assignments.form.instructions") }}</p>
          <p class="whitespace-pre-wrap text-sm text-ink">{{ assignment.instructions }}</p>
        </div>

        <!-- Chiffres -->
        <div class="mt-5 grid grid-cols-2 gap-3 border-t border-line pt-5 sm:grid-cols-5">
          <div v-for="s in stats" :key="s.label">
            <p class="text-2xl font-bold" :class="s.tone ?? 'text-ink'">{{ s.value }}</p>
            <p class="text-xs text-muted">{{ s.label }}</p>
          </div>
        </div>
      </section>

      <Message v-if="actionError" severity="error" :closable="false">{{ actionError }}</Message>

      <!-- ══ Copies ══ -->
      <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <header class="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-4">
          <h2 class="font-semibold text-ink">{{ t("teacher.assignments.detail.submissions") }}</h2>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="f in filters"
              :key="f.key"
              type="button"
              class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors"
              :class="
                activeFilter === f.key
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-line bg-card text-muted hover:border-primary/30'
              "
              @click="activeFilter = f.key"
            >
              {{ f.label }}
              <span class="rounded-full bg-card-2 px-1.5 text-[10px] text-muted">{{ f.count }}</span>
            </button>
          </div>
        </header>

        <p v-if="visibleRows.length === 0" class="px-5 py-10 text-center text-sm text-muted">
          {{ t("teacher.assignments.detail.empty_filter") }}
        </p>

        <ul v-else class="divide-y divide-line">
          <li v-for="row in visibleRows" :key="row.student_id" class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-5">
            <!-- Élève -->
            <div class="flex min-w-48 flex-1 items-center gap-3">
              <span
                class="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
              >
                {{ initials(row.student_name) }}
              </span>
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-ink">{{ row.student_name }}</p>
                <p class="truncate text-xs text-muted">
                  <template v-if="row.submitted_at">
                    {{ t("teacher.assignments.detail.submitted_on", { date: formatDateTime(row.submitted_at) }) }}
                  </template>
                  <template v-else-if="row.started_at">
                    {{ t("teacher.assignments.detail.started_on", { date: formatDateTime(row.started_at) }) }}
                  </template>
                  <template v-else>-</template>
                </p>
              </div>
            </div>

            <!-- Statut -->
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="rounded-full px-2 py-0.5 text-[11px] font-semibold" :class="stateBadge(row).class">
                {{ stateBadge(row).label }}
              </span>
              <span
                v-if="row.is_late"
                class="rounded-full bg-red-500/10 px-2 py-0.5 text-[11px] font-semibold text-red-600"
              >
                {{ t("teacher.assignments.detail.late") }}
              </span>
              <i
                v-if="row.has_annotated_file"
                class="pi pi-paperclip text-xs text-muted"
                v-tooltip.top="t('teacher.assignments.detail.annotated')"
              />
            </div>

            <!-- Note -->
            <span class="w-16 text-right text-sm font-bold" :class="scoreTone(row.final_score)">
              {{ row.final_score !== null ? `${Math.round(row.final_score)}/100` : "-" }}
            </span>

            <!-- Action -->
            <div class="w-28 text-right">
              <Button
                v-if="stateOf(row) === 'submitted'"
                :label="t('teacher.assignments.detail.grade')"
                icon="pi pi-pencil"
                size="small"
                @click="goToGrading(row.student_id)"
              />
              <Button
                v-else-if="stateOf(row) === 'graded'"
                :label="t('teacher.assignments.detail.review')"
                icon="pi pi-eye"
                text
                size="small"
                @click="goToGrading(row.student_id)"
              />
            </div>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SubmissionRowResponse } from "#shared/api";

definePageMeta({ layout: "enseignant", watermark: "Hausaufgaben" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const confirm = useConfirm();
const toast = useToast();
const store = useAssignmentsStore();
const { download, downloading } = useApiDownload();

const assignmentId = route.params.id as string;

const loading = ref(true);
const errorMessage = ref<string | null>(null);
const actionError = ref<string | null>(null);

const assignment = computed(() => (store.current?.id === assignmentId ? store.current : null));
const submissions = computed(() => assignment.value?.submissions ?? []);

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

function scoreTone(score: number | null) {
  if (score === null) return "text-muted";
  if (score >= 60) return "text-emerald-600";
  if (score >= 45) return "text-amber-600";
  return "text-red-600";
}

// ── État d'une copie ──
// Déduit des dates (graded_at, submitted_at, started_at) plutôt que du champ
// `status`, dont les valeurs exactes ne sont pas typées côté client.
type State = "not_started" | "in_progress" | "submitted" | "graded";

function stateOf(row: SubmissionRowResponse): State {
  if (row.graded_at) return "graded";
  if (row.submitted_at) return "submitted";
  if (row.started_at) return "in_progress";
  return "not_started";
}

function stateBadge(row: SubmissionRowResponse) {
  const s = stateOf(row);
  const classes: Record<State, string> = {
    not_started: "bg-card-2 text-muted",
    in_progress: "bg-sky-500/10 text-sky-600",
    submitted: "bg-amber-500/15 text-amber-600",
    graded: "bg-emerald-500/10 text-emerald-600",
  };
  return { label: t(`teacher.assignments.detail.state.${s}`), class: classes[s] };
}

// ── Échéance ──
const isPastDue = computed(() => !!assignment.value?.due_at && new Date(assignment.value.due_at).getTime() < Date.now());

const dueLabel = computed(() => {
  const due = assignment.value?.due_at;
  if (!due) return t("teacher.assignments.no_due");
  return isPastDue.value
    ? t("teacher.assignments.due_passed", { date: formatDateTime(due) })
    : t("teacher.assignments.due_on", { date: formatDateTime(due) });
});

const dueClass = computed(() => {
  if (assignment.value?.is_cancelled || !assignment.value?.due_at) return "text-muted";
  return isPastDue.value ? "text-red-600" : "text-ink";
});

// ── Chiffres ──
const hasSubmissions = computed(() => submissions.value.some((r) => !!r.submitted_at));

const stats = computed(() => {
  const a = assignment.value;
  if (!a) return [];
  const rows = submissions.value;
  const scores = rows.map((r) => r.final_score).filter((v): v is number => v !== null);
  const average = scores.length ? scores.reduce((x, y) => x + y, 0) / scores.length : null;
  const late = rows.filter((r) => r.is_late).length;
  return [
    { label: t("teacher.assignments.detail.stat_expected"), value: String(a.expected_count ?? rows.length) },
    { label: t("teacher.assignments.submitted"), value: String(a.submitted_count ?? 0) },
    { label: t("teacher.assignments.graded"), value: String(a.graded_count ?? 0) },
    {
      label: t("teacher.assignments.detail.stat_late"),
      value: String(late),
      tone: late > 0 ? "text-red-600" : undefined,
    },
    {
      label: t("teacher.assignments.detail.stat_average"),
      value: average !== null ? `${Math.round(average)}/100` : "-",
      tone: scoreTone(average),
    },
  ];
});

// ── Filtres ──
type FilterKey = "all" | "to_grade" | "graded" | "missing";
const activeFilter = ref<FilterKey>("all");

function matches(row: SubmissionRowResponse, key: FilterKey) {
  const s = stateOf(row);
  if (key === "to_grade") return s === "submitted";
  if (key === "graded") return s === "graded";
  if (key === "missing") return s === "not_started" || s === "in_progress";
  return true;
}

const filters = computed(() =>
  (["all", "to_grade", "graded", "missing"] as const).map((key) => ({
    key,
    label: t(`teacher.assignments.detail.filter.${key}`),
    count: submissions.value.filter((r) => matches(r, key)).length,
  })),
);

// À corriger d'abord, puis corrigés, puis le reste ; ordre alphabétique dans chaque groupe
const ORDRE: Record<State, number> = { submitted: 0, graded: 1, in_progress: 2, not_started: 3 };

const visibleRows = computed(() =>
  submissions.value
    .filter((r) => matches(r, activeFilter.value))
    .sort((a, b) => ORDRE[stateOf(a)] - ORDRE[stateOf(b)] || a.student_name.localeCompare(b.student_name)),
);

// ── Actions ──
function goToGrading(studentId: string) {
  navigateTo(localePath(`/enseignant/devoirs/${assignmentId}/${studentId}`));
}

async function downloadZip() {
  actionError.value = null;
  const result = await download(`/api/v1/assignments/${assignmentId}/schreiben.zip`, "schreiben.zip");
  if (!result.success) actionError.value = result.error || t("teacher.assignments.detail.download_error");
}

function confirmCancel() {
  confirm.require({
    header: t("teacher.assignments.detail.cancel"),
    message: t("teacher.assignments.detail.cancel_confirm"),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: t("teacher.assignments.detail.cancel"),
    rejectLabel: t("common.cancel"),
    acceptClass: "p-button-danger",
    accept: async () => {
      actionError.value = null;
      const result = await store.cancel(assignmentId);
      if (result.success) {
        toast.add({ severity: "success", summary: t("teacher.assignments.detail.cancelled_done"), life: 3000 });
      } else {
        actionError.value = result.error || t("teacher.assignments.detail.cancel_error");
      }
    },
  });
}

// ── Chargement ──
onMounted(async () => {
  const result = await store.fetchDetail(assignmentId);
  if (!result.success) errorMessage.value = result.error || t("common.load_error");
  loading.value = false;
});
</script>