<!-- components/start-deutsch/SprechenDuoQuestionCardQuestion.vue -->
<!--
  A2 Sprechen Teil 1 — cartes-questions "Fragen zur Person" (Geburtstag?
  / Wohnort? / Beruf? / Hobby?). En binôme : chaque candidat pose 4
  questions à l'autre avec ses cartes, puis inverse. Purement
  présentationnel — pas de correction en V1.
  content = { cards: string[] }
-->
<template>
  <div class="question-container">
    <div class="grid grid-cols-2 gap-3">
      <div
        v-for="(card, i) in question.content.cards"
        :key="i"
        class="flex aspect-4/3 flex-col items-center justify-center gap-1.5 rounded-lg border border-line bg-card p-3 text-center"
      >
        <span class="text-xs font-semibold uppercase tracking-wide text-ink-tertiary">
          {{ t("start_deutsch.sprechen.person_questions_label") }}
        </span>
        <span class="text-xl font-bold text-ink">{{ card }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  question: {
    id: string;
    question_number: number;
    content: { cards: string[] };
  };
}

defineProps<Props>();
const { t } = useI18n();
</script>