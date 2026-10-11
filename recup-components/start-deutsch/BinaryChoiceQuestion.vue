<!-- components/start-deutsch/BinaryChoiceQuestion.vue -->
<!--
  Un seul composant pour true_false (Richtig/Falsch) et ja_nein (Ja/Nein) —
  structurellement identiques, seuls les libellés changent. Passer
  variant="true_false" ou variant="ja_nein".

  IMPORTANT — deux sources possibles pour le texte à lire (cf.
  import_parsers.py::parse_true_false) :
  1. Texte PARTAGÉ par tout le Teil (Lesen Teil1, Hören Teil2) —
     teil.shared_content.text, affiché à GAUCHE (colonne sticky sur
     desktop), le statement+boutons à droite — évite le scroll sur les
     textes longs. Empilé sur mobile.
  2. Texte INDÉPENDANT par question (Lesen Teil3 "Hinweisschilder",
     multi_text=True) — question.content.context + question.content.text,
     courts (un panneau/une annonce), affichés dans le bloc question
     lui-même, pas besoin du layout deux-colonnes ici.
  Sans l'un ou l'autre, le statement Richtig/Falsch est incompréhensible
  hors contexte ("Sofia hat eine neue Wohnung." seul ne veut rien dire).
-->
<template>
  <div :class="hasSharedText ? 'lg:grid lg:grid-cols-2 lg:gap-6 lg:items-start' : ''">
    <div
      v-if="hasSharedText"
      class="question-container whitespace-pre-line text-sm leading-relaxed text-ink lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto"
    >
      {{ teil!.shared_content!.text }}
    </div>

    <div class="question-container mt-4 lg:mt-0">
      <!-- Contexte propre à la question (Teil3 multi-texte), ex: "An einer Wohnungstür" -->
      <p v-if="question.content.context" class="mb-2 text-sm font-semibold italic text-ink-secondary">
        {{ question.content.context }}
      </p>

      <p class="text-base font-semibold text-ink">{{ question.content.statement }}</p>

      <!-- Texte/panneau propre à la question (Teil3 multi-texte) -->
      <div
        v-if="question.content.text"
        class="mt-3 whitespace-pre-line rounded-lg border border-line bg-hover/40 p-4 text-sm leading-relaxed text-ink"
      >
        {{ question.content.text }}
      </div>

      <div class="mt-4 grid grid-cols-2 gap-3">
        <button
          v-for="choice in choices"
          :key="choice.value"
          type="button"
          class="flex items-center justify-center gap-2 rounded-lg border p-3 text-sm font-semibold transition-colors"
          :class="
            modelValue === choice.value
              ? 'border-primary-500 bg-primary-50 text-primary-700'
              : 'border-line bg-card text-ink hover:bg-hover'
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
      /** Propre à la question — Teil3 "Hinweisschilder" (multi-texte) */
      context?: string;
      /** Propre à la question — Teil3 "Hinweisschilder" (multi-texte) */
      text?: string;
    };
  };
  /** Teil parent — porte le texte source PARTAGÉ (Teil1/Hören Teil2) dans shared_content.text */
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