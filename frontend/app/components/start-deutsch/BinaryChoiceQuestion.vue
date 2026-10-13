<!-- components/start-deutsch/BinaryChoiceQuestion.vue -->
<!--
  Un seul composant pour true_false (Richtig/Falsch) et ja_nein (Ja/Nein) :
  même structure, seuls les libellés changent (variant="true_false" | "ja_nein").

  Deux sources possibles pour le texte à lire (cf. import_parsers.py::parse_true_false) :
  1. Texte PARTAGÉ par tout le Teil (Lesen Teil 1, Hören Teil 2) :
     teil.shared_content.text, à gauche (colonne sticky sur desktop),
     énoncé et boutons à droite. Empilé sur mobile.
  2. Texte PROPRE à la question (Lesen Teil 3 "Hinweisschilder") :
     question.content.context + question.content.text, affichés dans le bloc question.
-->
<template>
  <div :class="hasSharedText ? 'lg:grid lg:grid-cols-2 lg:items-start lg:gap-6' : ''">
    <div
      v-if="hasSharedText"
      class="whitespace-pre-line rounded-card border border-line bg-card p-4 text-sm leading-relaxed text-ink shadow-soft lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto"
    >
      {{ teil!.shared_content!.text }}
    </div>

    <div class="mt-4 rounded-card border border-line bg-card p-4 shadow-soft lg:mt-0">
      <!-- Contexte propre à la question (Teil 3), ex. "An einer Wohnungstür" -->
      <p v-if="question.content.context" class="mb-2 text-sm font-semibold italic text-muted">
        {{ question.content.context }}
      </p>

      <p class="text-base font-semibold text-ink">{{ question.content.statement }}</p>

      <!-- Panneau ou annonce propre à la question (Teil 3) -->
      <div
        v-if="question.content.text"
        class="mt-3 whitespace-pre-line rounded-leaf border border-line bg-card-2 p-4 text-sm leading-relaxed text-ink"
      >
        {{ question.content.text }}
      </div>

      <div class="mt-4 grid grid-cols-2 gap-3">
        <button
          v-for="choice in choices"
          :key="choice.value"
          type="button"
          class="flex items-center justify-center gap-2 rounded-leaf border p-3 text-sm font-semibold transition-colors"
          :class="
            modelValue === choice.value
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-ink hover:border-primary/30'
          "
          @click="$emit('update:modelValue', choice.value)"
        >
          <i :class="['pi', choice.icon]" />
          {{ choice.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  question: {
    id: string;
    question_number: number;
    content: {
      statement: string;
      /** Propre à la question (Teil 3 multi-texte) */
      context?: string;
      /** Propre à la question (Teil 3 multi-texte) */
      text?: string;
    };
  };
  /** Teil parent : porte le texte partagé (Teil 1, Hören Teil 2) dans shared_content.text */
  teil?: { shared_content?: { text?: string } | null };
  modelValue: string | null;
  variant: "true_false" | "ja_nein";
}

const props = defineProps<Props>();
defineEmits<{ "update:modelValue": [value: string] }>();

const hasSharedText = computed(() => !!props.teil?.shared_content?.text);

const choices = computed(() =>
  props.variant === "true_false"
    ? [
        { value: "richtig", label: "Richtig", icon: "pi-check" },
        { value: "falsch", label: "Falsch", icon: "pi-times" },
      ]
    : [
        { value: "ja", label: "Ja", icon: "pi-check" },
        { value: "nein", label: "Nein", icon: "pi-times" },
      ],
);
</script>