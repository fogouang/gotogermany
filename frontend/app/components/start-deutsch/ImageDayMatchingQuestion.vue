<!-- components/start-deutsch/ImageDayMatchingQuestion.vue -->
<!--
  Images communes au Teil : teil.shared_content.images = [{label, image_file}, ...].
  Une question = un jour (ex. "Dienstag"), l'étudiant choisit une image.
  Chaque lettre ne sert qu'une fois : le parent passe usedLabels, les lettres
  déjà prises par les autres questions.
-->
<template>
  <div class="rounded-card border border-line bg-card p-4 shadow-soft">
    <p class="text-base font-semibold text-ink">{{ question.content.day }}</p>

    <div class="mt-4 grid grid-cols-3 gap-3 sm:grid-cols-4">
      <button
        v-for="img in sharedImages"
        :key="img.label"
        type="button"
        :disabled="isTakenByOther(img.label)"
        class="group relative overflow-hidden rounded-leaf border-2 transition-colors disabled:cursor-not-allowed disabled:opacity-40"
        :class="
          modelValue === img.label
            ? 'border-primary'
            : 'border-line hover:border-primary/40'
        "
        @click="$emit('update:modelValue', img.label)"
      >
        <img
          :src="resolveImageUrl(img.image_file)"
          :alt="`Image ${img.label}`"
          class="aspect-square w-full object-cover"
        />
        <span
          class="absolute left-1 top-1 flex size-5 items-center justify-center rounded-full text-[10px] font-bold uppercase"
          :class="
            modelValue === img.label
              ? 'bg-primary text-white'
              : 'bg-card/90 text-muted'
          "
        >
          {{ img.label }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface SharedImage {
  label: string;
  image_file: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { day: string };
  };
  teil: {
    shared_content?: { images?: SharedImage[] } | null;
  };
  modelValue: string | null;
  /** Lettres déjà choisies par les autres questions du Teil */
  usedLabels?: string[];
  assetsBaseUrl?: string;
  level?: string;
  /** Numéro du sujet : les images sont rangées par sujet */
  subjectNumber?: number;
}

const props = withDefaults(defineProps<Props>(), {
  usedLabels: () => [],
  assetsBaseUrl: "",
  level: "",
  subjectNumber: 0,
});
defineEmits<{ "update:modelValue": [value: string] }>();

const sharedImages = computed(() => props.teil.shared_content?.images ?? []);

function isTakenByOther(label: string) {
  return props.usedLabels.includes(label) && props.modelValue !== label;
}

function resolveImageUrl(imageFile: string) {
  return `${props.assetsBaseUrl}/${props.level.toLowerCase()}/subject${props.subjectNumber}/images/${imageFile}`;
}
</script>