/**
 * stores/correction.store.ts
 *
 * tasks[].model_text (Mustertext) : version améliorée attendue, distincte de
 * corrected_text (correction minimale du texte de l'élève). Vide ("") pour
 * les corrections enregistrées avant cet ajout.
 */
import { defineStore } from "pinia";
import { CorrectionsService, OpenAPI } from "#shared/api";
import type { CorrectionResponse } from "#shared/api";

interface CorrectionState {
  // Correction courante (résultat affiché)
  current: CorrectionResponse | null;
  // Cache : sessionId → CorrectionResponse (évite de rappeler l'IA)
  cache: Record<string, CorrectionResponse>;
  loading: boolean;
  error: string | null;
}

export const useCorrectionStore = defineStore("correction", {
  state: (): CorrectionState => ({
    current: null,
    cache: {},
    loading: false,
    error: null,
  }),

  getters: {
    // Score en pourcentage arrondi
    scorePercentage: (state): number => {
      if (!state.current) return 0;
      return Math.round(state.current.score_percentage);
    },

    // Niveau CECRL calculé depuis le pourcentage
    cecrlLevel: (state): string => {
      if (!state.current) return "";
      const pct = state.current.score_percentage;
      const lvl = state.current.level.toUpperCase();
      // Même échelle que les prompts : 87 % et plus = niveau au-dessus (B1 -> B2, B2 -> C1)
      const NEXT: Record<string, string> = {
        A1: "A2",
        A2: "B1",
        B1: "B2",
        B2: "C1",
        C1: "C2",
      };
      const PREV: Record<string, string> = {
        A2: "A1",
        B1: "A2",
        B2: "B1",
        C1: "B2",
      };
      if (pct >= 87) return NEXT[lvl] ?? lvl;
      if (pct >= 70) return lvl + "+";
      if (pct >= 60) return lvl;
      if (pct >= 45) return lvl + "-";
      return PREV[lvl] ?? lvl;
    },

    // Critères de notation tels qu'envoyés par le backend (libellé et max inclus)
    criteriaList: (
      state,
    ): Array<{
      key: string;
      label: string;
      score: number;
      maxScore: number;
      feedback: string;
    }> => {
      if (!state.current) return [];
      return state.current.criteria.map((c) => ({
        key: c.key,
        label: c.label,
        score: c.score,
        maxScore: c.max_score,
        feedback: c.feedback ?? "",
      }));
    },

    // Feedbacks par tâche, avec la note et les sous-critères quand le barème en a (ex. ÖSD B2)
    taskList: (
      state,
    ): Array<{
      key: string;
      label: string;
      originalText: string;
      correctedText: string;
      modelText: string;
      strengths: string[];
      weaknesses: string[];
      score: number | null;
      maxScore: number | null;
      subCriteria: Array<{
        key: string;
        label: string;
        score: number;
        maxScore: number;
      }>;
    }> => {
      if (!state.current) return [];
      return state.current.tasks.map((t) => ({
        key: t.key,
        label: t.label,
        originalText: t.original_text ?? "",
        correctedText: t.corrected_text,
        modelText: t.model_text ?? "",
        strengths: t.main_strengths ?? [],
        weaknesses: t.main_weaknesses ?? [],
        score: t.score ?? null,
        maxScore: t.max_score ?? null,
        subCriteria: (t.sub_criteria ?? []).map((s) => ({
          key: s.key,
          label: s.label,
          score: s.score,
          maxScore: s.max_score,
        })),
      }));
    },

    isCached:
      (state) =>
      (sessionId: string): boolean => {
        return !!state.cache[sessionId];
      },
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    /**
     * Lancer ou récupérer la correction d'une session Schreiben.
     * Si déjà en cache local → pas d'appel réseau.
     */
    async correct(sessionId: string) {
      // Cache local d'abord
      if (this.cache[sessionId]) {
        this.current = this.cache[sessionId];
        return { success: true, data: this.current };
      }

      this._ensureApiConfig();
      this.loading = true;
      this.error = null;

      try {
        const result =
          await CorrectionsService.createCorrectionApiV1CorrectionsPost({
            exam_session_id: sessionId,
          });

        this.current = result;
        this.cache[sessionId] = result;
        return { success: true, data: result };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors de la correction IA";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    /**
     * Récupérer une correction existante par session (sans relancer l'IA).
     * Utile au chargement de la page résultats.
     */
    async fetchBySession(sessionId: string) {
      if (this.cache[sessionId]) {
        this.current = this.cache[sessionId];
        return { success: true, data: this.current };
      }

      this._ensureApiConfig();
      this.loading = true;
      this.error = null;

      try {
        const result =
          await CorrectionsService.getCorrectionBySessionApiV1CorrectionsSessionSessionIdGet(
            sessionId,
          );

        if (result) {
          this.current = result;
          this.cache[sessionId] = result;
        }
        return { success: true, data: result };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors du chargement";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    clearCurrent() {
      this.current = null;
      this.error = null;
    },
  },
});
