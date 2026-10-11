<template>
  <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
    <!-- Phase lecture -->
    <div v-if="phase === 'reading'" class="text-center space-y-3">
      <div class="flex items-center justify-center gap-2 text-amber-700">
        <i class="pi pi-eye"></i>
        <span class="text-sm font-medium">Lisez les questions</span>
      </div>
      <div class="text-3xl font-mono font-bold text-amber-600">
        {{ readCountdown }}
      </div>
      <p class="text-xs text-gray-400">L'audio démarrera automatiquement</p>
    </div>

    <!-- Phase écoute -->
    <div v-else class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <button
            :class="[
              'w-9 h-9 rounded-full flex items-center justify-center transition-colors',
              isPlaying
                ? 'bg-teal-600 text-white'
                : playsUsed >= maxPlays
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-teal-600 text-white hover:bg-teal-700',
            ]"
            :disabled="playsUsed >= maxPlays && !isPlaying"
            @click="togglePlay"
          >
            <i :class="['pi text-sm', isPlaying ? 'pi-pause' : 'pi-play']"></i>
          </button>
          <span class="text-sm text-gray-600">
            {{
              isPlaying
                ? "En cours..."
                : playsUsed >= maxPlays
                  ? "Audio terminé"
                  : "Écouter"
            }}
          </span>
        </div>

        <!-- Compteur écoutes -->
        <!-- <div class="flex items-center gap-1">
          <div
            v-for="n in maxPlays"
            :key="n"
            :class="[
              'w-2 h-2 rounded-full',
              n <= playsUsed ? 'bg-teal-600' : 'bg-gray-300',
            ]"
          />
          <span class="text-xs text-gray-400 ml-1"
            >{{ playsUsed }}/{{ maxPlays }}</span
          >
        </div> -->
      </div>

      <!-- Barre de progression -->
      <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
        <div
          class="bg-teal-500 h-1.5 rounded-full transition-all duration-300"
          :style="{ width: `${progress}%` }"
        />
      </div>

      <!-- Temps -->
      <div class="flex justify-between text-xs text-gray-400">
        <span>{{ formatTime(currentTime) }}</span>
        <span>{{ formatTime(duration) }}</span>
      </div>
    </div>

    <!-- Audio element -->
    <audio
      ref="audioEl"
      :src="src"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @loadedmetadata="onLoaded"
    />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  src: string;
  maxPlays?: number;
  readTime?: number; // secondes de lecture avant de pouvoir écouter
}>();

const audioEl = ref<HTMLAudioElement>();
const isPlaying = ref(false);
const playsUsed = ref(0);
const currentTime = ref(0);
const duration = ref(0);
const phase = ref<"reading" | "listening">("listening");
const readCountdown = ref(props.readTime || 0);

let readTimer: ReturnType<typeof setInterval> | null = null;

const maxPlays = computed(() => props.maxPlays ?? 2);

const progress = computed(() =>
  duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0,
);

// Démarrer le compte à rebours si readTime > 0
onMounted(() => {
  if (props.readTime && props.readTime > 0) {
    phase.value = "reading";
    readTimer = setInterval(() => {
      readCountdown.value--;
      if (readCountdown.value <= 0) {
        clearInterval(readTimer!);
        phase.value = "listening";
        // Auto-play premier écoute
        play();
      }
    }, 1000);
  }
});

onUnmounted(() => {
  if (readTimer) clearInterval(readTimer);
  audioEl.value?.pause();
});

const play = () => {
  if (!audioEl.value || playsUsed.value >= maxPlays.value) return;
  audioEl.value.currentTime = 0;
  audioEl.value.play();
  isPlaying.value = true;
  playsUsed.value++;
};

const togglePlay = () => {
  if (!audioEl.value) return;
  if (isPlaying.value) {
    audioEl.value.pause();
    isPlaying.value = false;
  } else {
    play();
  }
};

const onTimeUpdate = () => {
  currentTime.value = audioEl.value?.currentTime ?? 0;
};

const onEnded = () => {
  isPlaying.value = false;
  currentTime.value = 0;
};

const onLoaded = () => {
  duration.value = audioEl.value?.duration ?? 0;
};

const formatTime = (s: number) => {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
};
</script>
