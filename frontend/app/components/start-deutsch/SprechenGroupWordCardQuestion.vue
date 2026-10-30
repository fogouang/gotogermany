<!-- components/start-deutsch/SprechenGroupWordCardQuestion.vue -->
<!--
  A1 Sprechen Teil 2 : cartes mots par thème (ex. "Essen & Trinken" :
  Frühstück, Lieblingsessen, Sonntag...). Le candidat tire une carte et pose
  une question sur ce mot. Affichage seulement, pas de correction.
  content = { theme: string, cards: string[] }
-->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <p v-if="question.content.theme" class="mb-4 text-sm font-semibold uppercase tracking-wide text-muted">
      {{ t("start_deutsch.sprechen.theme_label") }} {{ question.content.theme }}
    </p>

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
      <div
        v-for="(card, i) in question.content.cards"
        :key="i"
        class="flex min-h-24 items-center justify-center rounded-leaf border border-line bg-card-2 p-3 text-center"
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