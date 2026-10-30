<!-- components/start-deutsch/SprechenDuoQuestionCardQuestion.vue -->
<!--
  A2 Sprechen Teil 1, "Fragen zur Person" : cartes Geburtstag? / Wohnort? /
  Beruf? / Hobby?. En binôme, chacun pose ses questions à l'autre.
  Affichage seulement, pas de correction.
  content = { cards: string[] }
-->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div
        v-for="(card, i) in question.content.cards"
        :key="i"
        class="flex min-h-28 flex-col items-center justify-center gap-1.5 rounded-leaf border border-line bg-card-2 p-4 text-center"
      >
        <span class="text-xs font-semibold uppercase tracking-wide text-faint">
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