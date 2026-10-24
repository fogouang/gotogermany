<template>
  <div class="rounded-card border border-line bg-card p-4 sm:p-5">
    <div class="flex items-center justify-between gap-3 mb-3">
      <p class="font-bold text-ink">
        {{ cfg.summary_title || t("session.q.summary") }}
      </p>
      <span
        :class="[
          'shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-semibold tabular-nums',
          isFull
            ? 'border-primary/30 bg-primary/10 text-primary'
            : 'border-line bg-card-2 text-muted',
        ]"
      >
        {{ t("session.q.marked_count", { n: count, max }) }}
      </span>
    </div>

    <!-- Hören 3 : le résumé n'apparaît qu'après l'écoute, comme à l'examen -->
    <div
      v-if="hidden"
      class="flex items-center gap-2 rounded-leaf border border-dashed border-line bg-card-2 px-4 py-6 text-sm text-muted"
    >
      <i class="pi pi-headphones text-[13px]"></i>
      {{ t("session.q.summary_after_listening") }}
    </div>

    <!-- Résumé : chaque phrase se marque d'un clic, un 2e clic retire la marque -->
    <p v-else class="text-[15px] text-ink leading-loose">
      <template v-for="s in sentences" :key="s.key">
        <span
          role="button"
          tabindex="0"
          :aria-pressed="isSelected(s.key)"
          :class="sentenceClass(s.key)"
          @click="onClick(s.key)"
          @keydown.enter.prevent="onClick(s.key)"
          @keydown.space.prevent="onClick(s.key)"
          >{{ s.text }}</span
        >{{ " " }}
      </template>
    </p>

    <p
      v-if="fullHint"
      class="mt-3 flex items-start gap-1.5 text-xs text-amber-600"
    >
      <i class="pi pi-exclamation-triangle mt-0.5 text-[11px]" />
      {{ t("session.q.slots_full", { max }) }}
    </p>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    teil: any;
    questions: any[];
    answers: Record<string, any>;
    hidden?: boolean;
  }>(),
  { hidden: false },
);

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const { t } = useI18n();

const cfg = computed<Record<string, any>>(() => props.teil.config || {});

// Phrases dans l'ordre de leur numéro ; la réponse attendue est ce numéro
const sentences = computed(() =>
  Object.entries(cfg.value.summary_sentences || {})
    .map(([key, text]) => ({ key: String(key), text: String(text) }))
    .sort((a, b) => Number(a.key) - Number(b.key)),
);

const { count, max, isFull, isSelected, toggle } = useSlotAnswers(
  toRef(props, "questions"),
  toRef(props, "answers"),
  (id, value) => emit("answer", id, value),
);

const fullHint = ref(false);
let hintTimer: ReturnType<typeof setTimeout> | null = null;

function onClick(key: string) {
  const ok = toggle(key, { answer: key });
  fullHint.value = !ok;
  if (hintTimer) clearTimeout(hintTimer);
  if (!ok) hintTimer = setTimeout(() => (fullHint.value = false), 3500);
}

const sentenceClass = (key: string) => [
  "cursor-pointer rounded px-0.5 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-primary/40",
  isSelected(key)
    ? "bg-primary/15 text-ink underline decoration-primary decoration-2 underline-offset-4"
    : "hover:bg-card-2",
];

onBeforeUnmount(() => {
  if (hintTimer) clearTimeout(hintTimer);
});
</script>