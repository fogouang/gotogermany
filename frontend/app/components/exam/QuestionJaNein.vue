<template>
  <div class="space-y-6">
    <!-- Topic/Context -->
    <div v-if="teil.topic" class="text-center mb-6">
      <h3 class="text-2xl font-bold text-gray-900">{{ teil.topic }}</h3>
    </div>

    <!-- Question actuelle avec commentaire -->
    <div v-if="currentQuestion" class="space-y-4">
      <!-- Numéro et auteur -->
      <div class="flex items-center gap-3 mb-2">
        <span class="bg-indigo-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold">
          {{ currentQuestion.number }}
        </span>
        <span class="font-bold text-gray-900">{{ currentQuestion.author }}</span>
      </div>

      <!-- Texte du commentaire -->
      <div class="bg-gray-50 p-6 rounded-lg border-l-4 border-indigo-500">
        <p class="text-gray-800 leading-relaxed">{{ currentQuestion.text }}</p>
      </div>

      <!-- Question d'interprétation -->
      <p class="text-lg font-medium text-gray-900 mt-6">
        Cette personne trouve-t-elle le Homeoffice positif ?
      </p>

      <!-- Options Ja/Nein -->
      <div class="flex gap-4">
        <div 
          class="flex-1 p-4 border-2 rounded-lg cursor-pointer transition-all"
          :class="userAnswer === 'ja' 
            ? 'border-green-500 bg-green-50' 
            : 'border-gray-200 hover:border-green-300'"
          @click="selectAnswer('ja')"
        >
          <div class="flex items-center gap-3">
            <RadioButton 
              :modelValue="userAnswer" 
              value="ja" 
              name="answer"
              @update:modelValue="selectAnswer"
            />
            <label class="font-medium cursor-pointer">Ja</label>
          </div>
        </div>

        <div 
          class="flex-1 p-4 border-2 rounded-lg cursor-pointer transition-all"
          :class="userAnswer === 'nein' 
            ? 'border-red-500 bg-red-50' 
            : 'border-gray-200 hover:border-red-300'"
          @click="selectAnswer('nein')"
        >
          <div class="flex items-center gap-3">
            <RadioButton 
              :modelValue="userAnswer" 
              value="nein" 
              name="answer"
              @update:modelValue="selectAnswer"
            />
            <label class="font-medium cursor-pointer">Nein</label>
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

const currentQuestion = computed(() => {
  return props.teil.questions?.[props.questionIndex]
})

const selectAnswer = (value: string) => {
  emit('answer', value)
}
</script>