<!-- pages/enseignant/devoirs/index.vue -->
<template>
  <div class="mx-auto max-w-5xl space-y-5">
    <!-- ── Barre d'action ── -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <IconField class="w-full sm:w-80">
        <InputIcon class="pi pi-search" />
        <InputText v-model="search" class="w-full" :placeholder="t('teacher.assignments.search')" />
      </IconField>
      <Button
        :label="t('teacher.assignments.new')"
        icon="pi pi-plus"
        @click="navigateTo(localePath('/enseignant/devoirs/nouveau'))"
      />
    </div>

    <!-- ── Onglets ── -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
        :class="
          activeTab === tab.key
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-line bg-card text-muted hover:border-primary/30'
        "
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span
          class="rounded-full px-1.5 text-xs"
          :class="tab.key === 'to_grade' && tab.count > 0 ? 'bg-amber-500/15 text-amber-600' : 'bg-card-2 text-muted'"
        >
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div v-for="n in 3" :key="n" class="h-32 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <!-- ── Aucun devoir du tout ── -->
    <div
      v-else-if="store.teaching.length === 0"
      class="rounded-card border border-dashed border-line bg-card p-10 text-center"
    >
      <i class="pi pi-file-edit mb-3 text-3xl text-faint" />
      <p class="font-medium text-ink">{{ t("teacher.assignments.empty_title") }}</p>
      <p class="mt-1 text-sm text-muted">{{ t("teacher.assignments.empty_text") }}</p>
    </div>

    <!-- ── Onglet vide ── -->
    <p
      v-else-if="visible.length === 0"
      class="rounded-card border border-dashed border-line bg-card p-8 text-center text-sm text-muted"
    >
      {{ t("teacher.assignments.empty_tab") }}
    </p>

    <!-- ── Liste ── -->
    <div v-else class="space-y-3">
      <NuxtLink
        v-for="a in visible"
        :key="a.id"
        :to="localePath(`/enseignant/devoirs/${a.id}`)"
        class="block rounded-card border border-line bg-card p-5 shadow-soft transition-colors hover:border-primary/30"
        :class="{ 'opacity-70': a.is_cancelled }"
      >
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold text-ink">{{ a.title }}</p>
            <p class="mt-0.5 truncate text-xs text-muted">
              {{ a.exam_name }} · {{ a.cefr_code }} · {{ a.subject_name }}
            </p>
          </div>

          <span
            v-if="a.is_cancelled"
            class="shrink-0 rounded-full bg-card-2 px-2.5 py-1 text-xs font-semibold text-muted"
          >
            {{ t("teacher.assignments.cancelled") }}
          </span>
          <span
            v-else-if="toGrade(a) > 0"
            class="shrink-0 rounded-full bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-600"
          >
            {{ t("teacher.assignments.to_grade_badge", { n: toGrade(a) }, toGrade(a)) }}
          </span>
        </div>

        <!-- Cibles -->
        <div v-if="a.targets?.length" class="mt-3 flex flex-wrap gap-1.5">
          <span
            v-for="target in a.targets"
            :key="`${target.type}-${target.id}`"
            class="inline-flex items-center gap-1 rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-medium text-muted"
          >
            <i :class="target.type === 'class' ? 'pi pi-users' : 'pi pi-user'" class="text-[10px]" />
            {{ target.name }}
          </span>
        </div>

        <div class="mt-4 grid gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
          <!-- Rendus -->
          <div>
            <div class="mb-1 flex justify-between text-xs">
              <span class="text-muted">{{ t("teacher.assignments.submitted") }}</span>
              <span class="font-semibold text-ink">{{ a.submitted_count ?? 0 }}/{{ a.expected_count ?? 0 }}</span>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-card-2">
              <div class="h-full rounded-full bg-primary" :style="{ width: pct(a.submitted_count, a.expected_count) }" />
            </div>
          </div>
          <!-- Corrigés -->
          <div>
            <div class="mb-1 flex justify-between text-xs">
              <span class="text-muted">{{ t("teacher.assignments.graded") }}</span>
              <span class="font-semibold text-ink">{{ a.graded_count ?? 0 }}/{{ a.submitted_count ?? 0 }}</span>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-card-2">
              <div class="h-full rounded-full bg-emerald-500" :style="{ width: pct(a.graded_count, a.submitted_count) }" />
            </div>
          </div>
          <!-- Échéance -->
          <p class="flex items-center gap-1.5 text-xs" :class="dueClass(a)">
            <i class="pi pi-clock text-[11px]" />
            {{ dueLabel(a) }}
          </p>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AssignmentSummaryResponse } from "#shared/api";

definePageMeta({ layout: "enseignant" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const store = useAssignmentsStore();

const loading = ref(true);
const errorMessage = ref<string | null>(null);
const search = ref("");

type TabKey = "to_grade" | "ongoing" | "closed" | "cancelled";
const activeTab = ref<TabKey>("ongoing");

function toGrade(a: AssignmentSummaryResponse) {
  return Math.max((a.submitted_count ?? 0) - (a.graded_count ?? 0), 0);
}

function isPastDue(a: AssignmentSummaryResponse) {
  return !!a.due_at && new Date(a.due_at).getTime() < Date.now();
}

// Un devoir n'est que dans un seul onglet
function tabOf(a: AssignmentSummaryResponse): TabKey {
  if (a.is_cancelled) return "cancelled";
  if (toGrade(a) > 0) return "to_grade";
  if (isPastDue(a)) return "closed";
  return "ongoing";
}

const tabs = computed(() => {
  const count = (k: TabKey) => store.teaching.filter((a) => tabOf(a) === k).length;
  return (["to_grade", "ongoing", "closed", "cancelled"] as const).map((key) => ({
    key,
    label: t(`teacher.assignments.tabs.${key}`),
    count: count(key),
  }));
});

const visible = computed(() => {
  const q = search.value.trim().toLowerCase();
  return store.teaching
    .filter((a) => tabOf(a) === activeTab.value)
    .filter(
      (a) =>
        !q ||
        a.title.toLowerCase().includes(q) ||
        a.subject_name.toLowerCase().includes(q) ||
        (a.targets ?? []).some((target) => target.name.toLowerCase().includes(q)),
    )
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
});

function pct(part?: number, total?: number) {
  if (!total) return "0%";
  return `${Math.min(Math.round(((part ?? 0) / total) * 100), 100)}%`;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function dueLabel(a: AssignmentSummaryResponse) {
  if (!a.due_at) return t("teacher.assignments.no_due");
  return isPastDue(a)
    ? t("teacher.assignments.due_passed", { date: formatDate(a.due_at) })
    : t("teacher.assignments.due_on", { date: formatDate(a.due_at) });
}

function dueClass(a: AssignmentSummaryResponse) {
  if (a.is_cancelled || !a.due_at) return "text-muted";
  return isPastDue(a) ? "text-red-600" : "text-ink";
}

onMounted(async () => {
  const result = await store.fetchTeaching();
  if (!result.success) {
    errorMessage.value = result.error || t("common.load_error");
  } else if (tabs.value.find((tab) => tab.key === "to_grade")!.count > 0) {
    // S'il y a des copies à corriger, on ouvre directement cet onglet
    activeTab.value = "to_grade";
  }
  loading.value = false;
});
</script>