<template>
  <div class="space-y-6">

    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">{{ t('simulator.title') }}</h1>
      <p class="text-sm text-gray-500">{{ t('simulator.subtitle') }}</p>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200">
      <button
        :class="['px-5 py-3 text-sm font-semibold border-b-2 transition-colors',
          activeTab === 'sujets' ? 'border-teal-600 text-teal-700' : 'border-transparent text-gray-500 hover:text-gray-700']"
        @click="switchTab('sujets')"
      >
        <i class="pi pi-list-check mr-2"></i>{{ t('simulator.tab_subjects') }}
      </button>
      <button
        :class="['px-5 py-3 text-sm font-semibold border-b-2 transition-colors',
          activeTab === 'resultats' ? 'border-teal-600 text-teal-700' : 'border-transparent text-gray-500 hover:text-gray-700']"
        @click="switchTab('resultats')"
      >
        <i class="pi pi-history mr-2"></i>{{ t('simulator.tab_results') }}
        <span v-if="store.results.length" class="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-teal-100 text-teal-700 font-bold">
          {{ store.results.length }}
        </span>
      </button>
    </div>

    <!-- TAB : Sujets -->
    <template v-if="activeTab === 'sujets'">

      <!-- Filtres -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in providers" :key="p.value"
          :class="['px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedProvider === p.value
              ? 'bg-teal-600 text-white border-teal-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-teal-300']"
          @click="toggleProvider(p.value)"
        >{{ p.label }}</button>

        <div class="w-px bg-gray-200 mx-1" />

        <button
          v-for="l in levels" :key="l.value"
          :class="['px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedLevel === l.value
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300']"
          @click="toggleLevel(l.value)"
        >{{ l.label }}</button>
      </div>

      <!-- Loading -->
      <div v-if="store.loading" class="flex justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <!-- Vide -->
      <div v-else-if="!store.subjects.length" class="text-center py-16 bg-white rounded-xl border border-gray-100">
        <i class="pi pi-inbox text-4xl text-gray-300 mb-3 block"></i>
        <p class="font-medium text-gray-600">{{ t('simulator.no_subjects_title') }}</p>
        <p class="text-sm text-gray-400 mb-4">{{ t('simulator.no_subjects_subtitle') }}</p>
        <Button :label="t('simulator.show_all')" icon="pi pi-refresh" @click="resetFilters" />
      </div>

      <!-- Liste sujets -->
      <div v-else class="space-y-3">
        <NuxtLink
          v-for="subject in store.subjects" :key="subject.id"
          :to="`/dashboard/simulateur/${subject.id}`"
          class="group bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-teal-200 transition-all flex items-start justify-between gap-4"
        >
          <div class="flex items-start gap-4">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 text-white text-xs font-bold"
              :class="providerBg(subject.provider)"
            >
              {{ subject.provider.slice(0, 2).toUpperCase() }}
            </div>
            <div>
              <p class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors">{{ subject.title }}</p>
              <p v-if="subject.description" class="text-xs text-gray-400 mt-0.5 line-clamp-1">{{ subject.description }}</p>
              <p class="text-xs text-gray-400 mt-1 line-clamp-1">{{ subject.tasks[0]?.scenario }}</p>
              <div class="flex items-center gap-2 mt-2">
                <Tag :value="subject.provider.toUpperCase()" :class="providerTagClass(subject.provider)" />
                <Tag :value="subject.level.toUpperCase()" severity="info" />
                <span class="text-xs text-gray-400">
                  {{ subject.tasks.length }} {{ subject.tasks.length > 1 ? t('simulator.tasks_plural') : t('simulator.tasks') }}
                </span>
              </div>
            </div>
          </div>
          <div class="shrink-0 flex items-center gap-1 text-teal-600 text-sm font-medium group-hover:gap-2 transition-all">
            {{ t('simulator.start') }} <i class="pi pi-arrow-right text-xs"></i>
          </div>
        </NuxtLink>
      </div>
    </template>

    <!-- TAB : Mes corrections -->
    <template v-else>
      <div v-if="store.loadingResults" class="flex justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <div v-else-if="!store.results.length" class="text-center py-16 bg-white rounded-xl border border-gray-100">
        <i class="pi pi-history text-4xl text-gray-300 mb-3 block"></i>
        <p class="font-medium text-gray-600">{{ t('simulator.no_results_title') }}</p>
        <p class="text-sm text-gray-400 mb-4">{{ t('simulator.no_results_subtitle') }}</p>
        <Button :label="t('simulator.see_subjects')" icon="pi pi-list-check" @click="switchTab('sujets')" />
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="result in store.results" :key="result.id"
          class="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-4">
              <div
                class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                :class="result.passed ? 'bg-green-500' : 'bg-orange-500'"
              >
                {{ Math.round(result.score_percentage) }}%
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ result.subject_title || t('simulator.deleted_subject') }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(result.created_at) }}</p>
                <div class="flex items-center gap-2 mt-2">
                  <Tag :value="result.provider.toUpperCase()" :class="providerTagClass(result.provider)" />
                  <Tag :value="result.level.toUpperCase()" severity="info" />
                  <Tag
                    :value="result.passed ? 'Bestanden ✓' : 'Nicht bestanden'"
                    :severity="result.passed ? 'success' : 'danger'"
                  />
                  <span class="text-xs text-gray-500 font-medium">{{ result.overall_score }} / {{ result.max_score }} pts</span>
                </div>
              </div>
            </div>
            <Button
              :label="t('simulator.see')" icon="pi pi-eye"
              size="small" outlined severity="secondary"
              @click="openResult(result)"
            />
          </div>
        </div>
      </div>
    </template>

    <!-- Dialog résultat -->
    <Dialog
      v-model:visible="resultDialog"
      :header="t('simulator.dialog_title')"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '600px' }"
    >
      <div v-if="selectedResult" class="space-y-4 mt-2">

        <!-- Score global -->
        <div
          class="rounded-xl p-5 text-white text-center"
          :class="selectedResult.passed ? 'bg-green-500' : 'bg-orange-500'"
        >
          <p class="text-3xl font-extrabold">{{ Math.round(selectedResult.score_percentage) }}%</p>
          <p class="font-semibold mt-1">{{ selectedResult.passed ? 'Prüfung bestanden ✓' : 'Nicht bestanden' }}</p>
          <p class="text-sm opacity-80 mt-0.5">{{ selectedResult.overall_score }} / {{ selectedResult.max_score }} points</p>
        </div>

        <!-- Appréciation -->
        <div v-if="selectedResult.result_data.appreciation" class="bg-gray-50 rounded-xl p-4">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{{ t('simulator.appreciation') }}</p>
          <p class="text-sm text-gray-700 leading-relaxed">{{ selectedResult.result_data.appreciation }}</p>
        </div>

        <!-- Critères -->
        <div class="space-y-2">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ t('simulator.criteria_scores') }}</p>
          <div v-for="c in criteriaList(selectedResult)" :key="c.key" class="flex items-center gap-3">
            <span class="text-xs text-gray-600 w-32 shrink-0">{{ c.label }}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-1.5">
              <div
                class="h-1.5 rounded-full transition-all"
                :class="c.pct >= 70 ? 'bg-green-500' : c.pct >= 50 ? 'bg-orange-400' : 'bg-red-400'"
                :style="{ width: c.pct + '%' }"
              />
            </div>
            <span class="text-xs font-bold text-gray-700 w-12 text-right">{{ c.score }} / {{ c.max }}</span>
          </div>
        </div>

        <!-- Conseils -->
        <div v-if="selectedResult.result_data.suggestions?.length" class="space-y-2">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{{ t('simulator.tips') }}</p>
          <ul class="space-y-1">
            <li v-for="(s, i) in selectedResult.result_data.suggestions" :key="i" class="flex items-start gap-2 text-sm text-gray-700">
              <span class="w-5 h-5 rounded-full bg-yellow-100 text-yellow-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                {{ Number(i) + 1 }}
              </span>
              {{ s }}
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <Button :label="t('simulator.close')" text @click="resultDialog = false" />
        <Button
          v-if="selectedResult"
          :label="t('simulator.redo')" icon="pi pi-refresh"
          @click="router.push(`/dashboard/simulateur/${selectedResult.subject_id}`); resultDialog = false"
        />
      </template>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from '~/stores/simulator'
import type { SimulatorResultResponse } from '#shared/api'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const { t } = useI18n()
useHead({ title: t('simulator.page_title') })

const store  = useSimulatorStore()
const router = useRouter()

const activeTab      = ref<'sujets' | 'resultats'>('sujets')
const resultDialog   = ref(false)
const selectedResult = ref<SimulatorResultResponse | null>(null)

const providers = computed(() => [
  { label: t('simulator.all'), value: '' },
  { label: 'Goethe', value: 'goethe' },
  { label: 'TELC',   value: 'telc'   },
  { label: 'ÖSD',    value: 'osd'    },
])

const levels = computed(() => [
  { label: t('simulator.all'), value: '' },
  { label: 'B1', value: 'b1' },
  { label: 'B2', value: 'b2' },
])

const selectedProvider = ref('')
const selectedLevel    = ref('')

const toggleProvider = (val: string) => {
  selectedProvider.value = selectedProvider.value === val ? '' : val
  reloadSubjects()
}
const toggleLevel = (val: string) => {
  selectedLevel.value = selectedLevel.value === val ? '' : val
  reloadSubjects()
}
const resetFilters = () => {
  selectedProvider.value = ''
  selectedLevel.value    = ''
  reloadSubjects()
}
const reloadSubjects = () => store.fetchSubjects(selectedProvider.value || undefined, selectedLevel.value || undefined)

const switchTab = (tab: 'sujets' | 'resultats') => {
  activeTab.value = tab
  if (tab === 'resultats' && !store.results.length) store.fetchMyResults()
}

const openResult = (result: SimulatorResultResponse) => {
  selectedResult.value = result
  resultDialog.value   = true
}

const criteriaList = (result: SimulatorResultResponse) => {
  const d   = result.result_data
  const max = _getCriteriaMax(result.provider, result.level)
  const toNum = (v: any): number => Number(v) || 0
  return [
    { key: 'aufgabe',   label: 'Aufgabenerfüllung', score: toNum(d.aufgabe_score),   max: max.aufgabe,   pct: Math.round((toNum(d.aufgabe_score)   / max.aufgabe)   * 100) },
    { key: 'kohaesion', label: 'Kohäsion',          score: toNum(d.kohaesion_score), max: max.kohaesion, pct: Math.round((toNum(d.kohaesion_score) / max.kohaesion) * 100) },
    { key: 'wortschatz',label: 'Wortschatz',         score: toNum(d.wortschatz_score),max: max.wortschatz,pct: Math.round((toNum(d.wortschatz_score)/ max.wortschatz)* 100) },
    { key: 'grammatik', label: 'Grammatik',          score: toNum(d.grammatik_score), max: max.grammatik, pct: Math.round((toNum(d.grammatik_score) / max.grammatik) * 100) },
  ]
}

const _getCriteriaMax = (provider: string, level: string) => {
  if (provider === 'telc') return { aufgabe: 15, kohaesion: 10, wortschatz: 10, grammatik: 10 }
  if (provider === 'osd' && level === 'b2') return { aufgabe: 28, kohaesion: 22, wortschatz: 22, grammatik: 18 }
  return { aufgabe: 30, kohaesion: 25, wortschatz: 25, grammatik: 20 }
}

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

const providerBg       = (p: string) => ({ goethe: 'bg-blue-500', telc: 'bg-purple-500', osd: 'bg-orange-500' }[p] ?? 'bg-gray-400')
const providerTagClass = (p: string) => ({ goethe: 'bg-blue-100 text-blue-700', telc: 'bg-purple-100 text-purple-700', osd: 'bg-orange-100 text-orange-700' }[p] ?? 'bg-gray-100 text-gray-600')

onMounted(() => reloadSubjects())
</script>