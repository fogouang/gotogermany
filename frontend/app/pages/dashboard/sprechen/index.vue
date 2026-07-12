<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">{{ t('sprechen.title') }}</h1>
      <p class="text-sm text-gray-500">{{ t('sprechen.subtitle') }}</p>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200">
      <button
        :class="[
          'px-5 py-3 text-sm font-semibold border-b-2 transition-colors',
          activeTab === 'sujets' ? 'border-teal-600 text-teal-700' : 'border-transparent text-gray-500 hover:text-gray-700',
        ]"
        @click="activeTab = 'sujets'"
      >
        <i class="pi pi-list-check mr-2" />{{ t('sprechen.tab_subjects') }}
      </button>
      <button
        :class="[
          'px-5 py-3 text-sm font-semibold border-b-2 transition-colors',
          activeTab === 'resultats' ? 'border-teal-600 text-teal-700' : 'border-transparent text-gray-500 hover:text-gray-700',
        ]"
        @click="switchToResults"
      >
        <i class="pi pi-history mr-2" />{{ t('sprechen.tab_results') }}
        <span v-if="results.length" class="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-teal-100 text-teal-700 font-bold">
          {{ results.length }}
        </span>
      </button>
    </div>

    <!-- TAB : Sujets -->
    <template v-if="activeTab === 'sujets'">
      <!-- Filtres provider (dérivés du vrai catalogue, pas de liste en dur) -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in availableProviders"
          :key="p"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedProvider === p ? 'bg-teal-600 text-white border-teal-600' : 'bg-white text-gray-600 border-gray-200 hover:border-teal-300',
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
            selectedLevel === l ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300',
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
      <div v-else-if="!sprechenSubjects.length" class="text-center py-16 bg-white rounded-xl border border-gray-100">
        <i class="pi pi-inbox text-4xl text-gray-300 mb-3 block" />
        <p class="font-medium text-gray-600">{{ t('sprechen.no_subjects_title') }}</p>
        <p class="text-sm text-gray-400 mb-4">{{ t('sprechen.no_subjects_subtitle') }}</p>
        <Button :label="t('sprechen.show_all')" icon="pi pi-refresh" @click="resetFilters" />
      </div>

      <!-- Grille sujets -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <NuxtLink
          v-for="subject in sprechenSubjects"
          :key="subject.id"
          :to="`/dashboard/sprechen/${subject.id}`"
          class="group bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-teal-200 transition-all flex flex-col gap-3"
        >
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-white text-xs font-bold bg-orange-500">
              <i class="pi pi-microphone" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors text-sm leading-snug">
                {{ subject.title }}
              </p>
            </div>
          </div>

          <p v-if="subject.preview" class="text-xs text-gray-500 line-clamp-2 leading-relaxed bg-gray-50 rounded-lg px-3 py-2">
            {{ subject.preview }}
          </p>

          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-2">
              <Tag :value="subject.provider.toUpperCase()" :class="providerTagClass(subject.provider)" />
              <Tag :value="subject.level" severity="info" />
              <span class="text-xs text-gray-400">
                {{ subject.teilCount }} {{ subject.teilCount > 1 ? t('sprechen.teile_plural') : t('sprechen.teil') }}
              </span>
            </div>
            <span class="text-xs text-teal-600 font-semibold flex items-center gap-1 group-hover:gap-2 transition-all">
              {{ t('sprechen.start') }}
              <i class="pi pi-arrow-right text-xs" />
            </span>
          </div>
        </NuxtLink>
      </div>
    </template>

    <!-- TAB : Historique -->
    <template v-else>
      <div v-if="loadingResults" class="flex justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <div v-else-if="!results.length" class="text-center py-16 bg-white rounded-xl border border-gray-100">
        <i class="pi pi-history text-4xl text-gray-300 mb-3 block" />
        <p class="font-medium text-gray-600">{{ t('sprechen.no_results_title') }}</p>
        <p class="text-sm text-gray-400 mb-4">{{ t('sprechen.no_results_subtitle') }}</p>
        <Button :label="t('sprechen.see_subjects')" icon="pi pi-list-check" @click="activeTab = 'sujets'" />
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div v-for="result in results" :key="result.session_id" class="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex flex-col gap-3">
          <div class="flex items-start gap-3">
            <div class="shrink-0 relative w-14 h-14">
              <svg class="w-14 h-14 -rotate-90" viewBox="0 0 56 56">
                <circle cx="28" cy="28" r="22" fill="none" stroke="#f3f4f6" stroke-width="6" />
                <circle
                  cx="28" cy="28" r="22" fill="none"
                  :stroke="result.passed ? '#22c55e' : '#f97316'"
                  stroke-width="6" stroke-linecap="round"
                  :stroke-dasharray="`${(result.total_score / result.total_max_score) * 138} 138`"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-xs font-extrabold text-gray-800 leading-none">
                  {{ Math.round((result.total_score / result.total_max_score) * 100) }}%
                </span>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 text-sm leading-snug">{{ result.subject_name }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(result.completed_at) }}</p>
              <div class="flex flex-wrap items-center gap-1.5 mt-1.5">
                <Tag :value="result.provider.toUpperCase()" :class="providerTagClass(result.provider)" />
                <Tag :value="result.level.toUpperCase()" severity="info" />
                <Tag :value="result.passed ? 'Bestanden ✓' : 'Nicht bestanden'" :severity="result.passed ? 'success' : 'danger'" />
              </div>
            </div>
          </div>
          <span class="text-xs font-bold" :class="result.passed ? 'text-green-600' : 'text-orange-500'">
            {{ result.total_score }} / {{ result.total_max_score }} pts
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { SprechenSimulatorService, OpenAPI } from '#shared/api';
import type { SessionHistoryItem } from '#shared/api';

definePageMeta({ layout: 'dashboard', middleware: 'auth' });

const { t } = useI18n();
useHead({ title: t('sprechen.page_title') });

const examsStore = useExamsStore();

const activeTab = ref<'sujets' | 'resultats'>('sujets');
const selectedProvider = ref('');
const selectedLevel = ref('');

// ---------------------------------------------------------------------
// Sujets — dérivés de useExamsStore, même pattern que
// examens/[slug].vue : fetchExamBySlug() charge l'arbre complet, on
// filtre ensuite côté client pour ne garder que les sujets qui ont un
// module "sprechen".
// ---------------------------------------------------------------------

const availableProviders = computed(() => {
  const set = new Set(examsStore.catalog.map((e) => e.provider));
  return [...set];
});

const availableLevels = computed(() => {
  const set = new Set<string>();
  examsStore.catalog.forEach((e) => e.levels?.forEach((l) => set.add(l.cefr_code)));
  return [...set];
});

interface SprechenSubjectCard {
  id: string;
  provider: string;
  level: string;
  title: string;
  preview?: string;
  teilCount: number;
}

const sprechenSubjects = computed<SprechenSubjectCard[]>(() => {
  const exam = examsStore.currentExam;
  if (!exam) return [];

  const cards: SprechenSubjectCard[] = [];
  for (const level of exam.levels ?? []) {
    if (selectedLevel.value && level.cefr_code !== selectedLevel.value) continue;

    for (const subject of level.subjects ?? []) {
      const sprechenModule = (subject.modules ?? []).find((m) => m.slug === 'sprechen');
      if (!sprechenModule) continue;

      const firstTeil = sprechenModule.teile?.[0];
      cards.push({
        id: subject.id,
        provider: exam.provider,
        level: level.cefr_code,
        title: subject.name || `${t('sprechen.subject_default')} ${subject.subject_number}`,
        preview: firstTeil?.instructions ?? undefined,
        teilCount: sprechenModule.teile?.length ?? 0,
      });
    }
  }
  return cards;
});

// Loads the full tree for the selected provider's exam whenever the
// provider filter changes. One Exam per provider is assumed (matches
// the exam_id+cefr_code unique constraint seen on Level) — adjust if
// a provider can span multiple Exam rows.
watch(selectedProvider, async (provider) => {
  if (!provider) return;
  const exam = examsStore.catalog.find((e) => e.provider === provider);
  if (exam) await examsStore.fetchExamBySlug(exam.slug);
});

const resetFilters = () => {
  // Only the level filter resets — clearing the provider too would
  // put us right back in the empty state the auto-select fix above
  // exists to avoid. Falls back to the first available provider if
  // none is selected yet (e.g. catalog was still loading).
  selectedLevel.value = '';
  if (!selectedProvider.value && availableProviders.value.length) {
    selectedProvider.value = availableProviders.value[0]!;
  }
};

// ---------------------------------------------------------------------
// Historique — le seul appel vraiment spécifique à Sprechen
// ---------------------------------------------------------------------

const results = ref<SessionHistoryItem[]>([]);
const loadingResults = ref(false);

async function fetchMyResults() {
  const config = useRuntimeConfig();
  OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001';
  const tokenCookie = useCookie('access_token');
  OpenAPI.TOKEN = tokenCookie.value ?? undefined;

  loadingResults.value = true;
  try {
    const response = await SprechenSimulatorService.getSprechenHistoryApiV1SprechenSimulatorHistoryGet(
      undefined,
      undefined,
      20,
      0,
      tokenCookie.value ?? undefined
    );
    results.value = response.items;
  } catch (error) {
    console.error('Fetch sprechen history error:', error);
  } finally {
    loadingResults.value = false;
  }
}

const switchToResults = () => {
  activeTab.value = 'resultats';
  if (!results.value.length) fetchMyResults();
};

// ---------------------------------------------------------------------

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

const providerTagClass = (p: string) =>
  ({
    goethe: 'bg-blue-100 text-blue-700',
    telc: 'bg-purple-100 text-purple-700',
    osd: 'bg-orange-100 text-orange-700',
  })[p] ?? 'bg-gray-100 text-gray-600';

onMounted(async () => {
  if (!examsStore.catalog.length) await examsStore.fetchCatalog();
  // Auto-select the first provider so the list isn't empty on first
  // load — requiring a click before showing anything reads as "no
  // subjects exist" rather than "pick a filter".
  if (!selectedProvider.value && availableProviders.value.length) {
    selectedProvider.value = availableProviders.value[0]!;
  }
});
</script>