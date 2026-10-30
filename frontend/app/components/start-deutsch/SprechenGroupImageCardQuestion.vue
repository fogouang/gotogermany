<!-- components/start-deutsch/SprechenGroupImageCardQuestion.vue -->
<!--
  A1 Sprechen Teil 3 : cartes images (objets du quotidien). Le candidat
  tire une carte et formule une demande, ou y répond.
  Affichage seulement : pas de choix à faire, pas de correction.
  content = { cards: [{ image_file: string, description?: string }] }
-->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <div class="grid grid-cols-3 gap-3 sm:grid-cols-4 lg:grid-cols-6">
      <div
        v-for="(card, i) in question.content.cards"
        :key="i"
        class="overflow-hidden rounded-leaf border border-line bg-card-2"
      >
        <img
          :src="resolveImageUrl(card.image_file)"
          :alt="card.description || `Karte ${i + 1}`"
          class="aspect-square w-full object-contain p-3"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ImageCard {
  image_file: string;
  description?: string;
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