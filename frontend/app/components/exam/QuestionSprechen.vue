<template>
  <div class="space-y-6">
    <!-- Info importante -->
    <div class="bg-orange-50 p-6 rounded-lg border-l-4 border-orange-500">
      <div class="flex items-start gap-3">
        <i class="pi pi-exclamation-triangle text-orange-600 text-2xl"></i>
        <div>
          <h3 class="font-bold text-gray-900 mb-2">Section orale - Examinateur requis</h3>
          <p class="text-gray-700">
            Cette section doit être réalisée avec un examinateur certifié. Lisez les consignes ci-dessous pour vous préparer.
          </p>
        </div>
      </div>
    </div>

    <!-- Carte de la tâche -->
    <div class="bg-white p-6 rounded-lg border-2 border-indigo-500 shadow-lg">
      <div class="flex items-center gap-3 mb-4">
        <i class="pi pi-microphone text-indigo-600 text-3xl"></i>
        <h3 class="text-2xl font-bold text-gray-900">{{ teil.name || `Teil ${teil.teil_number}` }}</h3>
      </div>

      <!-- Instructions -->
      <div class="bg-gray-50 p-4 rounded-lg mb-4">
        <p class="text-gray-800">{{ teil.instructions }}</p>
      </div>

      <!-- Thème/Situation -->
      <div v-if="teil.theme || teil.situation" class="mb-4">
        <h4 class="font-semibold text-gray-900 mb-2">Thema / Situation:</h4>
        <p class="text-gray-800 bg-blue-50 p-4 rounded-lg">
          {{ teil.theme || teil.situation }}
        </p>
      </div>

      <!-- Points à aborder -->
      <div v-if="teil.prompts" class="mb-4">
        <h4 class="font-semibold text-gray-900 mb-3">Punkte, die Sie ansprechen sollen:</h4>
        <ul class="space-y-2">
          <li 
            v-for="(prompt, idx) in teil.prompts" 
            :key="idx"
            class="flex items-start gap-3 bg-white p-3 rounded border-l-4 border-green-500"
          >
            <i class="pi pi-check-circle text-green-600 mt-1"></i>
            <span class="text-gray-800">{{ prompt }}</span>
          </li>
        </ul>
      </div>

      <!-- Temps de préparation -->
      <div class="flex gap-4 mt-6 p-4 bg-blue-50 rounded-lg">
        <div class="flex-1">
          <p class="text-sm text-gray-600">Temps de préparation</p>
          <p class="text-2xl font-bold text-blue-600">{{ teil.preparation_time || '3' }} min</p>
        </div>
        <div class="flex-1">
          <p class="text-sm text-gray-600">Temps de présentation</p>
          <p class="text-2xl font-bold text-blue-600">{{ teil.time_minutes }} min</p>
        </div>
      </div>
    </div>

    <!-- Checkbox pour marquer comme fait -->
    <div class="bg-white p-4 rounded-lg border border-gray-200">
      <div class="flex items-center gap-3">
        <Checkbox 
          v-model="isCompleted" 
          :binary="true"
          inputId="sprechen-done"
          @update:modelValue="handleComplete"
        />
        <label for="sprechen-done" class="cursor-pointer text-gray-800">
          J'ai pris connaissance des consignes et je suis prêt(e) à passer cette épreuve avec un examinateur
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  teil: any
  questionIndex: number
  userAnswer?: boolean
}>()

const emit = defineEmits<{
  answer: [value: boolean]
}>()

const isCompleted = ref(props.userAnswer || false)

const handleComplete = (value: boolean) => {
  emit('answer', value)
}

watch(() => props.userAnswer, (newVal) => {
  isCompleted.value = newVal || false
})
</script>