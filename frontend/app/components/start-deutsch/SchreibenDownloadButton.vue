<!-- components/start-deutsch/SchreibenDownloadButton.vue -->
<!--
  Téléchargement du PDF Schreiben (sujet et réponses), généré dans le
  navigateur par useSchreibenPdf.

  1. Bouton : visible quand toutes les tâches ont une réponse
     (free_text : texte non vide ; form_fill : tous les champs remplis).
  2. Automatique : quand le temps du Schreiben est écoulé (timeExpired),
     le PDF part avec les réponses en l'état, une seule fois par session.
     Le bouton reste ensuite disponible pour le retélécharger.
-->
<template>
  <div
    v-if="isComplete"
    class="rounded-card border border-primary/30 bg-primary/10 p-4"
  >
    <div class="flex items-start gap-3">
      <i class="pi pi-check-circle mt-0.5 text-lg text-primary" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-ink">
          {{ t("start_deutsch.schreiben.complete_title") }}
        </p>
        <p class="mt-0.5 text-sm text-muted">
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

  <div
    v-else-if="timeExpired"
    class="rounded-card border border-amber-500/30 bg-amber-500/10 p-4"
  >
    <div class="flex items-start gap-3">
      <i class="pi pi-clock mt-0.5 text-lg text-amber-600" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-ink">
          {{ t("start_deutsch.schreiben.time_up_title") }}
        </p>
        <p class="mt-0.5 text-sm text-muted">
          {{ t("start_deutsch.schreiben.time_up_description") }}
        </p>
      </div>
    </div>

    <Button
      class="mt-3"
      severity="warn"
      :label="t('start_deutsch.schreiben.download_button')"
      icon="pi pi-download"
      @click="handleDownload"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

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
  /** Vrai quand le temps du Schreiben est écoulé : téléchargement automatique unique */
  timeExpired?: boolean;
}

const props = withDefaults(defineProps<Props>(), { timeExpired: false });
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
    return fields.every(
      (f) => !!userAnswer?.[String(f.number)]?.toString().trim(),
    );
  }
  return false;
}

const isComplete = computed(
  () => props.teile.length > 0 && props.teile.every(isTeilAnswered),
);

function handleDownload() {
  download({
    subjectTitle: props.subjectTitle,
    level: props.level,
    studentName: props.studentName,
    teile: props.teile,
    answers: props.answers,
  });
}

// ── Téléchargement automatique : une seule fois, et seulement si le
// devoir n'est pas complet (sinon l'étudiant a déjà le bouton).
const hasAutoDownloaded = ref(false);

watch(
  () => props.timeExpired,
  (expired) => {
    if (expired && !isComplete.value && !hasAutoDownloaded.value) {
      hasAutoDownloaded.value = true;
      handleDownload();
    }
  },
);
</script>