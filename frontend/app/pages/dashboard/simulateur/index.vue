<!-- pages/dashboard/simulateur/index.vue -->
<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold text-ink">{{ t("simulator.title") }}</h1>
      <p class="mt-1 text-sm text-muted">{{ t("simulator.subtitle") }}</p>
    </header>

    <!-- ── Onglets ── -->
    <div class="flex border-b border-line">
      <button
        type="button"
        class="border-b-2 px-5 py-3 text-sm font-semibold transition-colors"
        :class="activeTab === 'sujets' ? 'border-primary text-primary' : 'border-transparent text-muted hover:text-ink'"
        @click="activeTab = 'sujets'"
      >
        <i class="pi pi-list-check mr-2" />{{ t("simulator.tab_subjects") }}
      </button>
      <button
        type="button"
        class="border-b-2 px-5 py-3 text-sm font-semibold transition-colors"
        :class="activeTab === 'resultats' ? 'border-primary text-primary' : 'border-transparent text-muted hover:text-ink'"
        @click="switchToResults"
      >
        <i class="pi pi-history mr-2" />{{ t("simulator.tab_results") }}
        <span
          v-if="store.results.length"
          class="ml-1.5 rounded-full bg-primary/10 px-1.5 py-0.5 text-xs font-bold text-primary"
        >
          {{ store.results.length }}
        </span>
      </button>
    </div>

    <!-- ══ Onglet Sujets ══ -->
    <template v-if="activeTab === 'sujets'">
      <!-- Filtres fournisseur / niveau, dérivés du vrai catalogue -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in availableProviders"
          :key="p"
          type="button"
          class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
          :class="
            selectedProvider === p
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30 hover:text-ink'
          "
          @click="selectedProvider = selectedProvider === p ? '' : p"
        >
          {{ p.toUpperCase() }}
        </button>
        <div class="mx-1 w-px bg-line" />
        <button
          v-for="l in availableLevels"
          :key="l"
          type="button"
          class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
          :class="
            selectedLevel === l
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30 hover:text-ink'
          "
          @click="selectedLevel = selectedLevel === l ? '' : l"
        >
          {{ l }}
        </button>
      </div>

      <!-- Chargement -->
      <div v-if="examsStore.loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div v-for="i in 4" :key="i" class="h-36 animate-pulse rounded-card bg-card-2" />
      </div>

      <!-- Vide -->
      <div
        v-else-if="!simulatorSubjects.length"
        class="rounded-card border border-line bg-card py-16 text-center shadow-soft"
      >
        <i class="pi pi-inbox mb-3 block text-4xl text-faint" />
        <p class="font-medium text-ink">{{ t("simulator.no_subjects_title") }}</p>
        <p class="mb-4 mt-1 text-sm text-muted">{{ t("simulator.no_subjects_subtitle") }}</p>
        <Button :label="t('simulator.show_all')" icon="pi pi-refresh" @click="resetFilters" />
      </div>

      <!-- Grille des sujets -->
      <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <NuxtLink
          v-for="subject in simulatorSubjects"
          :key="subject.id"
          :to="localePath(`/dashboard/simulateur/${subject.id}`)"
          class="group flex flex-col gap-3 rounded-card border border-line bg-card p-5 shadow-soft transition-all hover:border-primary/40"
        >
          <div class="flex items-start gap-3">
            <div
              class="flex size-10 shrink-0 items-center justify-center rounded-leaf text-xs font-bold"
              :class="providerTagClass(subject.provider)"
            >
              {{ subject.provider.slice(0, 2).toUpperCase() }}
            </div>
            <p class="min-w-0 flex-1 text-sm font-semibold leading-snug text-ink transition-colors group-hover:text-primary">
              {{ subject.title }}
            </p>
          </div>

          <p
            v-if="subject.preview"
            class="line-clamp-2 rounded-leaf bg-card-2 px-3 py-2 text-xs leading-relaxed text-muted"
          >
            {{ subject.preview }}
          </p>

          <div class="flex items-center justify-between gap-2 pt-1">
            <div class="flex flex-wrap items-center gap-2">
              <Tag :value="subject.provider.toUpperCase()" :class="providerTagClass(subject.provider)" />
              <Tag :value="subject.level.toUpperCase()" severity="info" />
              <span class="text-xs text-faint">
                {{ subject.taskCount }}
                {{ subject.taskCount > 1 ? t("simulator.tasks_plural") : t("simulator.tasks") }}
              </span>
            </div>
            <span class="flex shrink-0 items-center gap-1 text-xs font-semibold text-primary transition-all group-hover:gap-2">
              {{ t("simulator.start") }}
              <i class="pi pi-arrow-right text-xs" />
            </span>
          </div>
        </NuxtLink>
      </div>
    </template>

    <!-- ══ Onglet Mes corrections ══ -->
    <template v-else>
      <div v-if="store.loadingResults" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div v-for="i in 4" :key="i" class="h-44 animate-pulse rounded-card bg-card-2" />
      </div>

      <div
        v-else-if="!store.results.length"
        class="rounded-card border border-line bg-card py-16 text-center shadow-soft"
      >
        <i class="pi pi-history mb-3 block text-4xl text-faint" />
        <p class="font-medium text-ink">{{ t("simulator.no_results_title") }}</p>
        <p class="mb-4 mt-1 text-sm text-muted">{{ t("simulator.no_results_subtitle") }}</p>
        <Button :label="t('simulator.see_subjects')" icon="pi pi-list-check" @click="activeTab = 'sujets'" />
      </div>

      <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <button
          v-for="result in store.results"
          :key="result.id"
          type="button"
          class="flex flex-col gap-3 rounded-card border border-line bg-card p-5 text-left shadow-soft transition-all hover:border-primary/40"
          @click="openResult(result)"
        >
          <div class="flex w-full items-start gap-3">
            <!-- Score circulaire -->
            <div class="relative size-14 shrink-0">
              <svg class="size-14 -rotate-90" viewBox="0 0 56 56">
                <circle cx="28" cy="28" r="22" fill="none" class="stroke-card-2" stroke-width="6" />
                <circle
                  cx="28"
                  cy="28"
                  r="22"
                  fill="none"
                  :class="result.passed ? 'stroke-emerald-500' : 'stroke-orange-500'"
                  stroke-width="6"
                  stroke-linecap="round"
                  :stroke-dasharray="`${(result.score_percentage / 100) * 138} 138`"
                />
              </svg>
              <span class="absolute inset-0 flex items-center justify-center text-xs font-extrabold text-ink">
                {{ Math.round(result.score_percentage) }}%
              </span>
            </div>

            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold leading-snug text-ink">
                {{ result.subject_title || t("simulator.deleted_subject") }}
              </p>
              <p class="mt-0.5 text-xs text-faint">{{ formatDate(result.created_at) }}</p>
              <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                <Tag :value="result.provider.toUpperCase()" :class="['text-xs', providerTagClass(result.provider)]" />
                <Tag :value="result.level.toUpperCase()" severity="info" />
                <Tag
                  :value="result.passed ? t('simulator.passed') : t('simulator.not_passed')"
                  :severity="result.passed ? 'success' : 'danger'"
                />
              </div>
            </div>
          </div>

          <!-- Détail par critère -->
          <div class="w-full space-y-1.5 rounded-leaf bg-card-2 px-3 py-2.5">
            <div v-for="c in criteriaList(result)" :key="c.key" class="flex items-center gap-2">
              <span class="w-20 shrink-0 truncate text-xs text-muted">{{ c.label }}</span>
              <div class="h-1 flex-1 rounded-full bg-line">
                <div
                  class="h-1 rounded-full transition-all"
                  :class="c.pct >= 70 ? 'bg-emerald-500' : c.pct >= 50 ? 'bg-orange-400' : 'bg-red-500'"
                  :style="{ width: c.pct + '%' }"
                />
              </div>
              <span class="w-10 shrink-0 text-right text-xs tabular-nums text-muted">{{ c.score }}/{{ c.max }}</span>
            </div>
          </div>

          <div class="flex w-full items-center justify-between pt-1">
            <span class="text-xs font-bold" :class="result.passed ? 'text-emerald-600' : 'text-orange-600'">
              {{ result.overall_score }} / {{ result.max_score }} pts
            </span>
            <span class="flex items-center gap-1 text-xs font-semibold text-primary">
              {{ t("simulator.see") }} <i class="pi pi-arrow-right text-xs" />
            </span>
          </div>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from "~/stores/simulator";
import type { SimulatorResultResponse } from "#shared/api";

definePageMeta({ layout: "dashboard" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const router = useRouter();
useHead({ title: t("simulator.page_title") });

const examsStore = useExamsStore();
const store = useSimulatorStore(); // utilisé pour « Mes corrections » uniquement

const activeTab = ref<"sujets" | "resultats">("sujets");
const selectedProvider = ref("");
const selectedLevel = ref("");

// ── Sujets : dérivés de useExamsStore comme la page Sprechen.
// fetchExamBySlug() charge l'arbre complet, puis on garde les sujets
// qui ont un module « schreiben ».

const availableProviders = computed(() => [...new Set(examsStore.catalog.map((e) => e.provider))]);

const availableLevels = computed(() => {
  const set = new Set<string>();
  examsStore.catalog.forEach((e) => e.levels?.forEach((l) => set.add(l.cefr_code)));
  return [...set];
});

interface SimulatorSubjectCard {
  id: string;
  provider: string;
  level: string;
  title: string;
  preview?: string;
  taskCount: number;
}

const simulatorSubjects = computed<SimulatorSubjectCard[]>(() => {
  const exam = examsStore.currentExam;
  if (!exam) return [];

  const cards: SimulatorSubjectCard[] = [];
  for (const level of exam.levels ?? []) {
    if (selectedLevel.value && level.cefr_code !== selectedLevel.value) continue;

    for (const subject of level.subjects ?? []) {
      const schreibenModule = (subject.modules ?? []).find((m) => m.slug === "schreiben");
      if (!schreibenModule) continue;

      const firstTeil = schreibenModule.teile?.[0];
      cards.push({
        id: subject.id,
        provider: exam.provider,
        level: level.cefr_code,
        title: subject.name || `${t("simulator.subject_default")} ${subject.subject_number}`,
        preview: firstTeil?.instructions ?? undefined,
        taskCount: schreibenModule.teile?.length ?? 0,
      });
    }
  }
  return cards;
});

// Un fournisseur peut correspondre à plusieurs Exam en base (un par niveau,
// selon le slug d'import) : on résout le bon slug selon fournisseur ET niveau.
const targetExamSlug = computed(() => {
  if (!selectedProvider.value) return null;

  const candidates = examsStore.catalog.filter((e) => e.provider === selectedProvider.value);
  if (!candidates.length) return null;
  if (!selectedLevel.value) return candidates[0]!.slug;

  const match = candidates.find((e) => e.levels?.some((l) => l.cefr_code === selectedLevel.value));
  return (match ?? candidates[0]!).slug;
});

watch(
  targetExamSlug,
  async (slug) => {
    if (!slug) return;
    await examsStore.fetchExamBySlug(slug);
  },
  { immediate: true },
);

const resetFilters = () => {
  selectedProvider.value = "";
  selectedLevel.value = "";
  examsStore.clearCurrentExam();
};

// ── Historique : géré par useSimulatorStore ──

const switchToResults = () => {
  activeTab.value = "resultats";
  if (!store.results.length) store.fetchMyResults();
};

const openResult = (result: SimulatorResultResponse) => {
  store.loadResultIntoCorrection(result);
  router.push(localePath(`/dashboard/simulateur/${result.subject_id}/resultats`));
};

const criteriaList = (result: SimulatorResultResponse) => {
  const criteria = (result.result_data?.criteria ?? []) as Array<{
    key: string;
    label: string;
    score: number;
    max_score: number;
    feedback?: string;
  }>;

  return criteria.map((c) => ({
    key: c.key,
    label: c.label,
    score: c.score,
    max: c.max_score,
    pct: c.max_score ? Math.round((c.score / c.max_score) * 100) : 0,
  }));
};

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

// Couleur d'identité par fournisseur, en transparence pour rester lisible en sombre
const providerTagClass = (p: string) =>
  ({
    goethe: "bg-blue-500/10 text-blue-600",
    telc: "bg-purple-500/10 text-purple-600",
    osd: "bg-orange-500/10 text-orange-600",
  })[p.toLowerCase()] ?? "bg-card-2 text-muted";

onMounted(async () => {
  if (!examsStore.catalog.length) await examsStore.fetchCatalog();

  if (!selectedProvider.value) {
    const telc = availableProviders.value.find((p) => p.toLowerCase() === "telc");
    selectedProvider.value = telc ?? availableProviders.value[0] ?? "";
  }
});
</script>