// stores/adminCenters.ts
import { defineStore } from "pinia";
import { CentersService, OpenAPI } from "#shared/api";
import type {
  CenterCreateRequest,
  CenterResponse,
  BranchCreateRequest,
  LicenseFormulaCreateRequest,
  LicenseFormulaResponse,
  CenterLicenseActivateRequest,
  CenterLicenseExtendRequest,
} from "#shared/api";

interface AdminCentersState {
  centers: CenterResponse[];
  formulas: LicenseFormulaResponse[];
  loading: boolean;
  error: string | null;
}

export const useAdminCentersStore = defineStore("adminCenters", {
  state: (): AdminCentersState => ({
    centers: [],
    formulas: [],
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

    async fetchCenters(skip = 0, limit = 100) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        this.centers = await CentersService.listCentersApiV1CentersGet(
          skip,
          limit,
        );
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement centres";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchFormulas() {
      this._ensureApiConfig();
      try {
        this.formulas =
          await CentersService.listFormulasApiV1CentersFormulasGet();
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement formules",
        };
      }
    },

    async createCenter(data: CenterCreateRequest) {
      this._ensureApiConfig();
      try {
        const center = await CentersService.createCenterApiV1CentersPost(data);
        this.centers.push(center);
        return { success: true, center };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création centre",
        };
      }
    },

    async createBranch(centerId: string, data: BranchCreateRequest) {
      this._ensureApiConfig();
      try {
        const branch =
          await CentersService.createBranchApiV1CentersCenterIdBranchesPost(
            centerId,
            data,
          );
        return { success: true, branch };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création succursale",
        };
      }
    },

    async createFormula(data: LicenseFormulaCreateRequest) {
      this._ensureApiConfig();
      try {
        const formula =
          await CentersService.createFormulaApiV1CentersFormulasPost(data);
        this.formulas.push(formula);
        return { success: true, formula };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur création formule",
        };
      }
    },

    async activateLicense(
      centerId: string,
      data: CenterLicenseActivateRequest,
    ) {
      this._ensureApiConfig();
      try {
        const license =
          await CentersService.activateLicenseApiV1CentersCenterIdLicenseActivatePost(
            centerId,
            data,
          );
        return { success: true, license };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur activation licence",
        };
      }
    },

    async extendLicense(centerId: string, data: CenterLicenseExtendRequest) {
      this._ensureApiConfig();
      try {
        const license =
          await CentersService.extendLicenseApiV1CentersCenterIdLicenseExtendPost(
            centerId,
            data,
          );
        return { success: true, license };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur extension licence",
        };
      }
    },

    async fetchCertificate(
      centerId: string,
    ): Promise<{ success: boolean; certificateUrl?: string; error?: string }> {
      this._ensureApiConfig();
      try {
        const result =
          await CentersService.getLicenseCertificateAdminApiV1CentersCenterIdLicenseCertificateGet(
            centerId,
          );
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
  },
});
