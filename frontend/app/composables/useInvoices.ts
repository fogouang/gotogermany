/**
 * composables/useInvoices.ts
 */
import { useInvoicesStore } from "~/stores/invoice";

export const useInvoices = () => {
  // Composables Nuxt : appelés ici, dans le setup du composant qui utilise useInvoices
  const { locale } = useI18n();
  const config = useRuntimeConfig();
  const invoicesStore = useInvoicesStore();

  const intlLocale = computed(
    () =>
      (({ fr: "fr-FR", de: "de-DE" }) as Record<string, string>)[locale.value] ??
      "en-GB",
  );

  // Télécharger la facture PDF
  const downloadInvoice = (invoiceUrl: string, filename?: string) => {
    const base =
      (config.public.apiBaseUrl as string) || "http://localhost:8001";
    const fullUrl = invoiceUrl.startsWith("http")
      ? invoiceUrl
      : `${base}${invoiceUrl}`;
    const link = document.createElement("a");
    link.href = fullUrl;
    link.download = filename || "facture-gotogermany.pdf";
    link.target = "_blank";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Formater le montant
  const formatAmount = (amount: number) =>
    `${amount.toLocaleString(intlLocale.value)} FCFA`;

  // Formater la date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(intlLocale.value, {
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return {
    currentInvoice: computed(() => invoicesStore.currentInvoice),
    loading: computed(() => invoicesStore.loading),
    error: computed(() => invoicesStore.error),

    fetchInvoice: invoicesStore.fetchInvoice,
    generateInvoice: invoicesStore.generateInvoice,

    downloadInvoice,
    formatAmount,
    formatDate,
  };
};