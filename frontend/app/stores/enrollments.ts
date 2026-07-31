// stores/enrollments.ts
import { defineStore } from "pinia";
import { EnrollmentsService, InvoicesService, OpenAPI } from "#shared/api";
import type {
  CursusCreateRequest,
  CursusResponse,
  LevelEnrollmentCreateRequest,
  LevelEnrollmentResponse,
  PaymentCreateRequest,
  BalanceSummaryResponse,
  app__modules__enrollments__schemas__PaymentResponse as FormationPaymentResponse,
  RevenueSummaryResponse,
} from "#shared/api";

interface EnrollmentsState {
  cursusList: CursusResponse[];
  loading: boolean;
  error: string | null;
}

export const useEnrollmentsStore = defineStore("enrollments", {
  state: (): EnrollmentsState => ({
    cursusList: [],
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

    async fetchCursusList() {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        this.cursusList =
          await EnrollmentsService.listCursusApiV1EnrollmentsCursusGet();
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement des cursus";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async createCursus(data: CursusCreateRequest) {
      this._ensureApiConfig();
      try {
        const cursus =
          await EnrollmentsService.createCursusApiV1EnrollmentsCursusPost(data);
        this.cursusList.push(cursus);
        return { success: true, cursus };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création cursus",
        };
      }
    },

    async createLevelEnrollment(
      cursusId: string,
      data: LevelEnrollmentCreateRequest,
    ): Promise<{
      success: boolean;
      enrollment?: LevelEnrollmentResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const enrollment =
          await EnrollmentsService.createLevelEnrollmentApiV1EnrollmentsCursusCursusIdLevelsPost(
            cursusId,
            data,
          );
        return { success: true, enrollment };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création inscription",
        };
      }
    },

    async recordPayment(enrollmentId: string, data: PaymentCreateRequest) {
      this._ensureApiConfig();
      try {
        const payment =
          await EnrollmentsService.recordPaymentApiV1EnrollmentsLevelsEnrollmentIdPaymentsPost(
            enrollmentId,
            data,
          );
        return { success: true, payment };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur enregistrement paiement",
        };
      }
    },

    async fetchBalance(enrollmentId: string): Promise<{
      success: boolean;
      balance?: BalanceSummaryResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const balance =
          await EnrollmentsService.getBalanceApiV1EnrollmentsLevelsEnrollmentIdPaymentsBalanceGet(
            enrollmentId,
          );
        return { success: true, balance };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement solde",
        };
      }
    },

    // stores/enrollments.ts — ajouter dans actions
    async generateInvoice(paymentId: string): Promise<{
      success: boolean;
      invoiceUrl?: string;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const result =
          await InvoicesService.generateFormationInvoiceApiV1InvoicesGenerateFormationPaymentIdPost(
            paymentId,
          );
        const relativeUrl = (result as any).data?.invoice_url as string;
        const config = useRuntimeConfig();
        const base = config.public.apiBaseUrl || "http://localhost:8001";
        return { success: true, invoiceUrl: `${base}${relativeUrl}` };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur génération du reçu",
        };
      }
    },

    async fetchPayments(enrollmentId: string): Promise<{
      success: boolean;
      payments?: FormationPaymentResponse[];
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const payments =
          await EnrollmentsService.listPaymentsApiV1EnrollmentsLevelsEnrollmentIdPaymentsGet(
            enrollmentId,
          );
        return { success: true, payments };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement des paiements",
        };
      }
    },

    async fetchRevenueSummary(): Promise<{
      success: boolean;
      revenue?: RevenueSummaryResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      console.log(
        "[enrollments] EnrollmentsService.getRevenueSummaryApiV1EnrollmentsRevenueGet existe ?",
        typeof EnrollmentsService.getRevenueSummaryApiV1EnrollmentsRevenueGet,
      );
      try {
        const revenue =
          await EnrollmentsService.getRevenueSummaryApiV1EnrollmentsRevenueGet();
        console.log("[enrollments] fetchRevenueSummary résultat =", revenue);
        return { success: true, revenue };
      } catch (error: any) {
        console.error("[enrollments] fetchRevenueSummary RAW ERROR:", error);
        console.error("[enrollments] error.message:", error?.message);
        console.error("[enrollments] error.body:", error?.body);
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement du revenu",
        };
      }
    },
  },
});
