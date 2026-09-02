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
  CenterLicenseResponse,
  CenterCreditPoolRechargeRequest,
  CenterPoolResponse,
} from "#shared/api";

interface AdminCentersState {
  centers: CenterResponse[];
  formulas: LicenseFormulaResponse[];
  // Licence active par centre — clé = center_id. `null` = pas de licence
  // active, absent = pas encore chargée pour ce centre.
  licenses: Record<string, CenterLicenseResponse | null>;
  loading: boolean;
  error: string | null;
}

// NOTE: requête pour l'ajustement direct des dates de licence (début/fin).
// Correspond au schéma backend CenterLicenseDatesUpdateRequest (à ajouter
// dans app/modules/centers/schemas.py) — une fois le client OpenAPI
// régénéré, ce type pourra être remplacé par celui généré automatiquement
// depuis #shared/api.
export interface CenterLicenseDatesUpdateRequest {
  start_date: string; // "YYYY-MM-DD"
  end_date: string; // "YYYY-MM-DD"
}

export const useAdminCentersStore = defineStore("adminCenters", {
  state: (): AdminCentersState => ({
    centers: [],
    formulas: [],
    licenses: {},
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

    // ── Licence active d'un centre (pour affichage début/fin) ──────
    // NOTE: suppose un endpoint backend GET /api/v1/centers/{center_id}/license
    // (retourne la licence active ou null). Tant que cette méthode n'existe
    // pas sur CentersService (client généré), l'appel passe par un cast
    // `as any` — à retirer une fois l'endpoint ajouté côté backend et le
    // client régénéré.
    async fetchLicenseForCenter(centerId: string): Promise<{
      success: boolean;
      license?: CenterLicenseResponse | null;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const license = await (
          CentersService as any
        ).getCenterLicenseApiV1CentersCenterIdLicenseGet(centerId);
        this.licenses[centerId] = license ?? null;
        return { success: true, license: this.licenses[centerId] };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur chargement de la licence",
        };
      }
    },

    // Charge la licence active de chaque centre déjà présent dans
    // `this.centers` — à appeler après fetchCenters() pour peupler les
    // colonnes Début/Fin du tableau.
    async fetchAllLicenses() {
      await Promise.all(
        this.centers.map((center) => this.fetchLicenseForCenter(center.id)),
      );
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
        this.licenses[centerId] = license;
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
        this.licenses[centerId] = license;
        return { success: true, license };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur extension licence",
        };
      }
    },

    // ── Ajustement direct des dates de licence (début / fin) ──────
    // NOTE: suppose un endpoint backend PATCH
    // /api/v1/centers/{center_id}/license/dates (schéma
    // CenterLicenseDatesUpdateRequest côté backend). Cast `as any` en
    // attendant que le client OpenAPI soit régénéré avec cette méthode.
    async updateLicenseDates(
      centerId: string,
      data: CenterLicenseDatesUpdateRequest,
    ): Promise<{
      success: boolean;
      license?: CenterLicenseResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const license = await (
          CentersService as any
        ).updateLicenseDatesApiV1CentersCenterIdLicenseDatesPatch(
          centerId,
          data,
        );
        this.licenses[centerId] = license;
        return { success: true, license };
      } catch (error: any) {
        return {
          success: false,
          error:
            error.body?.detail || "Erreur mise à jour des dates de licence",
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

    // ── Rechargement du pool de crédits IA d'un centre ──────
    async rechargeCreditPool(
      centerId: string,
      data: CenterCreditPoolRechargeRequest,
    ): Promise<{
      success: boolean;
      pool?: CenterPoolResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const pool =
          await CentersService.rechargeCreditPoolApiV1CentersCenterIdCreditPoolRechargePost(
            centerId,
            data,
          );
        return { success: true, pool };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur rechargement du pool",
        };
      }
    },
    async toggleCenterActive(centerId: string): Promise<{
      success: boolean;
      center?: CenterResponse;
      error?: string;
    }> {
      this._ensureApiConfig();
      try {
        const center =
          await CentersService.toggleCenterActiveApiV1CentersCenterIdToggleActivePatch(
            centerId,
          );
        const index = this.centers.findIndex((c) => c.id === centerId);
        if (index !== -1) this.centers[index] = center;
        return { success: true, center };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || "Erreur changement de statut",
        };
      }
    },
  },
});