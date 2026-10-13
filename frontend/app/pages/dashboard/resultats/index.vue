<template>
  <div class="space-y-6 pb-10">
    <!-- En-tête -->
    <div>
      <h1 class="text-2xl sm:text-3xl font-bold text-ink">
        {{ t("my_results.title") }}
      </h1>
      <p class="mt-1 text-muted">{{ t("my_results.subtitle") }}</p>
    </div>

    <!-- Chargement -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
    </div>

    <!-- Vide -->
    <div
      v-else-if="sessions.length === 0"
      class="bg-card border border-line rounded-card px-6 py-16 text-center"
    >
      <span
        class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-card-2 mb-4"
      >
        <i class="pi pi-inbox text-2xl text-faint"></i>
      </span>
      <h3 class="text-lg font-semibold text-ink mb-1">
        {{ t("my_results.empty_title") }}
      </h3>
      <p class="text-sm text-muted mb-6">
        {{ t("my_results.empty_subtitle") }}
      </p>
      <Button
        :label="t('my_results.start_exam')"
        icon="pi pi-play"
        @click="navigateTo(localePath('/dashboard/examens'))"
      />
    </div>

    <template v-else>
      <!-- Statistiques -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div
          v-for="tile in statTiles"
          :key="tile.key"
          class="bg-card border border-line rounded-card p-4"
        >
          <p class="text-xs font-medium text-muted">{{ tile.label }}</p>
          <p :class="['mt-1 text-2xl font-bold tabular-nums', tile.color]">
            {{ tile.value }}
          </p>
        </div>
      </div>

      <!-- Filtres -->
      <div
        class="bg-card border border-line rounded-card p-3 flex flex-col sm:flex-row sm:items-center gap-3"
      >
        <Select
          v-model="filterStatus"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('my_results.all_statuses')"
          class="w-full sm:w-56"
        />
        <Select
          v-model="filterSort"
          :options="sortOptions"
          optionLabel="label"
          optionValue="value"
          class="w-full sm:w-56"
        />
        <Button
          v-if="filterStatus"
          :label="t('my_results.reset')"
          icon="pi pi-times"
          text
          severity="secondary"
          @click="filterStatus = ''"
        />
        <span class="sm:ml-auto text-xs text-muted">
          {{ filteredSessions.length }} / {{ sessions.length }}
        </span>
      </div>

      <!-- Liste -->
      <div class="space-y-3">
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="bg-card border border-line rounded-card p-4 sm:p-5 hover:border-primary/30 transition-colors"
        >
          <div class="flex flex-col sm:flex-row sm:items-center gap-4">
            <!-- Infos -->
            <div class="flex items-center gap-4 flex-1 min-w-0">
              <span
                :class="[
                  'w-11 h-11 rounded-leaf flex items-center justify-center shrink-0',
                  statusOf(session).chip,
                ]"
              >
                <i :class="['pi text-lg', statusOf(session).icon]"></i>
              </span>
              <div class="min-w-0">
                <p class="font-semibold text-ink truncate">
                  {{ session.exam_name }}
                  <span class="font-normal text-muted"
                    >·
                    {{
                      t("my_results.subject_n", { n: session.subject_number })
                    }}</span
                  >
                </p>
                <div class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1">
                  <Tag
                    :value="statusOf(session).label"
                    :severity="statusOf(session).severity"
                  />
                  <span class="text-xs text-muted">{{
                    formatDate(session.started_at)
                  }}</span>
                  <span
                    v-if="session.duration_seconds"
                    class="text-xs text-muted"
                  >
                    <i class="pi pi-clock text-[10px] mr-0.5"></i
                    >{{ formatDuration(session.duration_seconds) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Score + action -->
            <div class="flex items-center gap-5 sm:gap-6 shrink-0">
              <div class="w-28">
                <p
                  :class="[
                    'text-xl font-bold tabular-nums text-right',
                    statusOf(session).text,
                  ]"
                >
                  {{
                    hasScore(session) ? `${Math.round(session.score!)} %` : "-"
                  }}
                </p>
                <div
                  v-if="hasScore(session)"
                  class="mt-1.5 h-1.5 rounded-full bg-card-2 overflow-hidden"
                >
                  <div
                    :class="['h-full rounded-full', statusOf(session).bar]"
                    :style="{ width: `${Math.min(session.score!, 100)}%` }"
                  />
                </div>
              </div>

              <Button
                v-if="session.status === 'IN_PROGRESS'"
                icon="pi pi-play"
                :label="t('my_results.continue')"
                size="small"
                @click="openSession(session)"
              />
              <Button
                v-else
                icon="pi pi-eye"
                outlined
                rounded
                severity="secondary"
                :aria-label="t('my_results.view_detail')"
                v-tooltip.top="t('my_results.view_detail')"
                @click="openSession(session)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Charger plus -->
      <div v-if="hasMore" class="text-center pt-2">
        <Button
          :label="t('my_results.load_more')"
          icon="pi pi-chevron-down"
          outlined
          severity="secondary"
          :loading="loadingMore"
          @click="loadMore"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SessionListResponse } from "#shared/api";

definePageMeta({ layout: "dashboard" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const sessionStore = useSessionStore();

const LIMIT = 20;

const loading = ref(true);
const loadingMore = ref(false);
const sessions = ref<SessionListResponse[]>([]);
const filterStatus = ref("");
const filterSort = ref("desc");
const skip = ref(0);
const hasMore = ref(false);

// ── Filtres ───────────────────────────────────────────

const statusOptions = computed(() => [
  { label: t("my_results.all_statuses"), value: "" },
  { label: t("my_results.filter_passed"), value: "passed" },
  { label: t("my_results.filter_failed"), value: "failed" },
  { label: t("my_results.filter_pending"), value: "PENDING_REVIEW" },
  { label: t("my_results.filter_in_progress"), value: "IN_PROGRESS" },
]);

const sortOptions = computed(() => [
  { label: t("my_results.sort_desc"), value: "desc" },
  { label: t("my_results.sort_asc"), value: "asc" },
]);

const filteredSessions = computed(() => {
  let list = [...sessions.value];
  if (filterStatus.value === "passed")
    list = list.filter((s) => s.passed === true);
  else if (filterStatus.value === "failed")
    list = list.filter((s) => s.passed === false);
  else if (filterStatus.value)
    list = list.filter((s) => s.status === filterStatus.value);

  const time = (s: SessionListResponse) => new Date(s.started_at).getTime();
  list.sort((a, b) =>
    filterSort.value === "asc" ? time(a) - time(b) : time(b) - time(a),
  );
  return list;
});

// ── Statistiques ──────────────────────────────────────

const hasScore = (s: SessionListResponse) =>
  s.score !== null && s.score !== undefined;

const statTiles = computed(() => {
  const total = sessions.value.length;
  const passed = sessions.value.filter((s) => s.passed === true).length;
  const pending = sessions.value.filter(
    (s) => s.status === "PENDING_REVIEW",
  ).length;
  const scored = sessions.value.filter(hasScore);
  const avg = scored.length
    ? scored.reduce((sum, s) => sum + (s.score ?? 0), 0) / scored.length
    : null;

  return [
    {
      key: "total",
      label: t("my_results.stats.total"),
      value: String(total),
      color: "text-ink",
    },
    {
      key: "passed",
      label: t("my_results.stats.passed"),
      value: String(passed),
      color: "text-emerald-600",
    },
    {
      key: "avg",
      label: t("my_results.stats.avg_score"),
      value: avg !== null ? `${Math.round(avg)} %` : "-",
      color: "text-primary",
    },
    {
      key: "pending",
      label: t("my_results.stats.pending"),
      value: String(pending),
      color: "text-amber-600",
    },
  ];
});

// ── Statut d'une session ──────────────────────────────

function statusOf(s: SessionListResponse) {
  if (s.status === "IN_PROGRESS") {
    return {
      label: t("my_results.status.in_progress"),
      severity: "info",
      icon: "pi-play",
      chip: "bg-primary/10 text-primary",
      text: "text-muted",
      bar: "bg-primary",
    };
  }
  if (s.status === "PENDING_REVIEW") {
    return {
      label: t("my_results.status.pending_review"),
      severity: "warn",
      icon: "pi-clock",
      chip: "bg-amber-500/10 text-amber-600",
      text: "text-muted",
      bar: "bg-amber-500",
    };
  }
  if (s.passed === true) {
    return {
      label: t("my_results.status.passed"),
      severity: "success",
      icon: "pi-check-circle",
      chip: "bg-emerald-500/10 text-emerald-600",
      text: "text-emerald-600",
      bar: "bg-emerald-500",
    };
  }
  if (s.passed === false) {
    return {
      label: t("my_results.status.failed"),
      severity: "danger",
      icon: "pi-times-circle",
      chip: "bg-red-500/10 text-red-500",
      text: "text-red-500",
      bar: "bg-red-500",
    };
  }
  return {
    label: t("my_results.status.completed"),
    severity: "secondary",
    icon: "pi-circle",
    chip: "bg-card-2 text-muted",
    text: "text-ink",
    bar: "bg-primary",
  };
}

// ── Formatage ─────────────────────────────────────────

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

const formatDuration = (seconds: number) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return h > 0
    ? `${h} h ${String(m).padStart(2, "0")} min`
    : `${m} min ${String(s).padStart(2, "0")} s`;
};

// ── Navigation ────────────────────────────────────────

function openSession(s: SessionListResponse) {
  if (s.status === "IN_PROGRESS") {
    navigateTo(
      localePath({
        path: `/dashboard/examens/${s.exam_slug}/session`,
        query: {
          examId: s.exam_id,
          subjectId: s.subject_id,
          ...(s.module_slugs?.length
            ? { moduleSlugs: s.module_slugs.join(",") }
            : {}),
        },
      }),
    );
  } else {
    navigateTo(
      localePath({
        path: `/dashboard/examens/${s.exam_slug}/result`,
        query: { sessionId: s.id },
      }),
    );
  }
}

// ── Chargement ────────────────────────────────────────

async function loadSessions() {
  loading.value = true;
  const res = await sessionStore.getMySessions(0, LIMIT);
  if (res.success && res.data) {
    sessions.value = res.data;
    hasMore.value = res.data.length === LIMIT;
    skip.value = LIMIT;
  }
  loading.value = false;
}

async function loadMore() {
  loadingMore.value = true;
  const res = await sessionStore.getMySessions(skip.value, LIMIT);
  if (res.success && res.data) {
    sessions.value.push(...res.data);
    hasMore.value = res.data.length === LIMIT;
    skip.value += LIMIT;
  }
  loadingMore.value = false;
}

onMounted(loadSessions);
</script>
