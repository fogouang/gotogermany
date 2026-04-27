//composables/useExams.ts

import { useExamsStore } from "~/stores/exams";

export const useExams = () => {
  const examsStore = useExamsStore();

  // Charger le catalogue au montage
  const loadCatalog = async () => {
    if (examsStore.catalog.length === 0) {
      await examsStore.fetchCatalog();
    }
  };

  // Obtenir un niveau spécifique
  const getLevelByCode = (cefrCode: string) => {
    return examsStore.allLevels.find((level) => level.cefr_code === cefrCode);
  };

  // Obtenir les examens d'un provider
  const getExamsByProvider = (provider: string) => {
    return examsStore.examsByProvider[provider] || [];
  };

  // Obtenir le nombre de sujets d'un level
  const getSubjectCount = (levelId: string) => {
    for (const exam of examsStore.catalog) {
      for (const level of exam.levels ?? []) {
        if (level.id === levelId) return level.subject_count ?? 0;
      }
    }
    return 0;
  };

  return {
    // State
    catalog: computed(() => examsStore.catalog),
    currentExam: computed(() => examsStore.currentExam),
    loading: computed(() => examsStore.loading),
    error: computed(() => examsStore.error),

    // Getters
    examsByProvider: computed(() => examsStore.examsByProvider),
    allLevels: computed(() => examsStore.allLevels),
    freeLevels: computed(() => examsStore.freeLevels),

    // Actions
    loadCatalog,
    fetchExamDetail: examsStore.fetchExamDetail,
    fetchExamBySlug: examsStore.fetchExamBySlug,
    clearCurrentExam: examsStore.clearCurrentExam,

    importJson: examsStore.importJson,
    importAudio: examsStore.importAudio,

    // Helpers
    getLevelByCode,
    getExamsByProvider,
    getSubjectCount,
  };
};
