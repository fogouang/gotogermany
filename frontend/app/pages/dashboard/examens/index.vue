<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Examens disponibles</h1>
      <p class="text-gray-600">Choisissez un examen et commencez votre préparation</p>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-8">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <IconField iconPosition="left">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="searchQuery"
              placeholder="Rechercher un examen..."
              class="w-full"
            />
          </IconField>
        </div>
        <Select
          v-model="selectedProvider"
          :options="providers"
          optionLabel="label"
          optionValue="value"
          placeholder="Provider"
          class="w-full sm:w-44"
        />
        <Select
          v-model="selectedLevel"
          :options="cefrLevels"
          optionLabel="label"
          optionValue="value"
          placeholder="Niveau"
          class="w-full sm:w-44"
        />
        <Button
          v-if="searchQuery || selectedProvider || selectedLevel"
          icon="pi pi-times"
          text
          rounded
          severity="secondary"
          @click="resetFilters"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="examsStore.loading" class="flex justify-center py-20">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Empty -->
    <div v-else-if="filteredExams.length === 0" class="text-center py-20">
      <i class="pi pi-inbox text-5xl text-gray-300 mb-4 block"></i>
      <h3 class="text-lg font-semibold text-gray-700 mb-2">Aucun examen trouvé</h3>
      <p class="text-gray-500 mb-6">Essayez avec d'autres critères de recherche</p>
      <Button label="Réinitialiser" text @click="resetFilters" />
    </div>

    <!-- Exams grouped by provider -->
    <div v-else class="space-y-10">
      <div v-for="(exams, provider) in groupedExams" :key="provider">
        <!-- Provider header -->
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center">
            <i class="pi pi-bookmark text-teal-600 text-sm"></i>
          </div>
          <h2 class="text-lg font-bold text-gray-900">{{ getProviderName(String(provider)) }}</h2>
          <div class="flex-1 h-px bg-gray-100"></div>
          <span class="text-xs text-gray-400">{{ exams.length }} examen(s)</span>
        </div>

        <!-- Exam list — vertical cards -->
        <div class="space-y-4">
          <div
            v-for="exam in exams"
            :key="exam.id"
            class="group bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md hover:border-teal-200 transition-all duration-200 overflow-hidden"
          >
            <div class="flex items-stretch">
              <!-- Left accent -->
              <div class="w-1.5 bg-linear-to-b from-teal-500 to-teal-300 shrink-0 group-hover:from-teal-400 group-hover:to-blue-400 transition-all duration-300"></div>

              <!-- Content -->
              <div class="flex-1 px-6 py-5">
                <div class="flex items-start justify-between gap-4">
                  <!-- Left: info -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-xs font-semibold text-teal-600 uppercase tracking-wide">
                        {{ exam.provider.toUpperCase() }}
                      </span>
                    </div>
                    <h3 class="text-lg font-bold text-gray-900 group-hover:text-teal-700 transition-colors mb-2 truncate">
                      {{ exam.name }}
                    </h3>
                    <p class="text-sm text-gray-500 line-clamp-1 mb-3">
                      {{ exam.description || 'Préparez-vous efficacement pour cet examen d\'allemand.' }}
                    </p>

                    <!-- Levels tags -->
                    <div class="flex flex-wrap gap-2">
                      <div
                        v-for="level in exam.levels"
                        :key="level.id"
                        class="flex items-center gap-1.5"
                      >
                        <Tag
                          :value="level.cefr_code"
                          :severity="getLevelSeverity(level.cefr_code)"
                        />
                        <span v-if="level.has_access" class="text-xs text-green-600 font-medium flex items-center gap-0.5">
                          <i class="pi pi-check-circle text-xs"></i> Accès actif
                        </span>
                        <span v-else-if="level.is_free" class="text-xs text-blue-500 font-medium flex items-center gap-0.5">
                          <i class="pi pi-lock-open text-xs"></i> Gratuit
                        </span>
                        <span v-else class="text-xs text-gray-400 font-medium flex items-center gap-0.5">
                          <i class="pi pi-lock text-xs"></i> Premium
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Right: actions -->
                  <div class="flex flex-col gap-2 shrink-0">
                    <Button
                      label="Commencer"
                      icon="pi pi-play"
                      size="small"
                      class="bg-gradient-primary! border-transparent! whitespace-nowrap"
                      @click="startExam(exam)"
                    />
                    <Button
                      label="Détails"
                      icon="pi pi-info-circle"
                      size="small"
                      outlined
                      severity="secondary"
                      class="whitespace-nowrap"
                      @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamCatalogResponse } from '#shared/api'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth',
})

const examsStore = useExamsStore()

const searchQuery = ref('')
const selectedProvider = ref('')
const selectedLevel = ref('')

const providers = computed(() => [
  { label: 'Tous les providers', value: '' },
  { label: 'Goethe', value: 'Goethe' },
  { label: 'ÖSD', value: 'ÖSD' },
  { label: 'TELC', value: 'TELC' },
])

const cefrLevels = [
  { label: 'Tous les niveaux', value: '' },
  { label: 'A1', value: 'A1' },
  { label: 'A2', value: 'A2' },
  { label: 'B1', value: 'B1' },
  { label: 'B2', value: 'B2' },
  { label: 'C1', value: 'C1' },
  { label: 'C2', value: 'C2' },
]

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
  if (selectedProvider.value) {
    exams = exams.filter(e => e.provider === selectedProvider.value)
  }
  if (selectedLevel.value) {
    exams = exams.filter(e => e.levels?.some(l => l.cefr_code === selectedLevel.value))
  }
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

const getProviderName = (provider: string) => {
  const names: Record<string, string> = {
    Goethe: 'Goethe-Institut',
    ÖSD: 'Österreichisches Sprachdiplom',
    TELC: 'TELC Deutsch',
  }
  return names[provider] || provider
}

const getLevelSeverity = (cefrCode: string) => {
  const s: Record<string, any> = {
    A1: 'success', A2: 'success',
    B1: 'info', B2: 'info',
    C1: 'warning', C2: 'danger',
  }
  return s[cefrCode] || 'secondary'
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedProvider.value = ''
  selectedLevel.value = ''
}

const startExam = (exam: ExamCatalogResponse) => {
  navigateTo(`/dashboard/examens/${exam.slug}`)
}

onMounted(async () => {
  if (examsStore.catalog.length === 0) {
    await examsStore.fetchCatalog()
  }
})
</script>