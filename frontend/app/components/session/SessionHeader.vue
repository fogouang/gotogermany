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
          <!-- Durée conseillée du Teil (Goethe : « vorgeschlagene Arbeitszeit ») -->
          <span v-if="teilMinutes" class="text-faint">
            · {{ t("session.player.suggested_minutes", { n: teilMinutes }) }}
          </span>
        </p>
      </div>

      <!-- Progression des réponses -->
      <div class="hidden md:flex flex-col items-end gap-1 w-40 shrink-0">
        <span class="text-[11px] text-muted tabular-nums">
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

    <!-- Teile du module : onglets cliquables avec leur avancement -->
    <nav
      v-if="steps?.length"
      class="max-w-7xl mx-auto px-3 sm:px-4 pb-2 flex gap-1.5 overflow-x-auto"
      :aria-label="moduleName"
    >
      <button
        v-for="(step, i) in steps"
        :key="i"
        type="button"
        :aria-current="i === stepIndex ? 'step' : undefined"
        :class="[
          'flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors',
          i === stepIndex
            ? 'border-primary/30 bg-primary/10 text-primary'
            : isDone(step)
              ? 'border-line bg-card text-ink hover:border-primary/30'
              : 'border-line bg-card text-muted hover:border-primary/30 hover:text-ink',
        ]"
        @click="emit('goto', i)"
      >
        <i
          v-if="isDone(step)"
          class="pi pi-check-circle text-[11px] text-emerald-600"
        ></i>
        <span>{{ step.label }}</span>
        <span
          v-if="step.total > 0"
          :class="[
            'tabular-nums',
            i === stepIndex ? 'text-primary/70' : 'text-faint',
          ]"
        >
          {{ step.answered }}/{{ step.total }}
        </span>
      </button>
    </nav>

    <!-- Sans détail des Teile : simple barre d'étapes -->
    <div v-else class="max-w-7xl mx-auto px-3 sm:px-4 pb-2 flex gap-1">
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
type HeaderStep = {
  label: string; // « Teil 1 »
  answered: number;
  total: number;
};

const { t } = useI18n();

const emit = defineEmits<{
  exit: [];
  font: [delta: number];
  goto: [index: number];
}>();

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
  // Facultatifs : onglets des Teile et durée conseillée du Teil en cours
  steps?: HeaderStep[];
  teilMinutes?: number | null;
}>();

const isDone = (step: HeaderStep) => step.total > 0 && step.answered >= step.total;

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