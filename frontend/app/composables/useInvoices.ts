/**
 * composables/useInvoices.ts
 */
import { useInvoicesStore } from '~/stores/invoice'

export const useInvoices = () => {
  const invoicesStore = useInvoicesStore()

  // Télécharger la facture PDF
  const downloadInvoice = (invoiceUrl: string, filename?: string) => {
    const config = useRuntimeConfig()
    const base = (config.public.apiBaseUrl as string) || 'http://localhost:8001'
    const fullUrl = invoiceUrl.startsWith('http') ? invoiceUrl : `${base}${invoiceUrl}`
    const link = document.createElement('a')
    link.href = fullUrl
    link.download = filename || 'facture-gotogermany.pdf'
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Formater le montant
  const formatAmount = (amount: number) => `${amount.toLocaleString('fr-FR')} FCFA`

  // Formater la date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit', month: 'long', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  }

  return {
    currentInvoice: computed(() => invoicesStore.currentInvoice),
    loading: computed(() => invoicesStore.loading),
    error: computed(() => invoicesStore.error),

    fetchInvoice: invoicesStore.fetchInvoice,
    generateInvoice: invoicesStore.generateInvoice,

    downloadInvoice,
    formatAmount,
    formatDate,
  }
}