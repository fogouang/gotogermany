<!-- components/start-deutsch/SchreibenDownloadButton.vue -->
<!--
  Deux déclencheurs pour le téléchargement du PDF (sujet + réponses),
  100% côté client via useSchreibenPdf — pas de backend :

  1. Manuel : bouton visible quand TOUTES les tâches du module Schreiben
     ont une réponse (free_text: texte non vide ; form_fill: tous les
     champs remplis).
  2. Automatique : le parent (session.vue) passe timeExpired=true quand
     le compteur du module Schreiben atteint 0 — déclenche le
     téléchargement immédiatement avec les réponses en l'état (même
     incomplètes), une seule fois par session (hasAutoDownloaded).

  Les deux cas sont indépendants : un étudiant qui termine avant la fin
  du temps voit le cas 1 ; un étudiant à qui le temps manque déclenche
  le cas 2, sans jamais les deux à la fois pour la même session (une
  fois auto-téléchargé, le bouton manuel reste disponible en re-téléchargement
  si besoin, mais l'auto ne se redéclenche jamais).
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

  <div v-else-if="timeExpired" class="rounded-xl border border-amber-200 bg-amber-50 p-4">
    <div class="flex items-start gap-3">
      <i class="pi pi-clock mt-0.5 text-lg text-amber-600" />
      <div class="flex-1">
        <p class="text-sm font-semibold text-amber-800">
          {{ t("start_deutsch.schreiben.time_up_title") }}
        </p>
        <p class="mt-0.5 text-sm text-amber-700">
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
  /** Passé à true par le parent quand le compteur du module Schreiben
   * atteint 0 — déclenche un téléchargement automatique unique. */
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

// ── Déclenchement automatique — une seule fois, uniquement si le devoir
// n'était pas déjà complet (dans ce cas le téléchargement est manuel,
// via le bouton du bloc "complete" ci-dessus, pas besoin d'auto).
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