// store/sprechen.ts
import { defineStore } from "pinia";
import { SprechenSimulatorService, OpenAPI } from "#shared/api";
import type { SessionHistoryItem } from "#shared/api";

// ASSUMPTION — not confirmed yet: SprechenSubjectListItem doesn't
// exist in #shared/api because the backend listing endpoint hasn't
// been built. Once it is (mirroring ExamService.get_subjects, filtered
// to subjects with a "sprechen" module) and the client is regenerated,
// swap this local interface for the real generated type and delete
// this comment block.
export interface SprechenSubjectListItem {
  id: string;
  provider: string;
  level: string;
  title: string;
  description?: string;
  preview?: string;
  teil_count: number;
}

interface SprechenState {
  subjects: SprechenSubjectListItem[];
  results: SessionHistoryItem[];
  loading: boolean;
  loadingResults: boolean;
  error: string | null;
}

export const useSprechenStore = defineStore("sprechen", {
  state: (): SprechenState => ({
    subjects: [],
    results: [],
    loading: false,
    loadingResults: false,
    error: null,
  }),

  getters: {
    subjectsByProvider: (state) => {
      const grouped: Record<string, SprechenSubjectListItem[]> = {};
      (state.subjects ?? []).forEach((subject) => {
        const provider = subject.provider || "unknown";
        if (!grouped[provider]) grouped[provider] = [];
        grouped[provider].push(subject);
      });
      return grouped;
    },
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
      return tokenCookie.value ?? undefined;
    },

    /**
     * TODO — blocked on the backend listing endpoint not existing yet
     * (see the interface comment above). Once
     * `GET /api/v1/sprechen-simulator/subjects` exists and the OpenAPI
     * client is regenerated, replace the body below with the real
     * generated call, same shape as fetchCatalog() in store/exams.ts:
     *
     *   const subjects = await SprechenSimulatorService
     *     .getSprechenSubjectsApiV1SprechenSimulatorSubjectsGet(provider, level);
     *   this.subjects = subjects;
     */
    async fetchSubjects(provider?: string, level?: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        throw new Error(
          "fetchSubjects: backend listing endpoint not implemented yet"
        );
      } catch (error: any) {
        console.error("Fetch sprechen subjects error:", error);
        this.error = error.body?.detail || "Erreur lors du chargement";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchMyResults(provider?: string, level?: string) {
      const accessToken = this._ensureApiConfig();
      this.loadingResults = true;
      this.error = null;
      try {
        const response =
          await SprechenSimulatorService.getSprechenHistoryApiV1SprechenSimulatorHistoryGet(
            provider,
            level,
            20,
            0,
            accessToken
          );
        this.results = response.items;
        return { success: true, data: response };
      } catch (error: any) {
        console.error("Fetch sprechen history error:", error);
        this.error = error.body?.detail || "Erreur lors du chargement";
        return { success: false, error: this.error };
      } finally {
        this.loadingResults = false;
      }
    },

    clearError() {
      this.error = null;
    },
  },
});