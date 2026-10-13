// app/composables/useActiveLevel.ts
// Niveau actif de l'étudiant : celui sur lequel tout l'espace se recentre.
// - Étudiant individuel : préférence enregistrée dans target_level_id (PATCH /users/me).
// - Élève de centre : niveau fixé par le centre, non modifiable.
import type { ExamCatalogResponse, LevelAccessResponse } from "#shared/api";

export interface LevelOption {
  exam: ExamCatalogResponse;
  level: LevelAccessResponse;
}

export function useActiveLevel() {
  const authStore = useAuthStore();
  const examsStore = useExamsStore();
  const { isCenterStudent } = useVisibleCatalog();

  /** Niveaux proposés : uniquement ceux qui ont des sujets */
  const options = computed<LevelOption[]>(() =>
    examsStore.catalog.flatMap((exam) =>
      (exam.levels ?? [])
        .filter((level) => (level.subject_count ?? 0) > 0)
        .map((level) => ({ exam, level })),
    ),
  );

  /** Choix par défaut : un niveau payé, sinon gratuit, sinon le premier avec des sujets */
  const defaultOption = computed<LevelOption | null>(
    () =>
      options.value.find((o) => o.level.has_access) ??
      options.value.find((o) => o.level.is_free) ??
      options.value[0] ??
      null,
  );

  const findById = (levelId: string | null) => {
    if (!levelId) return null;
    for (const exam of examsStore.catalog) {
      const level = exam.levels?.find((l) => l.id === levelId);
      if (level) return { exam, level };
    }
    return null;
  };

  const activeOption = computed<LevelOption | null>(() => {
    const chosen = findById(authStore.targetLevelId);
    if (chosen) return chosen;
    return isCenterStudent.value ? null : defaultOption.value;
  });

  /** Étudiant individuel qui n'a jamais choisi son niveau */
  const needsOnboarding = computed(
    () =>
      authStore.isStudent && !isCenterStudent.value && !authStore.targetLevelId,
  );

  const canSwitch = computed(() => !isCenterStudent.value);

  async function ensureCatalog() {
    if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
  }

  async function setActiveLevel(
    levelId: string,
  ): Promise<{ success: boolean; error?: string }> {
    if (!canSwitch.value) return { success: false, error: "" };
    if (levelId === authStore.targetLevelId) return { success: true };
    return authStore.setTargetLevel(levelId);
  }

  return {
    options,
    defaultOption,
    activeOption,
    needsOnboarding,
    canSwitch,
    ensureCatalog,
    setActiveLevel,
  };
}
