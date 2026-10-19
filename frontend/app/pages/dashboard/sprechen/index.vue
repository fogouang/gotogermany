<!--sprechen/index.vue-->
<template>
  <div class="space-y-6 pb-10">
    <!-- En-tête -->
    <div>
      <h1 class="text-2xl font-bold text-ink">{{ t("sprechen.title") }}</h1>
      <p class="text-sm text-muted">{{ t("sprechen.subtitle") }}</p>
    </div>

    <!-- Onglets -->
    <div class="flex border-b border-line">
      <button
        type="button"
        :class="tabClass('sujets')"
        @click="activeTab = 'sujets'"
      >
        <i class="pi pi-list-check mr-2" />{{ t("sprechen.tab_subjects") }}
      </button>
      <button
        type="button"
        :class="tabClass('resultats')"
        @click="switchToResults"
      >
        <i class="pi pi-history mr-2" />{{ t("sprechen.tab_results") }}
        <span
          v-if="results.length"
          class="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-primary/10 text-primary font-bold"
        >
          {{ results.length }}
        </span>
      </button>
    </div>

    <!-- ── Sujets ── -->
    <template v-if="activeTab === 'sujets'">
      <!-- Filtres (dérivés du catalogue) -->
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="p in availableProviders"
          :key="p"
          type="button"
          :class="chipClass(selectedProvider === p)"
          @click="selectedProvider = selectedProvider === p ? '' : p"
        >
          {{ info(p).name }}
        </button>
        <span class="w-px h-6 bg-line mx-1" />
        <button
          v-for="l in availableLevels"
          :key="l"
          type="button"
          :class="chipClass(selectedLevel === l)"
          @click="selectedLevel = selectedLevel === l ? '' : l"
        >
          {{ l }}
        </button>
      </div>

      <div v-if="examsStore.loading" class="flex justify-center py-12">
        <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
      </div>

      <div
        v-else-if="!sprechenSubjects.length"
        class="text-center py-16 bg-card border border-line rounded-card"
      >
        <i class="pi pi-inbox text-4xl text-faint mb-3 block" />
        <p class="font-medium text-ink">
          {{ t("sprechen.no_subjects_title") }}
        </p>
        <p class="text-sm text-muted mb-4">
          {{ t("sprechen.no_subjects_subtitle") }}
        </p>
        <Button
          :label="t('sprechen.show_all')"
          icon="pi pi-refresh"
          @click="resetFilters"
        />
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <NuxtLink
          v-for="subject in sprechenSubjects"
          :key="subject.id"
          :to="localePath(`/dashboard/sprechen/apercu/${subject.id}`)"
          class="group bg-card border border-line rounded-card p-5 hover:border-primary/40 hover:shadow-soft transition-all flex flex-col gap-3"
        >
          <div class="flex items-start gap-3">
            <span
              class="w-10 h-10 rounded-leaf flex items-center justify-center shrink-0 bg-primary/10 text-primary"
            >
              <i class="pi pi-microphone" />
            </span>
            <p
              class="flex-1 min-w-0 font-semibold text-ink group-hover:text-primary transition-colors text-sm leading-snug"
            >
              {{ subject.title }}
            </p>
          </div>

          <ul
            v-if="subject.teile.length"
            class="space-y-1 rounded-leaf bg-card-2 px-3 py-2"
          >
            <li
              v-for="teil in subject.teile"
              :key="teil.number"
              class="flex items-baseline gap-2 text-xs"
            >
              <span class="shrink-0 font-semibold text-faint"
                >Teil {{ teil.number }}</span
              >
              <span class="min-w-0 truncate text-muted">
                {{ teil.name
                }}<template v-if="teil.topic">
                  ·
                  <span class="font-medium text-ink">{{
                    teil.topic
                  }}</span></template
                >
              </span>
            </li>
          </ul>

          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'text-[11px] font-semibold px-2 py-0.5 rounded-full',
                  info(subject.provider).badge,
                ]"
              >
                {{ info(subject.provider).name }}
              </span>
              <span
                class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-card-2 border border-line text-ink"
              >
                {{ subject.level }}
              </span>
              <span class="text-xs text-muted">
                {{ subject.teilCount }}
                {{
                  subject.teilCount > 1
                    ? t("sprechen.teile_plural")
                    : t("sprechen.teil")
                }}
              </span>
            </div>
            <span
              class="text-xs text-primary font-semibold flex items-center gap-1 group-hover:gap-2 transition-all"
            >
              {{ t("sprechen.view_subject") }}
              <i class="pi pi-arrow-right text-xs" />
            </span>
          </div>
        </NuxtLink>
      </div>
    </template>

    <!-- ── Historique ── -->
    <template v-else>
      <div v-if="loadingResults" class="flex justify-center py-12">
        <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
      </div>

      <div
        v-else-if="!results.length"
        class="text-center py-16 bg-card border border-line rounded-card"
      >
        <i class="pi pi-history text-4xl text-faint mb-3 block" />
        <p class="font-medium text-ink">{{ t("sprechen.no_results_title") }}</p>
        <p class="text-sm text-muted mb-4">
          {{ t("sprechen.no_results_subtitle") }}
        </p>
        <Button
          :label="t('sprechen.see_subjects')"
          icon="pi pi-list-check"
          @click="activeTab = 'sujets'"
        />
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="result in results"
          :key="result.session_id"
          class="bg-card border border-line rounded-card p-5 flex flex-col gap-3"
        >
          <div class="flex items-start gap-3">
            <div class="shrink-0 relative w-14 h-14">
              <svg class="w-14 h-14 -rotate-90" viewBox="0 0 56 56">
                <circle
                  cx="28"
                  cy="28"
                  r="22"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="6"
                  class="text-line"
                />
                <circle
                  cx="28"
                  cy="28"
                  r="22"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="6"
                  stroke-linecap="round"
                  :class="result.passed ? 'text-emerald-500' : 'text-amber-500'"
                  :stroke-dasharray="`${(percentOf(result) / 100) * 138} 138`"
                />
              </svg>
              <span
                class="absolute inset-0 flex items-center justify-center text-xs font-extrabold text-ink tabular-nums"
              >
                {{ percentOf(result) }}%
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-ink text-sm leading-snug">
                {{ result.subject_name }}
              </p>
              <p class="text-xs text-muted mt-0.5">
                {{ formatDate(result.completed_at) }}
              </p>
              <div class="flex flex-wrap items-center gap-1.5 mt-1.5">
                <span
                  :class="[
                    'text-[11px] font-semibold px-2 py-0.5 rounded-full',
                    info(result.provider).badge,
                  ]"
                >
                  {{ info(result.provider).name }}
                </span>
                <span
                  class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-card-2 border border-line text-ink"
                >
                  {{ result.level.toUpperCase() }}
                </span>
                <Tag
                  :value="
                    result.passed
                      ? t('sprechen_subject.passed')
                      : t('sprechen_subject.not_passed')
                  "
                  :severity="result.passed ? 'success' : 'danger'"
                />
              </div>
            </div>
          </div>
          <span
            :class="[
              'text-xs font-bold tabular-nums',
              result.passed ? 'text-emerald-600' : 'text-amber-600',
            ]"
          >
            {{ result.total_score }} / {{ result.total_max_score }}
            {{ t("sprechen_subject.points") }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { SprechenSimulatorService, OpenAPI } from "#shared/api";
import type { SessionHistoryItem } from "#shared/api";

definePageMeta({ layout: "dashboard" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const { info } = useProviders();
useHead({ title: t("sprechen.page_title") });

const examsStore = useExamsStore();

const activeTab = ref<"sujets" | "resultats">("sujets");
const selectedProvider = ref("");
const selectedLevel = ref("");

const ORAL_SLUGS = ["sprechen", "muendlicher_ausdruck", "mündlicher_ausdruck"];

const tabClass = (tab: "sujets" | "resultats") => [
  "px-5 py-3 text-sm font-semibold border-b-2 transition-colors",
  activeTab.value === tab
    ? "border-primary text-primary"
    : "border-transparent text-muted hover:text-ink",
];

const chipClass = (active: boolean) => [
  "px-4 py-1.5 rounded-full text-sm font-medium border transition-colors",
  active
    ? "bg-primary text-white border-primary"
    : "bg-card text-ink border-line hover:border-primary/40",
];

// ── Sujets : arbre de l'examen filtré sur les sujets ayant un module oral ──

const availableProviders = computed(() => [
  ...new Set(examsStore.catalog.map((e) => e.provider)),
]);

const availableLevels = computed(() => {
  const set = new Set<string>();
  examsStore.catalog.forEach((e) =>
    e.levels?.forEach((l) => set.add(l.cefr_code)),
  );
  return [...set];
});

interface SprechenSubjectCard {
  id: string;
  provider: string;
  level: string;
  title: string;
  teile: { number: number; name: string; topic: string | null }[];
  teilCount: number;
}

const sprechenSubjects = computed<SprechenSubjectCard[]>(() => {
  const exam = examsStore.currentExam;
  if (!exam) return [];

  const cards: SprechenSubjectCard[] = [];
  for (const level of exam.levels ?? []) {
    if (selectedLevel.value && level.cefr_code !== selectedLevel.value)
      continue;

    for (const subject of level.subjects ?? []) {
      const sprechenModule = (subject.modules ?? []).find((m) =>
        ORAL_SLUGS.includes(m.slug?.trim().toLowerCase()),
      );
      if (!sprechenModule) continue;

      const teile = [...(sprechenModule.teile ?? [])]
        .sort((a, b) => a.teil_number - b.teil_number)
        .map((teil) => {
          const config = (teil.config ?? {}) as Record<string, unknown>;
          const topic = config.topic ?? config.thema ?? config.title;
          return {
            number: teil.teil_number,
            name:
              typeof config.name === "string"
                ? config.name
                : `Teil ${teil.teil_number}`,
            topic: typeof topic === "string" ? topic : null,
          };
        });

      cards.push({
        id: subject.id,
        provider: exam.provider,
        level: level.cefr_code,
        title:
          subject.name ||
          `${t("sprechen.subject_default")} ${subject.subject_number}`,
        teile,
        teilCount: teile.length,
      });
    }
  }
  return cards;
});

// Un fournisseur peut avoir plusieurs Exam (un par niveau) : on choisit le bon slug
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
    if (slug) await examsStore.fetchExamBySlug(slug);
  },
  { immediate: true },
);

const resetFilters = () => {
  selectedProvider.value = "";
  selectedLevel.value = "";
  examsStore.clearCurrentExam();
};

// ── Historique du simulateur ──────────────────────────

const results = ref<SessionHistoryItem[]>([]);
const loadingResults = ref(false);

const percentOf = (r: SessionHistoryItem) =>
  r.total_max_score ? Math.round((r.total_score / r.total_max_score) * 100) : 0;

async function fetchMyResults() {
  const config = useRuntimeConfig();
  OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
  const tokenCookie = useCookie("access_token");
  OpenAPI.TOKEN = tokenCookie.value ?? undefined;

  loadingResults.value = true;
  try {
    const response =
      await SprechenSimulatorService.getSprechenHistoryApiV1SprechenSimulatorHistoryGet(
        undefined,
        undefined,
        20,
        0,
        tokenCookie.value ?? undefined,
      );
    results.value = response.items;
  } catch (error) {
    console.error("Fetch sprechen history error:", error);
  } finally {
    loadingResults.value = false;
  }
}

const switchToResults = () => {
  activeTab.value = "resultats";
  if (!results.value.length) fetchMyResults();
};

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

onMounted(async () => {
  if (!examsStore.catalog.length) await examsStore.fetchCatalog();

  // TELC par défaut, sinon la liste reste vide tant qu'aucun filtre n'est choisi
  if (!selectedProvider.value) {
    const telc = availableProviders.value.find(
      (p) => p.toLowerCase() === "telc",
    );
    selectedProvider.value = telc ?? availableProviders.value[0] ?? "";
  }
});
</script>
