/**
 * composables/useAiCredits.ts
 *
 * Composable pour les crédits IA (Schreiben).
 * Couvre : solde, pricing, achat MyCoolPay, historique.
 * L'accord manuel admin passe par adminGrantCredits().
 */
import { AiCreditsService } from "#shared/api";
import type {
  CreditBalanceResponse,
  CreditPricingResponse,
  CreditPurchaseHistoryItem,
  CreditPurchaseResponse,
} from "#shared/api";

export const useAiCredits = () => {
  // ── State local ─────────────────────────────────────────────
  const balance       = ref<CreditBalanceResponse | null>(null)
  const pricing       = ref<CreditPricingResponse | null>(null)
  const history       = ref<CreditPurchaseHistoryItem[]>([])
  const totalSpent    = ref(0)
  const totalPurchased = ref(0)

  const loading        = ref(false)
  const loadingPurchase = ref(false)
  const lastPurchase   = ref<CreditPurchaseResponse | null>(null)
  const error          = ref<string | null>(null)

  // ── Pricing (public, pas besoin d'auth) ─────────────────────
  const fetchPricing = async () => {
    try {
      const res = await AiCreditsService.getPricingApiV1AiCreditsPricingGet()
      pricing.value = res.data ?? null
    } catch {
      // silencieux — pricing non critique
    }
  }

  // ── Solde utilisateur ────────────────────────────────────────
  const fetchBalance = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await AiCreditsService.getBalanceApiV1AiCreditsBalanceGet()
      balance.value = res.data ?? null
    } catch (err: any) {
      error.value = err?.body?.message ?? "Impossible de récupérer le solde"
    } finally {
      loading.value = false
    }
  }

  // ── Historique achats ────────────────────────────────────────
  const fetchHistory = async () => {
    loading.value = true
    try {
      const res = await AiCreditsService.getHistoryApiV1AiCreditsHistoryGet()
      history.value       = res.data?.purchases ?? []
      totalSpent.value    = res.data?.total_spent ?? 0
      totalPurchased.value = res.data?.total_credits_purchased ?? 0
    } catch {
      history.value = []
    } finally {
      loading.value = false
    }
  }

  // ── Achat via MyCoolPay ──────────────────────────────────────
  const purchaseCredits = async (data: {
    credits: number
    payment_method: string
    phone_number?: string | null
  }) => {
    loadingPurchase.value = true
    error.value = null
    try {
      const res = await AiCreditsService.purchaseCreditsApiV1AiCreditsPurchasePost({
        credits: data.credits,
        payment_method: data.payment_method,
        phone_number: data.phone_number ?? null,
      })
      lastPurchase.value = res.data ?? null
      return { success: true, data: res.data }
    } catch (err: any) {
      const msg = err?.body?.message ?? "Erreur lors de l'achat"
      error.value = msg
      return { success: false, message: msg }
    } finally {
      loadingPurchase.value = false
    }
  }

  // ── Admin : accord manuel ────────────────────────────────────
  const adminGrantCredits = async (data: {
    user_id: string
    credits: number
  }) => {
    try {
      const res = await AiCreditsService.adminGrantApiV1AiCreditsAdminGrantPost({
        user_id: data.user_id,
        credits: data.credits,
      })
      return { success: true, data: res.data }
    } catch (err: any) {
      return {
        success: false,
        message: err?.body?.message ?? "Erreur lors de l'accord des crédits",
      }
    }
  }

  // ── Helpers ──────────────────────────────────────────────────
  const priceFor = (credits: number): string => {
    const p = pricing.value?.price_per_credit ?? 50
    return `${(credits * p).toLocaleString("fr-FR")} FCFA`
  }

  const formatDate = (dateStr: string): string =>
    new Date(dateStr).toLocaleDateString("fr-FR")

  const statusLabel = (status: string): string => ({
    COMPLETED: "Payé",
    PENDING:   "En attente",
    FAILED:    "Échoué",
    MANUAL:    "Manuel",
  }[status] ?? status)

  const statusSeverity = (status: string) => ({
    COMPLETED: "success",
    PENDING:   "warn",
    FAILED:    "danger",
    MANUAL:    "info",
  }[status] ?? "secondary")

  return {
    // State
    balance,
    pricing,
    history,
    totalSpent,
    totalPurchased,
    loading,
    loadingPurchase,
    lastPurchase,
    error,

    // Computed utiles
    aiCredits:        computed(() => balance.value?.ai_credits ?? 0),
    pricePerCredit:   computed(() => pricing.value?.price_per_credit ?? 50),
    minPurchase:      computed(() => pricing.value?.min_purchase ?? 5),
    maxPurchase:      computed(() => pricing.value?.max_purchase ?? 500),
    pricingExamples:  computed(() => pricing.value?.examples ?? []),

    // Actions
    fetchPricing,
    fetchBalance,
    fetchHistory,
    purchaseCredits,
    adminGrantCredits,

    // Helpers
    priceFor,
    formatDate,
    statusLabel,
    statusSeverity,
  }
}