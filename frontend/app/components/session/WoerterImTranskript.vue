<template>
  <div class="rounded-card border border-line bg-card p-4 sm:p-5">
    <div class="flex items-center justify-between gap-3 mb-3">
      <p class="text-xs font-semibold uppercase tracking-wide text-faint">
        {{ t("session.q.transcript") }}
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

    <!-- Texte affiché : chaque mot se marque d'un clic, un 2e clic retire la marque -->
    <p class="text-[15px] text-ink leading-loose whitespace-pre-line">
      <template v-for="tok in tokens" :key="tok.index">
        <template v-if="!tok.word">{{ tok.raw }}</template>
        <template v-else
          >{{ tok.before
          }}<span
            role="button"
            tabindex="0"
            :aria-pressed="isSelected(keyFor(tok.index))"
            :class="wordClass(tok.index)"
            @click="onClick(tok)"
            @keydown.enter.prevent="onClick(tok)"
            @keydown.space.prevent="onClick(tok)"
            >{{ tok.word }}</span
          >{{ tok.after }}</template
        >
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
type Token = {
  index: number;
  raw: string;
  before: string;
  word: string;
  after: string;
};

const props = defineProps<{
  text: string;
  questions: any[];
  answers: Record<string, any>;
}>();

const emit = defineEmits<{ answer: [questionId: string, value: any] }>();

const { t } = useI18n();

// Découpe en mots en gardant espaces, retours à la ligne et ponctuation
const tokens = computed<Token[]>(() =>
  (props.text || "").split(/(\s+)/).map((raw, index) => {
    if (!raw || /^\s+$/.test(raw)) {
      return { index, raw, before: "", word: "", after: "" };
    }
    const m = raw.match(/^([^\p{L}\p{N}]*)(.*?)([^\p{L}\p{N}]*)$/u);
    return {
      index,
      raw,
      before: m?.[1] ?? "",
      word: m?.[2] ?? raw,
      after: m?.[3] ?? "",
    };
  }),
);

// La réponse envoyée est le mot ; la position sert à ne surligner que le mot cliqué
const keyFor = (index: number) => `i${index}`;

const { count, max, isFull, isSelected, toggle } = useSlotAnswers(
  toRef(props, "questions"),
  toRef(props, "answers"),
  (id, value) => emit("answer", id, value),
  (a) => (a?.index != null ? keyFor(Number(a.index)) : `w${a?.answer}`),
);

const fullHint = ref(false);
let hintTimer: ReturnType<typeof setTimeout> | null = null;

function onClick(tok: Token) {
  const ok = toggle(keyFor(tok.index), { answer: tok.word, index: tok.index });
  fullHint.value = !ok;
  if (hintTimer) clearTimeout(hintTimer);
  if (!ok) hintTimer = setTimeout(() => (fullHint.value = false), 3500);
}

const wordClass = (index: number) => [
  "cursor-pointer rounded px-0.5 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-primary/40",
  isSelected(keyFor(index))
    ? "bg-primary text-white"
    : "hover:bg-primary/10",
];

onBeforeUnmount(() => {
  if (hintTimer) clearTimeout(hintTimer);
});
</script>