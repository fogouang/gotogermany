<!-- components/start-deutsch/FreeTextQuestion.vue -->
<!--
  content = { prompt, content_points: string[], min_words?, max_words? }
  user_answer = { text: string }
  Pas de correction ici — juste la saisie. La correction IA (grille A-E)
  se déclenche séparément après le submit de la session (cf. session.vue).
-->
<template>
  <div class="question-container">
    <p class="text-sm text-ink-secondary whitespace-pre-line">{{ question.content.prompt }}</p>

    <ul v-if="question.content.content_points?.length" class="mt-3 space-y-1.5">
      <li
        v-for="(point, i) in question.content.content_points"
        :key="i"
        class="flex items-start gap-2 text-sm text-ink"
      >
        <i class="pi pi-circle-fill text-primary-500 text-[6px] mt-2 shrink-0" />
        {{ point }}
      </li>
    </ul>

    <Textarea
      class="mt-4 w-full"
      :model-value="text"
      rows="6"
      auto-resize
      @update:model-value="onTextChange"
    />

    <div class="mt-2 flex items-center justify-between text-xs">
      <span :class="wordCountColor">
        {{ t("start_deutsch.free_text.word_count", { count: wordCount }) }}
        <span v-if="wordRangeLabel"> · {{ wordRangeLabel }}</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  question: {
    id: string;
    question_number: number;
    content: {
      prompt: string;
      content_points?: string[];
      min_words?: number | null;
      max_words?: number | null;
    };
  };
  modelValue: { text?: string } | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{ "update:modelValue": [value: { text: string }] }>();
const { t } = useI18n();

const text = computed(() => props.modelValue?.text ?? "");

const wordCount = computed(() => {
  const trimmed = text.value.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
});

const wordRangeLabel = computed(() => {
  const { min_words, max_words } = props.question.content;
  if (min_words && max_words) return `${min_words}-${max_words} ${t("start_deutsch.free_text.words")}`;
  if (min_words) return `≥ ${min_words} ${t("start_deutsch.free_text.words")}`;
  return "";
});

const wordCountColor = computed(() => {
  const { min_words, max_words } = props.question.content;
  if (min_words && wordCount.value < min_words) return "text-danger-500 font-semibold";
  if (max_words && wordCount.value > max_words) return "text-amber-600 font-semibold";
  return "text-ink-tertiary";
});

function onTextChange(value: string | undefined) {
  emit("update:modelValue", { text: value ?? "" });
}
</script>