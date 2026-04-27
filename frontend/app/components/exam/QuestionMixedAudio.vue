<template>
  <div class="space-y-6">
    <!-- Audio player -->
    <div
      v-if="currentAudio"
      class="bg-indigo-50 p-6 rounded-lg border-2 border-indigo-500"
    >
      <div class="flex items-center gap-4 mb-4">
        <i class="pi pi-volume-up text-indigo-600 text-2xl"></i>
        <div class="flex-1">
          <h3 class="font-bold text-gray-900">
            Audio {{ currentAudio.audio_number }}
          </h3>
          <p class="text-sm text-gray-600">{{ currentAudio.audio_type }}</p>
        </div>
      </div>

      <audio
        ref="audioPlayer"
        controls
        class="w-full"
        @ended="handleAudioEnded"
      >
        <source
          :src="getAudioPath(currentAudio.audio_file)"
          type="audio/mpeg"
        />
        Votre navigateur ne supporte pas l'élément audio.
      </audio>

      <div class="mt-4 flex items-center gap-2 text-sm text-gray-600">
        <i class="pi pi-info-circle"></i>
        <span>Vous pouvez écouter l'audio {{ audioPlayCount }}/2 fois</span>
      </div>
    </div>

    <!-- Questions pour cet audio -->
    <div v-if="currentQuestions" class="space-y-6">
      <div
        v-for="(question, idx) in currentQuestions"
        :key="question.number"
        class="bg-white p-6 rounded-lg border border-gray-200"
      >
        <!-- Question Richtig/Falsch -->
        <div v-if="question.type === 'richtig_falsch'" class="space-y-4">
          <p class="text-lg font-medium text-gray-900">
            {{ question.number }}. {{ question.statement }}
          </p>

          <div class="flex gap-4">
            <div
              class="flex-1 p-4 border-2 rounded-lg cursor-pointer transition-all"
              :class="
                userAnswers[question.number] === 'richtig'
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-green-300'
              "
              @click="selectAnswer(question.number, 'richtig')"
            >
              <div class="flex items-center gap-3">
                <RadioButton
                  :modelValue="userAnswers[question.number]"
                  value="richtig"
                  :name="`answer-${question.number}`"
                />
                <label class="font-medium cursor-pointer">Richtig</label>
              </div>
            </div>

            <div
              class="flex-1 p-4 border-2 rounded-lg cursor-pointer transition-all"
              :class="
                userAnswers[question.number] === 'falsch'
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 hover:border-red-300'
              "
              @click="selectAnswer(question.number, 'falsch')"
            >
              <div class="flex items-center gap-3">
                <RadioButton
                  :modelValue="userAnswers[question.number]"
                  value="falsch"
                  :name="`answer-${question.number}`"
                />
                <label class="font-medium cursor-pointer">Falsch</label>
              </div>
            </div>
          </div>
        </div>

        <!-- Question QCM -->
        <div v-else-if="question.type === 'qcm_abc'" class="space-y-4">
          <p class="text-lg font-medium text-gray-900">
            {{ question.number }}. {{ question.stem }}
          </p>

          <div class="space-y-3">
            <div
              v-for="(option, key) in question.options"
              :key="key"
              class="p-4 border-2 rounded-lg cursor-pointer transition-all"
              :class="
                userAnswers[question.number] === key
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-indigo-300'
              "
              @click="selectAnswer(question.number, key)"
            >
              <div class="flex items-start gap-3">
                <RadioButton
                  :modelValue="userAnswers[question.number]"
                  :value="key"
                  :name="`answer-${question.number}`"
                />
                <label class="cursor-pointer flex-1">
                  <span class="font-bold text-indigo-600"
                    >{{ String(key).toUpperCase() }})</span
                  >
                  {{ option }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  teil: any;
  questionIndex: number;
  userAnswer?: any;
}>();

const emit = defineEmits<{
  answer: [value: any];
}>();

const audioPlayer = ref<HTMLAudioElement | null>(null);
const audioPlayCount = ref(0);
const userAnswers = ref<Record<number, any>>({});

// Trouver l'audio actuel basé sur questionIndex
const currentAudioIndex = computed(() => {
  if (!props.teil.audios) return 0;

  let questionCount = 0;
  for (let i = 0; i < props.teil.audios.length; i++) {
    const audio = props.teil.audios[i];
    const audioQuestionsCount = audio.questions?.length || 0;

    if (props.questionIndex < questionCount + audioQuestionsCount) {
      return i;
    }
    questionCount += audioQuestionsCount;
  }
  return 0;
});

const currentAudio = computed(() => {
  return props.teil.audios?.[currentAudioIndex.value];
});

const currentQuestions = computed(() => {
  return currentAudio.value?.questions || [];
});

const getAudioPath = (audioFile: string) => {
  // Nettoie le chemin et retourne le bon path
  const cleanPath = audioFile.replace(/\\/g, "/");
  const filename = cleanPath.split("/").pop();
  return `/data/audio/${filename}`;
};

const handleAudioEnded = () => {
  audioPlayCount.value++;
  if (audioPlayCount.value >= 2) {
    // Limite de 2 écoutes
    console.log("Limite d'écoute atteinte");
  }
};

const selectAnswer = (questionNumber: number, answer: any) => {
  userAnswers.value[questionNumber] = answer;

  // Émettre toutes les réponses pour cet audio
  emit("answer", userAnswers.value);
};

// Initialiser les réponses depuis userAnswer
watch(
  () => props.userAnswer,
  (newVal) => {
    if (newVal && typeof newVal === "object") {
      userAnswers.value = { ...newVal };
    }
  },
  { immediate: true },
);

// Reset play count quand on change d'audio
watch(currentAudioIndex, () => {
  audioPlayCount.value = 0;
});
</script>
