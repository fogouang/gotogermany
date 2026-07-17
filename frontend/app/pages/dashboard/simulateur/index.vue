<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t("simulator.title") }}
      </h1>
      <p class="text-sm text-gray-500">{{ t("simulator.subtitle") }}</p>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200">
      <button
        :class="[
          'px-5 py-3 text-sm font-semibold border-b-2 transition-colors',
          activeTab === 'sujets'
            ? 'border-teal-600 text-teal-700'
            : 'border-transparent text-gray-500 hover:text-gray-700',
        ]"
        @click="activeTab = 'sujets'"
      >
        <i class="pi pi-list-check mr-2"></i>{{ t("simulator.tab_subjects") }}
      </button>
      <button
        :class="[
          'px-5 py-3 text-sm font-semibold border-b-2 transition-colors',
          activeTab === 'resultats'
            ? 'border-teal-600 text-teal-700'
            : 'border-transparent text-gray-500 hover:text-gray-700',
        ]"
        @click="switchToResults"
      >
        <i class="pi pi-history mr-2"></i>{{ t("simulator.tab_results") }}
        <span
          v-if="store.results.length"
          class="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-teal-100 text-teal-700 font-bold"
        >
          {{ store.results.length }}
        </span>
      </button>
    </div>

    <!-- TAB : Sujets -->
    <template v-if="activeTab === 'sujets'">
      <!-- Filtres provider/level (dérivés du vrai catalogue, pas de liste en dur) -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in availableProviders"
          :key="p"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedProvider === p
              ? 'bg-teal-600 text-white border-teal-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-teal-300',
          ]"
          @click="selectedProvider = selectedProvider === p ? '' : p"
        >
          {{ p.toUpperCase() }}
        </button>
        <div class="w-px bg-gray-200 mx-1" />
        <button
          v-for="l in availableLevels"
          :key="l"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedLevel === l
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300',
          ]"
          @click="selectedLevel = selectedLevel === l ? '' : l"
        >
          {{ l }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="examsStore.loading" class="flex justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <!-- Vide -->
      <div
        v-else-if="!simulatorSubjects.length"
        class="text-center py-16 bg-white rounded-xl border border-gray-100"
      >
        <i class="pi pi-inbox text-4xl text-gray-300 mb-3 block"></i>
        <p class="font-medium text-gray-600">
          {{ t("simulator.no_subjects_title") }}
        </p>
        <p class="text-sm text-gray-400 mb-4">
          {{ t("simulator.no_subjects_subtitle") }}
        </p>
        <Button
          :label="t('simulator.show_all')"
          icon="pi pi-refresh"
          @click="resetFilters"
        />
      </div>

      <!-- Grille sujets — 1 col mobile, 2 col desktop -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <NuxtLink
          v-for="subject in simulatorSubjects"
          :key="subject.id"
          :to="`/dashboard/simulateur/${subject.id}`"
          class="group bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-teal-200 transition-all flex flex-col gap-3"
        >
          <!-- Header card -->
          <div class="flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-white text-xs font-bold"
              :class="providerBg(subject.provider)"
            >
              {{ subject.provider.slice(0, 2).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p
                class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors text-sm leading-snug"
              >
                {{ subject.title }}
              </p>
            </div>
          </div>

          <!-- Scénario -->
          <p
            v-if="subject.preview"
            class="text-xs text-gray-500 line-clamp-2 leading-relaxed bg-gray-50 rounded-lg px-3 py-2"
          >
            {{ subject.preview }}
          </p>

          <!-- Footer card -->
          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-2">
              <Tag
                :value="subject.provider.toUpperCase()"
                :class="providerTagClass(subject.provider)"
              />
              <Tag :value="subject.level.toUpperCase()" severity="info" />
              <span class="text-xs text-gray-400">
                {{ subject.taskCount }}
                {{
                  subject.taskCount > 1
                    ? t("simulator.tasks_plural")
                    : t("simulator.tasks")
                }}
              </span>
            </div>
            <span
              class="text-xs text-teal-600 font-semibold flex items-center gap-1 group-hover:gap-2 transition-all"
            >
              {{ t("simulator.start") }}
              <i class="pi pi-arrow-right text-xs"></i>
            </span>
          </div>
        </NuxtLink>
      </div>
    </template>

    <!-- TAB : Mes corrections (inchangé — reste sur le store dédié) -->
    <template v-else>
      <div v-if="store.loadingResults" class="flex justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <div
        v-else-if="!store.results.length"
        class="text-center py-16 bg-white rounded-xl border border-gray-100"
      >
        <i class="pi pi-history text-4xl text-gray-300 mb-3 block"></i>
        <p class="font-medium text-gray-600">
          {{ t("simulator.no_results_title") }}
        </p>
        <p class="text-sm text-gray-400 mb-4">
          {{ t("simulator.no_results_subtitle") }}
        </p>
        <Button
          :label="t('simulator.see_subjects')"
          icon="pi pi-list-check"
          @click="activeTab = 'sujets'"
        />
      </div>

      <!-- Grille résultats — 1 col mobile, 2 col desktop -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="result in store.results"
          :key="result.id"
          class="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-teal-200 transition-all cursor-pointer flex flex-col gap-3"
          @click="openResult(result)"
        >
          <!-- Header résultat -->
          <div class="flex items-start gap-3">
            <!-- Score circulaire -->
            <div class="shrink-0 relative w-14 h-14">
              <svg class="w-14 h-14 -rotate-90" viewBox="0 0 56 56">
                <circle
                  cx="28"
                  cy="28"
                  r="22"
                  fill="none"
                  stroke="#f3f4f6"
                  stroke-width="6"
                />
                <circle
                  cx="28"
                  cy="28"
                  r="22"
                  fill="none"
                  :stroke="result.passed ? '#22c55e' : '#f97316'"
                  stroke-width="6"
                  stroke-linecap="round"
                  :stroke-dasharray="`${(result.score_percentage / 100) * 138} 138`"
                />
              </svg>
              <div
                class="absolute inset-0 flex flex-col items-center justify-center"
              >
                <span class="text-xs font-extrabold text-gray-800 leading-none"
                  >{{ Math.round(result.score_percentage) }}%</span
                >
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm leading-snug">
                {{ result.subject_title || t("simulator.deleted_subject") }}
              </p>
              <p class="text-xs text-gray-400 mt-0.5">
                {{ formatDate(result.created_at) }}
              </p>
              <div class="flex flex-wrap items-center gap-1.5 mt-1.5">
                <Tag
                  :value="result.provider.toUpperCase()"
                  :class="['text-xs', providerTagClass(result.provider)]"
                />
                <Tag :value="result.level.toUpperCase()" severity="info" />
                <Tag
                  :value="result.passed ? 'Bestanden ✓' : 'Nicht bestanden'"
                  :severity="result.passed ? 'success' : 'danger'"
                />
              </div>
            </div>
          </div>

          <!-- Score détaillé — mini barres -->
          <div class="space-y-1.5 bg-gray-50 rounded-lg px-3 py-2.5">
            <div
              v-for="c in criteriaList(result)"
              :key="c.key"
              class="flex items-center gap-2"
            >
              <span class="text-xs text-gray-400 w-20 shrink-0">{{
                c.label
              }}</span>
              <div class="flex-1 bg-gray-200 rounded-full h-1">
                <div
                  class="h-1 rounded-full transition-all"
                  :class="
                    c.pct >= 70
                      ? 'bg-green-500'
                      : c.pct >= 50
                        ? 'bg-orange-400'
                        : 'bg-red-400'
                  "
                  :style="{ width: c.pct + '%' }"
                />
              </div>
              <span class="text-xs text-gray-500 w-8 text-right shrink-0"
                >{{ c.score }}/{{ c.max }}</span
              >
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between pt-1">
            <span
              class="text-xs font-bold"
              :class="result.passed ? 'text-green-600' : 'text-orange-500'"
            >
              {{ result.overall_score }} / {{ result.max_score }} pts
            </span>
            <span
              class="text-xs text-teal-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all"
            >
              {{ t("simulator.see") }} <i class="pi pi-arrow-right text-xs"></i>
            </span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from "~/stores/simulator";
import type { SimulatorResultResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
useHead({ title: t("simulator.page_title") });

const examsStore = useExamsStore();
const store = useSimulatorStore(); // reste utilisé pour "Mes corrections" uniquement

const activeTab = ref<"sujets" | "resultats">("sujets");
const selectedProvider = ref("");
const selectedLevel = ref("");

// ---------------------------------------------------------------------
// Sujets — dérivés de useExamsStore, exactement comme la page Sprechen :
// fetchExamBySlug() charge l'arbre complet, on filtre ensuite côté
// client pour ne garder que les sujets qui ont un module "schreiben".
// ---------------------------------------------------------------------

const availableProviders = computed(() => {
  const set = new Set(examsStore.catalog.map((e) => e.provider));
  return [...set];
});

const availableLevels = computed(() => {
  const set = new Set<string>();
  examsStore.catalog.forEach((e) =>
    e.levels?.forEach((l) => set.add(l.cefr_code)),
  );
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
    if (selectedLevel.value && level.cefr_code !== selectedLevel.value)
      continue;

    for (const subject of level.subjects ?? []) {
      const schreibenModule = (subject.modules ?? []).find(
        (m) => m.slug === "schreiben",
      );
      if (!schreibenModule) continue;

      const firstTeil = schreibenModule.teile?.[0];
      cards.push({
        id: subject.id,
        provider: exam.provider,
        level: level.cefr_code,
        title:
          subject.name ||
          `${t("simulator.subject_default")} ${subject.subject_number}`,
        preview: firstTeil?.instructions ?? undefined,
        taskCount: schreibenModule.teile?.length ?? 0,
      });
    }
  }
  return cards;
});

// Résout le bon Exam (slug) à charger selon provider ET niveau — un
// provider peut correspondre à plusieurs Exam distincts en base (un
// par niveau, selon le slug utilisé à l'import), pas un seul Exam
// avec plusieurs Level.
const targetExamSlug = computed(() => {
  if (!selectedProvider.value) return null;

  const candidates = examsStore.catalog.filter(
    (e) => e.provider === selectedProvider.value,
  );
  if (!candidates.length) return null;

  if (!selectedLevel.value) return candidates[0]!.slug;

  const match = candidates.find((e) =>
    e.levels?.some((l) => l.cefr_code === selectedLevel.value),
  );
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

// ---------------------------------------------------------------------
// Historique — reste géré par useSimulatorStore (données de résultats
// spécifiques, pas du catalogue d'examens)
// ---------------------------------------------------------------------

const switchToResults = () => {
  activeTab.value = "resultats";
  if (!store.results.length) store.fetchMyResults();
};

const openResult = (result: SimulatorResultResponse) => {
  store.loadResultIntoCorrection(result);
  router.push(`/dashboard/simulateur/${result.subject_id}/resultats`);
};

const criteriaList = (result: SimulatorResultResponse) => {
  const d = result.result_data;
  const max = _getCriteriaMax(result.provider, result.level);
  const toNum = (v: any): number => Number(v) || 0;
  return [
    {
      key: "aufgabe",
      label: "Aufgabe",
      score: toNum(d.aufgabe_score),
      max: max.aufgabe,
      pct: Math.round((toNum(d.aufgabe_score) / max.aufgabe) * 100),
    },
    {
      key: "kohaesion",
      label: "Kohäsion",
      score: toNum(d.kohaesion_score),
      max: max.kohaesion,
      pct: Math.round((toNum(d.kohaesion_score) / max.kohaesion) * 100),
    },
    {
      key: "wortschatz",
      label: "Wortschatz",
      score: toNum(d.wortschatz_score),
      max: max.wortschatz,
      pct: Math.round((toNum(d.wortschatz_score) / max.wortschatz) * 100),
    },
    {
      key: "grammatik",
      label: "Grammatik",
      score: toNum(d.grammatik_score),
      max: max.grammatik,
      pct: Math.round((toNum(d.grammatik_score) / max.grammatik) * 100),
    },
  ];
};

const _getCriteriaMax = (provider: string, level: string) => {
  if (provider === "telc")
    return { aufgabe: 15, kohaesion: 10, wortschatz: 10, grammatik: 10 };
  if (provider === "osd" && level === "b2")
    return { aufgabe: 28, kohaesion: 22, wortschatz: 22, grammatik: 18 };
  return { aufgabe: 30, kohaesion: 25, wortschatz: 25, grammatik: 20 };
};

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

const providerBg = (p: string) =>
  ({ goethe: "bg-blue-500", telc: "bg-purple-500", osd: "bg-orange-500" })[p] ??
  "bg-gray-400";
const providerTagClass = (p: string) =>
  ({
    goethe: "bg-blue-100 text-blue-700",
    telc: "bg-purple-100 text-purple-700",
    osd: "bg-orange-100 text-orange-700",
  })[p] ?? "bg-gray-100 text-gray-600";

const router = useRouter();
</script>
