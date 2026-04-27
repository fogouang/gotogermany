/**
 * stores/invoices.store.ts
 */
import { defineStore } from 'pinia'
import { InvoicesService, OpenAPI } from '#shared/api'
import type { InvoiceResponse } from '#shared/api'

interface InvoicesState {
  currentInvoice: InvoiceResponse | null
  loading: boolean
  error: string | null
}

export const useInvoicesStore = defineStore('invoices', {
  state: (): InvoicesState => ({
    currentInvoice: null,
    loading: false,
    error: null,
  }),

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig()
      OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001'
      const tokenCookie = useCookie('access_token')
      OpenAPI.TOKEN = tokenCookie.value ?? undefined
    },

    async fetchInvoice(paymentId: string) {
      this._ensureApiConfig()
      this.loading = true
      this.error = null
      try {
        const invoice = await InvoicesService.getInvoiceApiV1InvoicesPaymentPaymentIdGet(paymentId)
        this.currentInvoice = invoice
        return { success: true, data: invoice }
      } catch (error: any) {
        this.error = error.body?.detail || 'Facture introuvable'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async generateInvoice(paymentId: string) {
      this._ensureApiConfig()
      this.loading = true
      this.error = null
      try {
        await InvoicesService.generateInvoiceApiV1InvoicesGeneratePaymentIdPost(paymentId)
        // Recharger après génération
        return await this.fetchInvoice(paymentId)
      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur génération facture'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
  },
})