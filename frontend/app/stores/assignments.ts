// stores/assignments.ts
import { defineStore } from "pinia";
import { AssignmentsService, OpenAPI } from "#shared/api";
import type {
  AssignmentCreate,
  AssignmentDetailResponse,
  AssignmentSummaryResponse,
  BankSubjectResponse,
  GradeRequest,
  SubmissionGradingResponse,
} from "#shared/api";

type Result<T> = { success: true; data: T } | { success: false; error: string };

interface AssignmentsState {
  teaching: AssignmentSummaryResponse[];
  bank: BankSubjectResponse[];
  current: AssignmentDetailResponse | null;
  loading: boolean;
}

// Renvoie le message du backend s'il existe, sinon "" : la page affiche alors sa propre clé traduite
function erreur(error: any): string {
  const detail = error?.body?.detail;
  return typeof detail === "string" ? detail : "";
}

export const useAssignmentsStore = defineStore("assignments", {
  state: (): AssignmentsState => ({
    teaching: [],
    bank: [],
    current: null,
    loading: false,
  }),

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    // ── Enseignant ─────────────────────────────
    async fetchTeaching(): Promise<Result<AssignmentSummaryResponse[]>> {
      this._ensureApiConfig();
      this.loading = true;
      try {
        this.teaching = await AssignmentsService.myTeachingAssignmentsApiV1AssignmentsTeachingGet();
        return { success: true, data: this.teaching };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      } finally {
        this.loading = false;
      }
    },

    async fetchBank(levelId?: string | null): Promise<Result<BankSubjectResponse[]>> {
      this._ensureApiConfig();
      try {
        this.bank = await AssignmentsService.subjectBankApiV1AssignmentsBankGet(levelId ?? null);
        return { success: true, data: this.bank };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },

    async create(payload: AssignmentCreate): Promise<Result<AssignmentDetailResponse>> {
      this._ensureApiConfig();
      try {
        const created = await AssignmentsService.createAssignmentApiV1AssignmentsPost(payload);
        this.current = created;
        return { success: true, data: created };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },

    async fetchDetail(assignmentId: string): Promise<Result<AssignmentDetailResponse>> {
      this._ensureApiConfig();
      try {
        this.current = await AssignmentsService.assignmentDetailApiV1AssignmentsAssignmentIdGet(assignmentId);
        return { success: true, data: this.current };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },

    async cancel(assignmentId: string): Promise<Result<true>> {
      this._ensureApiConfig();
      try {
        await AssignmentsService.cancelAssignmentApiV1AssignmentsAssignmentIdCancelPost(assignmentId);
        const row = this.teaching.find((a) => a.id === assignmentId);
        if (row) row.is_cancelled = true;
        if (this.current?.id === assignmentId) this.current.is_cancelled = true;
        return { success: true, data: true };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },

    // ── Correction ─────────────────────────────
    async fetchSubmission(
      assignmentId: string,
      studentId: string,
    ): Promise<Result<SubmissionGradingResponse>> {
      this._ensureApiConfig();
      try {
        const data =
          await AssignmentsService.submissionForGradingApiV1AssignmentsAssignmentIdSubmissionsStudentIdGet(
            assignmentId,
            studentId,
          );
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },

    async grade(
      assignmentId: string,
      studentId: string,
      payload: GradeRequest,
    ): Promise<Result<SubmissionGradingResponse>> {
      this._ensureApiConfig();
      try {
        const data =
          await AssignmentsService.gradeSubmissionApiV1AssignmentsAssignmentIdSubmissionsStudentIdGradePost(
            assignmentId,
            studentId,
            payload,
          );
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },

    async uploadAnnotated(assignmentId: string, studentId: string, file: File): Promise<Result<true>> {
      this._ensureApiConfig();
      try {
        // Le modèle généré type le fichier en string (binary) : on passe le File tel quel
        await AssignmentsService.uploadAnnotatedCopyApiV1AssignmentsAssignmentIdSubmissionsStudentIdAnnotatedPost(
          assignmentId,
          studentId,
          { file: file as unknown as string },
        );
        return { success: true, data: true };
      } catch (error: any) {
        return { success: false, error: erreur(error) };
      }
    },
  },
});