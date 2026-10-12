// stores/adminCenters.ts
import { defineStore } from "pinia";
import { CentersService, OpenAPI } from "#shared/api";
import type {
  CenterCreateRequest,
  CenterResponse,
  BranchCreateRequest,
  CenterCreditPoolRechargeRequest,
  CenterPoolResponse,
} from "#shared/api";

interface AdminCentersState {
  centers: CenterResponse[];
  loading: boolean;
  error: string | null;
}

export const useAdminCentersStore = defineStore("adminCenters", {
  state: (): AdminCentersState => ({
    centers: [],
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