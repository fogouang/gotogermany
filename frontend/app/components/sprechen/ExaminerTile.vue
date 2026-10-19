<script setup lang="ts">
import ExaminerAvatar from "~/components/sprechen/ExaminerAvatar.vue";

withDefaults(
  defineProps<{
    avatarUrl: string;
    name?: string | null;
    role?: string | null;
    speaking?: boolean;
    listening?: boolean;
  }>(),
  {
    name: null,
    role: null,
    speaking: false,
    listening: false,
  },
);

const { t } = useI18n();

const avatarRef = ref<{
  getAudioOutput: () => { ctx: AudioContext; node: AudioNode } | null;
  resume: () => Promise<void>;
} | null>(null);

defineExpose({
  getAudioOutput: () => avatarRef.value?.getAudioOutput() ?? null,
  resume: () => avatarRef.value?.resume(),
});
</script>

<template>
  <div
    class="relative h-full w-full overflow-hidden rounded-card border bg-linear-to-b from-card-2 to-card shadow-soft transition-colors duration-300"
    :class="speaking ? 'border-primary/60' : 'border-line'"
  >
    <!-- Halo doux derrière l'examinatrice -->
    <div
      class="pointer-events-none absolute left-1/2 top-[-20%] h-3/4 w-3/4 -translate-x-1/2 rounded-full bg-primary/10 blur-3xl"
    />

    <div class="absolute inset-0">
      <ClientOnly>
        <ExaminerAvatar
          ref="avatarRef"
          :avatar-url="avatarUrl"
          :speaking="speaking"
          :listening="listening"
          camera-view="upper"
        >
          <template #fallback>
            <span
              class="grid size-24 place-items-center rounded-full bg-primary/10 text-primary"
            >
              <i class="pi pi-user text-4xl" />
            </span>
          </template>
        </ExaminerAvatar>
      </ClientOnly>
    </div>

    <!-- Dégradé bas pour la lisibilité du badge -->
    <div
      class="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-linear-to-t from-canvas/60 to-transparent"
    />

    <!-- Badge nom -->
    <div
      class="absolute bottom-3 left-3 flex items-center gap-2.5 rounded-leaf bg-canvas/75 px-3 py-2 backdrop-blur-md"
    >
      <div class="flex h-4 items-end gap-0.5" aria-hidden="true">
        <span
          v-for="i in 4"
          :key="i"
          class="w-1 rounded-full bg-primary"
          :class="speaking ? 'voice-bar' : 'h-1 opacity-50'"
          :style="speaking ? { animationDelay: `${i * 0.12}s` } : undefined"
        />
      </div>
      <div class="leading-tight">
        <p class="text-sm font-semibold text-ink">
          {{ name ?? t("sprechen_subject.call.examiner_default_name") }}
        </p>
        <p class="text-[0.7rem] text-muted">
          {{ role ?? t("sprechen_subject.call.examiner_role") }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.voice-bar {
  animation: voice-bar 0.9s ease-in-out infinite;
}

@keyframes voice-bar {
  0%,
  100% {
    height: 25%;
  }
  50% {
    height: 100%;
  }
}
</style>