<!-- components/start-deutsch/SprechenDuoMonologueCardQuestion.vue -->
<!--
  A2 Sprechen Teil 2, "von sich erzählen" : une question centrale
  (ex. "Was machen Sie mit Ihrem Geld?") et quatre pistes autour
  (Kleidung? / Miete? / Sparen? / Reisen?) à développer seul.
  Affichage seulement, pas de correction.

  Sur la feuille officielle, quatre traits partent de la question vers les
  coins. Ici : la question en haut, les quatre pistes en grille 2 x 2 en
  dessous, chacune avec une flèche vers la question. Reste lisible sur mobile.
  content = { central_question: string, sub_prompts: string[] }
-->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <div
      class="mx-auto max-w-md rounded-leaf border-2 border-primary bg-primary/10 p-4 text-center"
    >
      <p class="text-lg font-bold text-ink">
        {{ question.content.central_question }}
      </p>
    </div>

    <div class="mt-3 grid grid-cols-2 gap-3">
      <div
        v-for="(prompt, i) in question.content.sub_prompts"
        :key="i"
        class="flex flex-col items-center gap-1 rounded-leaf border border-line bg-card-2 p-3 text-center"
      >
        <i class="pi pi-arrow-up text-xs text-faint" />
        <span class="font-semibold text-ink">{{ prompt }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  question: {
    id: string;
    question_number: number;
    content: { central_question: string; sub_prompts: string[] };
  };
}

defineProps<Props>();
</script>