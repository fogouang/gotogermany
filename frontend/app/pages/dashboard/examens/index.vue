<template>
  <div class="space-y-6">

    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">{{ t('dashboard_exams.title') }}</h1>
      <p class="text-sm text-gray-500 mt-1">{{ t('dashboard_exams.subtitle') }}</p>
    </div>

    <!-- Filtres -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <IconField iconPosition="left">
            <InputIcon class="pi pi-search" />
            <InputText v-model="searchQuery" :placeholder="t('dashboard_exams.search_placeholder')" class="w-full" />
          </IconField>
        </div>
        <Select
          v-model="selectedProvider"
          :options="providers"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('dashboard_exams.provider_placeholder')"
          class="w-full sm:w-40"
        />
        <Select
          v-model="selectedLevel"
          :options="cefrLevels"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('dashboard_exams.level_placeholder')"
          class="w-full sm:w-36"
        />
        <Button
          v-if="searchQuery || selectedProvider || selectedLevel"
          icon="pi pi-times"
          text rounded severity="secondary"
          @click="resetFilters"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="examsStore.loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Vide -->
    <div v-else-if="filteredExams.length === 0" class="text-center py-16 bg-white rounded-xl border border-gray-100">
      <i class="pi pi-inbox text-4xl text-gray-300 mb-3 block"></i>
      <p class="font-medium text-gray-600">{{ t('dashboard_exams.empty_title') }}</p>
      <p class="text-sm text-gray-400 mb-4">{{ t('dashboard_exams.empty_subtitle') }}</p>
      <Button :label="t('dashboard_exams.reset')" text @click="resetFilters" />
    </div>

    <!-- Liste groupée par provider -->
    <div v-else class="space-y-8">
      <div v-for="(exams, provider) in groupedExams" :key="provider">

        <!-- Provider header -->
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold"
            :class="providerBg(String(provider))"
          >
            {{ String(provider).slice(0, 2).toUpperCase() }}
          </div>
          <h2 class="text-sm font-bold text-gray-700 uppercase tracking-wide">
            {{ getProviderName(String(provider)) }}
          </h2>
          <div class="flex-1 h-px bg-gray-100"></div>
          <span class="text-xs text-gray-400">{{ exams.length }} {{ t('dashboard_exams.exam_count') }}</span>
        </div>

        <!-- Liste examens -->
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <button
            v-for="exam in exams"
            :key="exam.id"
            class="group w-full flex items-center gap-4 px-6 py-5 hover:bg-gray-50 transition-colors text-left border-b border-gray-50 last:border-0"
            @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
          >
            <!-- Icône -->
            <div
              class="w-11 h-11 rounded-xl flex items-center justify-center text-white text-xs font-bold shrink-0"
              :class="providerBg(exam.provider)"
            >
              {{ exam.provider.slice(0, 2).toUpperCase() }}
            </div>

            <!-- Infos -->
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors">
                {{ exam.name }}
              </p>
              <p class="text-xs text-gray-400 mt-0.5 line-clamp-1">
                {{ exam.description || t('dashboard_exams.default_desc') }}
              </p>
              <!-- Niveaux + accès -->
              <div class="flex flex-wrap items-center gap-2 mt-2">
                <div v-for="level in exam.levels" :key="level.id">
                  <span
                    v-if="level.has_access"
                    class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-green-50 text-green-700"
                  >
                    <i class="pi pi-check-circle text-xs"></i>
                    {{ level.cefr_code }} — {{ t('dashboard_exams.access_active') }}
                  </span>
                  <span
                    v-else-if="level.is_free"
                    class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-teal-50 text-teal-700"
                  >
                    <i class="pi pi-lock-open text-xs"></i>
                    {{ level.cefr_code }} — {{ t('dashboard_exams.free') }}
                  </span>
                  <span
                    v-else
                    class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-500"
                  >
                    <i class="pi pi-lock text-xs"></i>
                    {{ level.cefr_code }} — {{ t('dashboard_exams.premium') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- CTA -->
            <div class="shrink-0 flex items-center gap-2">
              <span class="text-xs text-teal-600 font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                {{ t('dashboard_exams.see_subjects') }}
              </span>
              <i class="pi pi-arrow-right text-gray-300 group-hover:text-teal-500 group-hover:translate-x-1 transition-all"></i>
            </div>
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { ExamCatalogResponse } from '#shared/api'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const { t } = useI18n()
const examsStore = useExamsStore()

const searchQuery      = ref('')
const selectedProvider = ref('')
const selectedLevel    = ref('')

const providers = computed(() => [
  { label: t('dashboard_exams.all_providers'), value: '' },
  { label: 'Goethe', value: 'Goethe' },
  { label: 'ÖSD',    value: 'ÖSD'    },
  { label: 'TELC',   value: 'TELC'   },
])

const cefrLevels = computed(() => [
  { label: t('dashboard_exams.all_levels'), value: '' },
  { label: 'B1', value: 'B1' },
  { label: 'B2', value: 'B2' },
])

const filteredExams = computed(() => {
  let exams = examsStore.catalog
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    exams = exams.filter(e =>
      e.name.toLowerCase().includes(q) ||
      e.description?.toLowerCase().includes(q) ||
      e.provider.toLowerCase().includes(q)
    )
  }
  if (selectedProvider.value) exams = exams.filter(e => e.provider === selectedProvider.value)
  if (selectedLevel.value)    exams = exams.filter(e => e.levels?.some(l => l.cefr_code === selectedLevel.value))
  return exams
})

const groupedExams = computed(() => {
  const grouped: Record<string, ExamCatalogResponse[]> = {}
  filteredExams.value.forEach(exam => {
    const p = exam.provider || 'Autre'
    if (!grouped[p]) grouped[p] = []
    grouped[p].push(exam)
  })
  return grouped
})

const getProviderName = (provider: string) => ({
  Goethe: 'Goethe-Institut',
  ÖSD:    'Österreichisches Sprachdiplom',
  TELC:   'TELC Deutsch',
}[provider] ?? provider)

const providerBg = (p: string) => ({
  Goethe: 'bg-blue-500',
  ÖSD:    'bg-orange-500',
  TELC:   'bg-purple-500',
}[p] ?? 'bg-gray-400')

const resetFilters = () => {
  searchQuery.value      = ''
  selectedProvider.value = ''
  selectedLevel.value    = ''
}

onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog()
})
</script>