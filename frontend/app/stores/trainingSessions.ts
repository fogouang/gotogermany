import { defineStore } from "pinia";
import { TrainingSessionsService, OpenAPI } from "#shared/api";
import type {
  TrainingSessionCreateRequest,
  TrainingSessionUpdateRequest,
  TrainingSessionResponse,
  TrainingSessionTeacherResponse,
  TrainingSessionStudentResponse,
  TeacherAssignRequest,
  StudentEnrollRequest,
  StudentEndRequest,
  TrainingSessionStatsResponse,
  TeacherCommentResponse,
} from "#shared/api";

// Le backend renvoie toujours teachers/students (défaut []), mais le
// typegen les marque optionnels car le schéma Pydantic a une valeur par
// défaut. On normalise ici une bonne fois pour toutes, et ce type devient
// la source de vérité pour tout le frontend — plus jamais de `?? []`
// ni de `possibly undefined` à gérer dans les pages qui consomment ce store.
export type NormalizedTrainingSession = TrainingSessionResponse & {
  teachers: TrainingSessionTeacherResponse[];
  students: TrainingSessionStudentResponse[];
};

function normalizeSession(
  s: TrainingSessionResponse,
): NormalizedTrainingSession {
  return {
    ...s,
    teachers: s.teachers ?? [],
    students: s.students ?? [],
  };
}

interface TrainingSessionsState {
  sessions: NormalizedTrainingSession[];
  loading: boolean;
  error: string | null;
}

export const useTrainingSessionsStore = defineStore("trainingSessions", {
  state: (): TrainingSessionsState => ({
    sessions: [],
    loading: false,
    error: null,
  }),
  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    async fetchByCenter(): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const sessions =
          await TrainingSessionsService.listSessionsByCenterApiV1TrainingSessionsByCenterGet();
        this.sessions = sessions.map(normalizeSession);
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement des sessions";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async fetchByBranch(): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const sessions =
          await TrainingSessionsService.listSessionsByBranchApiV1TrainingSessionsByBranchGet();
        this.sessions = sessions.map(normalizeSession);
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement des sessions";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async createSession(data: TrainingSessionCreateRequest): Promise<{
      success: boolean;
      session?: NormalizedTrainingSession;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const session =
          await TrainingSessionsService.createSessionApiV1TrainingSessionsPost(
            data,
          );
        const normalized = normalizeSession(session);
        this.sessions.unshift(normalized);
        return { success: true, session: normalized };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création session",
        };
      }
    },

    async updateSession(
      sessionId: string,
      data: TrainingSessionUpdateRequest,
    ): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        const updated =
          await TrainingSessionsService.updateSessionApiV1TrainingSessionsSessionIdPatch(
            sessionId,
            data,
          );
        const index = this.sessions.findIndex((s) => s.id === sessionId);
        if (index !== -1) this.sessions[index] = normalizeSession(updated);
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur mise à jour session",
        };
      }
    },

    async assignTeacher(
      sessionId: string,
      data: TeacherAssignRequest,
    ): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        await TrainingSessionsService.assignTeacherApiV1TrainingSessionsSessionIdTeachersPost(
          sessionId,
          data,
        );
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur affectation enseignant",
        };
      }
    },

    async removeTeacher(
      sessionId: string,
      teacherId: string,
    ): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        await TrainingSessionsService.removeTeacherApiV1TrainingSessionsSessionIdTeachersTeacherIdDelete(
          sessionId,
          teacherId,
        );
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur retrait enseignant",
        };
      }
    },

    async enrollStudent(
      sessionId: string,
      data: StudentEnrollRequest,
    ): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        await TrainingSessionsService.enrollStudentApiV1TrainingSessionsSessionIdStudentsPost(
          sessionId,
          data,
        );
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur inscription étudiant",
        };
      }
    },

    async endStudent(
      sessionId: string,
      studentId: string,
      data: StudentEndRequest,
    ): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        await TrainingSessionsService.endStudentApiV1TrainingSessionsSessionIdStudentsStudentIdEndPatch(
          sessionId,
          studentId,
          data,
        );
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur clôture étudiant",
        };
      }
    },

    async fetchStats(sessionId: string): Promise<{
      success: boolean;
      stats?: TrainingSessionStatsResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const stats =
          await TrainingSessionsService.getSessionStatsApiV1TrainingSessionsSessionIdStatsGet(
            sessionId,
          );
        return { success: true, stats };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement statistiques",
        };
      }
    },

    async fetchCommentsForDirector(studentId: string): Promise<{
      success: boolean;
      comments?: TeacherCommentResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const comments =
          await TrainingSessionsService.listStudentCommentsForDirectorApiV1TrainingSessionsStudentsStudentIdCommentsAllGet(
            studentId,
          );
        return { success: true, comments };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement des commentaires",
        };
      }
    },
  },
});
