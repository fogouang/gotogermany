<template>
  <div class="max-w-3xl mx-auto p-6 space-y-6">

    <!-- Instructions -->
    <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p class="text-sm text-blue-800 font-medium">{{ teil.instructions }}</p>
    </div>

    <!-- Temps de préparation -->
    <div class="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <i class="pi pi-clock text-amber-600"></i>
      <span class="text-sm text-amber-800 font-medium">
        Vous avez {{ teil.time_minutes }} minutes pour cette partie
      </span>
    </div>

    <!-- Teil 1 : planification commune -->
    <div v-if="teil.format_type === 'oral_interaction'" class="space-y-5">
      <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-amber-800 mb-3">Scénario :</p>
        <p class="text-sm text-amber-900">{{ question?.content?.scenario }}</p>
      </div>

      <div v-if="question?.content?.prompts?.length" class="bg-white border border-gray-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-gray-700 mb-3">Points à aborder :</p>
        <ul class="space-y-2">
          <li
            v-for="(prompt, i) in question.content.prompts"
            :key="i"
            class="flex gap-3 text-sm text-gray-700"
          >
            <span class="w-5 h-5 bg-teal-100 text-teal-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
              {{ (i as number)  + 1 }}
            </span>
            {{ prompt }}
          </li>
        </ul>
      </div>

      <!-- Notes de préparation -->
      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <!-- Enregistrement -->
      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre réponse :
        </p>
        <AudioRecorder
          v-if="sessionId"
          :session-id="sessionId"
          :teil-number="teil.teil_number"
          :question-id="question?.id || ''"
          @recorded="onRecorded"
        />
      </div>
    </div>

    <!-- Teil 2 : monologue avec slides -->
    <div v-else-if="teil.format_type === 'oral_monologue'" class="space-y-5">

      <!-- Sélection thème -->
      <div v-if="!selectedTheme" class="space-y-3">
        <p class="text-sm font-semibold text-gray-700">Choisissez votre thème :</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            v-for="(theme, key) in question?.content?.themes"
            :key="key"
            class="p-6 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-teal-400 transition-colors"
            @click="selectedTheme = (key as string)"
          >
            <p class="font-semibold text-gray-900">{{ theme.title }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ theme.slides?.length }} folies</p>
          </button>
        </div>
      </div>

      <!-- Slides + enregistrement -->
      <div v-else class="space-y-5">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">
            {{ question?.content?.themes?.[selectedTheme]?.title }}
          </h3>
          <button class="text-xs text-gray-400 hover:text-gray-600" @click="selectedTheme = null">
            Changer de thème
          </button>
        </div>

        <!-- Slides navigation -->
        <div class="flex gap-2 overflow-x-auto pb-2">
          <button
            v-for="(slide, i) in currentSlides"
            :key="i"
            :class="[
              'shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
              activeSlide === (i as number)
                ? 'border-teal-500 bg-teal-50 text-teal-700'
                : 'border-gray-200 text-gray-500 hover:border-gray-300',
            ]"
            @click="activeSlide = (i as number)"
          >
            Folie {{ (i as number) + 1 }}
          </button>
        </div>

        <!-- Folie active -->
        <div class="bg-white border-2 border-teal-200 rounded-xl p-6 min-h-24">
          <div class="flex items-start gap-3">
            <span class="w-8 h-8 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">
              {{ activeSlide + 1 }}
            </span>
            <p class="text-base text-gray-800 font-medium">
              {{ currentSlides[activeSlide] }}
            </p>
          </div>
        </div>

        <!-- Notes -->
        <NotesArea
          :question="question"
          :answer="answers[question?.id]?.user_answer"
          @answer="onNotes"
        />

        <!-- Enregistrement -->
        <div>
          <p class="text-sm font-semibold text-gray-700 mb-3">
            <i class="pi pi-microphone mr-2"></i>Enregistrez votre présentation :
          </p>
          <AudioRecorder
            v-if="sessionId"
            :session-id="sessionId"
            :teil-number="teil.teil_number"
            :question-id="question?.id || ''"
            @recorded="onRecorded"
          />
        </div>
      </div>
    </div>

    <!-- Teil 3 : feedback -->
    <div v-else-if="teil.format_type === 'oral_feedback'" class="space-y-5">
      <div class="bg-white border border-gray-200 rounded-xl p-5">
        <p class="text-sm font-semibold text-gray-700 mb-3">Tâches :</p>
        <ul class="space-y-2">
          <li
            v-for="(task, i) in question?.content?.tasks"
            :key="i"
            class="flex gap-3 text-sm text-gray-700"
          >
            <span class="w-5 h-5 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
              {{ (i as number) + 1 }}
            </span>
            {{ task }}
          </li>
        </ul>
      </div>

      <NotesArea
        :question="question"
        :answer="answers[question?.id]?.user_answer"
        @answer="onNotes"
      />

      <div>
        <p class="text-sm font-semibold text-gray-700 mb-3">
          <i class="pi pi-microphone mr-2"></i>Enregistrez votre réaction :
        </p>
        <AudioRecorder
          v-if="sessionId"
          :session-id="sessionId"
          :teil-number="teil.teil_number"
          :question-id="question?.id || ''"
          @recorded="onRecorded"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AudioRecorder from '~/components/session/AudioRecorder.vue'
import NotesArea from '~/components/session/NotesArea.vue'

const props = defineProps<{
  teil: any
  questions: any[]
  answers: Record<string, any>
  sessionId?: string
}>()

const emit = defineEmits<{ answer: [questionId: string, value: any] }>()

const selectedTheme = ref<string | null>(null)
const activeSlide = ref(0)

const question = computed(() => props.questions[0])

const currentSlides = computed(() => {
  if (!selectedTheme.value) return []
  return question.value?.content?.themes?.[selectedTheme.value]?.slides || []
})

const onNotes = (val: any) => {
  if (!question.value) return
  const existing = props.answers[question.value.id]?.user_answer || {}
  emit('answer', question.value.id, { ...existing, text: val.text })
}

const onRecorded = (audioFile: string, url: string) => {
  if (!question.value) return
  const existing = props.answers[question.value.id]?.user_answer || {}
  emit('answer', question.value.id, { ...existing, audio_file: audioFile })
}
</script>