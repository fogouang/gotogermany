export function useVisibleCatalog() {
  const authStore = useAuthStore();
  const examsStore = useExamsStore();
  const startDeutschStore = useStartDeutschSessionStore();
  const { centerLevelCode } = useLearningTrack();

  const isCenterStudent = computed(() => !!authStore.branchId);

  const visibleCatalog = computed(() => {
    if (!isCenterStudent.value) return examsStore.catalog;

    const targetLevelId = authStore.targetLevelId;
    if (!targetLevelId) return [];

    return examsStore.catalog
      .map((exam) => {
        const levels = (exam.levels ?? []).filter(
          (l) => l.id === targetLevelId,
        );
        if (levels.length === 0) return null;
        return { ...exam, levels };
      })
      .filter((e): e is NonNullable<typeof e> => e !== null);
  });

  // Start Deutsch : l'élève de centre ne voit que son niveau (A1 ou A2)
  const visibleStartDeutschSubjects = computed(() => {
    if (!isCenterStudent.value) return startDeutschStore.subjects;
    const code = authStore.targetSdLevel ?? centerLevelCode.value;
    if (code !== "A1" && code !== "A2") return [];
    return startDeutschStore.subjects.filter((s) => s.level === code);
  });

  // Slug de l'examen assigné : bloque l'accès direct par URL à
  // un autre examen pour un étudiant de centre.
  const assignedExamSlug = computed(() => {
    if (!isCenterStudent.value) return null;
    return visibleCatalog.value[0]?.slug ?? null;
  });

  return {
    isCenterStudent,
    visibleCatalog,
    visibleStartDeutschSubjects,
    assignedExamSlug,
  };
}
