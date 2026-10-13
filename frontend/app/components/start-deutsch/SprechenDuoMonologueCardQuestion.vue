<!-- components/start-deutsch/SprechenDuoMonologueCardQuestion.vue -->
<!--
  A2 Sprechen Teil 2 — "von sich erzählen". Une question centrale (ex.
  "Was machen Sie mit Ihrem Geld?") avec 4 sous-thèmes autour (Kleidung?
  / Lebensmittel, Miete? / Sparen? / Reisen?) que le candidat développe
  en mini-monologue. Purement présentationnel — pas de correction en V1.

  Simplification volontaire par rapport au Kandidatenblatt officiel : au
  lieu de 4 lignes diagonales exactes vers les coins (fragile en
  responsive), on utilise un layout hub-and-spoke en grille CSS — la
  question centrale en haut, les 4 sous-thèmes en dessous en 2x2, chacun
  avec une flèche vers le haut indiquant le lien vers la question
  centrale. Even sur mobile ça reste lisible (empile proprement).
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
