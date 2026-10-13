<!-- components/start-deutsch/Matching2OptionsQuestion.vue -->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <p class="text-base font-semibold text-ink">{{ question.content.scenario }}</p>

    <div class="mt-4 grid gap-3 sm:grid-cols-2">
      <button
        v-for="opt in question.content.options"
        :key="opt.label"
        type="button"
        class="relative min-w-0 rounded-leaf border p-4 pl-10 text-left text-sm transition-colors"
        :class="
          modelValue === opt.label
            ? 'border-primary bg-primary/10'
            : 'border-line bg-card hover:border-primary/30'
        "
        @click="$emit('update:modelValue', opt.label)"
      >
        <span
          class="absolute left-3 top-4 flex size-5 items-center justify-center rounded-full text-xs font-bold uppercase"
          :class="modelValue === opt.label ? 'bg-primary text-white' : 'bg-card-2 text-muted'"
        >
          {{ opt.label }}
        </span>
        <p class="break-all font-mono text-xs text-faint">{{ opt.url }}</p>
        <p class="mt-1 text-ink">{{ opt.text }}</p>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface MatchingOption {
  label: string;
  url: string;
  text: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { scenario: string; options: MatchingOption[] };
  };
  modelValue: string | null;
}

defineProps<Props>();
defineEmits<{ "update:modelValue": [value: string] }>();
</script>