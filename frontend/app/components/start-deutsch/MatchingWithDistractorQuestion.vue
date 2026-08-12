<!-- components/start-deutsch/MatchingWithDistractorQuestion.vue -->
<!--
  Nécessite teil.shared_content.ads = [{label, url, text}, ...] — le pool
  d'annonces est commun à toutes les questions du Teil, pas répété par
  question. Voir le patch de modèle (StartDeutschTeil.shared_content).
-->
<template>
  <div class="question-container">
    <p class="text-base font-semibold text-ink">{{ question.content.profile }}</p>

    <div class="mt-4 grid gap-2 sm:grid-cols-2">
      <button
        v-for="ad in sharedAds"
        :key="ad.label"
        type="button"
        class="rounded-lg border p-3 text-left text-sm transition-colors"
        :class="
          modelValue === ad.label
            ? 'border-primary-500 bg-primary-50'
            : 'border-line bg-card hover:bg-hover'
        "
        @click="$emit('update:modelValue', ad.label)"
      >
        <span class="mr-1.5 font-semibold uppercase text-ink-tertiary">{{ ad.label }})</span>
        <span class="font-mono text-xs text-ink-tertiary">{{ ad.url }}</span>
        <p class="mt-1 text-ink">{{ ad.text }}</p>
      </button>

      <button
        type="button"
        class="flex items-center justify-center gap-2 rounded-lg border border-dashed p-3 text-sm font-semibold transition-colors"
        :class="
          modelValue === 'X'
            ? 'border-primary-500 bg-primary-50 text-primary-700'
            : 'border-line text-ink-secondary hover:bg-hover'
        "
        @click="$emit('update:modelValue', 'X')"
      >
        <i class="pi pi-ban" /> Aucune solution
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface SharedAd {
  label: string;
  url: string;
  text: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { profile: string };
  };
  teil: {
    shared_content?: { ads?: SharedAd[] } | null;
  };
  modelValue: string | null;
}

const props = defineProps<Props>();
defineEmits<{ "update:modelValue": [value: string] }>();

const sharedAds = computed(() => props.teil.shared_content?.ads ?? []);
</script>