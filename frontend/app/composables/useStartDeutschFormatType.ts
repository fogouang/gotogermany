// composables/useStartDeutschFormatType.ts
//
// Un seul point de vérité pour savoir, à partir d'un format_type, quel
// composant de question afficher et comment le traiter. Évite de disperser
// des if/else sur les 15 format_type dans chaque page/composant.

export type StartDeutschFormatType =
  | "mc_text"
  | "mc_image"
  | "true_false"
  | "matching_2options"
  | "matching_with_distractor"
  | "image_day_matching"
  | "ja_nein"
  | "form_fill"
  | "free_text"
  | "sprechen_group_intro"
  | "sprechen_group_word_card"
  | "sprechen_group_image_card"
  | "sprechen_duo_question_card"
  | "sprechen_duo_monologue_card"
  | "sprechen_duo_negotiation";

interface FormatTypeMeta {
  /** Nom du composant Vue à monter pour ce format_type (à créer un par un). */
  component: string;
  /** true si la correction est automatique côté backend (QCM, matching, etc.) */
  isAutoCorrected: boolean;
  /** true si ce Teil s'appuie sur un fichier audio (Hören) */
  needsAudio: boolean;
  /** true si c'est un format Sprechen (groupe A1 ou duo A2) */
  isSprechen: boolean;
  /** true si c'est le format libre Schreiben nécessitant la correction IA A-E */
  isFreeText: boolean;
  /** Module auquel ce format_type appartient normalement, pour affichage/regroupement */
  module: "lesen" | "hoeren" | "schreiben" | "sprechen";
}

const FORMAT_TYPE_META: Record<StartDeutschFormatType, FormatTypeMeta> = {
  mc_text: {
    component: "McTextQuestion",
    isAutoCorrected: true,
    needsAudio: false,
    isSprechen: false,
    isFreeText: false,
    module: "lesen", // aussi utilisé en hoeren — needsAudio le distingue au cas par cas
  },
  mc_image: {
    component: "McImageQuestion",
    isAutoCorrected: true,
    needsAudio: true,
    isSprechen: false,
    isFreeText: false,
    module: "hoeren",
  },
  true_false: {
    component: "TrueFalseQuestion",
    isAutoCorrected: true,
    needsAudio: false,
    isSprechen: false,
    isFreeText: false,
    module: "lesen",
  },
  matching_2options: {
    component: "Matching2OptionsQuestion",
    isAutoCorrected: true,
    needsAudio: false,
    isSprechen: false,
    isFreeText: false,
    module: "lesen",
  },
  matching_with_distractor: {
    component: "MatchingWithDistractorQuestion",
    isAutoCorrected: true,
    needsAudio: false,
    isSprechen: false,
    isFreeText: false,
    module: "lesen",
  },
  image_day_matching: {
    component: "ImageDayMatchingQuestion",
    isAutoCorrected: true,
    needsAudio: true,
    isSprechen: false,
    isFreeText: false,
    module: "hoeren",
  },
  ja_nein: {
    component: "JaNeinQuestion",
    isAutoCorrected: true,
    needsAudio: true,
    isSprechen: false,
    isFreeText: false,
    module: "hoeren",
  },
  form_fill: {
    component: "FormFillQuestion",
    isAutoCorrected: true,
    needsAudio: false,
    isSprechen: false,
    isFreeText: false,
    module: "schreiben",
  },
  free_text: {
    component: "FreeTextQuestion",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: false,
    isFreeText: true,
    module: "schreiben",
  },
  sprechen_group_intro: {
    component: "SprechenGroupIntro",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: true,
    isFreeText: false,
    module: "sprechen",
  },
  sprechen_group_word_card: {
    component: "SprechenGroupWordCard",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: true,
    isFreeText: false,
    module: "sprechen",
  },
  sprechen_group_image_card: {
    component: "SprechenGroupImageCard",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: true,
    isFreeText: false,
    module: "sprechen",
  },
  sprechen_duo_question_card: {
    component: "SprechenDuoQuestionCard",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: true,
    isFreeText: false,
    module: "sprechen",
  },
  sprechen_duo_monologue_card: {
    component: "SprechenDuoMonologueCard",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: true,
    isFreeText: false,
    module: "sprechen",
  },
  sprechen_duo_negotiation: {
    component: "SprechenDuoNegotiation",
    isAutoCorrected: false,
    needsAudio: false,
    isSprechen: true,
    isFreeText: false,
    module: "sprechen",
  },
};

const FALLBACK_META: FormatTypeMeta = {
  component: "UnknownQuestion",
  isAutoCorrected: false,
  needsAudio: false,
  isSprechen: false,
  isFreeText: false,
  module: "lesen",
};

export function useStartDeutschFormatType(formatType: string | undefined | null) {
  const meta = computed<FormatTypeMeta>(() => {
    if (!formatType) return FALLBACK_META;
    return FORMAT_TYPE_META[formatType as StartDeutschFormatType] ?? FALLBACK_META;
  });

  return {
    meta,
    componentName: computed(() => meta.value.component),
    isAutoCorrected: computed(() => meta.value.isAutoCorrected),
    needsAudio: computed(() => meta.value.needsAudio),
    isSprechen: computed(() => meta.value.isSprechen),
    isFreeText: computed(() => meta.value.isFreeText),
  };
}