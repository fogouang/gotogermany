<!-- pages/enseignant/etudiants/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Barre d'outils ── -->
    <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
        <IconField class="w-full sm:max-w-xs">
          <InputIcon class="pi pi-search" />
          <InputText v-model="search" class="w-full" :placeholder="t('teacher.students.search')" />
        </IconField>
        <Select
          v-if="classOptions.length > 1"
          v-model="classFilter"
          :options="classOptions"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('teacher.students.all_classes')"
          showClear
          class="w-full sm:w-56"
        />
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="s in sorts"
          :key="s.key"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            sortKey === s.key
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30'
          "
          @click="sortKey = s.key"
        >
          {{ s.label }}
        </button>
      </div>
    </div>

    <p v-if="!loading && !errorMessage" class="text-sm text-muted">
      {{ t("teacher.students.count", { n: rows.length }, rows.length) }}
    </p>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div v-for="n in 5" :key="n" class="h-16 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="rows.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <i class="pi pi-users" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{ students.length === 0 ? t("teacher.students.empty") : t("teacher.students.no_results") }}
      </p>
    </div>

    <!-- ── Liste ── -->
    <template v-else>
      <ul class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <li v-for="row in pagedRows" :key="row.student_id" class="flex items-center gap-2 pr-3 sm:pr-4">
          <NuxtLink
            :to="localePath(`/enseignant/etudiants/${row.student_id}`)"
            class="flex min-w-0 flex-1 flex-wrap items-center gap-x-5 gap-y-2 px-4 py-3.5 transition-colors hover:bg-card-2 sm:px-5"
          >
            <!-- Élève -->
            <div class="flex min-w-48 flex-1 items-center gap-3">
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
              >
                {{ initials(row.student_name) }}
              </span>
              <div class="min-w-0">
                <p class="truncate font-medium text-ink">{{ row.student_name }}</p>
                <p class="truncate text-xs text-muted">{{ row.classLabels.join(" · ") }}</p>
              </div>
            </div>

            <!-- Score moyen -->
            <div class="w-36">
              <div class="flex items-baseline justify-between text-xs">
                <span class="text-muted">{{ t("centre.progress.average") }}</span>
                <span class="font-semibold" :class="scoreTone(row.average_score)">
                  {{ row.average_score !== null ? `${Math.round(row.average_score)}/100` : "-" }}
                </span>
              </div>
              <div class="mt-1.5 h-1.5 overflow-hidden rounded-full bg-card-2">
                <div
                  class="h-full rounded-full"
                  :class="scoreBar(row.average_score)"
                  :style="{ width: `${Math.min(100, row.average_score ?? 0)}%` }"
                />
              </div>
            </div>

            <!-- Sessions + activité -->
            <div class="w-32 text-xs">
              <p class="font-medium text-ink">{{ t("centre.progress.sessions", row.total_sessions) }}</p>
              <p :class="isInactive(row.last_session_at) ? 'text-amber-600' : 'text-muted'">
                {{ lastActivity(row.last_session_at) }}
              </p>
            </div>
          </NuxtLink>

          <Button
            icon="pi pi-microphone"
            rounded
            size="small"
            class="shrink-0"
            v-tooltip.left="t('teacher.classes.launch_live')"
            :aria-label="t('teacher.classes.launch_live')"
            @click="goToLaunchLive(row.student_id)"
          />
        </li>
      </ul>

      <Paginator
        v-if="rows.length > 10"
        :rows="rowsPerPage"
        :total-records="rows.length"
        :first="firstRecordIndex"
        :rows-per-page-options="[10, 20, 50]"
        class="rounded-card border border-line"
        @page="onPageChange"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { StudentProgressResponse } from "#shared/api";

definePageMeta({ layout: "enseignant", watermark: "Lernende" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const teacherPortalStore = useTeacherPortalStore();

const loading = ref(true);
const errorMessage = ref<string | null>(null);
const progressByStudent = ref<Map<string, StudentProgressResponse>>(new Map());

const DAY = 24 * 60 * 60 * 1000;
const SEUIL_INACTIF = 7; // jours sans session avant de signaler l'élève

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function scoreTone(score: number | null) {
  if (score === null) return "text-muted";
  if (score >= 60) return "text-emerald-600";
  if (score >= 45) return "text-amber-600";
  return "text-red-600";
}

function scoreBar(score: number | null) {
  if (score === null) return "bg-transparent";
  if (score >= 60) return "bg-emerald-500";
  if (score >= 45) return "bg-amber-500";
  return "bg-red-500";
}

function isInactive(dateStr: string | null) {
  if (!dateStr) return true;
  return Date.now() - new Date(dateStr).getTime() > SEUIL_INACTIF * DAY;
}

function lastActivity(dateStr: string | null) {
  if (!dateStr) return t("centre.progress.never");
  const jours = Math.round((new Date(dateStr).getTime() - Date.now()) / DAY);
  return new Intl.RelativeTimeFormat(locale.value, { numeric: "auto" }).format(jours, "day");
}

// Élèves actifs de toutes les classes de l'enseignant, sans doublon,
// avec leurs classes et leurs statistiques agrégées
const students = computed(() => {
  const map = new Map<
    string,
    {
      student_id: string;
      student_name: string;
      classIds: string[];
      classLabels: string[];
      average_score: number | null;
      total_sessions: number;
      last_session_at: string | null;
    }
  >();
  for (const session of teacherPortalStore.mySessions) {
    const classLabel = session.label ? `${session.level_name} · ${session.label}` : session.level_name;
    for (const s of session.students) {
      if (s.ended_at) continue;
      const existing = map.get(s.student_id);
      if (existing) {
        if (!existing.classIds.includes(session.id)) {
          existing.classIds.push(session.id);
          existing.classLabels.push(classLabel);
        }
        continue;
      }
      const progress = progressByStudent.value.get(s.student_id);
      map.set(s.student_id, {
        student_id: s.student_id,
        student_name: s.student_name,
        classIds: [session.id],
        classLabels: [classLabel],
        average_score: progress?.average_score ?? null,
        total_sessions: progress?.total_sessions ?? 0,
        last_session_at: progress?.last_session_at ?? null,
      });
    }
  }
  return [...map.values()];
});

// ── Filtres + tri ──
const search = ref("");
const classFilter = ref<string | null>(null);

const classOptions = computed(() =>
  teacherPortalStore.mySessions
    .filter((s) => s.students.some((x) => !x.ended_at))
    .map((s) => ({
      value: s.id,
      label: s.label ? `${s.level_name} · ${s.label}` : s.level_name,
    })),
);

type SortKey = "activity" | "score_asc" | "name";
const sortKey = ref<SortKey>("activity");

const sorts = computed(() => [
  { key: "activity" as const, label: t("centre.progress.sort_activity") },
  { key: "score_asc" as const, label: t("centre.progress.sort_struggling") },
  { key: "name" as const, label: t("centre.progress.sort_name") },
]);

const temps = (d: string | null) => (d ? new Date(d).getTime() : 0);

const rows = computed(() => {
  const q = search.value.trim().toLowerCase();
  const list = students.value
    .filter((r) => !classFilter.value || r.classIds.includes(classFilter.value))
    .filter((r) => !q || r.student_name.toLowerCase().includes(q));
  return [...list].sort((a, b) => {
    if (sortKey.value === "name") return a.student_name.localeCompare(b.student_name);
    if (sortKey.value === "score_asc")
      // Les élèves en difficulté d'abord ; ceux sans score à la fin
      return (a.average_score ?? 101) - (b.average_score ?? 101);
    return temps(b.last_session_at) - temps(a.last_session_at);
  });
});

// ── Pagination ──
const rowsPerPage = ref(8);
const firstRecordIndex = ref(0);

const pagedRows = computed(() =>
  rows.value.slice(firstRecordIndex.value, firstRecordIndex.value + rowsPerPage.value),
);

function onPageChange(event: { first: number; rows: number }) {
  firstRecordIndex.value = event.first;
  rowsPerPage.value = event.rows;
}

watch([search, classFilter, sortKey], () => {
  firstRecordIndex.value = 0;
});

function goToLaunchLive(studentId: string) {
  navigateTo({ path: localePath("/enseignant/live/nouveau"), query: { student_id: studentId } });
}

// ── Chargement ──
async function loadData() {
  loading.value = true;
  const [sessionsResult, progressResult] = await Promise.all([
    teacherPortalStore.fetchMySessions(),
    teacherPortalStore.fetchStudentsProgress(),
  ]);

  errorMessage.value = sessionsResult.success ? null : sessionsResult.error || t("common.load_error");

  if (progressResult.success) {
    progressByStudent.value = new Map((progressResult.progress ?? []).map((p) => [p.student_id, p]));
  }

  loading.value = false;
}

onMounted(loadData);
</script>