<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    micActive?: boolean;
    speaking?: boolean;
    cameraEnabled?: boolean;
  }>(),
  {
    micActive: false,
    speaking: false,
    cameraEnabled: false,
  },
);

const emit = defineEmits<{
  "camera-error": [];
}>();

const { t } = useI18n();

// ── Niveau du micro (anneau qui réagit à la voix) ──
// Flux dédié à l'affichage : rien n'est envoyé au serveur ici.
const level = ref(0);
let meterStream: MediaStream | null = null;
let meterCtx: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let rafId = 0;

async function startMeter() {
  stopMeter();
  try {
    meterStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    return;
  }
  meterCtx = new AudioContext();
  const source = meterCtx.createMediaStreamSource(meterStream);
  analyser = meterCtx.createAnalyser();
  analyser.fftSize = 256;
  source.connect(analyser);

  const data = new Uint8Array(analyser.fftSize);
  const tick = () => {
    if (!analyser) return;
    analyser.getByteTimeDomainData(data);
    let sum = 0;
    for (const v of data) {
      const x = (v - 128) / 128;
      sum += x * x;
    }
    level.value = Math.min(1, Math.sqrt(sum / data.length) * 4);
    rafId = requestAnimationFrame(tick);
  };
  tick();
}

function stopMeter() {
  cancelAnimationFrame(rafId);
  analyser = null;
  meterStream?.getTracks().forEach((track) => track.stop());
  meterStream = null;
  meterCtx?.close();
  meterCtx = null;
  level.value = 0;
}

watch(
  () => props.micActive,
  (on) => {
    if (on) startMeter();
    else stopMeter();
  },
);

// ── Webcam (locale uniquement, rien n'est envoyé au serveur) ──
const videoEl = ref<HTMLVideoElement | null>(null);
const camError = ref(false);
let camStream: MediaStream | null = null;

async function startCam() {
  camError.value = false;
  try {
    camStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 320, height: 240, facingMode: "user" },
      audio: false,
    });
    await nextTick();
    if (videoEl.value) videoEl.value.srcObject = camStream;
  } catch {
    camError.value = true;
    emit("camera-error");
  }
}

function stopCam() {
  camStream?.getTracks().forEach((track) => track.stop());
  camStream = null;
  if (videoEl.value) videoEl.value.srcObject = null;
}

watch(
  () => props.cameraEnabled,
  (on) => {
    if (on) startCam();
    else stopCam();
  },
);

const showVideo = computed(() => props.cameraEnabled && !camError.value);

const pulseStyle = computed(() => ({
  transform: `scale(${1 + level.value * 0.6})`,
  opacity: 0.25 + level.value * 0.6,
}));

onMounted(() => {
  if (props.micActive) startMeter();
  if (props.cameraEnabled) startCam();
});

onBeforeUnmount(() => {
  stopMeter();
  stopCam();
});
</script>

<template>
  <div
    class="relative overflow-hidden rounded-card border bg-card-2 shadow-soft transition-colors duration-300"
    :class="speaking ? 'border-primary/70' : 'border-line'"
  >
    <video
      v-show="showVideo"
      ref="videoEl"
      autoplay
      muted
      playsinline
      class="size-full -scale-x-100 object-cover"
    />

    <div v-if="!showVideo" class="grid size-full place-items-center">
      <span class="relative grid size-14 place-items-center">
        <span
          class="absolute inset-0 rounded-full bg-primary/40 transition-transform duration-100"
          :style="pulseStyle"
        />
        <span
          class="relative grid size-14 place-items-center rounded-full bg-primary text-primary-950"
        >
          <i class="pi pi-user text-xl" />
        </span>
      </span>
    </div>

    <div
      class="absolute bottom-1.5 left-1.5 flex items-center gap-1 rounded-md bg-canvas/75 px-1.5 py-0.5 text-[0.65rem] font-semibold text-ink backdrop-blur"
    >
      <i
        class="pi pi-microphone text-[0.6rem]"
        :class="level > 0.08 ? 'text-primary' : 'text-faint'"
      />
      {{ t("sprechen_subject.you") }}
    </div>
  </div>
</template>