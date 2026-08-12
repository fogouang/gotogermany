<!-- components/start-deutsch/SchreibenDownloadButton.vue -->
<!--
  Affiché uniquement quand TOUTES les tâches du module Schreiben ont une
  réponse (free_text: texte non vide ; form_fill: tous les champs
  remplis). Génère un PDF (sujet + réponses) 100% côté client via
  useSchreibenPdf — pas de backend, l'étudiant télécharge et envoie
  lui-même le fichier à son formateur.
-->
<template>
  <div v-if="isComplete" class="rounded-xl border border-primary-200 bg-primary-50 p-4">
    <div class="flex items-start gap-3">
      <i class="pi pi-check-circle mt-0.5 text-lg text-primary-600" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-primary-800">
          {{ t("start_deutsch.schreiben.complete_title") }}
        </p>
        <p class="mt-0.5 text-sm text-primary-700">
          {{ t("start_deutsch.schreiben.complete_description") }}
        </p>
      </div>
    </div>

    <Button
      class="mt-3"
      :label="t('start_deutsch.schreiben.download_button')"
      icon="pi pi-download"
      @click="handleDownload"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface SchreibenTeil {
  id: string;
  teil_number: number;
  format_type: string;
  instructions?: string | null;
  questions?: Array<{
    id: string;
    content: {
      prompt?: string;
      content_points?: string[];
      prompt_text?: string;
      fields?: Array<{ number: number | string; label: string }>;
    };
  }>;
}

interface Props {
  subjectTitle: string;
  level: string;
  studentName: string;
  teile: SchreibenTeil[];
  /** answers[questionId].user_answer */
  answers: Record<string, any>;
}

const props = defineProps<Props>();
const { t } = useI18n();
const { download } = useSchreibenPdf();

function isTeilAnswered(teil: SchreibenTeil): boolean {
  const question = teil.questions?.[0];
  if (!question) return false;
  const userAnswer = props.answers[question.id]?.user_answer;

  if (teil.format_type === "free_text") {
    return !!userAnswer?.text?.trim();
  }
  if (teil.format_type === "form_fill") {
    const fields = question.content.fields ?? [];
    if (!fields.length) return false;
    return fields.every((f) => !!userAnswer?.[String(f.number)]?.toString().trim());
  }
  return false;
}

const isComplete = computed(() => props.teile.length > 0 && props.teile.every(isTeilAnswered));

function handleDownload() {
  download({
    subjectTitle: props.subjectTitle,
    level: props.level,
    studentName: props.studentName,
    teile: props.teile,
    answers: props.answers,
  });
}
</script>