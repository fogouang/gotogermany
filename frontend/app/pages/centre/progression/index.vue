<!-- pages/centre/progression/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Barre d'outils ── -->
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <IconField class="w-full sm:max-w-sm">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="search"
          class="w-full"
          :placeholder="t('centre.progress.search_placeholder')"
        />
      </IconField>
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

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="n in 5"
        :key="n"
        class="h-16 animate-pulse rounded-card bg-card-2"
      />
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
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-chart-line" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{
          progress.length === 0
            ? t("centre.progress.empty_title")
            : t("centre.progress.no_results")
        }}
      </p>
      <p v-if="progress.length === 0" class="max-w-sm text-xs text-muted">
        {{ t("centre.progress.empty_text") }}
      </p>
    </div>

    <!-- ── Liste ── -->
    <template v-else>
      <ul
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li v-for="row in pagedRows" :key="row.student_id">
          <NuxtLink
            :to="localePath(`/centre/progression/${row.student_id}`)"
            class="flex flex-wrap items-center gap-x-5 gap-y-2 px-5 py-4 transition-colors hover:bg-card-2"
          >
            <!-- Élève -->
            <div class="flex min-w-48 flex-1 items-center gap-3">
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
              >
                {{ initials(row.student_name) }}
              </span>
              <div class="min-w-0">
                <p class="truncate font-medium text-ink">
                  {{ row.student_name }}
                </p>
                <p
                  v-if="authStore.isDirector"
                  class="truncate text-xs text-muted"
                >
                  {{ row.branch_name }}
                </p>
              </div>
            </div>

            <!-- Score moyen -->
            <div class="w-40">
              <div class="flex items-baseline justify-between text-xs">
                <span class="text-muted">{{
                  t("centre.progress.average")
                }}</span>
                <span
                  class="font-semibold"
                  :class="scoreTone(row.average_score)"
                >
                  {{
                    row.average_score !== null
                      ? `${Math.round(row.average_score)}/100`
                      : "-"
                  }}
                </span>
              </div>
              <div class="mt-1.5 h-1.5 overflow-hidden rounded-full bg-card-2">
                <div
                  class="h-full rounded-full"
                  :class="scoreBar(row.average_score)"
                  :style="{
                    width: `${Math.min(100, row.average_score ?? 0)}%`,
                  }"
                />
              </div>
            </div>

            <!-- Sessions + activité -->
            <div class="w-36 text-xs">
              <p class="font-medium text-ink">
                {{ t("centre.progress.sessions", row.total_sessions) }}
              </p>
              <p
                :class="
                  isInactive(row.last_session_at)
                    ? 'text-amber-600'
                    : 'text-muted'
                "
              >
                {{ lastActivity(row.last_session_at) }}
              </p>
            </div>

            <i class="pi pi-chevron-right hidden text-xs text-muted sm:block" />
          </NuxtLink>
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

definePageMeta({ layout: "centre", watermark: "Fortschritt" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();

const loading = ref(true);
const progress = ref<StudentProgressResponse[]>([]);
const errorMessage = ref<string | null>(null);

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

// « il y a 3 jours », « vor 3 Tagen », « 3 days ago » : formaté par le navigateur
function lastActivity(dateStr: string | null) {
  if (!dateStr) return t("centre.progress.never");
  const jours = Math.round((new Date(dateStr).getTime() - Date.now()) / DAY);
  return new Intl.RelativeTimeFormat(locale.value, { numeric: "auto" }).format(
    jours,
    "day",
  );
}

// ── Recherche + tri ──
const search = ref("");
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
  const list = progress.value.filter(
    (r) =>
      !q ||
      r.student_name.toLowerCase().includes(q) ||
      (r.branch_name ?? "").toLowerCase().includes(q),
  );
  return [...list].sort((a, b) => {
    if (sortKey.value === "name")
      return a.student_name.localeCompare(b.student_name);
    if (sortKey.value === "score_asc")
      // Les élèves en difficulté d'abord ; ceux sans score à la fin
      return (a.average_score ?? 101) - (b.average_score ?? 101);
    return temps(b.last_session_at) - temps(a.last_session_at);
  });
});

// ── Pagination ──
const rowsPerPage = ref(9);
const firstRecordIndex = ref(0);

const pagedRows = computed(() =>
  rows.value.slice(
    firstRecordIndex.value,
    firstRecordIndex.value + rowsPerPage.value,
  ),
);

function onPageChange(event: { first: number; rows: number }) {
  firstRecordIndex.value = event.first;
  rowsPerPage.value = event.rows;
}

// Nouvelle recherche ou nouveau tri : on revient à la première page
watch([search, sortKey], () => {
  firstRecordIndex.value = 0;
});

async function loadProgress() {
  loading.value = true;
  const result = await centerStaffStore.fetchStudentProgress();
  if (result.success) {
    progress.value = result.progress ?? [];
    errorMessage.value = null;
  } else {
    errorMessage.value = result.error || t("common.load_error");
  }
  loading.value = false;
}

onMounted(loadProgress);
</script>
