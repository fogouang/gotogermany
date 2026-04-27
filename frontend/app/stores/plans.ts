/**
 * stores/plans.store.ts
 */
import { defineStore } from 'pinia'
import { PlansService, OpenAPI } from '#shared/api'
import type { PlanResponse } from '#shared/api'

interface PlansState {
  plans: PlanResponse[]
  loading: boolean
  error: string | null
}

export const usePlansStore = defineStore('plans', {
  state: (): PlansState => ({
    plans: [],
    loading: false,
    error: null,
  }),

  getters: {
    activePlans: (state) => state.plans.filter(p => p.is_active),
    sortedPlans: (state) => [...state.plans].sort((a, b) => a.display_order - b.display_order),
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig()
      OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001'
      const tokenCookie = useCookie('access_token')
      OpenAPI.TOKEN = tokenCookie.value ?? undefined
    },

    async fetchPlans() {
      this._ensureApiConfig()
      this.loading = true
      this.error = null
      try {
        const plans = await PlansService.getPlansApiV1PlansGet()
        this.plans = plans
        return { success: true, data: plans }
      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur lors du chargement des plans'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async createPlan(data: { name: string; duration_days: number; price: number; description?: string | null; display_order?: number; is_active?: boolean }) {
      this._ensureApiConfig()
      this.loading = true
      this.error = null
      try {
        const plan = await PlansService.createPlanApiV1PlansPost(data)
        this.plans.push(plan)
        this.plans.sort((a, b) => a.display_order - b.display_order)
        return { success: true, data: plan }
      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur lors de la création'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async updatePlan(planId: string, data: { name?: string | null; duration_days?: number | null; price?: number | null; description?: string | null; display_order?: number | null; is_active?: boolean | null }) {
      this._ensureApiConfig()
      this.loading = true
      this.error = null
      try {
        const updated = await PlansService.updatePlanApiV1PlansPlanIdPatch(planId, data)
        const idx = this.plans.findIndex(p => p.id === planId)
        if (idx !== -1) this.plans[idx] = updated
        return { success: true, data: updated }
      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur lors de la modification'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async deletePlan(planId: string) {
      this._ensureApiConfig()
      try {
        await PlansService.deletePlanApiV1PlansPlanIdDelete(planId)
        this.plans = this.plans.filter(p => p.id !== planId)
        return { success: true }
      } catch (error: any) {
        return { success: false, error: error.body?.detail || 'Erreur lors de la suppression' }
      }
    },
  },
})