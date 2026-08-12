<!-- components/start-deutsch/SprechenGroupImageCardQuestion.vue -->
<!--
  A1 Sprechen Teil 3 — cartes-images (objets du quotidien : pomme, chaise,
  crayon...). Le candidat pioche une carte et formule une demande /
  réagit à propos de l'objet. Purement présentationnel — pas de
  correction en V1, pas de sélection possible (contrairement à
  McImageQuestion qui, lui, attend un choix).
  content = { cards: [{ image_file: string }] }
-->
<template>
  <div class="question-container">
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <div
        v-for="(card, i) in question.content.cards"
        :key="i"
        class="overflow-hidden rounded-lg border border-line bg-card"
      >
        <img
          :src="resolveImageUrl(card.image_file)"
          :alt="`Karte ${i + 1}`"
          class="aspect-square w-full object-contain p-3"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ImageCard {
  image_file: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { cards: ImageCard[] };
  };
  assetsBaseUrl?: string;
  level?: string;
  subjectNumber?: number;
}

const props = withDefaults(defineProps<Props>(), {
  assetsBaseUrl: "",
  level: "",
  subjectNumber: 0,
});

function resolveImageUrl(imageFile: string) {
  return `${props.assetsBaseUrl}/${props.level.toLowerCase()}/subject${props.subjectNumber}/images/${imageFile}`;
}
</script>