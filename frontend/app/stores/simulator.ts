// stores/simulator.ts
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

    criteriaList: (state) => {
      if (!state.correction) return [];
      const c = state.correction;
      const f = c.criteria_feedbacks as Record<string, string>;
      const maxMap = _getCriteriaMax(c.provider, c.level);
      return [
        {
          key: "aufgabe",
          label: "Aufgabenerfüllung",
          score: c.aufgabe_score,
          maxScore: maxMap.aufgabe,
          feedback: f.aufgabe_feedback || "",
        },
        {
          key: "kohaesion",
          label: "Kohäsion",
          score: c.kohaesion_score,
          maxScore: maxMap.kohaesion,
          feedback: f.kohaesion_feedback || "",
        },
        {
          key: "wortschatz",
          label: "Wortschatz",
          score: c.wortschatz_score,
          maxScore: maxMap.wortschatz,
          feedback: f.wortschatz_feedback || "",
        },
        {
          key: "grammatik",
          label: "Grammatik",
          score: c.grammatik_score,
          maxScore: maxMap.grammatik,
          feedback: f.grammatik_feedback || "",
        },
      ];
    },

    taskList: (state) => {
      if (!state.correction) return [];
      const tf = state.correction.task_feedbacks as Record<string, any>;
      return Object.entries(tf).map(([key, val]) => ({
        key,
        label: _taskLabel(key),
        correctedText: val.corrected_text || "",
        strengths: val.main_strengths || [],
        weaknesses: val.main_weaknesses || [],
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

function _getCriteriaMax(provider: string, level: string) {
  if (provider === "telc")
    return { aufgabe: 15, kohaesion: 10, wortschatz: 10, grammatik: 10 };
  if (provider === "osd" && level === "b2")
    return { aufgabe: 28, kohaesion: 22, wortschatz: 22, grammatik: 18 };
  return { aufgabe: 30, kohaesion: 25, wortschatz: 25, grammatik: 20 };
}

function _taskLabel(key: string): string {
  return { task1: "Teil 1", task2: "Teil 2", task3: "Teil 3" }[key] ?? key;
}
