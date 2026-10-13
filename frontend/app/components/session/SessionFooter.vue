<template>
  <footer class="bg-card border-t border-line sticky bottom-0 z-50">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 h-16 flex items-center justify-between gap-2">
      <!-- Précédent -->
      <div class="w-28 sm:w-36 flex justify-start">
        <template v-if="canPrev">
          <Button
            class="hidden! sm:inline-flex!"
            :label="t('session.previous')"
            icon="pi pi-arrow-left"
            outlined
            severity="secondary"
            @click="emit('prev')"
          />
          <Button
            class="sm:hidden!"
            icon="pi pi-arrow-left"
            outlined
            severity="secondary"
            :aria-label="t('session.previous')"
            @click="emit('prev')"
          />
        </template>
      </div>

      <!-- Feuille de réponses -->
      <button
        type="button"
        class="flex items-center gap-2 px-3 py-2 rounded-leaf border border-line hover:border-primary/40 hover:bg-primary/5 transition-colors"
        @click="emit('sheet')"
      >
        <i class="pi pi-th-large text-primary text-sm"></i>
        <span class="hidden sm:inline text-sm font-medium text-ink">
          {{ t("session.player.answer_sheet") }}
        </span>
        <span class="text-xs font-semibold text-muted tabular-nums">{{ answered }}/{{ total }}</span>
      </button>

      <!-- Suivant / Terminer -->
      <div class="w-28 sm:w-36 flex justify-end">
        <template v-if="!isLastStep">
          <Button
            class="hidden! sm:inline-flex!"
            :label="t('session.next')"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="emit('next')"
          />
          <Button
            class="sm:hidden!"
            icon="pi pi-arrow-right"
            :aria-label="t('session.next')"
            @click="emit('next')"
          />
        </template>
        <Button
          v-else
          :label="finishLabel"
          icon="pi pi-check"
          severity="success"
          size="small"
          @click="emit('finish')"
        />
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { t } = useI18n();

const emit = defineEmits<{ prev: []; next: []; finish: []; sheet: [] }>();

defineProps<{
  canPrev: boolean;
  isLastStep: boolean;
  finishLabel: string;
  answered: number;
  total: number;
}>();
</script>