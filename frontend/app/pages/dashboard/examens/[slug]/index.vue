<template>
  <div class="space-y-6">

    <!-- Loading -->
    <div v-if="pending || examsStore.loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <div v-else-if="!exam" class="text-center py-16 bg-white rounded-xl border border-gray-100">
      <i class="pi pi-exclamation-triangle text-4xl text-red-400 mb-3 block"></i>
      <p class="font-medium text-gray-700">{{ t('exam_detail.not_found') }}</p>
      <Button :label="t('exam_detail.back')" outlined class="mt-4" @click="navigateTo('/dashboard/examens')" />
    </div>

    <div v-else class="space-y-6">

      <!-- Header -->
      <div class="flex items-center gap-3">
        <Button icon="pi pi-arrow-left" text rounded @click="navigateTo('/dashboard/examens')" />
        <div>
          <p class="text-xs font-bold uppercase tracking-widest" :class="providerText(exam.provider)">
            {{ exam.provider }}
          </p>
          <h1 class="text-2xl font-bold text-gray-900">{{ exam.name }}</h1>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ exam.levels?.length || 0 }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ t('exam_detail.levels') }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ totalSubjects }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ t('exam_detail.subjects') }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ freeLevelsCount }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ t('exam_detail.free_levels') }}</p>
        </div>
      </div>

      <!-- Niveaux -->
      <div class="space-y-8">
        <div v-for="level in sortedLevels" :key="level.id">

          <!-- Level header -->
          <div class="flex items-center gap-3 mb-4">
            <div :class="['w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm shrink-0', getLevelBg(level.cefr_code)]">
              {{ level.cefr_code }}
            </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900">
                {{ t('exam_detail.level_prefix') }} {{ level.cefr_code }} - {{ getLevelName(level.cefr_code) }}
              </p>
              <p class="text-xs text-gray-400">
                {{ level.subjects?.length || 0 }} {{ t('exam_detail.subjects_count') }} ·
                {{ t('exam_detail.min_score') }} : {{ level.total_pass_score }}
              </p>
            </div>
            <Tag v-if="hasAccess(level)"    :value="t('exam_detail.access_active')" severity="success" />
            <Tag v-else-if="level.is_free"  :value="t('exam_detail.free')"          severity="info"    />
            <Tag v-else                      :value="t('exam_detail.premium')"        severity="warning" />
          </div>

          <!-- Modules du niveau -->
          <div class="flex flex-wrap gap-2 mb-4 px-1">
            <div
              v-for="module in level.subjects?.[0]?.modules"
              :key="module.id"
              :class="['flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium', getModuleColor(module.slug)]"
            >
              <i :class="['pi text-xs', getModuleIcon(module.slug)]"></i>
              {{ module.name }}
              <span class="opacity-60">{{ module.time_limit_minutes }}min</span>
            </div>
          </div>

          <!-- Sujets -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <button
              v-for="subject in level.subjects"
              :key="subject.id"
              class="group bg-white border border-gray-100 rounded-xl px-5 py-4 hover:border-teal-300 hover:shadow-md transition-all text-left flex items-center gap-4 shadow-sm"
              @click="goToSubject(level, subject)"
            >
              <div class="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center shrink-0 group-hover:bg-teal-50 transition-colors border border-gray-100">
                <span class="text-sm font-bold text-gray-400 group-hover:text-teal-600 transition-colors">
                  {{ subject.subject_number }}
                </span>
              </div>

              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors text-sm">
                  {{ subject.name || `${t('exam_detail.subject_default')} ${subject.subject_number}` }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5">
                  {{ subject.modules?.length || 0 }} {{ t('exam_detail.modules') }} ·
                  {{ subject.modules?.reduce((s, m) => s + (m.time_limit_minutes || 0), 0) }} min
                </p>
                <span
                  v-if="hasAccess(level) || level.is_free"
                  class="inline-flex items-center gap-1 text-xs font-medium text-green-600 mt-1"
                >
                  <i class="pi pi-check-circle text-xs"></i> {{ t('exam_detail.available') }}
                </span>
                <span v-else class="inline-flex items-center gap-1 text-xs font-medium text-gray-400 mt-1">
                  <i class="pi pi-lock text-xs"></i> {{ t('exam_detail.premium') }}
                </span>
              </div>

              <i class="pi pi-arrow-right text-gray-200 group-hover:text-teal-400 group-hover:translate-x-1 transition-all shrink-0 text-sm"></i>
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamDetailResponse, LevelWithSubjectsResponse } from '#shared/api'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const { t } = useI18n()
const route      = useRoute()
const examsStore = useExamsStore()
const slug       = computed(() => route.params.slug as string)

const { pending } = await useAsyncData(
  `exam-${route.params.slug}`,
  async () => {
    await Promise.all([
      examsStore.fetchExamBySlug(route.params.slug as string),
      examsStore.catalog.length === 0 ? examsStore.fetchCatalog() : Promise.resolve(),
    ])
  },
  { server: false },
)

const exam = computed<ExamDetailResponse | null>(() => examsStore.currentExam)

const sortedLevels = computed(() => {
  if (!exam.value?.levels) return []
  return [...exam.value.levels].sort((a, b) => a.display_order - b.display_order)
})

const totalSubjects  = computed(() => exam.value?.levels?.reduce((sum, l) => sum + (l.subjects?.length || 0), 0) ?? 0)
const freeLevelsCount = computed(() => exam.value?.levels?.filter(l => l.is_free).length ?? 0)

const hasAccess = (level: LevelWithSubjectsResponse): boolean => {
  const catalogExam  = examsStore.catalog.find(e => e.slug === slug.value)
  const catalogLevel = catalogExam?.levels?.find(l => l.id === level.id)
  return catalogLevel?.has_access ?? level.is_free
}

const goToSubject = (level: LevelWithSubjectsResponse, subject: any) => {
  if (!exam.value) return
  if (!hasAccess(level) && !level.is_free) {
    navigateTo(`/dashboard/paiement?exam_id=${exam.value.id}`)
    return
  }
  navigateTo({
    path:  `/dashboard/examens/${slug.value}/${subject.id}`,
    query: { examId: exam.value.id },
  })
}

const getLevelName = (code: string) => t(`exam_detail.level_names.${code}`) ?? code

const getLevelBg = (code: string) => ({
  B1: 'bg-blue-100 text-blue-700',
  B2: 'bg-blue-100 text-blue-700',
  C1: 'bg-purple-100 text-purple-700',
  C2: 'bg-purple-100 text-purple-700',
}[code] ?? 'bg-gray-100 text-gray-700')

const providerText = (p: string) => ({
  Goethe: 'text-blue-600',
  ÖSD:    'text-orange-600',
  TELC:   'text-purple-600',
}[p] ?? 'text-gray-500')

const getModuleIcon = (s: string) => {
  if (s.includes('lesen'))    return 'pi-book'
  if (s.includes('horen') || s.includes('hören')) return 'pi-volume-up'
  if (s.includes('schreiben')) return 'pi-pencil'
  if (s.includes('sprechen')) return 'pi-microphone'
  return 'pi-file'
}

const getModuleColor = (s: string) => {
  if (s.includes('lesen'))    return 'bg-blue-100 text-blue-600'
  if (s.includes('horen') || s.includes('hören')) return 'bg-purple-100 text-purple-600'
  if (s.includes('schreiben')) return 'bg-green-100 text-green-600'
  if (s.includes('sprechen')) return 'bg-orange-100 text-orange-600'
  return 'bg-gray-100 text-gray-600'
}
</script>