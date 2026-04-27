<template>
  <div class="space-y-6">
    <!-- Stats rapides -->
    <div class="grid grid-cols-2 gap-3">
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-gray-900">
          {{ sessionStore.answeredQuestions }}
        </div>
        <div class="text-xs text-gray-500">Répondues</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-gray-900">
          {{ sessionStore.totalQuestions - sessionStore.answeredQuestions }}
        </div>
        <div class="text-xs text-gray-500">Restantes</div>
      </div>
    </div>

    <!-- Légende -->
    <div class="flex items-center gap-4 text-xs text-gray-500">
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded bg-teal-600"></div>
        <span>Répondue</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded bg-gray-200"></div>
        <span>Non répondue</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-4 h-4 rounded border-2 border-teal-600 bg-white"></div>
        <span>Actuelle</span>
      </div>
    </div>

    <!-- Navigation par module et teil -->
    <div
      v-for="module in sessionStore.modules"
      :key="module.id"
      class="space-y-3"
    >
      <!-- Module header -->
      <div class="flex items-center gap-2">
        <div
          :class="['w-6 h-6 rounded flex items-center justify-center', getModuleColor(module.slug)]"
        >
          <i :class="['pi text-xs', getModuleIcon(module.slug)]"></i>
        </div>
        <h4 class="font-semibold text-sm text-gray-900">{{ module.name }}</h4>
      </div>

      <!-- Teile -->
      <div
        v-for="teil in module.teile"
        :key="teil.id"
        class="pl-4 space-y-2"
      >
        <p class="text-xs text-gray-500 font-medium">
          Teil {{ teil.teil_number }}
        </p>

        <!-- Grille de questions -->
        <div class="flex flex-wrap gap-2">
          <button
            v-for="question in teil.questions"
            :key="question.id"
            :class="[
              'w-9 h-9 rounded text-sm font-medium transition-all',
              getQuestionClass(question.id, getGlobalIndex(question.id)),
            ]"
            @click="selectQuestion(getGlobalIndex(question.id))"
          >
            {{ question.question_number }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ select: [index: number] }>()

const sessionStore = useSessionStore()

const getGlobalIndex = (questionId: string): number => {
  return sessionStore.questions.findIndex((q) => q.id === questionId)
}

const getQuestionClass = (questionId: string, globalIndex: number): string => {
  const isCurrent = globalIndex === sessionStore.currentQuestionIndex
  const isAnswered = sessionStore.isAnswered(questionId)

  if (isCurrent)
    return 'border-2 border-teal-600 bg-white text-teal-700 ring-2 ring-teal-200'
  if (isAnswered) return 'bg-teal-600 text-white hover:bg-teal-700'
  return 'bg-gray-200 text-gray-700 hover:bg-gray-300'
}

const selectQuestion = (index: number) => {
  emit('select', index)
}

const getModuleIcon = (slug: string) => {
  const icons: Record<string, string> = {
    horen: 'pi-volume-up',
    lesen: 'pi-book',
    schreiben: 'pi-pencil',
    sprechen: 'pi-microphone',
  }
  for (const key in icons) {
    if (slug.toLowerCase().includes(key)) return icons[key]
  }
  return 'pi-file'
}

const getModuleColor = (slug: string) => {
  const colors: Record<string, string> = {
    horen: 'bg-purple-100 text-purple-600',
    lesen: 'bg-blue-100 text-blue-600',
    schreiben: 'bg-green-100 text-green-600',
    sprechen: 'bg-orange-100 text-orange-600',
  }
  for (const key in colors) {
    if (slug.toLowerCase().includes(key)) return colors[key]
  }
  return 'bg-gray-100 text-gray-600'
}
</script>