<!-- pages/centre/sessions/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Statuts + création ── -->
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <div class="flex flex-wrap gap-2">
        <button
          v-for="f in statusFilters"
          :key="f.key"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            activeFilter === f.key
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30'
          "
          @click="activeFilter = f.key"
        >
          {{ f.label }} · {{ f.count }}
        </button>
      </div>
      <Button
        :label="t('centre.classes.new')"
        icon="pi pi-plus"
        class="w-full sm:w-auto"
        @click="openCreateDialog"
      />
    </div>

    <!-- ── Filtres ── -->
    <div class="flex flex-col gap-2 lg:flex-row lg:items-center">
      <IconField class="w-full lg:max-w-xs">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="search"
          class="w-full"
          :placeholder="t('centre.classes.search')"
        />
      </IconField>
      <Select
        v-model="levelFilter"
        :options="levelOptions"
        :placeholder="t('centre.classes.filter_level')"
        showClear
        class="w-full lg:w-40"
      />
      <Select
        v-model="teacherFilter"
        :options="teacherOptions"
        optionLabel="label"
        optionValue="value"
        :placeholder="t('centre.classes.filter_teacher')"
        showClear
        filter
        class="w-full lg:w-56"
      />
      <Select
        v-if="authStore.isDirector && branches.length > 1"
        v-model="branchFilter"
        :options="branches"
        optionLabel="name"
        optionValue="id"
        :placeholder="t('centre.classes.filter_branch')"
        showClear
        class="w-full lg:w-48"
      />
      <Button
        v-if="hasExtraFilters"
        :label="t('centre.classes.reset_filters')"
        icon="pi pi-filter-slash"
        text
        size="small"
        @click="resetFilters"
      />
    </div>

    <!-- ── Chargement ── -->
    <div
      v-if="loading"
      class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
    >
      <div
        v-for="n in 3"
        :key="n"
        class="h-48 animate-pulse rounded-card bg-card-2"
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
      v-else-if="filteredSessions.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-calendar" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{ t("centre.classes.empty_title") }}
      </p>
      <p class="max-w-md text-xs text-muted">
        {{ t("centre.classes.empty_text") }}
      </p>
    </div>

    <!-- ── Classes groupées par mois ── -->
    <template v-else>
      <section v-for="group in groupedPage" :key="group.key" class="space-y-3">
        <h3 class="flex items-baseline gap-2 text-sm font-semibold text-ink">
          {{ group.label }}
          <span class="text-xs font-normal text-muted">
            ·
            {{
              t("centre.classes.month_count", { n: group.total }, group.total)
            }}
          </span>
        </h3>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          <NuxtLink
            v-for="session in group.items"
            :key="session.id"
            :to="localePath(`/centre/sessions/${session.id}`)"
            class="group relative isolate flex flex-col overflow-hidden rounded-card border border-line bg-card p-5 shadow-soft transition-colors hover:border-primary/40"
            :class="{ 'opacity-70': statusOf(session) === 'finished' }"
          >
            <CardWatermark
              :text="cefrOf(session.level_name)"
              icon="pi pi-users"
              :tone="watermarkTone(session)"
              placement="fill"
              glow="full"
            />

            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate font-semibold text-ink">
                  {{ session.label || session.level_name }}
                </p>
                <p v-if="session.label" class="truncate text-xs text-muted">
                  {{ session.level_name }}
                </p>
              </div>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="statusBadge(session).class"
              >
                {{ statusBadge(session).label }}
              </span>
            </div>

            <p class="mt-3 flex items-center gap-1.5 text-xs text-muted">
              <i class="pi pi-calendar text-[11px]" />
              {{ period(session) }}
            </p>
            <p
              v-if="authStore.isDirector && session.branch_name"
              class="mt-1 flex items-center gap-1.5 text-xs text-muted"
            >
              <i class="pi pi-map-marker text-[11px]" />
              {{ session.branch_name }}
            </p>

            <div class="mt-4 grid grid-cols-2 gap-3 border-t border-line pt-4">
              <div>
                <p class="text-xl font-bold text-ink">
                  {{ activeStudentCount(session) }}
                </p>
                <p class="text-[11px] text-muted">
                  {{
                    t(
                      "centre.classes.active_label",
                      { total: session.students.length },
                      activeStudentCount(session),
                    )
                  }}
                </p>
              </div>
              <div>
                <p
                  class="text-xl font-bold"
                  :class="
                    session.teachers.length ? 'text-ink' : 'text-amber-600'
                  "
                >
                  {{ session.teachers.length }}
                </p>
                <p class="text-[11px] text-muted">
                  {{
                    t("centre.classes.teachers_label", session.teachers.length)
                  }}
                </p>
              </div>
            </div>

            <p
              class="mt-4 flex items-center justify-end gap-1.5 text-xs font-medium text-primary opacity-80 transition-opacity group-hover:opacity-100"
            >
              {{ t("centre.classes.open") }}
              <i
                class="pi pi-arrow-right text-[10px] transition-transform group-hover:translate-x-0.5"
              />
            </p>
          </NuxtLink>
        </div>
      </section>

      <Paginator
        v-if="filteredSessions.length > 12"
        :rows="rowsPerPage"
        :total-records="filteredSessions.length"
        :first="firstRecordIndex"
        :rows-per-page-options="[12, 24, 48]"
        class="rounded-card border border-line"
        @page="onPageChange"
      />
    </template>

    <!-- ══ Création ══ -->
    <Dialog
      v-model:visible="showCreateDialog"
      :header="t('centre.classes.new')"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleCreateSession">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.form.level") }} <span class="text-red-600">*</span>
          </label>
          <Select
            v-model="createForm.level_id"
            :options="allLevels"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('centre.form.level_placeholder')"
            class="w-full"
            filter
          />
        </div>
        <div v-if="authStore.isDirector">
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.form.branch") }} <span class="text-red-600">*</span>
          </label>
          <Select
            v-model="createForm.branch_id"
            :options="branches"
            optionLabel="name"
            optionValue="id"
            :placeholder="t('centre.form.branch_placeholder')"
            class="w-full"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.classes.name") }}
            <span class="font-normal text-muted">{{
              t("centre.form.optional")
            }}</span>
          </label>
          <InputText
            v-model="createForm.label"
            class="w-full"
            :placeholder="t('centre.classes.name_placeholder')"
          />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("centre.classes.start_date") }}
              <span class="text-red-600">*</span>
            </label>
            <DatePicker
              v-model="createForm.start_date"
              class="w-full"
              dateFormat="dd/mm/yy"
              showIcon
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("centre.classes.end_date") }}
              <span class="font-normal text-muted">{{
                t("centre.form.optional")
              }}</span>
            </label>
            <DatePicker
              v-model="createForm.end_date"
              class="w-full"
              dateFormat="dd/mm/yy"
              showIcon
              :minDate="createForm.start_date ?? undefined"
            />
          </div>
        </div>
        <Message v-if="createError" severity="error" :closable="false">{{
          createError
        }}</Message>
      </form>
      <template #footer>
        <Button
          :label="t('common.cancel')"
          text
          @click="showCreateDialog = false"
        />
        <Button
          :label="t('common.create')"
          icon="pi pi-check"
          :loading="creating"
          @click="handleCreateSession"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { BranchResponse, UserAdminResponse } from "#shared/api";
import type { NormalizedTrainingSession } from "~/stores/trainingSessions";

definePageMeta({ layout: "centre", watermark: "Klassen" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const trainingSessionsStore = useTrainingSessionsStore();
const examsStore = useExamsStore();
const toast = useToast();

const loading = ref(true);
const sessions = ref<NormalizedTrainingSession[]>([]);
const errorMessage = ref<string | null>(null);
const branches = ref<BranchResponse[]>([]);
const teachers = ref<UserAdminResponse[]>([]);

const allLevels = computed(() => [
  ...examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
  { label: "Start Deutsch - A1", value: "sd:A1" },
  { label: "Start Deutsch - A2", value: "sd:A2" },
]);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function activeStudentCount(session: NormalizedTrainingSession) {
  return session.students.filter((s) => !s.ended_at).length;
}

// ── Statut d'une classe ──
type Statut = "upcoming" | "ongoing" | "finished";

function statusOf(session: NormalizedTrainingSession): Statut {
  const now = Date.now();
  if (session.end_date && new Date(session.end_date).getTime() < now)
    return "finished";
  if (new Date(session.start_date).getTime() > now) return "upcoming";
  return "ongoing";
}

function statusBadge(session: NormalizedTrainingSession) {
  const s = statusOf(session);
  if (s === "finished")
    return {
      label: t("centre.classes.status.finished"),
      class: "bg-card-2 text-muted",
    };
  if (s === "upcoming")
    return {
      label: t("centre.classes.status.upcoming"),
      class: "bg-sky-500/10 text-sky-600",
    };
  return {
    label: t("centre.classes.status.ongoing"),
    class: "bg-emerald-500/10 text-emerald-600",
  };
}

// Extrait le niveau CECR du nom (« TELC Deutsch B1 » → « B1 ») pour le filigrane
function cefrOf(levelName: string) {
  return levelName.match(/\b([ABC][12])\b/)?.[1] ?? null;
}

function watermarkTone(session: NormalizedTrainingSession) {
  const s = statusOf(session);
  if (s === "finished") return "neutral";
  if (s === "upcoming") return "sky";
  return "amber";
}

function period(session: NormalizedTrainingSession) {
  const start = formatDate(session.start_date);
  return session.end_date
    ? t("centre.classes.period", { start, end: formatDate(session.end_date) })
    : t("centre.classes.period_open", { start });
}

// ── Filtres ──
type FilterKey = "all" | Statut;
const activeFilter = ref<FilterKey>("all");
const search = ref("");
const levelFilter = ref<string | null>(null);
const teacherFilter = ref<string | null>(null); // id enseignant, ou "__none__"
const branchFilter = ref<string | null>(null);

const NO_TEACHER = "__none__";

const statusFilters = computed(() => {
  const count = (s: Statut) =>
    sessions.value.filter((x) => statusOf(x) === s).length;
  return [
    {
      key: "all" as const,
      label: t("centre.classes.filter_all"),
      count: sessions.value.length,
    },
    {
      key: "ongoing" as const,
      label: t("centre.classes.status.ongoing"),
      count: count("ongoing"),
    },
    {
      key: "upcoming" as const,
      label: t("centre.classes.status.upcoming"),
      count: count("upcoming"),
    },
    {
      key: "finished" as const,
      label: t("centre.classes.status.finished"),
      count: count("finished"),
    },
  ];
});

// Niveaux présents dans les classes (B1, B2…), triés
const levelOptions = computed(() =>
  [
    ...new Set(sessions.value.map((s) => cefrOf(s.level_name) ?? s.level_name)),
  ].sort(),
);

const teacherOptions = computed(() => [
  { label: t("centre.classes.filter_no_teacher"), value: NO_TEACHER },
  ...teachers.value
    .map((x) => ({ label: x.full_name, value: x.id }))
    .sort((a, b) => a.label.localeCompare(b.label)),
]);

const hasExtraFilters = computed(
  () =>
    !!search.value.trim() ||
    !!levelFilter.value ||
    !!teacherFilter.value ||
    !!branchFilter.value,
);

function resetFilters() {
  search.value = "";
  levelFilter.value = null;
  teacherFilter.value = null;
  branchFilter.value = null;
}

const ORDRE: Record<Statut, number> = { ongoing: 0, upcoming: 1, finished: 2 };

// Plus récentes d'abord (pour que les mois s'enchaînent), puis en cours avant à venir et terminées
const filteredSessions = computed(() => {
  const q = search.value.trim().toLowerCase();
  return sessions.value
    .filter(
      (s) => activeFilter.value === "all" || statusOf(s) === activeFilter.value,
    )
    .filter(
      (s) =>
        !levelFilter.value ||
        (cefrOf(s.level_name) ?? s.level_name) === levelFilter.value,
    )
    .filter((s) => {
      if (!teacherFilter.value) return true;
      if (teacherFilter.value === NO_TEACHER) return s.teachers.length === 0;
      return s.teachers.some((x) => x.teacher_id === teacherFilter.value);
    })
    .filter((s) => !branchFilter.value || s.branch_id === branchFilter.value)
    .filter(
      (s) =>
        !q ||
        (s.label ?? "").toLowerCase().includes(q) ||
        s.level_name.toLowerCase().includes(q) ||
        s.teachers.some((x) => x.teacher_name.toLowerCase().includes(q)),
    )
    .sort(
      (a, b) =>
        new Date(b.start_date).getTime() - new Date(a.start_date).getTime() ||
        ORDRE[statusOf(a)] - ORDRE[statusOf(b)],
    );
});

// ── Pagination ──
const rowsPerPage = ref(12);
const firstRecordIndex = ref(0);

function onPageChange(event: { first: number; rows: number }) {
  firstRecordIndex.value = event.first;
  rowsPerPage.value = event.rows;
}

watch([activeFilter, search, levelFilter, teacherFilter, branchFilter], () => {
  firstRecordIndex.value = 0;
});

// ── Groupement par mois de début (sur la page affichée) ──
function monthKey(dateStr: string) {
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function monthLabel(dateStr: string) {
  const label = new Date(dateStr).toLocaleDateString(locale.value, {
    month: "long",
    year: "numeric",
  });
  return label.charAt(0).toUpperCase() + label.slice(1);
}

// Total par mois sur toute la liste filtrée, pas seulement la page
const monthTotals = computed(() => {
  const totals = new Map<string, number>();
  for (const s of filteredSessions.value) {
    const k = monthKey(s.start_date);
    totals.set(k, (totals.get(k) ?? 0) + 1);
  }
  return totals;
});

const groupedPage = computed(() => {
  const page = filteredSessions.value.slice(
    firstRecordIndex.value,
    firstRecordIndex.value + rowsPerPage.value,
  );
  const groups: {
    key: string;
    label: string;
    total: number;
    items: NormalizedTrainingSession[];
  }[] = [];
  for (const s of page) {
    const key = monthKey(s.start_date);
    let group = groups.find((g) => g.key === key);
    if (!group) {
      group = {
        key,
        label: monthLabel(s.start_date),
        total: monthTotals.value.get(key) ?? 0,
        items: [],
      };
      groups.push(group);
    }
    group.items.push(s);
  }
  return groups;
});

// ── Chargement ──
async function loadData() {
  loading.value = true;

  const [sessionsResult, teacherResult, , branchResult] = await Promise.all([
    authStore.isDirector
      ? trainingSessionsStore.fetchByCenter()
      : trainingSessionsStore.fetchByBranch(),
    centerStaffStore.fetchTeachers(),
    examsStore.catalog.length === 0
      ? examsStore.fetchCatalog()
      : Promise.resolve(),
    authStore.isDirector
      ? centerStaffStore.fetchMyBranches()
      : Promise.resolve(null),
  ]);

  sessions.value = trainingSessionsStore.sessions;
  errorMessage.value = sessionsResult.success
    ? null
    : trainingSessionsStore.error || t("common.load_error");

  teachers.value = teacherResult.success ? (teacherResult.teachers ?? []) : [];
  if (branchResult?.success) branches.value = branchResult.branches ?? [];

  loading.value = false;
}

// ══ Création ══
const showCreateDialog = ref(false);
const creating = ref(false);
const createError = ref<string | null>(null);
const createForm = ref<{
  level_id: string;
  branch_id: string;
  label: string;
  start_date: Date | null;
  end_date: Date | null;
}>({
  level_id: "",
  branch_id: "",
  label: "",
  start_date: null,
  end_date: null,
});

function openCreateDialog() {
  createForm.value = {
    level_id: "",
    branch_id: branches.value.length === 1 ? branches.value[0]!.id : "",
    label: "",
    start_date: new Date(),
    end_date: null,
  };
  createError.value = null;
  showCreateDialog.value = true;
}

async function handleCreateSession() {
  const f = createForm.value;
  if (!f.level_id || !f.start_date || (authStore.isDirector && !f.branch_id)) {
    createError.value = t("centre.form.required_fields");
    return;
  }
  if (f.end_date && f.end_date <= f.start_date) {
    createError.value = t("centre.classes.dates_error");
    return;
  }

  creating.value = true;
  createError.value = null;

  const isSd = f.level_id.startsWith("sd:");

  const result = await trainingSessionsStore.createSession({
    level_id: isSd ? null : f.level_id,
    sd_level: isSd ? (f.level_id.slice(3) as "A1" | "A2") : null,
    branch_id: authStore.isDirector ? f.branch_id : null,
    label: f.label.trim() || null,
    start_date: f.start_date.toISOString(),
    end_date: f.end_date ? f.end_date.toISOString() : null,
  });

  creating.value = false;

  if (result.success) {
    showCreateDialog.value = false;
    toast.add({
      severity: "success",
      summary: t("centre.classes.created"),
      life: 3000,
    });
    // On enchaîne sur le détail pour affecter enseignant et élèves
    if (result.session) {
      await navigateTo(localePath(`/centre/sessions/${result.session.id}`));
    } else {
      sessions.value = trainingSessionsStore.sessions;
    }
  } else {
    createError.value = result.error || t("centre.form.create_error");
  }
}

onMounted(loadData);
</script>
