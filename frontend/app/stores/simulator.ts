// stores/simulator.ts
//
// ⚠️ criteriaList / taskList ne font plus aucun branchement par provider —
// _getCriteriaMax a disparu. Le backend (response_normalizer.py) renvoie
// désormais directement `criteria: [...]` et `tasks: [...]` déjà dans la
// forme attendue par l'UI, quel que soit l'examen (3 ou 4 critères pour
// telc/Goethe, structure ÖSD B2 avec sub_criteria agrégée en amont côté
// backend). Ces deux getters ne font plus qu'un renommage de champs
// (snake_case backend -> camelCase frontend).
import { defineStore } from "pinia";
import { SchreibenSimulatorService, OpenAPI } from "#shared/api";
import type {
  SchreibenSubjectResponse,
  SimulatorCorrectResponse,
  SimulatorResultResponse,
} from "#shared/api";

interface SimulatorState {
  subjects: SchreibenSubjectResponse[];
  currentSubject: SchreibenSubjectResponse | null;
  correction: SimulatorCorrectResponse | null;
  results: SimulatorResultResponse[];
  loading: boolean;
  correcting: boolean;
  loadingResults: boolean;
  error: string | null;
  correctionError: string | null;
  originalAnswers: Record<string, string>;
}

export const useSimulatorStore = defineStore("simulator", {
  state: (): SimulatorState => ({
    subjects: [],
    currentSubject: null,
    correction: null,
    results: [],
    loading: false,
    correcting: false,
    loadingResults: false,
    error: null,
    correctionError: null,
    originalAnswers: {},
  }),

  getters: {
    scorePercentage: (state): number => {
      if (!state.correction) return 0;
      return Math.round(state.correction.score_percentage);
    },

    cecrlLevel: (state): string => {
      if (!state.correction) return "";
      const pct = state.correction.score_percentage;
      const lvl = state.correction.level.toUpperCase();
      if (pct >= 87) return "C1";
      if (pct >= 70) return lvl + "+";
      if (pct >= 60) return lvl;
      if (pct >= 45) return lvl + "-";
      return state.correction.level === "b2" ? "B1" : "A2";
    },

    // ÖSD B2 uniquement : vrai plancher officiel (>=10/30), distinct du
    // `passed` interne à 60%. Undefined pour les autres examens.
    floorReached: (state): boolean | undefined => {
      return state.correction?.floor_reached ?? undefined;
    },

    criteriaList: (state) => {
      if (!state.correction) return [];
      return state.correction.criteria.map((c) => ({
        key: c.key,
        label: c.label,
        score: c.score,
        maxScore: c.max_score,
        feedback: c.feedback,
      }));
    },

    taskList: (state) => {
      if (!state.correction) return [];
      return state.correction.tasks.map((t) => ({
        key: t.key,
        label: t.label,
        correctedText: t.corrected_text,
        strengths: t.main_strengths,
        weaknesses: t.main_weaknesses,
        // Optionnels — présents seulement pour les barèmes qui notent la
        // tâche individuellement (ex. ÖSD B2 : score/15 + détail A/K/T/L/F).
        score: t.score ?? null,
        maxScore: t.max_score ?? null,
        subCriteria: (t.sub_criteria ?? []).map((sc) => ({
          key: sc.key,
          label: sc.label,
          score: sc.score,
          maxScore: sc.max_score,
        })),
      }));
    },
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    loadResultIntoCorrection(result: SimulatorResultResponse) {
      // result.result_data contient déjà la forme normalisée complète
      // (criteria/tasks/...), persistée telle quelle au moment de la
      // correction — aucun retraitement nécessaire ici.
      this.correction = {
        subject_id: result.subject_id,
        provider: result.provider,
        level: result.level,
        overall_score: result.overall_score,
        max_score: result.max_score,
        passed: result.passed,
        score_percentage: result.score_percentage,
        ...result.result_data,
      } as any;
    },

    async fetchSubjects(provider?: string | null, level?: string | null) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        this.subjects =
          await SchreibenSimulatorService.listSubjectsApiV1SchreibenSimulatorGet(
            provider ?? null,
            level ?? null,
          );
        return { success: true };
      } catch (e: any) {
        this.error = e.body?.detail || "Erreur de chargement";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchAllSubjects(
      provider?: string | null,
      level?: string | null,
      activeOnly: boolean = true,
    ) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        this.subjects =
          await SchreibenSimulatorService.listAllSubjectsApiV1SchreibenSimulatorAdminAllGet(
            provider ?? null,
            level ?? null,
            activeOnly,
          );
        return { success: true };
      } catch (e: any) {
        this.error = e.body?.detail || "Erreur de chargement";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchSubject(subjectId: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        this.currentSubject =
          await SchreibenSimulatorService.getSubjectApiV1SchreibenSimulatorSubjectIdGet(
            subjectId,
          );
        return { success: true };
      } catch (e: any) {
        this.error = e.body?.detail || "Sujet introuvable";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async createSubject(data: any) {
      this._ensureApiConfig();
      try {
        const result =
          await SchreibenSimulatorService.createSubjectApiV1SchreibenSimulatorPost(
            data,
          );
        return { success: true, data: result };
      } catch (e: any) {
        return {
          success: false,
          error: e.body?.detail || "Erreur lors de la création",
        };
      }
    },

    async updateSubject(subjectId: string, data: any) {
      this._ensureApiConfig();
      try {
        const result =
          await SchreibenSimulatorService.updateSubjectApiV1SchreibenSimulatorSubjectIdPatch(
            subjectId,
            data,
          );
        return { success: true, data: result };
      } catch (e: any) {
        return {
          success: false,
          error: e.body?.detail || "Erreur lors de la mise à jour",
        };
      }
    },

    async deleteSubject(subjectId: string) {
      this._ensureApiConfig();
      try {
        await SchreibenSimulatorService.deleteSubjectApiV1SchreibenSimulatorSubjectIdDelete(
          subjectId,
        );
        this.subjects = this.subjects.filter((s) => s.id !== subjectId);
        return { success: true };
      } catch (e: any) {
        return {
          success: false,
          error: e.body?.detail || "Erreur lors de la suppression",
        };
      }
    },

    async correct(subjectId: string, taskTexts: string[]) {
      this._ensureApiConfig();
      this.correcting = true;
      this.correctionError = null;

      // Sauvegarder les textes originaux
      this.originalAnswers = {};
      taskTexts.forEach((text, i) => {
        this.originalAnswers[`task${i + 1}`] = text;
      });

      try {
        this.correction =
          await SchreibenSimulatorService.correctSubmissionApiV1SchreibenSimulatorCorrectPost(
            { subject_id: subjectId, task_texts: taskTexts },
          );

        // ← Décrémenter le crédit après succès
        const authStore = useAuthStore();
        authStore.aiCredits = Math.max(0, authStore.aiCredits - 1);

        return { success: true };
      } catch (e: any) {
        this.correctionError =
          e.body?.detail || "Erreur lors de la correction IA";
        return { success: false, error: this.correctionError };
      } finally {
        this.correcting = false;
      }
    },

    async toggleActive(subjectId: string) {
      this._ensureApiConfig();
      const subject = this.subjects.find((s) => s.id === subjectId);
      if (!subject) return { success: false, error: "Sujet introuvable" };
      try {
        const updated =
          await SchreibenSimulatorService.updateSubjectApiV1SchreibenSimulatorSubjectIdPatch(
            subjectId,
            { is_active: !subject.is_active },
          );
        const index = this.subjects.findIndex((s) => s.id === subjectId);
        if (index !== -1) this.subjects[index] = updated;
        return { success: true };
      } catch (e: any) {
        return {
          success: false,
          error: e.body?.detail || "Erreur lors de la mise à jour",
        };
      }
    },

    async fetchMyResults() {
      this._ensureApiConfig();
      this.loadingResults = true;
      try {
        this.results =
          await SchreibenSimulatorService.myResultsApiV1SchreibenSimulatorMyResultsGet();
        return { success: true };
      } catch (e: any) {
        return {
          success: false,
          error: e.body?.detail || "Erreur de chargement",
        };
      } finally {
        this.loadingResults = false;
      }
    },

    clearCorrection() {
      this.correction = null;
      this.correctionError = null;
    },

    clearSubject() {
      this.currentSubject = null;
      this.error = null;
    },
  },
});