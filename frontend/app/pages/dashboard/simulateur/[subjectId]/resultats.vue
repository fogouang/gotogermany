<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Pas de correction -->
    <div v-if="!correction" class="max-w-lg mx-auto pt-20 px-6 text-center space-y-4">
      <i class="pi pi-inbox text-gray-300 text-4xl"></i>
      <p class="text-gray-500 text-sm">{{ t('simulator_result.no_correction') }}</p>
      <Button :label="t('simulator_result.back_simulator')" outlined @click="goBack" />
    </div>

    <!-- Résultats -->
    <div v-else class="max-w-3xl mx-auto px-4 py-8 space-y-5">

      <!-- Hero Score -->
      <div class="rounded-2xl overflow-hidden" :class="correction.passed ? 'bg-green-600' : 'bg-orange-500'">
        <div class="px-6 pt-6 pb-4 flex items-start justify-between gap-4">
          <div>
            <p class="text-xs text-white/70 font-semibold uppercase tracking-widest mb-1">
              {{ correction.provider.toUpperCase() }} · {{ correction.level.toUpperCase() }}
            </p>
            <h1 class="text-2xl font-bold text-white">
              {{ correction.passed ? '🎉 Prüfung bestanden !' : 'Nicht bestanden' }}
            </h1>
          </div>
          <div class="relative w-20 h-20 shrink-0">
            <svg class="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="8" />
              <circle cx="40" cy="40" r="32" fill="none" stroke="white" stroke-width="8" stroke-linecap="round"
                :stroke-dasharray="`${(correction.score_percentage / 100) * 201} 201`" />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-white font-bold text-lg leading-none">{{ store.cecrlLevel }}</span>
              <span class="text-white/70 text-xs">{{ Math.round(correction.score_percentage) }}%</span>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 divide-x divide-white/20 bg-black/10">
          <div class="px-4 py-3 text-center">
            <p class="text-white/70 text-xs uppercase tracking-wide mb-0.5">{{ t('simulator_result.score') }}</p>
            <p class="text-white font-bold text-base">{{ correction.overall_score }}/{{ correction.max_score }}</p>
          </div>
          <div class="px-4 py-3 text-center">
            <p class="text-white/70 text-xs uppercase tracking-wide mb-0.5">{{ t('simulator_result.success_rate') }}</p>
            <p class="text-white font-bold text-base">{{ Math.round(correction.score_percentage) }}%</p>
          </div>
          <div class="px-4 py-3 text-center">
            <p class="text-white/70 text-xs uppercase tracking-wide mb-0.5">{{ t('simulator_result.level') }}</p>
            <p class="text-white font-bold text-base">{{ store.cecrlLevel }}</p>
          </div>
        </div>

        <!-- Appréciation -->
        <div class="px-6 py-4 bg-black/10 border-t border-white/10">
          <p class="text-sm text-white/90 leading-relaxed italic">
            <i class="pi pi-comment mr-2 not-italic text-white/50"></i>{{ correction.appreciation }}
          </p>
        </div>
      </div>

      <!-- Critères -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
          <i class="pi pi-chart-bar text-teal-600"></i>
          <h2 class="font-semibold text-gray-800 text-sm">{{ t('simulator_result.criteria_title') }}</h2>
        </div>
        <div class="divide-y divide-gray-100">
          <div v-for="c in store.criteriaList" :key="c.key" class="px-5 py-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">{{ c.label }}</span>
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-400">{{ c.score }}/{{ c.maxScore }}</span>
                <span :class="['text-xs font-bold px-2 py-0.5 rounded-full',
                  scoreRatio(c.score, c.maxScore) >= 0.7 ? 'bg-green-100 text-green-700' :
                  scoreRatio(c.score, c.maxScore) >= 0.5 ? 'bg-orange-100 text-orange-700' : 'bg-red-100 text-red-700']">
                  {{ Math.round(scoreRatio(c.score, c.maxScore) * 100) }}%
                </span>
              </div>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5 mb-2">
              <div class="h-1.5 rounded-full transition-all" :class="barColor(c.score, c.maxScore)"
                :style="{ width: `${(c.score / c.maxScore) * 100}%` }" />
            </div>
            <p class="text-xs text-gray-500 leading-relaxed">{{ c.feedback }}</p>
          </div>
        </div>
      </div>

      <!-- Feedbacks par tâche -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
          <i class="pi pi-file-edit text-teal-600"></i>
          <h2 class="font-semibold text-gray-800 text-sm">{{ t('simulator_result.task_title') }}</h2>
        </div>
        <Tabs v-model:value="activeTaskTab">
          <TabList class="px-5 pt-3">
            <Tab v-for="task in store.taskList" :key="task.key" :value="task.key" class="text-sm">
              {{ task.label }}
            </Tab>
          </TabList>
          <TabPanels>
            <TabPanel v-for="task in store.taskList" :key="task.key" :value="task.key" class="px-5 py-5 space-y-5">

              <!-- Points forts -->
              <div v-if="task.strengths.length">
                <p class="text-xs font-semibold text-green-700 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <i class="pi pi-check-circle"></i> {{ t('simulator_result.strengths') }}
                </p>
                <ul class="space-y-1.5">
                  <li v-for="(s, i) in task.strengths" :key="i"
                    class="flex items-start gap-2 text-sm text-gray-700 bg-green-50 rounded-lg px-3 py-2">
                    <i class="pi pi-check text-green-500 mt-0.5 shrink-0 text-xs"></i>
                    <span>{{ s }}</span>
                  </li>
                </ul>
              </div>

              <!-- À améliorer -->
              <div v-if="task.weaknesses.length">
                <p class="text-xs font-semibold text-orange-700 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <i class="pi pi-exclamation-circle"></i> {{ t('simulator_result.to_improve') }}
                </p>
                <ul class="space-y-1.5">
                  <li v-for="(w, i) in task.weaknesses" :key="i"
                    class="flex items-start gap-2 text-sm text-gray-700 bg-orange-50 rounded-lg px-3 py-2">
                    <i class="pi pi-times text-orange-400 mt-0.5 shrink-0 text-xs"></i>
                    <span>{{ w }}</span>
                  </li>
                </ul>
              </div>

              <!-- Texte corrigé -->
              <div v-if="task.correctedText">
                <p class="text-xs font-semibold text-teal-700 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <i class="pi pi-sparkles"></i> {{ t('simulator_result.corrected_text') }}
                </p>
                <div class="bg-teal-50 border border-teal-200 rounded-xl p-4">
                  <p class="text-sm text-gray-800 whitespace-pre-line leading-relaxed">{{ task.correctedText }}</p>
                </div>
              </div>

            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>

      <!-- Corrections détaillées -->
      <div v-if="correction.corrections_list?.length" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
          <i class="pi pi-pencil text-orange-500"></i>
          <h2 class="font-semibold text-gray-800 text-sm">{{ t('simulator_result.detailed_corrections') }}</h2>
          <span class="ml-auto bg-orange-100 text-orange-700 text-xs font-bold px-2 py-0.5 rounded-full">
            {{ correction.corrections_list.length }}
          </span>
        </div>
        <div class="divide-y divide-gray-100">
          <div v-for="(c, i) in correction.corrections_list" :key="i"
            class="px-5 py-3 flex items-start gap-3 hover:bg-gray-50 transition-colors">
            <span class="text-xs bg-gray-100 text-gray-500 font-semibold px-1.5 py-0.5 rounded mt-0.5 shrink-0">
              T{{ c.task || '1' }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm flex flex-wrap items-center gap-x-2 gap-y-1">
                <span class="line-through text-red-500">{{ c.error }}</span>
                <span class="text-gray-400">→</span>
                <span class="text-green-600 font-medium">{{ c.correction }}</span>
              </p>
              <p class="text-xs text-gray-400 mt-0.5 leading-relaxed">{{ c.explanation }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Conseils -->
      <div v-if="correction.suggestions?.length" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
          <i class="pi pi-lightbulb text-yellow-500"></i>
          <h2 class="font-semibold text-gray-800 text-sm">{{ t('simulator_result.tips') }}</h2>
        </div>
        <ul class="divide-y divide-gray-100">
          <li v-for="(s, i) in correction.suggestions" :key="i"
            class="px-5 py-3 flex items-start gap-3 text-sm text-gray-700">
            <span class="w-5 h-5 rounded-full bg-yellow-100 text-yellow-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
              {{ i + 1 }}
            </span>
            <span>{{ s }}</span>
          </li>
        </ul>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 pb-8">
        <Button :label="t('simulator_result.redo')"           icon="pi pi-refresh" outlined class="flex-1" @click="goBack" />
        <Button :label="t('simulator_result.choose_another')" icon="pi pi-list"    class="flex-1"           @click="goToList" />
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from '~/stores/simulator'

definePageMeta({ layout: 'default', middleware: 'auth' })

const { t }  = useI18n()
const route  = useRoute()
const router = useRouter()
const store  = useSimulatorStore()

const subjectId  = route.params.subjectId as string
const correction = computed(() => store.correction)

const activeTaskTab = ref<string>(store.taskList?.[0]?.key ?? '')

const goBack   = () => router.push(`/dashboard/simulateur/${subjectId}`)
const goToList = () => router.push('/dashboard/simulateur')

const scoreRatio = (score: number, max: number) => score / max
const barColor   = (score: number, max: number) => {
  const p = score / max
  return p >= 0.7 ? 'bg-green-500' : p >= 0.5 ? 'bg-orange-400' : 'bg-red-400'
}

onMounted(() => { if (!store.correction) router.replace('/dashboard/simulateur') })

useHead({ title: t('simulator_result.page_title') })
</script>