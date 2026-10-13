<template>
  <Dialog
    v-model:visible="visible"
    :header="t('session.player.answer_sheet')"
    :modal="true"
    :dismissableMask="true"
    :style="{ width: '92vw', maxWidth: '560px' }"
  >
    <p class="text-xs text-muted mb-4">{{ t("session.player.answer_sheet_hint") }}</p>

    <div class="space-y-5">
      <div v-for="group in groups" :key="group.stepIndex">
        <p
          :class="[
            'text-xs font-semibold uppercase tracking-wide mb-2',
            group.current ? 'text-primary' : 'text-muted',
          ]"
        >
          {{ group.label }}
        </p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="q in group.questions"
            :key="q.id"
            type="button"
            :class="[
              'w-10 h-10 rounded-lg text-sm font-semibold border transition-colors tabular-nums',
              q.answered
                ? 'bg-primary text-white border-primary'
                : 'bg-card text-ink border-line hover:border-primary/50',
              group.current ? 'ring-2 ring-primary/25' : '',
            ]"
            @click="emit('go', group.stepIndex)"
          >
            {{ q.number }}
          </button>
        </div>
      </div>
    </div>

    <div class="mt-6 pt-4 border-t border-line flex items-center gap-5 text-xs text-muted">
      <span class="flex items-center gap-2">
        <span class="w-3.5 h-3.5 rounded bg-primary"></span>
        {{ t("session.player.legend_answered") }}
      </span>
      <span class="flex items-center gap-2">
        <span class="w-3.5 h-3.5 rounded border border-line bg-card"></span>
        {{ t("session.player.legend_empty") }}
      </span>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
const { t } = useI18n();

const visible = defineModel<boolean>("visible", { default: false });

const emit = defineEmits<{ go: [stepIndex: number] }>();

defineProps<{
  groups: {
    stepIndex: number;
    current: boolean;
    label: string;
    questions: { id: string; number: number; answered: boolean }[];
  }[];
}>();
</script>