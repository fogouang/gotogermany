<template>
  <header class="bg-card border-b border-line sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 h-14 flex items-center gap-3">
      <!-- Quitter -->
      <button
        type="button"
        class="w-8 h-8 shrink-0 flex items-center justify-center rounded-full text-muted hover:bg-card-2 hover:text-ink transition-colors"
        :aria-label="t('session.quit')"
        @click="emit('exit')"
      >
        <i class="pi pi-times text-sm"></i>
      </button>

      <!-- Examen / module / Teil -->
      <div class="min-w-0 flex-1">
        <p class="text-sm font-semibold text-ink leading-tight truncate">
          {{ examName }}
          <span class="font-normal text-faint">· {{ t("session.subject") }} {{ subjectNumber }}</span>
        </p>
        <p class="text-xs text-muted leading-tight truncate">
          {{ moduleName }} · {{ teilLabel }}
        </p>
      </div>

      <!-- Progression des réponses -->
      <div class="hidden md:flex flex-col items-end gap-1 w-40 shrink-0">
        <span class="text-[11px] text-muted">
          {{ t("session.player.answered", { answered, total }) }}
        </span>
        <div class="w-full h-1.5 rounded-full bg-card-2 overflow-hidden">
          <div
            class="h-full bg-primary rounded-full transition-all duration-300"
            :style="{ width: `${progress}%` }"
          />
        </div>
      </div>

      <!-- Taille du texte -->
      <div class="flex items-center rounded-lg border border-line overflow-hidden shrink-0">
        <button
          type="button"
          class="w-8 h-8 flex items-center justify-center text-xs font-semibold text-ink hover:bg-card-2 disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="!canFontDown"
          :aria-label="t('session.player.font_smaller')"
          :title="t('session.player.font_smaller')"
          @click="emit('font', -1)"
        >
          A−
        </button>
        <span class="w-px h-5 bg-line"></span>
        <button
          type="button"
          class="w-8 h-8 flex items-center justify-center text-sm font-semibold text-ink hover:bg-card-2 disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="!canFontUp"
          :aria-label="t('session.player.font_bigger')"
          :title="t('session.player.font_bigger')"
          @click="emit('font', 1)"
        >
          A+
        </button>
      </div>

      <!-- Chrono -->
      <div
        :class="[
          'flex items-center gap-2 px-3 py-1.5 rounded-lg font-mono text-sm sm:text-base font-bold tabular-nums shrink-0 transition-colors',
          timeRemaining < 60
            ? 'bg-red-500/10 text-red-600 animate-pulse'
            : timeRemaining < 300
              ? 'bg-amber-500/10 text-amber-600'
              : 'bg-card-2 text-ink',
        ]"
        role="timer"
      >
        <i class="pi pi-clock text-xs"></i>
        <span>{{ formattedTime }}</span>
      </div>
    </div>

    <!-- Teile du bloc -->
    <div class="max-w-7xl mx-auto px-3 sm:px-4 pb-2 flex gap-1">
      <div
        v-for="i in stepCount"
        :key="i"
        :class="[
          'h-1 flex-1 rounded-full transition-colors',
          i - 1 < stepIndex ? 'bg-primary' : i - 1 === stepIndex ? 'bg-primary/50' : 'bg-card-2',
        ]"
      />
    </div>
  </header>
</template>

<script setup lang="ts">
const { t } = useI18n();

const emit = defineEmits<{ exit: []; font: [delta: number] }>();

const props = defineProps<{
  examName: string;
  subjectNumber: number;
  moduleName: string;
  teilLabel: string;
  stepIndex: number;
  stepCount: number;
  answered: number;
  total: number;
  timeRemaining: number;
  canFontDown: boolean;
  canFontUp: boolean;
}>();

const progress = computed(() =>
  props.total > 0 ? Math.round((props.answered / props.total) * 100) : 0,
);

const formattedTime = computed(() => {
  const total = Math.max(0, props.timeRemaining);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const mm = String(m).padStart(2, "0");
  const ss = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
});
</script>