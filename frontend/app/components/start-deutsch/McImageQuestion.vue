<!-- components/start-deutsch/McImageQuestion.vue -->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <p class="text-base font-semibold text-ink">{{ question.content.question }}</p>

    <!-- Trois images de taille moyenne, lisibles sans prendre tout l'écran -->
    <div class="mt-4 grid max-w-xl grid-cols-3 gap-2 sm:gap-3">
      <button
        v-for="opt in question.content.options"
        :key="opt.label"
        type="button"
        class="group relative overflow-hidden rounded-leaf border-2 bg-white transition-colors"
        :class="modelValue === opt.label ? 'border-primary ring-2 ring-primary/30' : 'border-line hover:border-primary/40'"
        @click="$emit('update:modelValue', opt.label)"
      >
        <img
          :src="resolveImageUrl(opt.image_file)"
          :alt="opt.image_description || `Option ${opt.label}`"
          class="aspect-square w-full object-contain p-1.5"
          loading="lazy"
        />
        <span
          class="absolute left-1.5 top-1.5 flex size-6 items-center justify-center rounded-full text-xs font-bold uppercase shadow-sm"
          :class="modelValue === opt.label ? 'bg-primary text-white' : 'bg-card text-ink'"
        >
          {{ opt.label }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface McImageOption {
  label: string;
  image_file: string;
  image_description?: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { question: string; options: McImageOption[] };
  };
  modelValue: string | null;
  /** Base des fichiers Start Deutsch (audio, images) */
  assetsBaseUrl?: string;
  /** Niveau (A1, A2) : les images sont rangées dans <niveau>/subject<N>/images/ */
  level?: string;
  /** Numéro du sujet : les images sont rangées par sujet */
  subjectNumber?: number;
}

const props = withDefaults(defineProps<Props>(), { assetsBaseUrl: "", level: "", subjectNumber: 0 });
defineEmits<{ "update:modelValue": [value: string] }>();

function resolveImageUrl(imageFile: string) {
  return `${props.assetsBaseUrl}/${props.level.toLowerCase()}/subject${props.subjectNumber}/images/${imageFile}`;
}
</script>