<template>
  <div class="space-y-6">
    <!-- Audio player -->
    <div
      v-if="teil.audio_file"
      class="bg-indigo-50 p-6 rounded-lg border-2 border-indigo-500"
    >
      <div class="flex items-center gap-4 mb-4">
        <i class="pi pi-volume-up text-indigo-600 text-2xl"></i>
        <div class="flex-1">
          <h3 class="font-bold text-gray-900">Diskussionsrunde</h3>
          <p class="text-sm text-gray-600">{{ getSpeakersText() }}</p>
        </div>
      </div>

      <audio
        ref="audioPlayer"
        controls
        class="w-full"
        @ended="handleAudioEnded"
      >
        <source :src="getAudioPath(teil.audio_file)" type="audio/mpeg" />
        Votre navigateur ne supporte pas l'élément audio.
      </audio>

      <div class="mt-4 flex items-center gap-2 text-sm text-gray-600">
        <i class="pi pi-info-circle"></i>
        <span>Vous pouvez écouter l'audio {{ audioPlayCount }}/2 fois</span>
      </div>
    </div>

    <!-- Liste des speakers -->
    <div v-if="teil.speakers" class="bg-blue-50 p-4 rounded-lg">
      <h4 class="font-semibold text-gray-900 mb-2">Sprecher:</h4>
      <div class="flex flex-col gap-2">
        <div
          v-for="(name, key) in teil.speakers"
          :key="key"
          class="px-4 py-2 bg-white rounded-lg font-medium border-2 border-blue-300"
        >
          <span class="font-bold text-blue-600"
            >{{ String(key).toUpperCase() }})</span
          >
          {{ name }}
        </div>
      </div>
    </div>

    <!-- Question actuelle -->
    <div
      v-if="currentQuestion"
      class="bg-white p-6 rounded-lg border border-gray-200"
    >
      <p class="text-lg font-medium text-gray-900 mb-4">
        {{ currentQuestion.number }}. {{ currentQuestion.statement }}
      </p>

      <div class="space-y-3">
        <div
          v-for="(name, key) in teil.speakers"
          :key="key"
          class="p-4 border-2 rounded-lg cursor-pointer transition-all"
          :class="
            userAnswer === String(key)
              ? 'border-indigo-500 bg-indigo-50'
              : 'border-gray-200 hover:border-indigo-300'
          "
          @click="selectAnswer(String(key))"
        >
          <div class="flex items-center gap-3">
            <RadioButton
              :modelValue="userAnswer"
              :value="String(key)"
              :name="`answer-${currentQuestion.number}`"
            />
            <label class="cursor-pointer font-medium">
              <span class="font-bold text-indigo-600"
                >{{ String(key).toUpperCase() }})</span
              >
              {{ name }}
            </label>
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

const audioPlayer = ref<HTMLAudioElement | null>(null);
const audioPlayCount = ref(0);

const currentQuestion = computed(() => {
  return props.teil.questions?.[props.questionIndex];
});

const getSpeakersText = () => {
  if (!props.teil.speakers) return "Mehrere Sprecher";
  return Object.values(props.teil.speakers).join(", ");
};

const getAudioPath = (audioFile: string) => {
  const cleanPath = audioFile.replace(/\\/g, "/");
  const filename = cleanPath.split("/").pop();
  return `/data/audio/${filename}`;
};

const handleAudioEnded = () => {
  audioPlayCount.value++;
};

const selectAnswer = (answer: string) => {
  emit("answer", answer);
};
</script>
