<script setup lang="ts">
const props = defineProps<{
  state: "preparing" | "agent" | "student" | "waiting";
  timerLabel?: string | null;
  timerAlert?: boolean;
  transcriptAvailable: boolean;
  transcriptVisible: boolean;
  cameraEnabled: boolean;
}>();

const emit = defineEmits<{
  "toggle-transcript": [];
  "toggle-camera": [];
}>();

const { t } = useI18n();

const status = computed(() => {
  switch (props.state) {
    case "preparing":
      return {
        label: t("sprechen_subject.call.status_preparing"),
        icon: "pi pi-pause-circle",
        cls: "bg-card-2 text-muted",
      };
    case "agent":
      return {
        label: t("sprechen_subject.examiner_speaking"),
        icon: "pi pi-volume-up",
        cls: "bg-primary/15 text-primary",
      };
    case "student":
      return {
        label: t("sprechen_subject.your_turn"),
        icon: "pi pi-microphone",
        cls: "bg-emerald-500/15 text-emerald-600",
      };
    default:
      return {
        label: t("sprechen_subject.call.status_waiting"),
        icon: "pi pi-clock",
        cls: "bg-card-2 text-muted",
      };
  }
});

const toggleClass = (on: boolean) =>
  on
    ? "border-primary/40 bg-primary/10 text-primary"
    : "border-line text-muted hover:bg-card-2 hover:text-ink";
</script>

<template>
  <div
    class="shrink-0 border-t border-line bg-card/80 px-4 py-3 backdrop-blur-md"
  >
    <div class="flex flex-wrap items-center justify-between gap-3">
      <!-- Statut -->
      <span
        class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold"
        :class="status.cls"
      >
        <i :class="status.icon" class="text-[0.7rem]" />
        {{ status.label }}
      </span>

      <!-- Chrono du Teil -->
      <span
        v-if="timerLabel"
        class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold tabular-nums"
        :class="
          timerAlert
            ? 'animate-pulse border-red-400/40 bg-red-500/15 text-red-600'
            : 'border-primary/25 bg-primary/10 text-primary'
        "
      >
        <i class="pi pi-clock text-[0.7rem]" />
        {{ timerLabel }}
      </span>

      <!-- Actions -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          :aria-label="
            cameraEnabled
              ? t('sprechen_subject.call.camera_off')
              : t('sprechen_subject.call.camera_on')
          "
          class="grid size-10 place-items-center rounded-full border transition-colors"
          :class="toggleClass(cameraEnabled)"
          @click="emit('toggle-camera')"
        >
          <i
            :class="cameraEnabled ? 'pi pi-video' : 'pi pi-eye-slash'"
            class="text-sm"
          />
        </button>

        <button
          v-if="transcriptAvailable"
          type="button"
          :aria-label="
            transcriptVisible
              ? t('sprechen_subject.call.hide_transcript')
              : t('sprechen_subject.call.show_transcript')
          "
          class="grid size-10 place-items-center rounded-full border transition-colors"
          :class="toggleClass(transcriptVisible)"
          @click="emit('toggle-transcript')"
        >
          <i class="pi pi-align-left text-sm" />
        </button>
      </div>
    </div>
  </div>
</template>