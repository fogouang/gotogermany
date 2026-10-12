// stores/sales.ts
import { defineStore } from "pinia";
import { SalesService, OpenAPI } from "#shared/api";
import type {
  ActivationRequest,
  ActivationResponse,
  CommissionRuleCreate,
  CommissionRuleResponse,
  CommissionRuleUpdate,
  PartnerSaleResponse,
  PartnerSettingsUpdate,
  PartnerSummaryResponse,
  SettlementCreate,
  SettlementResponse,
} from "#shared/api";

export type PartnerType = "center" | "ambassador";

type Result<T> = { success: true; data: T } | { success: false; error: string };

interface SalesState {
  // Partenaire connecté (directeur de centre ou ambassadeur)
  mySummary: PartnerSummaryResponse | null;
  mySales: PartnerSaleResponse[];
  mySettlements: SettlementResponse[];
  // Admin
  partners: PartnerSummaryResponse[];
  rules: CommissionRuleResponse[];
}

function erreur(error: any, fallback: string): string {
  const detail = error?.body?.detail;
  return typeof detail === "string" ? detail : fallback;
}

export const useSalesStore = defineStore("sales", {
  state: (): SalesState => ({
    mySummary: null,
    mySales: [],
    mySettlements: [],
    partners: [],
    rules: [],
  }),

  getters: {
    /** Total que les partenaires doivent à la plateforme */
    totalOwedToPlatform: (s) =>
      s.partners.reduce((sum, p) => sum + p.owed_to_platform, 0),
    /** Total que la plateforme doit aux partenaires */
    totalOwedToPartners: (s) =>
      s.partners.reduce((sum, p) => sum + p.owed_to_partner, 0),
    blockedPartners: (s) => s.partners.filter((p) => p.is_blocked),
    overduePartners: (s) =>
      s.partners
        .filter((p) => p.overdue_amount > 0)
        .sort((a, b) => b.overdue_amount - a.overdue_amount),
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    // ── Partenaire connecté ─────────────────────────────
    async fetchMySummary(): Promise<Result<PartnerSummaryResponse>> {
      this._ensureApiConfig();
      try {
        this.mySummary = await SalesService.mySummaryApiV1SalesMeSummaryGet();
        return { success: true, data: this.mySummary };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement du solde") };
      }
    },

    async fetchMySales(limit = 50, offset = 0): Promise<Result<PartnerSaleResponse[]>> {
      this._ensureApiConfig();
      try {
        this.mySales = await SalesService.mySalesApiV1SalesMeSalesGet(limit, offset);
        return { success: true, data: this.mySales };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement des ventes") };
      }
    },

    async fetchMySettlements(): Promise<Result<SettlementResponse[]>> {
      this._ensureApiConfig();
      try {
        this.mySettlements =
          await SalesService.mySettlementsApiV1SalesMeSettlementsGet();
        return { success: true, data: this.mySettlements };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement des règlements") };
      }
    },

    async activateAccount(data: ActivationRequest): Promise<Result<ActivationResponse>> {
      this._ensureApiConfig();
      try {
        const res = await SalesService.activateAccountApiV1SalesActivationsPost(data);
        return { success: true, data: res };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur lors de l'activation") };
      }
    },

    // ── Admin : partenaires ─────────────────────────────
    async fetchPartners(): Promise<Result<PartnerSummaryResponse[]>> {
      this._ensureApiConfig();
      try {
        this.partners = await SalesService.partnersOverviewApiV1SalesAdminPartnersGet();
        return { success: true, data: this.partners };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement des partenaires") };
      }
    },

    async fetchPartnerSales(
      type: PartnerType,
      id: string,
      limit = 50,
      offset = 0,
    ): Promise<Result<PartnerSaleResponse[]>> {
      this._ensureApiConfig();
      try {
        const res =
          await SalesService.partnerSalesApiV1SalesAdminPartnersPartnerTypePartnerIdSalesGet(
            type,
            id,
            limit,
            offset,
          );
        return { success: true, data: res };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement des ventes") };
      }
    },

    async fetchPartnerSettlements(
      type: PartnerType,
      id: string,
    ): Promise<Result<SettlementResponse[]>> {
      this._ensureApiConfig();
      try {
        const res =
          await SalesService.partnerSettlementsApiV1SalesAdminPartnersPartnerTypePartnerIdSettlementsGet(
            type,
            id,
          );
        return { success: true, data: res };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement des règlements") };
      }
    },

    async updatePartnerSettings(
      type: PartnerType,
      id: string,
      data: PartnerSettingsUpdate,
    ): Promise<Result<PartnerSummaryResponse>> {
      this._ensureApiConfig();
      try {
        const res =
          await SalesService.updatePartnerSettingsApiV1SalesAdminPartnersPartnerTypePartnerIdSettingsPatch(
            type,
            id,
            data,
          );
        this._replacePartner(res);
        return { success: true, data: res };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur mise à jour du partenaire") };
      }
    },

    async createSettlement(data: SettlementCreate): Promise<Result<SettlementResponse>> {
      this._ensureApiConfig();
      try {
        const res = await SalesService.createSettlementApiV1SalesAdminSettlementsPost(data);
        return { success: true, data: res };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur enregistrement du règlement") };
      }
    },

    _replacePartner(p: PartnerSummaryResponse) {
      const i = this.partners.findIndex(
        (x) => x.partner_id === p.partner_id && x.partner_type === p.partner_type,
      );
      if (i !== -1) this.partners[i] = p;
    },

    // ── Admin : règles de commission ────────────────────
    async fetchRules(): Promise<Result<CommissionRuleResponse[]>> {
      this._ensureApiConfig();
      try {
        this.rules = await SalesService.listRulesApiV1SalesAdminCommissionRulesGet();
        return { success: true, data: this.rules };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur chargement des règles") };
      }
    },

    async createRule(data: CommissionRuleCreate): Promise<Result<CommissionRuleResponse>> {
      this._ensureApiConfig();
      try {
        const rule = await SalesService.createRuleApiV1SalesAdminCommissionRulesPost(data);
        this.rules.push(rule);
        return { success: true, data: rule };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur création de la règle") };
      }
    },

    async updateRule(
      id: string,
      data: CommissionRuleUpdate,
    ): Promise<Result<CommissionRuleResponse>> {
      this._ensureApiConfig();
      try {
        const rule =
          await SalesService.updateRuleApiV1SalesAdminCommissionRulesRuleIdPatch(id, data);
        const i = this.rules.findIndex((r) => r.id === id);
        if (i !== -1) this.rules[i] = rule;
        return { success: true, data: rule };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur mise à jour de la règle") };
      }
    },

    async deleteRule(id: string): Promise<Result<null>> {
      this._ensureApiConfig();
      try {
        await SalesService.deleteRuleApiV1SalesAdminCommissionRulesRuleIdDelete(id);
        this.rules = this.rules.filter((r) => r.id !== id);
        return { success: true, data: null };
      } catch (error: any) {
        return { success: false, error: erreur(error, "Erreur suppression de la règle") };
      }
    },
  },
});