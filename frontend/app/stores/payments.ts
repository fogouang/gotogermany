/**
 * stores/payments.store.ts
 */
import { defineStore } from 'pinia'
import { PaymentsService, OpenAPI } from '#shared/api'
import type { PaymentInitiateRequest, PaymentInitiateResponse, PaymentResponse, PaymentStatusResponse } from '#shared/api'

interface PaymentsState {
  // Paiement en cours
  currentPayment: PaymentInitiateResponse | null
  // Statut du polling
  currentStatus: PaymentStatusResponse | null
  // Historique
  myPayments: PaymentResponse[]
  loading: boolean
  error: string | null
  // Polling
  pollingInterval: ReturnType<typeof setInterval> | null
}

export const usePaymentsStore = defineStore('payments', {
  state: (): PaymentsState => ({
    currentPayment: null,
    currentStatus: null,
    myPayments: [],
    loading: false,
    error: null,
    pollingInterval: null,
  }),

  getters: {
    isPending: (state) => state.currentStatus?.payment_status === 'PENDING',
    isCompleted: (state) => state.currentStatus?.payment_status === 'COMPLETED',
    isFailed: (state) => state.currentStatus?.payment_status === 'FAILED',
    accessGranted: (state) => state.currentStatus?.exam_access_granted ?? false,
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig()
      OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001'
      const tokenCookie = useCookie('access_token')
      OpenAPI.TOKEN = tokenCookie.value ?? undefined
    },

    async initiatePayment(data: PaymentInitiateRequest) {
      this._ensureApiConfig()
      this.loading = true
      this.error = null
      this.currentPayment = null
      this.currentStatus = null
      try {
        const response = await PaymentsService.initiatePaymentApiV1PaymentsPost(data)
        this.currentPayment = response
        return { success: true, data: response }
      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur lors du paiement'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async checkStatus(transactionReference: string) {
      this._ensureApiConfig()
      try {
        const status = await PaymentsService.getPaymentStatusApiV1PaymentsStatusTransactionReferenceGet(
          transactionReference
        )
        this.currentStatus = status
        return { success: true, data: status }
      } catch (error: any) {
        return { success: false, error: error.body?.detail }
      }
    },

    startPolling(transactionReference: string, onComplete: (status: PaymentStatusResponse) => void) {
      this.stopPolling()
      this.pollingInterval = setInterval(async () => {
        const res = await this.checkStatus(transactionReference)
        if (res.success && res.data) {
          if (res.data.payment_status === 'COMPLETED' || res.data.payment_status === 'FAILED') {
            this.stopPolling()
            onComplete(res.data)
          }
        }
      }, 5000)
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },

    async fetchMyPayments() {
      this._ensureApiConfig()
      this.loading = true
      try {
        const payments = await PaymentsService.getMyPaymentsApiV1PaymentsMeGet()
        this.myPayments = payments
        return { success: true, data: payments }
      } catch (error: any) {
        this.error = error.body?.detail || 'Erreur chargement historique'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    resetPayment() {
      this.stopPolling()
      this.currentPayment = null
      this.currentStatus = null
      this.error = null
    },
  },
})