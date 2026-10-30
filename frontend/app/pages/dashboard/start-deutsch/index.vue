<!-- pages/dashboard/start-deutsch/index.vue -->
<template>
  <div class="space-y-6">
    <!-- ── En-tête ── -->
    <header>
      <h1 class="text-2xl font-bold text-ink">
        {{ t("start_deutsch.title") }}
      </h1>
      <p class="mt-1 text-sm text-muted">{{ t("start_deutsch.subtitle") }}</p>
    </header>

    <!-- ── Bandeau : entraînement inclus, pas un vrai examen ── -->
    <div
      class="flex items-start gap-3 rounded-card border border-primary/30 bg-primary/10 px-5 py-4"
    >
      <i class="pi pi-info-circle mt-0.5 shrink-0 text-primary" />
      <p class="text-sm text-ink">{{ t("start_deutsch.info_banner") }}</p>
    </div>

    <!-- ── Filtre niveau ── -->
    <div v-if="!isCenterStudent" class="flex flex-wrap gap-2">
      <button
        v-for="opt in levelOptions"
        :key="opt.value"
        type="button"
        class="rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
        :class="
          filterLevel === opt.value
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-line bg-card text-muted hover:border-primary/30 hover:text-ink'
        "
        @click="setLevelFilter(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- ── Chargement ── -->
    <div
      v-if="store.subjectsLoading"
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="i in 6"
        :key="i"
        class="h-32 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="filteredSubjects.length === 0"
      class="rounded-card border border-line bg-card py-16 text-center shadow-soft"
    >
      <i class="pi pi-inbox mb-3 block text-4xl text-faint" />
      <p class="text-sm text-muted">{{ t("start_deutsch.empty") }}</p>
    </div>

    <!-- ── Cartes sujets ── -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="subject in filteredSubjects"
        :key="subject.id"
        type="button"
        class="group flex flex-col items-start gap-3 rounded-card border bg-card p-5 text-left shadow-soft transition-all hover:border-primary/40"
        :class="
          subject.is_locked
            ? 'border-line opacity-80'
            : attemptOf(subject.id)
              ? 'border-line'
              : 'border-primary/30'
        "
        @click="openSubject(subject)"
      >
        <div class="flex w-full items-center justify-between gap-2">
          <span
            class="inline-flex size-10 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary"
          >
            {{ subject.level }}
          </span>

          <span
            v-if="subject.is_locked"
            class="inline-flex items-center gap-1 rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted"
          >
            <i class="pi pi-lock text-[10px]" />
            {{ t("start_deutsch.catalog.locked") }}
          </span>
          <!-- Déjà tenté ou pas -->
          <span
            v-else-if="attemptOf(subject.id)"
            class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="attemptOf(subject.id)!.badge"
          >
            <i class="pi text-[10px]" :class="attemptOf(subject.id)!.icon" />
            {{ attemptOf(subject.id)!.label }}
          </span>
          <span
            v-else
            class="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary"
          >
            <i class="pi pi-sparkles text-[10px]" />
            {{ t("start_deutsch.catalog.not_attempted") }}
          </span>
        </div>

        <div class="min-w-0">
          <p
            class="font-semibold text-ink transition-colors group-hover:text-primary"
          >
            {{ subject.title }}
          </p>
          <p class="mt-1 line-clamp-2 text-xs text-muted">
            {{
              t(
                `start_deutsch.catalog.description_${subject.level.toLowerCase()}`,
              )
            }}
          </p>
        </div>

        <div
          class="mt-auto flex w-full items-center justify-between border-t border-line pt-3 text-xs text-muted"
        >
          <span v-if="attemptOf(subject.id)">
            {{
              t(
                "start_deutsch.catalog.attempts",
                { n: attemptOf(subject.id)!.count },
                attemptOf(subject.id)!.count,
              )
            }}
          </span>
          <span v-else>{{ t("start_deutsch.catalog.never") }}</span>
          <i
            class="pi pi-arrow-right text-faint transition-all group-hover:translate-x-1 group-hover:text-primary"
          />
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { StartDeutschSessionListItem } from "#shared/api";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();
const store = useStartDeutschSessionStore();

const { isCenterStudent, visibleStartDeutschSubjects } = useVisibleCatalog();

const filterLevel = ref<"A1" | "A2" | "">("");

const levelOptions = computed(() => [
  { label: t("start_deutsch.all_levels"), value: "" as const },
  { label: "A1", value: "A1" as const },
  { label: "A2", value: "A2" as const },
]);

const filteredSubjects = computed(() =>
  filterLevel.value
    ? store.subjects.filter((s) => s.level === filterLevel.value)
    : store.subjects,
);

function setLevelFilter(value: "A1" | "A2" | "") {
  filterLevel.value = value;
}

// Sujet fermé : paiement du niveau. Sinon : on lance la session.
function openSubject(subject: {
  id: string;
  level: string;
  is_locked?: boolean;
}) {
  if (subject.is_locked) {
    navigateTo(
      localePath({
        path: "/dashboard/paiement",
        query: { sd_level: subject.level },
      }),
    );
    return;
  }
  navigateTo(localePath(`/dashboard/start-deutsch/${subject.id}/session`));
}

// ── Tentatives de l'élève : dernière tentative et nombre, par sujet ──
const mySessions = ref<StartDeutschSessionListItem[]>([]);

const attempts = computed(() => {
  const out: Record<
    string,
    { last: StartDeutschSessionListItem; count: number }
  > = {};
  for (const s of mySessions.value) {
    const entry = out[s.subject_id];
    if (!entry) out[s.subject_id] = { last: s, count: 1 };
    else {
      entry.count += 1;
      if (s.started_at > entry.last.started_at) entry.last = s;
    }
  }
  return out;
});

function attemptOf(subjectId: string) {
  const entry = attempts.value[subjectId];
  if (!entry) return null;
  const { last, count } = entry;

  if (last.status === "IN_PROGRESS") {
    return {
      count,
      label: t("start_deutsch.catalog.in_progress"),
      icon: "pi-play",
      badge: "bg-sky-500/10 text-sky-600",
    };
  }
  if (last.status === "PENDING_REVIEW" || last.score_percent == null) {
    return {
      count,
      label: t("start_deutsch.catalog.pending"),
      icon: "pi-clock",
      badge: "bg-amber-500/15 text-amber-600",
    };
  }
  const score = Math.round(last.score_percent);
  return {
    count,
    label: t("start_deutsch.catalog.last_score", { score }),
    icon: last.passed ? "pi-check-circle" : "pi-refresh",
    badge: last.passed
      ? "bg-emerald-500/10 text-emerald-600"
      : "bg-red-500/10 text-red-600",
  };
}

onMounted(async () => {
  const [, sessions] = await Promise.all([
    store.subjects.length === 0 ? store.fetchSubjects() : Promise.resolve(),
    store.getMySessions(0, 100),
  ]);
  if (sessions.success) mySessions.value = sessions.data;
});
</script>
