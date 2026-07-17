// stores/referrals.ts
import { defineStore } from "pinia";
import { ReferralsService, OpenAPI, PaymentsService } from "#shared/api";
import type { ReferralDashboardResponse } from "#shared/api";

interface ReferralsState {
  dashboard: ReferralDashboardResponse | null;
  loading: boolean;
  error: string | null;
  settingAmbassador: boolean;
  ambassadorError: string | null;
}

export const useReferralsStore = defineStore("referrals", {
  state: (): ReferralsState => ({
    dashboard: null,
    loading: false,
    error: null,
    settingAmbassador: false,
    ambassadorError: null,
  }),

  getters: {
    referredCount: (state): number => state.dashboard?.referred_count ?? 0,
    totalEarnings: (state): number => state.dashboard?.total_earnings ?? 0,
    referralLink: (state): string => state.dashboard?.referral_link ?? "",
    referredUsers: (state) => state.dashboard?.referred_users ?? [],
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
      return tokenCookie.value ?? undefined;
    },

    async fetchDashboard() {
      const accessToken = this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        this.dashboard =
          await ReferralsService.myReferralDashboardApiV1ReferralsMeGet(
            accessToken,
          );
        return { success: true };
      } catch (e: any) {
        this.error =
          e.body?.detail ||
          "Erreur lors du chargement du tableau de parrainage";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async setAmbassadorStatus(userId: string, isAmbassador: boolean) {
      const accessToken = this._ensureApiConfig();
      this.settingAmbassador = true;
      this.ambassadorError = null;
      try {
        await ReferralsService.setAmbassadorStatusApiV1ReferralsAdminSetAmbassadorPost(
          { user_id: userId, is_ambassador: isAmbassador },
          accessToken,
        );
        return { success: true };
      } catch (e: any) {
        this.ambassadorError =
          e.body?.detail ||
          "Erreur lors de la mise à jour du statut ambassadeur";
        return { success: false, error: this.ambassadorError };
      } finally {
        this.settingAmbassador = false;
      }
    },
    async validateManualPayment(
      userId: string,
      levelId: string,
      planId: string,
      note?: string,
    ) {
      const accessToken = this._ensureApiConfig();
      this.settingAmbassador = true; // réutilise l'indicateur de chargement existant
      this.ambassadorError = null;
      try {
        await PaymentsService.createAmbassadorManualPaymentApiV1PaymentsManualAmbassadorPost(
          {
            user_id: userId,
            level_id: levelId,
            plan_id: planId,
            note: note || null,
          },
          accessToken,
        );
        await this.fetchDashboard(); // rafraîchit la liste + les gains après validation
        return { success: true };
      } catch (e: any) {
        this.ambassadorError =
          e.body?.detail || "Erreur lors de la validation du paiement";
        return { success: false, error: this.ambassadorError };
      } finally {
        this.settingAmbassador = false;
      }
    },

    clearDashboard() {
      this.dashboard = null;
      this.error = null;
    },
  },
});
