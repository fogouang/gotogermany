import { defineStore } from "pinia";
import { PartnersService, OpenAPI } from "#shared/api";
import type {
  PartnerDetailResponse,
  PartnerCreateRequest,
  PartnerUpdateRequest,
  PartnerStatsResponse,
} from "#shared/api";

interface AdminPartnersState {
  partners: PartnerDetailResponse[];
  loading: boolean;
  error: string | null;
}

export const useAdminPartnersStore = defineStore("adminPartners", {
  state: (): AdminPartnersState => ({
    partners: [],
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

    async fetchPartners() {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const data = await PartnersService.listPartnersApiV1PartnersGet();
        this.partners = data;
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur chargement partenaires";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async createPartner(data: PartnerCreateRequest) {
      this._ensureApiConfig();
      try {
        const created = await PartnersService.createPartnerApiV1PartnersPost(data);
        this.partners.unshift(created);
        return { success: true, data: created };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    async updatePartner(partnerId: string, data: PartnerUpdateRequest) {
      this._ensureApiConfig();
      try {
        const updated = await PartnersService.updatePartnerApiV1PartnersPartnerIdPatch(
          partnerId, data
        );
        const index = this.partners.findIndex(p => p.id === partnerId);
        if (index !== -1) this.partners[index] = updated;
        return { success: true, data: updated };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    async deletePartner(partnerId: string) {
      this._ensureApiConfig();
      try {
        await PartnersService.deletePartnerApiV1PartnersPartnerIdDelete(partnerId);
        this.partners = this.partners.filter(p => p.id !== partnerId);
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    async getStats(partnerId: string): Promise<PartnerStatsResponse | null> {
      this._ensureApiConfig();
      try {
        return await PartnersService.getPartnerStatsApiV1PartnersPartnerIdStatsGet(partnerId);
      } catch {
        return null;
      }
    },
  },
});