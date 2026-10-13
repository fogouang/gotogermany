<!-- components/start-deutsch/McTextQuestion.vue -->
<!--
  Deux usages selon le Teil :
  - Hören (messages indépendants) : pas de texte partagé
  - Lesen A2 (article, panneau ou e-mail partagé) : teil.shared_content.text
    à gauche (colonne sticky sur desktop), question et options à droite.
    Empilé sur mobile.
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
      <p class="text-base font-semibold text-ink">{{ question.content.question }}</p>

      <div class="mt-4 space-y-2">
        <label
          v-for="opt in question.content.options"
          :key="opt.label"
          class="flex cursor-pointer items-start gap-3 rounded-leaf border p-3 transition-colors"
          :class="
            modelValue === opt.label
              ? 'border-primary bg-primary/10'
              : 'border-line hover:border-primary/30'
          "
        >
          <RadioButton
            :model-value="modelValue"
            :value="opt.label"
            :name="`mc-text-${question.id}`"
            @update:model-value="$emit('update:modelValue', $event)"
          />
          <span class="text-sm text-ink">
            <span class="mr-1.5 font-semibold uppercase text-faint">{{ opt.label }})</span>
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
  /** Teil parent : porte le texte partagé (Lesen), absent pour Hören */
  teil?: { shared_content?: { text?: string } | null };
  modelValue: string | null;
}

const props = defineProps<Props>();
defineEmits<{ "update:modelValue": [value: string] }>();

const hasSharedText = computed(() => !!props.teil?.shared_content?.text);
</script>