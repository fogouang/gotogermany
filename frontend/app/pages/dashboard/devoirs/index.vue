<template>
  <div class="space-y-5 pb-10">
    <p class="text-sm text-muted">{{ t("student_assignments.subtitle") }}</p>

    <!-- ── Onglets ── -->
    <div class="flex gap-1 rounded-leaf border border-line bg-card p-1 sm:w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="flex flex-1 items-center justify-center gap-2 rounded-leaf px-4 py-2 text-sm font-medium transition-colors sm:flex-none"
        :class="activeTab === tab.key ? 'bg-primary/10 text-primary' : 'text-muted hover:text-ink'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span
          class="rounded-full px-1.5 text-[11px] font-semibold"
          :class="activeTab === tab.key ? 'bg-primary text-white' : 'bg-card-2 text-muted'"
        >
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="grid gap-3 xl:grid-cols-2">
      <div v-for="n in 4" :key="n" class="h-36 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="loadError"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-red-500/10 text-red-600">
        <i class="pi pi-exclamation-triangle" />
      </span>
      <p class="text-sm text-muted">{{ t("student_assignments.error") }}</p>
      <Button :label="t('student_assignments.retry')" icon="pi pi-refresh" size="small" outlined @click="load" />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="visible.length === 0"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <i :class="activeTab === 'todo' ? 'pi pi-check-circle' : 'pi pi-inbox'" />
      </span>
      <p class="text-sm text-muted">{{ t(`student_assignments.empty_${activeTab}`) }}</p>
    </div>

    <!-- ── Liste ── -->
    <div v-else class="grid gap-3 xl:grid-cols-2">
      <article
        v-for="a in visible"
        :key="a.id"
        class="flex flex-col gap-4 rounded-card border bg-card p-5 shadow-soft"
        :class="a.is_late && isTodo(a) ? 'border-red-500/40' : 'border-line'"
      >
        <header class="flex items-start gap-3">
          <span class="flex size-11 shrink-0 items-center justify-center rounded-leaf bg-violet-500/10 text-sm font-bold text-violet-600">
            {{ a.cefr_code }}
          </span>
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold leading-snug text-ink">{{ a.title }}</h3>
            <p class="mt-0.5 truncate text-xs text-muted">
              {{ a.exam_name }} · {{ t("student_assignments.by", { name: a.teacher_name }) }}
            </p>
          </div>
          <span class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold" :class="statusStyle(a.status)">
            {{ t(`student_assignments.status.${a.status}`) }}
          </span>
        </header>

        <p v-if="a.instructions" class="whitespace-pre-line rounded-leaf bg-card-2 px-3 py-2.5 text-sm text-ink">
          {{ a.instructions }}
        </p>

        <footer class="mt-auto flex flex-wrap items-center justify-between gap-3 border-t border-line pt-3">
          <p class="flex items-center gap-1.5 text-xs" :class="a.is_late && isTodo(a) ? 'font-semibold text-red-600' : 'text-muted'">
            <i class="pi text-[10px]" :class="a.is_late && isTodo(a) ? 'pi-exclamation-circle' : 'pi-calendar'" />
            <template v-if="a.is_late && isTodo(a)">{{ t("student_assignments.late") }} · </template>
            {{ a.due_at ? t("student_assignments.due", { date: formatDateTime(a.due_at) }) : t("student_assignments.no_due") }}
          </p>

          <!-- Actions selon le statut -->
          <Button
            v-if="a.status === 'pending'"
            :label="t('student_assignments.start')"
            icon="pi pi-play"
            size="small"
            @click="open(a)"
          />
          <Button
            v-else-if="a.status === 'in_progress'"
            :label="t('student_assignments.continue')"
            icon="pi pi-arrow-right"
            iconPos="right"
            size="small"
            @click="open(a)"
          />
          <span v-else-if="a.status === 'submitted'" class="text-xs text-muted">
            <i class="pi pi-hourglass mr-1 text-[10px]" />{{ t("student_assignments.waiting") }}
          </span>
          <span
            v-else-if="a.status === 'graded'"
            class="flex items-baseline gap-1.5 rounded-leaf bg-emerald-500/10 px-3 py-1.5 text-emerald-600"
          >
            <span class="text-xs">{{ t("student_assignments.score") }}</span>
            <span class="text-lg font-bold">{{ a.final_score != null ? Math.round(a.final_score) : "-" }}</span>
          </span>
        </footer>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AssignmentsService } from "#shared/api";
import type { StudentAssignmentResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Hausaufgaben" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();

type Tab = "todo" | "submitted" | "graded";

const assignments = ref<StudentAssignmentResponse[]>([]);
const loading = ref(true);
const loadError = ref(false);
const activeTab = ref<Tab>("todo");

// ── Format ──
const intlLocale = computed(() => ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ?? "en-GB");
const formatDateTime = (d: string) =>
  new Date(d).toLocaleDateString(intlLocale.value, { day: "2-digit", month: "long", hour: "2-digit", minute: "2-digit" });

const statusStyle = (s: string) =>
  ({
    pending: "bg-sky-500/10 text-sky-600",
    in_progress: "bg-amber-500/15 text-amber-600",
    submitted: "bg-violet-500/10 text-violet-600",
    graded: "bg-emerald-500/10 text-emerald-600",
  })[s] ?? "bg-card-2 text-muted";

const isTodo = (a: StudentAssignmentResponse) => a.status === "pending" || a.status === "in_progress";

// ── Répartition ──
const todo = computed(() =>
  assignments.value
    .filter(isTodo)
    // en retard d'abord, puis échéance la plus proche, sans échéance à la fin
    .sort(
      (a, b) =>
        Number(b.is_late) - Number(a.is_late) ||
        (a.due_at ?? "9999").localeCompare(b.due_at ?? "9999"),
    ),
);
const submitted = computed(() => assignments.value.filter((a) => a.status === "submitted"));
const graded = computed(() =>
  assignments.value
    .filter((a) => a.status === "graded")
    .sort((a, b) => (b.due_at ?? "").localeCompare(a.due_at ?? "")),
);

const tabs = computed(() => [
  { key: "todo" as const, label: t("student_assignments.tabs.todo"), count: todo.value.length },
  { key: "submitted" as const, label: t("student_assignments.tabs.submitted"), count: submitted.value.length },
  { key: "graded" as const, label: t("student_assignments.tabs.graded"), count: graded.value.length },
]);

const visible = computed(() =>
  activeTab.value === "todo" ? todo.value : activeTab.value === "submitted" ? submitted.value : graded.value,
);

// ── Actions ──
const open = (a: StudentAssignmentResponse) => navigateTo(localePath(`/dashboard/devoirs/${a.id}`));

// ── Chargement ──
async function load() {
  loading.value = true;
  loadError.value = false;
  try {
    authStore._ensureApiConfig();
    assignments.value = await AssignmentsService.myAssignmentsApiV1AssignmentsMeGet();
    // S'il n'y a rien à faire mais des corrections, on ouvre directement l'onglet utile
    if (todo.value.length === 0 && graded.value.length > 0) activeTab.value = "graded";
  } catch {
    loadError.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>