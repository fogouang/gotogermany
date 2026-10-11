<!-- components/start-deutsch/SprechenGroupWordCardQuestion.vue -->
<!--
  A1 Sprechen Teil 2 — cartes-mots par thème (ex. "Essen & Trinken":
  Frühstück, Lieblingsessen, Sonntag, Bier, Fleisch, Brot). Le candidat
  pioche une carte et pose une question à un autre candidat autour de ce
  mot. Purement présentationnel — pas de correction en V1.
  content = { theme: string, cards: string[] }
-->
<template>
  <div class="question-container">
    <p v-if="question.content.theme" class="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-secondary">
      {{ t("start_deutsch.sprechen.theme_label") }} {{ question.content.theme }}
    </p>

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <div
        v-for="(card, i) in question.content.cards"
        :key="i"
        class="flex aspect-4/3 items-center justify-center rounded-lg border border-line bg-card p-3 text-center"
      >
        <span class="text-lg font-bold text-ink">{{ card }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  question: {
    id: string;
    question_number: number;
    content: { theme?: string; cards: string[] };
  };
}

defineProps<Props>();
const { t } = useI18n();
</script>