<template>
  <div
    :class="[
      'rounded-leaf border px-4 py-3 transition-colors',
      state === 'playing' || state === 'gap'
        ? 'border-primary/40 bg-primary/5'
        : 'border-line bg-card-2',
    ]"
  >
    <div class="flex items-center gap-3">
      <!-- Icône d'état / bouton si lecture bloquée -->
      <button
        v-if="state === 'blocked'"
        type="button"
        class="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-white hover:opacity-90"
        :aria-label="t('session.horen.blocked_action')"
        @click="playOnce"
      >
        <i class="pi pi-play text-sm"></i>
      </button>
      <div
        v-else
        :class="[
          'flex size-9 shrink-0 items-center justify-center rounded-full',
          state === 'playing'
            ? 'bg-primary text-white'
            : state === 'done'
              ? 'bg-emerald-500/10 text-emerald-600'
              : state === 'error'
                ? 'bg-red-500/10 text-red-500'
                : 'border border-line bg-card text-muted',
        ]"
      >
        <i :class="['pi text-sm', stateIcon, state === 'playing' ? 'animate-pulse' : '']"></i>
      </div>

      <!-- Statut, écoutes et progression -->
      <div class="min-w-0 flex-1">
        <div class="flex items-center justify-between gap-2">
          <p class="truncate text-sm font-medium text-ink">{{ stateLabel }}</p>
          <span class="flex shrink-0 items-center gap-1.5">
            <span
              v-for="n in maxPlays"
              :key="n"
              :class="['size-2 rounded-full', n <= playsUsed ? 'bg-primary' : 'bg-line']"
            />
            <span class="ml-0.5 text-xs tabular-nums text-muted">
              {{ t("session.horen.play_count", { n: Math.min(Math.max(playsUsed, 1), maxPlays), total: maxPlays }) }}
            </span>
          </span>
        </div>

        <!-- Progression (non cliquable : pas de retour en arrière) -->
        <div class="mt-2 flex items-center gap-2">
          <span class="w-9 text-[11px] tabular-nums text-faint">{{ formatTime(currentTime) }}</span>
          <div class="h-2.5 flex-1 overflow-hidden rounded-full bg-line/60">
            <div
              class="h-full rounded-full bg-primary transition-[width] duration-300"
              :style="{ width: `${progress}%` }"
            />
          </div>
          <span class="w-9 text-right text-[11px] tabular-nums text-faint">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- Volume : icône + petit panneau -->
      <div class="relative shrink-0">
        <button
          type="button"
          class="flex size-9 items-center justify-center rounded-full text-muted transition-colors hover:bg-card hover:text-ink"
          :aria-label="t('session.horen.volume')"
          :aria-expanded="volumeOpen"
          @click="volumeOpen = !volumeOpen"
        >
          <i :class="['pi text-sm', volumeIcon]"></i>
        </button>
        <div
          v-if="volumeOpen"
          class="absolute right-0 top-full z-20 mt-2 flex items-center gap-2 rounded-leaf border border-line bg-card px-3 py-2 shadow-soft"
          @mouseleave="volumeOpen = false"
        >
          <input
            v-model.number="volume"
            type="range"
            min="0"
            max="1"
            step="0.05"
            class="w-28 cursor-pointer accent-current text-primary"
            :aria-label="t('session.horen.volume')"
          />
          <span class="w-8 text-right text-xs tabular-nums text-muted">{{ Math.round(volume * 100) }}</span>
        </div>
      </div>
    </div>

    <audio
      ref="audioEl"
      :src="src"
      preload="auto"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @loadedmetadata="onLoaded"
      @error="onError"
    />
  </div>
</template>

<script setup lang="ts">
type PlayerState = "waiting" | "playing" | "gap" | "blocked" | "done" | "error";

const { t } = useI18n();

const props = withDefaults(
  defineProps<{
    src: string;
    maxPlays?: number;
    playsUsed?: number;   // écoutes déjà démarrées (géré par le parent)
    active?: boolean;     // c'est au tour de cet audio
    gapSeconds?: number;  // pause entre deux écoutes
  }>(),
  { maxPlays: 1, playsUsed: 0, active: false, gapSeconds: 5 },
);

const emit = defineEmits<{
  start: [];  // une écoute démarre (le parent incrémente playsUsed)
  done: [];   // toutes les écoutes sont terminées
}>();

const audioEl = ref<HTMLAudioElement>();
const state = ref<PlayerState>(props.playsUsed >= props.maxPlays ? "done" : "waiting");
const currentTime = ref(0);
const duration = ref(0);
const gapLeft = ref(0);

let gapTimer: ReturnType<typeof setInterval> | null = null;

// ── Volume mémorisé ───────────────────────────────────

const VOLUME_KEY = "gtg_exam_volume";
const volume = ref(1);
const volumeOpen = ref(false);

const volumeIcon = computed(() => {
  if (volume.value <= 0) return "pi-volume-off";
  if (volume.value < 0.5) return "pi-volume-down";
  return "pi-volume-up";
});

watch(volume, (v) => {
  if (audioEl.value) audioEl.value.volume = v;
  try {
    localStorage.setItem(VOLUME_KEY, String(v));
  } catch {
    /* stockage indisponible */
  }
});

// ── Affichage ─────────────────────────────────────────

const progress = computed(() =>
  duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0,
);

const stateIcon = computed(() => {
  switch (state.value) {
    case "playing": return "pi-volume-up";
    case "gap": return "pi-replay";
    case "done": return "pi-check";
    case "error": return "pi-exclamation-triangle";
    default: return "pi-clock";
  }
});

const stateLabel = computed(() => {
  switch (state.value) {
    case "playing": return t("session.horen.playing");
    case "gap": return t("session.horen.replay_in", { n: gapLeft.value });
    case "blocked": return t("session.horen.blocked");
    case "done": return t("session.horen.finished");
    case "error": return t("session.horen.audio_error");
    default: return t("session.horen.waiting");
  }
});

const formatTime = (s: number) => {
  if (!Number.isFinite(s)) return "0:00";
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
};

// ── Lecture ───────────────────────────────────────────

function clearGap() {
  if (gapTimer) {
    clearInterval(gapTimer);
    gapTimer = null;
  }
}

async function playOnce() {
  const el = audioEl.value;
  if (!el) return;
  clearGap();
  el.currentTime = 0;
  el.volume = volume.value;
  try {
    await el.play();
    state.value = "playing";
    emit("start");
  } catch {
    // Lecture automatique refusée : on attend un clic
    state.value = "blocked";
  }
}

function beginNext() {
  if (props.playsUsed >= props.maxPlays) {
    state.value = "done";
    emit("done");
    return;
  }
  playOnce();
}

function startGap() {
  state.value = "gap";
  gapLeft.value = props.gapSeconds;
  gapTimer = setInterval(() => {
    gapLeft.value--;
    if (gapLeft.value <= 0) {
      clearGap();
      playOnce();
    }
  }, 1000);
}

function onEnded() {
  currentTime.value = 0;
  if (props.playsUsed < props.maxPlays) startGap();
  else {
    state.value = "done";
    emit("done");
  }
}

function onTimeUpdate() {
  currentTime.value = audioEl.value?.currentTime ?? 0;
}

function onLoaded() {
  duration.value = audioEl.value?.duration ?? 0;
}

function onError() {
  state.value = "error";
  if (props.active) emit("done"); // ne bloque pas l'enchaînement des audios
}

// ── Cycle de vie ──────────────────────────────────────

watch(
  () => props.active,
  (isActive) => {
    if (isActive && state.value !== "playing") beginNext();
  },
);

onMounted(() => {
  try {
    const raw = localStorage.getItem(VOLUME_KEY);
    if (raw !== null) {
      const v = Number(raw);
      if (v >= 0 && v <= 1) volume.value = v;
    }
  } catch {
    /* ignore */
  }
  if (props.active) beginNext();
});

onBeforeUnmount(() => {
  clearGap();
  audioEl.value?.pause();
});
</script>