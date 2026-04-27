<template>
  <div class="space-y-6">
    <!-- Audio player si présent (Hören Teil 3) -->
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

    <!-- Stimulus text (le texte du blog) -->
    <div
      v-if="teil.stimulus_text"
      class="bg-gray-50 p-6 rounded-lg border-l-4 border-indigo-500"
    >
      <div class="prose max-w-none whitespace-pre-line text-gray-800">
        {{ teil.stimulus_text }}
      </div>
    </div>

    <!-- Question -->
    <div v-if="currentQuestion" class="space-y-4">
      <p class="text-lg font-medium text-gray-900">
        {{ currentQuestion.number }}. {{ currentQuestion.statement }}
      </p>
      <div class="flex gap-4">
        <div
          class="flex-1 p-4 border-2 rounded-lg cursor-pointer transition-all"
          :class="
            userAnswer === 'richtig'
              ? 'border-green-500 bg-green-50'
              : 'border-gray-200 hover:border-green-300'
          "
          @click="selectAnswer('richtig')"
        >
          <div class="flex items-center gap-3">
            <RadioButton
              :modelValue="userAnswer"
              value="richtig"
              name="answer"
            />
            <label class="font-medium cursor-pointer">Richtig</label>
          </div>
        </div>
        <div
          class="flex-1 p-4 border-2 rounded-lg cursor-pointer transition-all"
          :class="
            userAnswer === 'falsch'
              ? 'border-red-500 bg-red-50'
              : 'border-gray-200 hover:border-red-300'
          "
          @click="selectAnswer('falsch')"
        >
          <div class="flex items-center gap-3">
            <RadioButton
              :modelValue="userAnswer"
              value="falsch"
              name="answer"
            />
            <label class="font-medium cursor-pointer">Falsch</label>
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
  userAnswer?: string;
}>();

const emit = defineEmits<{
  answer: [value: string];
}>();

const audioPlayer = ref<HTMLAudioElement | null>(null)
const audioPlayCount = ref(0)

const currentQuestion = computed(() => {
  return props.teil.questions?.[props.questionIndex];
});

const getAudioPath = (audioFile: string) => {
  const cleanPath = audioFile.replace(/\\/g, '/');
  const filename = cleanPath.split('/').pop();
  return `/data/audio/${filename}`;
}

const handleAudioEnded = () => {
  audioPlayCount.value++
}

const selectAnswer = (value: string) => {
  emit("answer", value);
};
</script>