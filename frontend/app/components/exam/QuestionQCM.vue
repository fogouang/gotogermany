<template>
  <div class="space-y-6">
    <!-- Audio player si présent (Hören Teil 2) -->
    <div v-if="teil.audio_file" class="bg-indigo-50 p-6 rounded-lg border-2 border-indigo-500">
      <div class="flex items-center gap-4 mb-4">
        <i class="pi pi-volume-up text-indigo-600 text-2xl"></i>
        <div class="flex-1">
          <h3 class="font-bold text-gray-900">{{ teil.audio_title || 'Audio' }}</h3>
          <p class="text-sm text-gray-600">{{ teil.audio_type || 'Hörtext' }}</p>
        </div>
      </div>

      <audio 
        ref="audioPlayer"
        controls 
        class="w-full"
        @ended="handleAudioEnded"
      >
        <source :src="getAudioPath(teil.audio_file)" type="audio/mpeg">
        Votre navigateur ne supporte pas l'élément audio.
      </audio>

      <div class="mt-4 flex items-center gap-2 text-sm text-gray-600">
        <i class="pi pi-info-circle"></i>
        <span>Vous pouvez écouter l'audio {{ audioPlayCount }}/2 fois</span>
      </div>
    </div>

    <!-- Stimulus text si présent -->
    <div v-if="getCurrentStimulus()" class="bg-gray-50 p-6 rounded-lg border-l-4 border-indigo-500">
      <div class="prose max-w-none whitespace-pre-line">
        {{ getCurrentStimulus() }}
      </div>
    </div>

    <!-- Question -->
    <div v-if="currentQuestion" class="space-y-4">
      <p class="text-lg font-medium text-gray-900">
        {{ currentQuestion.number }}. {{ currentQuestion.stem }}
      </p>
      <div class="space-y-3">
        <div 
          v-for="(option, key) in currentQuestion.options"
          :key="key"
          class="p-4 border-2 rounded-lg cursor-pointer transition-all"
          :class="userAnswer === String(key)
            ? 'border-indigo-500 bg-indigo-50' 
            : 'border-gray-200 hover:border-indigo-300'"
          @click="selectAnswer(String(key))"
        >
          <div class="flex items-start gap-3">
            <RadioButton 
              :modelValue="userAnswer" 
              :value="String(key)" 
              name="answer"
              @update:modelValue="selectAnswer"
            />
            <label class="cursor-pointer flex-1">
              <span class="font-bold text-indigo-600">{{ String(key).toUpperCase() }})</span>
              {{ option }}
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  teil: any
  questionIndex: number
  userAnswer?: string
}>()

const emit = defineEmits<{
  answer: [value: string]
}>()

const audioPlayer = ref<HTMLAudioElement | null>(null)
const audioPlayCount = ref(0)

const currentQuestion = computed(() => {
  // Pour Teil 2 de Lesen, il y a des texts avec questions
  if (props.teil.texts && props.teil.texts.length > 0) {
    // Trouver la question dans les texts
    for (const text of props.teil.texts) {
      const question = text.questions.find((q: any) => 
        q.number === props.questionIndex + (props.teil.texts[0].questions[0].number)
      )
      if (question) return question
    }
  }
  
  // Pour Teil 5 et autres formats QCM simples, ou Hören Teil 2
  return props.teil.questions?.[props.questionIndex]
})

const getCurrentStimulus = () => {
  // Pour Teil 2 avec texts multiples
  if (props.teil.texts && props.teil.texts.length > 0) {
    for (const text of props.teil.texts) {
      const hasQuestion = text.questions.some((q: any) => 
        q.number === props.questionIndex + (props.teil.texts[0].questions[0].number)
      )
      if (hasQuestion) return text.stimulus_text
    }
  }
  
  // Pour Teil 5 avec stimulus_text global
  return props.teil.stimulus_text
}

const getAudioPath = (audioFile: string) => {
  const cleanPath = audioFile.replace(/\\/g, '/');
  const filename = cleanPath.split('/').pop();
  return `/data/audio/${filename}`;
}

const handleAudioEnded = () => {
  audioPlayCount.value++
}

const selectAnswer = (value: string) => {
  emit('answer', value)
}
</script>