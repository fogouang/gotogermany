<!-- components/start-deutsch/SprechenGroupIntroQuestion.vue -->
<!--
  A1 Sprechen Teil 1 — "Stellen Sie sich vor." Liste de mots-clés
  (Name? / Alter? / Land? ...) que le candidat utilise pour se présenter
  à l'oral. Purement présentationnel — pas de correction en V1, donc pas
  de model-value à gérer ici.
  content = { prompts: string[] }
-->
<template>
  <div class="question-container">
    <ul class="divide-y divide-line">
      <li
        v-for="(prompt, i) in question.content.prompts"
        :key="i"
        class="flex items-center justify-between gap-4 py-3"
      >
        <span class="text-lg font-bold text-ink">{{ prompt }}</span>
        <span class="h-px flex-1 border-b border-dashed border-line" />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
interface Props {
  question: {
    id: string;
    question_number: number;
    content: { prompts: string[] };
  };
}

defineProps<Props>();
</script>