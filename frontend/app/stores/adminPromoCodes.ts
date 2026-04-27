import { defineStore } from "pinia";
import { PromoCodesService, OpenAPI } from "#shared/api";
import type {
  PromoCodeResponse,
  PromoCodeCreateRequest,
  PromoCodeUpdateRequest,
} from "#shared/api";

interface AdminPromoCodesState {
  codes: PromoCodeResponse[];
  loading: boolean;
  error: string | null;
}

export const useAdminPromoCodesStore = defineStore("adminPromoCodes", {
  state: (): AdminPromoCodesState => ({
    codes: [],
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

    async fetchCodes() {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const data = await PromoCodesService.listPromoCodesApiV1PromoCodesGet();
        this.codes = data;
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement codes promo";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async createCode(data: PromoCodeCreateRequest) {
      this._ensureApiConfig();
      try {
        const created = await PromoCodesService.createPromoCodeApiV1PromoCodesPost(data);
        this.codes.unshift(created);
        return { success: true, data: created };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    async updateCode(codeId: string, data: PromoCodeUpdateRequest) {
      this._ensureApiConfig();
      try {
        const updated = await PromoCodesService.updatePromoCodeApiV1PromoCodesCodeIdPatch(
          codeId, data
        );
        const index = this.codes.findIndex(c => c.id === codeId);
        if (index !== -1) this.codes[index] = updated;
        return { success: true, data: updated };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    async deleteCode(codeId: string) {
      this._ensureApiConfig();
      try {
        await PromoCodesService.deletePromoCodeApiV1PromoCodesCodeIdDelete(codeId);
        this.codes = this.codes.filter(c => c.id !== codeId);
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },
  },
});