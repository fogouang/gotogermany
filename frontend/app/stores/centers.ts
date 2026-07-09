// stores/centerStaff.ts
import { defineStore } from "pinia";
import { UsersService, CentersService, OpenAPI } from "#shared/api";
import type {
  StudentResponse,
  StudentCreateRequest,
  StudentTargetUpdateRequest,
  StudentCreditAdjustRequest,
  StudentAccessDatesUpdateRequest,
  StudentProgressResponse,
  SecretaryCreateRequest,
  UserAdminResponse,
  BranchCreateRequest,
  LicenseUsageResponse,
  BranchResponse,
  CenterPoolResponse,
  CenterCreditTransactionResponse,
  StudentDetailedProgressResponse,
} from "#shared/api";

interface CenterStaffState {
  students: StudentResponse[];
  progress: StudentProgressResponse[];
  loading: boolean;
  error: string | null;
}

export const useCenterStaffStore = defineStore("centerStaff", {
  state: (): CenterStaffState => ({
    students: [],
    progress: [],
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

    // ── Directeur ──────────────────────────
    async createSecretary(data: SecretaryCreateRequest): Promise<{
      success: boolean;
      secretary?: UserAdminResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const secretary =
          await UsersService.createSecretaryApiV1UsersSecretariesPost(data);
        return { success: true, secretary };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création secrétaire",
        };
      }
    },

    async fetchStudentsByCenter(): Promise<{
      success: boolean;
      students?: StudentResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const students =
          await UsersService.listStudentsByCenterApiV1UsersStudentsByCenterGet();
        this.students = students;
        return { success: true, students };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement étudiants";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async fetchMyUsage(): Promise<{
      success: boolean;
      usage?: LicenseUsageResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const usage =
          await CentersService.getMyCenterUsageApiV1CentersMeUsageGet();
        return { success: true, usage };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement licence";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async fetchMyBranches(): Promise<{
      success: boolean;
      branches?: BranchResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const branches =
          await CentersService.listMyBranchesApiV1CentersMeBranchesGet();
        return { success: true, branches };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement succursales",
        };
      }
    },

    async fetchSecretaries(): Promise<{
      success: boolean;
      secretaries?: UserAdminResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const secretaries =
          await UsersService.listSecretariesApiV1UsersSecretariesGet();
        return { success: true, secretaries };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement secrétaires",
        };
      }
    },

    async createMyBranch(data: BranchCreateRequest) {
      this._ensureApiConfig();
      try {
        const branch =
          await CentersService.createMyBranchApiV1CentersMeBranchesPost(data);
        return { success: true, branch };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création succursale",
        };
      }
    },

    async fetchMyCertificate(): Promise<{
      success: boolean;
      certificateUrl?: string;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const result =
          await CentersService.getMyLicenseCertificateApiV1CentersMeLicenseCertificateGet();
        const relativeUrl = (result as any).certificate_url as string;
        const config = useRuntimeConfig();
        const base = config.public.apiBaseUrl || "http://localhost:8001";
        return { success: true, certificateUrl: `${base}${relativeUrl}` };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur génération attestation",
        };
      }
    },

    // ── Directeur : activation/désactivation d'un étudiant ──
    async toggleStudentActivation(studentId: string): Promise<{
      success: boolean;
      student?: StudentResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const updated =
          await UsersService.toggleStudentActivationApiV1UsersStudentsStudentIdActivationPatch(
            studentId,
          );
        const index = this.students.findIndex((s) => s.id === studentId);
        if (index !== -1) this.students[index] = updated;
        return { success: true, student: updated };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur activation/désactivation",
        };
      }
    },

    // ── Directeur : ajustement de la fenêtre d'accès ────────
    async updateStudentAccessDates(
      studentId: string,
      data: StudentAccessDatesUpdateRequest,
    ): Promise<{
      success: boolean;
      student?: StudentResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const updated =
          await UsersService.updateStudentAccessDatesApiV1UsersStudentsStudentIdAccessDatesPatch(
            studentId,
            data,
          );
        const index = this.students.findIndex((s) => s.id === studentId);
        if (index !== -1) this.students[index] = updated;
        return { success: true, student: updated };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur mise à jour des dates",
        };
      }
    },

    // ── Directeur + Secrétaire : ajustement de crédits ──────
    async adjustStudentCredits(
      studentId: string,
      data: StudentCreditAdjustRequest,
    ): Promise<{
      success: boolean;
      student?: StudentResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const updated =
          await UsersService.adjustStudentCreditsApiV1UsersStudentsStudentIdCreditsPatch(
            studentId,
            data,
          );
        const index = this.students.findIndex((s) => s.id === studentId);
        if (index !== -1) this.students[index] = updated;
        return { success: true, student: updated };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur ajustement des crédits",
        };
      }
    },

    // ── Directeur + Secrétaire : progression des étudiants ──
    async fetchStudentProgress(): Promise<{
      success: boolean;
      progress?: StudentProgressResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const progress =
          await UsersService.getStudentProgressApiV1UsersStudentsProgressGet();
        this.progress = progress;
        return { success: true, progress };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement progression";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async fetchMyPool(): Promise<{
      success: boolean;
      pool?: CenterPoolResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const pool =
          await CentersService.getMyCenterPoolApiV1CentersMePoolGet();
        return { success: true, pool };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement du pool",
        };
      }
    },

    async updateDefaultCredits(defaultCredits: number): Promise<{
      success: boolean;
      pool?: CenterPoolResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const pool =
          await CentersService.updateDefaultCreditsApiV1CentersMeDefaultCreditsPatch(
            {
              default_credits_per_student: defaultCredits,
            },
          );
        return { success: true, pool };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur mise à jour du défaut",
        };
      }
    },

    async fetchCreditTransactions(): Promise<{
      success: boolean;
      transactions?: CenterCreditTransactionResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const transactions =
          await CentersService.getMyCenterCreditTransactionsApiV1CentersMeCreditTransactionsGet();
        return { success: true, transactions };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement historique",
        };
      }
    },

    async fetchMyCreditTransactions(): Promise<{
      success: boolean;
      transactions?: CenterCreditTransactionResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const transactions =
          await CentersService.getMyCreditTransactionsApiV1CentersMeCreditTransactionsMineGet();
        return { success: true, transactions };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement historique",
        };
      }
    },

    async fetchStudentProgressDetail(studentId: string): Promise<{
      success: boolean;
      detail?: StudentDetailedProgressResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const detail =
          await UsersService.getStudentProgressDetailApiV1UsersStudentsStudentIdProgressDetailGet(
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

    // ── Secrétaire ─────────────────────────
    async createStudent(data: StudentCreateRequest) {
      this._ensureApiConfig();
      try {
        const student =
          await UsersService.createStudentApiV1UsersStudentsPost(data);
        this.students.push(student);
        return { success: true, student };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création étudiant",
        };
      }
    },

    async fetchStudentsByBranch(): Promise<{
      success: boolean;
      students?: StudentResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const students =
          await UsersService.listStudentsByBranchApiV1UsersStudentsByBranchGet();
        this.students = students;
        return { success: true, students };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement étudiants";
        return { success: false, error: this.error ?? undefined };
      } finally {
        this.loading = false;
      }
    },

    async updateStudentTarget(
      studentId: string,
      data: StudentTargetUpdateRequest,
    ) {
      this._ensureApiConfig();
      try {
        const updated =
          await UsersService.updateStudentTargetApiV1UsersStudentsStudentIdTargetPatch(
            studentId,
            data,
          );
        const index = this.students.findIndex((s) => s.id === studentId);
        if (index !== -1) this.students[index] = updated;
        return { success: true, student: updated };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur mise à jour cible",
        };
      }
    },
  },
});
