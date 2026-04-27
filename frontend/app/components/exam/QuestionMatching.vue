<template>
  <div class="space-y-6">
    <!-- Annonces (a-j) -->
    <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
      <h3 class="font-bold text-gray-900 mb-4">Anzeigen</h3>
      <div class="grid gap-4">
        <div 
          v-for="(text, key) in teil.anzeigen" 
          :key="key"
          class="bg-white p-4 rounded border-l-4 border-indigo-500"
        >
          <div class="flex items-start gap-3">
            <span class="font-bold text-indigo-600 text-lg">{{ key }})</span>
            <p class="text-gray-800">{{ text }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Situations avec input -->
    <div class="space-y-4">
      <h3 class="font-bold text-gray-900 mb-4">Situationen</h3>
      
      <div 
        v-for="question in getCurrentQuestions" 
        :key="question.number"
        class="bg-white p-6 rounded-lg border-2 border-gray-200"
      >
        <div class="flex items-start gap-4">
          <span class="font-bold text-gray-900 text-lg">{{ question.number }}.</span>
          <div class="flex-1">
            <p class="text-gray-800 mb-4">{{ question.situation }}</p>
            
            <div class="flex items-center gap-3">
              <label class="text-sm font-medium text-gray-700">Anzeige:</label>
              
              <!-- Input avec boutons helper -->
              <div class="flex items-center gap-2">
                <InputText
                  v-model="userAnswers[question.number]"
                  class="w-16 text-center font-bold"
                  maxlength="1"
                  @input="handleInput(question.number)"
                  placeholder="-"
                />
                
                <!-- Boutons quick select -->
                <div class="flex gap-1 flex-wrap">
                  <Button
                    v-for="letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', '0']"
                    :key="letter"
                    :label="letter"
                    size="small"
                    :outlined="userAnswers[question.number] !== letter"
                    :severity="userAnswers[question.number] === letter ? 'success' : 'secondary'"
                    @click="selectAnswer(question.number, letter)"
                    class="w-8 h-8 p-0"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Info -->
    <div class="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
      <div class="flex items-start gap-3">
        <i class="pi pi-info-circle text-yellow-600 mt-1"></i>
        <div class="text-sm text-gray-700">
          <p class="font-semibold mb-1">Rappel :</p>
          <ul class="list-disc list-inside space-y-1">
            <li>Chaque annonce (a-j) peut être utilisée une seule fois</li>
            <li>Si aucune annonce ne correspond, écrivez <strong>0</strong></li>
            <li>Quatre annonces resteront inutilisées</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  teil: any
  questionIndex: number
  userAnswer?: Record<number, string>
}>()

const emit = defineEmits<{
  answer: [value: Record<number, string>]
}>()

const userAnswers = ref<Record<number, string>>({})

const getCurrentQuestions = computed(() => {
  return props.teil.questions || []
})

const handleInput = (questionNumber: number) => {
  const value = userAnswers.value[questionNumber]?.toLowerCase()
  
  // Valide seulement a-j ou 0
  if (value && !/^[a-j0]$/.test(value)) {
    userAnswers.value[questionNumber] = ''
    return
  }
  
  emitAnswers()
}

const selectAnswer = (questionNumber: number, letter: string) => {
  userAnswers.value[questionNumber] = letter
  emitAnswers()
}

const emitAnswers = () => {
  emit('answer', { ...userAnswers.value })
}

// Initialiser depuis userAnswer
watch(() => props.userAnswer, (newVal) => {
  if (newVal && typeof newVal === 'object') {
    userAnswers.value = { ...newVal }
  }
}, { immediate: true })
</script>