// store/liveSession.ts
import { defineStore } from "pinia";
import { LiveSessionService, OpenAPI } from "#shared/api";
import type {
  LiveSessionResponse,
  CreateLiveSessionRequest,
  SubmitNotesRequest,
} from "#shared/api";

interface LiveSessionState {
  launched: LiveSessionResponse[];
  mine: LiveSessionResponse[];
  loading: boolean;
  error: string | null;
}

export const useLiveSessionStore = defineStore("liveSession", {
  state: (): LiveSessionState => ({
    launched: [],
    mine: [],
    loading: false,
    error: null,
  }),

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
      return tokenCookie.value ?? undefined;
    },

    // ── Commun (candidat ou examinateur) ──

    async getSession(liveSessionId: string): Promise<{
      success: boolean;
      session?: LiveSessionResponse;
      error?: string;
    }> {
      const accessToken = this._ensureApiConfig();
      try {
        const session =
          await LiveSessionService.getLiveSessionApiV1LiveSessionLiveSessionIdGet(
            liveSessionId,
            accessToken,
          );
        return { success: true, session };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement de la session",
        };
      }
    },

    async getSubjectContent(liveSessionId: string): Promise<{
      success: boolean;
      content?: any;
      error?: string;
    }> {
      const accessToken = this._ensureApiConfig();
      try {
        // NOTE : nom de méthode à confirmer une fois le client OpenAPI
        // régénéré, même remarque que pour getSession() plus haut.
        const content =
          await LiveSessionService.getLiveSessionSubjectApiV1LiveSessionLiveSessionIdSubjectGet(
            liveSessionId,
            accessToken,
          );
        return { success: true, content };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement du sujet",
        };
      }
    },

    // ── Examinateur ────────────────────────

    async createSession(data: CreateLiveSessionRequest): Promise<{
      success: boolean;
      session?: LiveSessionResponse;
      error?: string;
    }> {
      const accessToken = this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const session =
          await LiveSessionService.createLiveSessionApiV1LiveSessionPost(
            data,
            accessToken,
          );
        this.launched.unshift(session);
        return { success: true, session };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors du lancement de la session";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async submitNotes(
      liveSessionId: string,
      data: SubmitNotesRequest,
    ): Promise<{ success: boolean; session?: LiveSessionResponse; error?: string }> {
      const accessToken = this._ensureApiConfig();
      try {
        const session =
          await LiveSessionService.submitExaminerNotesApiV1LiveSessionLiveSessionIdNotesPatch(
            liveSessionId,
            data,
            accessToken,
          );
        const index = this.launched.findIndex((s) => s.id === liveSessionId);
        if (index !== -1) this.launched[index] = session;
        return { success: true, session };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur lors de l'envoi des notes",
        };
      }
    },

    async fetchLaunched(): Promise<{ success: boolean; error?: string }> {
      const accessToken = this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const response =
          await LiveSessionService.getLaunchedLiveSessionsApiV1LiveSessionLaunchedGet(
            20,
            0,
            accessToken,
          );
        this.launched = response.items;
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement des sessions";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    // ── Étudiant ───────────────────────────

    async fetchMine(): Promise<{ success: boolean; error?: string }> {
      const accessToken = this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const response =
          await LiveSessionService.getMyLiveSessionsApiV1LiveSessionMineGet(
            20,
            0,
            accessToken,
          );
        this.mine = response.items;
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement des sessions";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    clearError() {
      this.error = null;
    },
  },
});