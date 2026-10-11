<!-- components/start-deutsch/McImageQuestion.vue -->
<template>
  <div class="question-container">
    <p class="text-base font-semibold text-ink">{{ question.content.question }}</p>

    <div class="mt-4 grid grid-cols-3 gap-3">
      <button
        v-for="opt in question.content.options"
        :key="opt.label"
        type="button"
        class="group relative overflow-hidden rounded-lg border-2 transition-colors"
        :class="modelValue === opt.label ? 'border-primary-500' : 'border-line hover:border-primary-300'"
        @click="$emit('update:modelValue', opt.label)"
      >
        <img
          :src="resolveImageUrl(opt.image_file)"
          :alt="`Option ${opt.label}`"
          class="aspect-square w-full object-cover"
        />
        <span
          class="absolute left-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold uppercase"
          :class="
            modelValue === opt.label
              ? 'bg-primary-500 text-white'
              : 'bg-white/90 text-ink-secondary'
          "
        >
          {{ opt.label }}
        </span>
        <i
          v-if="modelValue === opt.label"
          class="pi pi-check-circle absolute bottom-1.5 right-1.5 text-lg text-primary-500"
        />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface McImageOption {
  label: string;
  image_file: string;
}

interface Props {
  question: {
    id: string;
    question_number: number;
    content: { question: string; options: McImageOption[] };
  };
  modelValue: string | null;
  /** Base URL vers le dossier des assets Start Deutsch (audio/images) */
  assetsBaseUrl?: string;
  /** Niveau (A1/A2) — nécessaire pour reconstruire le chemin exact, puisque
   * image_file ne contient que le nom de fichier nu (ex. "hoeren_teil1_q1_a.png"),
   * alors que le stockage réel est <STORAGE_ROOT>/<level>/images/<filename>
   * (cf. import_service.py::import_images). Contrairement à audio_file, qui
   * lui contient déjà le chemin relatif complet. */
  level?: string;
  /** Numéro du sujet — évite les collisions de noms de fichiers entre sujets du même niveau */
  subjectNumber?: number;
}

const props = withDefaults(defineProps<Props>(), { assetsBaseUrl: "", level: "", subjectNumber: 0 });
defineEmits<{ "update:modelValue": [value: string] }>();

function resolveImageUrl(imageFile: string) {
  return `${props.assetsBaseUrl}/${props.level.toLowerCase()}/subject${props.subjectNumber}/images/${imageFile}`;
}
</script>