<template>
  <div class="space-y-6">
    <!-- Scenario/Instructions -->
    <div v-if="teil.scenario" class="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
      <h3 class="font-bold text-gray-900 mb-2">{{ t('session.schreiben.situation') }}</h3>
      <p class="text-gray-800">{{ teil.scenario }}</p>
    </div>

    <!-- Stimulus pour Teil 2 (Meinungsäußerung) -->
    <div v-if="teil.stimulus" class="bg-gray-50 p-6 rounded-lg border-l-4 border-indigo-500">
      <div class="flex items-start gap-3 mb-3">
        <i class="pi pi-user text-indigo-600 text-xl"></i>
        <div>
          <p class="font-bold text-gray-900">{{ teil.stimulus_author }}</p>
          <p class="text-sm text-gray-600">{{ new Date().toLocaleDateString('fr-FR') }}</p>
        </div>
      </div>
      <p class="text-gray-800 italic">"{{ teil.stimulus }}"</p>
    </div>

    <!-- Points à traiter -->
    <div v-if="teil.prompts" class="bg-yellow-50 p-4 rounded-lg">
      <h4 class="font-semibold text-gray-900 mb-2">{{ t('session.schreiben.points_to_cover') }}</h4>
      <ul class="space-y-1">
        <li v-for="(prompt, idx) in teil.prompts" :key="idx" class="flex items-start gap-2">
          <i class="pi pi-check text-green-600 mt-1"></i>
          <span class="text-gray-700">{{ prompt }}</span>
        </li>
      </ul>
    </div>

    <!-- Zone de texte -->
    <div class="bg-white p-6 rounded-lg border-2 border-gray-200">
      <div class="flex justify-between items-center mb-4">
        <label class="font-semibold text-gray-900">{{ t('session.schreiben.your_answer') }}</label>
        <span class="text-sm text-gray-500">
          {{ t('session.schreiben.word_count', { count: wordCount, target: teil.word_count_target }) }}
        </span>
      </div>
      
      <Textarea
        v-model="text"
        rows="15"
        class="w-full"
        :placeholder="t('session.schreiben.placeholder')"
        @input="updateText"
      />

      <div class="mt-4 flex justify-between items-center text-sm text-gray-600">
        <span>{{ t('session.schreiben.suggested_time', { minutes: teil.time_minutes }) }}</span>
        <span :class="wordCount < teil.word_count_target * 0.8 ? 'text-orange-600' : 'text-green-600'">
          {{ wordCount < teil.word_count_target * 0.8 ? t('session.schreiben.too_short') : t('session.schreiben.length_ok') }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

const props = defineProps<{
  teil: any
  questionIndex: number
  userAnswer?: string
}>()

const emit = defineEmits<{
  answer: [value: string]
}>()

const text = ref(props.userAnswer || '')

const wordCount = computed(() => {
  return text.value.trim().split(/\s+/).filter(w => w.length > 0).length
})

const updateText = () => {
  emit('answer', text.value)
}

watch(() => props.userAnswer, (newVal) => {
  if (newVal !== text.value) {
    text.value = newVal || ''
  }
})
</script>