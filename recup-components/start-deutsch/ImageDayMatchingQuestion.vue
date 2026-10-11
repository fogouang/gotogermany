<!-- components/start-deutsch/ImageDayMatchingQuestion.vue -->
<!--
  Nécessite teil.shared_content.images = [{label, image_file}, ...]. Une
  question = un jour (ex. "Dienstag"), l'étudiant choisit une des images
  partagées. Chaque lettre ne doit être utilisée qu'une fois — la
  contrainte "déjà pris" se calcule via usedLabels (props), le composant
  parent (qui itère les questions du Teil) la fournit.
-->
<template>
  <div class="question-container">
    <p class="text-base font-semibold text-ink">{{ question.content.day }}</p>

    <div class="mt-4 grid grid-cols-3 gap-3 sm:grid-cols-4">
      <button
        v-for="img in sharedImages"
        :key="img.label"
        type="button"
        :disabled="isTakenByOther(img.label)"
        class="group relative overflow-hidden rounded-lg border-2 transition-colors disabled:cursor-not-allowed disabled:opacity-40"
        :class="modelValue === img.label ? 'border-primary-500' : 'border-line hover:border-primary-300'"
        @click="$emit('update:modelValue', img.label)"
      >
        <img
          :src="resolveImageUrl(img.image_file)"
          :alt="`Image ${img.label}`"
          class="aspect-square w-full object-cover"
        />
        <span
          class="absolute left-1 top-1 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold uppercase"
          :class="
            modelValue === img.label
              ? 'bg-primary-500 text-white'
              : 'bg-white/90 text-ink-secondary'
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
  /** Lettres déjà choisies par les AUTRES questions du même Teil (chaque lettre ne sert qu'une fois) */
  usedLabels?: string[];
  assetsBaseUrl?: string;
  level?: string;
  /** Numéro du sujet — évite les collisions de noms de fichiers entre sujets du même niveau */
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