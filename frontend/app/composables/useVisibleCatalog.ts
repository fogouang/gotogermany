export function useVisibleCatalog() {
  const authStore = useAuthStore();
  const examsStore = useExamsStore();

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

  // Slug de l'examen assigné — sert à bloquer l'accès direct par URL à
  // un autre examen pour un étudiant de centre.
  const assignedExamSlug = computed(() => {
    if (!isCenterStudent.value) return null;
    return visibleCatalog.value[0]?.slug ?? null;
  });

  return { isCenterStudent, visibleCatalog, assignedExamSlug };
}