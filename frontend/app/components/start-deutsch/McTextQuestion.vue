<!-- components/start-deutsch/McTextQuestion.vue -->
<!--
  Deux usages selon le Teil :
  - Hören (5 messages indépendants) : pas de texte partagé, teil.shared_content.text absent
  - Lesen A2 (1 article/panneau/email partagé) : teil.shared_content.text présent,
    affiché à gauche (colonne sticky sur desktop), question+options à droite —
    évite le scroll constant texte→question→texte sur les longs articles.
    Sur mobile, reste empilé (texte au-dessus, question en dessous).
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
      <p class="text-base font-semibold text-ink">{{ question.content.question }}</p>

      <div class="mt-4 space-y-2">
        <label
          v-for="opt in question.content.options"
          :key="opt.label"
          class="flex cursor-pointer items-start gap-3 rounded-lg border border-line p-3 transition-colors hover:bg-hover"
          :class="{ 'border-primary-500 bg-primary-50': modelValue === opt.label }"
        >
          <RadioButton
            :model-value="modelValue"
            :value="opt.label"
            name="mc-text"
            @update:model-value="$emit('update:modelValue', $event)"
          />
          <span class="text-sm text-ink">
            <span class="mr-1.5 font-semibold uppercase text-ink-tertiary">{{ opt.label }})</span>
            {{ opt.text }}
          </span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface McTextOption {
  label: string;
  text: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { question: string; options: McTextOption[] };
  };
  /** Teil parent — porte le texte partagé (Lesen), absent pour Hören */
  teil?: { shared_content?: { text?: string } | null };
  modelValue: string | null;
}

const props = defineProps<Props>();
defineEmits<{ "update:modelValue": [value: string] }>();

const hasSharedText = computed(() => !!props.teil?.shared_content?.text);
</script>