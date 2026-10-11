<!-- components/start-deutsch/QuestionRenderer.vue -->
<!--
  Point d'entrée unique pour afficher une question, quel que soit son
  format_type. S'appuie sur useStartDeutschFormatType pour savoir quel
  composant monter — évite un mur de v-if dans les pages de session.

  Les 6 format_type Sprechen sont présentationnels uniquement (pas de
  correction en V1, cf. commentaire dans import_parsers.py) — ils
  reçoivent question/teil/assets mais n'émettent pas de model-value,
  contrairement aux formats notés automatiquement.
-->
<template>
  <McTextQuestion
    v-if="formatType === 'mc_text'"
    :question="question"
    :teil="teil"
    :model-value="modelValue?.answer ?? null"
    @update:model-value="emitAnswer({ answer: $event })"
  />

  <BinaryChoiceQuestion
    v-else-if="formatType === 'true_false' || formatType === 'ja_nein'"
    :question="question"
    :teil="teil"
    :variant="formatType"
    :model-value="modelValue?.answer ?? null"
    @update:model-value="emitAnswer({ answer: $event })"
  />

  <McImageQuestion
    v-else-if="formatType === 'mc_image'"
    :question="question"
    :assets-base-url="assetsBaseUrl"
    :level="level"
    :subject-number="subjectNumber"
    :model-value="modelValue?.answer ?? null"
    @update:model-value="emitAnswer({ answer: $event })"
  />

  <Matching2OptionsQuestion
    v-else-if="formatType === 'matching_2options'"
    :question="question"
    :model-value="modelValue?.answer ?? null"
    @update:model-value="emitAnswer({ answer: $event })"
  />

  <MatchingWithDistractorQuestion
    v-else-if="formatType === 'matching_with_distractor'"
    :question="question"
    :teil="teil"
    :model-value="modelValue?.answer ?? null"
    @update:model-value="emitAnswer({ answer: $event })"
  />

  <ImageDayMatchingQuestion
    v-else-if="formatType === 'image_day_matching'"
    :question="question"
    :teil="teil"
    :assets-base-url="assetsBaseUrl"
    :level="level"
    :subject-number="subjectNumber"
    :used-labels="usedLabels"
    :model-value="modelValue?.answer ?? null"
    @update:model-value="emitAnswer({ answer: $event })"
  />

  <FormFillQuestion
    v-else-if="formatType === 'form_fill'"
    :question="question"
    :model-value="modelValue ?? {}"
    @update:model-value="emitAnswer($event)"
  />

  <FreeTextQuestion
    v-else-if="formatType === 'free_text'"
    :question="question"
    :model-value="modelValue ?? {}"
    @update:model-value="emitAnswer($event)"
  />

  <!-- Sprechen A1 (groupe) -->
  <SprechenGroupIntroQuestion
    v-else-if="formatType === 'sprechen_group_intro'"
    :question="question"
  />

  <SprechenGroupWordCardQuestion
    v-else-if="formatType === 'sprechen_group_word_card'"
    :question="question"
  />

  <SprechenGroupImageCardQuestion
    v-else-if="formatType === 'sprechen_group_image_card'"
    :question="question"
    :assets-base-url="assetsBaseUrl"
    :level="level"
    :subject-number="subjectNumber"
  />

  <!-- Sprechen A2 (duo) -->
  <SprechenDuoQuestionCardQuestion
    v-else-if="formatType === 'sprechen_duo_question_card'"
    :question="question"
  />

  <SprechenDuoMonologueCardQuestion
    v-else-if="formatType === 'sprechen_duo_monologue_card'"
    :question="question"
  />

  <SprechenDuoNegotiationQuestion
    v-else-if="formatType === 'sprechen_duo_negotiation'"
    :question="question"
  />

  <div v-else class="question-container flex items-center gap-2 text-sm text-ink-secondary">
    <i class="pi pi-hourglass" />
    Ce type de question ({{ formatType }}) arrive dans une prochaine mise à jour.
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import McTextQuestion from "./McTextQuestion.vue";
import BinaryChoiceQuestion from "./BinaryChoiceQuestion.vue";
import McImageQuestion from "./McImageQuestion.vue";
import Matching2OptionsQuestion from "./Matching2OptionsQuestion.vue";
import MatchingWithDistractorQuestion from "./MatchingWithDistractorQuestion.vue";
import ImageDayMatchingQuestion from "./ImageDayMatchingQuestion.vue";
import FormFillQuestion from "./FormFillQuestion.vue";
import FreeTextQuestion from "./FreeTextQuestion.vue";
import SprechenGroupIntroQuestion from "./SprechenGroupIntroQuestion.vue";
import SprechenGroupWordCardQuestion from "./SprechenGroupWordCardQuestion.vue";
import SprechenGroupImageCardQuestion from "./SprechenGroupImageCardQuestion.vue";
import SprechenDuoQuestionCardQuestion from "./SprechenDuoQuestionCardQuestion.vue";
import SprechenDuoMonologueCardQuestion from "./SprechenDuoMonologueCardQuestion.vue";
import SprechenDuoNegotiationQuestion from "./SprechenDuoNegotiationQuestion.vue";

interface Props {
  question: {
    id: string;
    question_number: number;
    content: any;
  };
  teil: {
    format_type: string;
    shared_content?: any;
  };
  modelValue: Record<string, any> | null;
  assetsBaseUrl?: string;
  /** Niveau (A1/A2) — nécessaire pour reconstruire l'URL exacte des images */
  level?: string;
  /** Numéro du sujet — nécessaire depuis qu'il peut exister plusieurs sujets
   * par niveau (évite les collisions de noms de fichiers entre sujets) */
  subjectNumber?: number;
  /** Pour image_day_matching : lettres déjà utilisées par les autres questions du Teil */
  usedLabels?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  assetsBaseUrl: "",
  level: "",
  subjectNumber: 0,
  usedLabels: () => [],
});
const emit = defineEmits<{ "update:modelValue": [value: Record<string, any>] }>();

const formatType = computed(() => props.teil.format_type);

function emitAnswer(value: Record<string, any>) {
  emit("update:modelValue", value);
}
</script>