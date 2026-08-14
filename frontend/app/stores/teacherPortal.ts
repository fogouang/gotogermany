import { defineStore } from "pinia";
import { TrainingSessionsService, OpenAPI } from "#shared/api";
import type {
  TrainingSessionResponse,
  TrainingSessionTeacherResponse,
  TrainingSessionStudentResponse,
  StudentDetailedProgressResponse,
  TeacherCommentCreateRequest,
  TeacherCommentResponse,
  StudentProgressResponse,
} from "#shared/api";

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

interface TeacherPortalState {
  mySessions: NormalizedTrainingSession[];
  loading: boolean;
  error: string | null;
}

export const useTeacherPortalStore = defineStore("teacherPortal", {
  state: (): TeacherPortalState => ({
    mySessions: [],
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

    async fetchMySessions(): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const sessions =
          await TrainingSessionsService.listMySessionsApiV1TrainingSessionsMineGet();
        this.mySessions = sessions.map(normalizeSession);
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement des sessions";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async fetchStudentProgress(studentId: string): Promise<{
      success: boolean;
      detail?: StudentDetailedProgressResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const detail =
          await TrainingSessionsService.getStudentProgressForTeacherApiV1TrainingSessionsStudentsStudentIdProgressGet(
            studentId,
          );
        return { success: true, detail };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement du détail",
        };
      }
    },

    async fetchSessionResult(
      studentId: string,
      sessionId: string,
    ): Promise<{ success: boolean; result?: any; error?: string }> {
      this._ensureApiConfig();
      try {
        const result =
          await TrainingSessionsService.getStudentSessionResultForTeacherApiV1TrainingSessionsStudentsStudentIdSessionsSessionIdResultGet(
            studentId,
            sessionId,
          );
        return { success: true, result };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement du résultat",
        };
      }
    },

    async fetchComments(studentId: string): Promise<{
      success: boolean;
      comments?: TeacherCommentResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const comments =
          await TrainingSessionsService.listStudentCommentsForTeacherApiV1TrainingSessionsStudentsStudentIdCommentsGet(
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

    async addComment(
      studentId: string,
      data: TeacherCommentCreateRequest,
    ): Promise<{
      success: boolean;
      comment?: TeacherCommentResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const comment =
          await TrainingSessionsService.addStudentCommentApiV1TrainingSessionsStudentsStudentIdCommentsPost(
            studentId,
            data,
          );
        return { success: true, comment };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur ajout du commentaire",
        };
      }
    },

    async fetchStudentsProgress(): Promise<{
      success: boolean;
      progress?: StudentProgressResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const progress =
          await TrainingSessionsService.getStudentsProgressForTeacherApiV1TrainingSessionsStudentsProgressGet();
        return { success: true, progress };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement de la progression",
        };
      }
    },
  },
});
