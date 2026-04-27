/**
 * composables/usePayments.ts
 */
import { usePaymentsStore } from "~/stores/payments";
import type { PaymentStatusResponse } from "#shared/api";

export const usePayments = () => {
  const paymentsStore = usePaymentsStore();
  const router = useRouter();

  // Initier un paiement et démarrer le polling
  const pay = async (data: {
    exam_id: string;
    plan_id: string;
    operator: string;
    phone_number: string;
    promo_code?: string | null;
  }) => {
    const res = await paymentsStore.initiatePayment(data);
    if (!res.success) return res;

    // Démarrer le polling automatique
    paymentsStore.startPolling(
      res.data!.transaction_reference,
      (status: PaymentStatusResponse) => {
        if (
          status.payment_status === "COMPLETED" &&
          status.exam_access_granted
        ) {
          // Rediriger vers la page de succès
          router.push({
            path: "/dashboard/paiement/succes",
            query: { ref: res.data!.transaction_reference },
          });
        }
      },
    );

    return res;
  };

  // Formater le statut en texte lisible
  const formatStatus = (status: string): string => {
    const map: Record<string, string> = {
      PENDING: "En attente",
      COMPLETED: "Payé",
      FAILED: "Échoué",
    };
    return map[status] || status;
  };

  // Formater le montant
  const formatAmount = (amount: number): string => {
    return `${amount.toLocaleString("fr-FR")} FCFA`;
  };

  // Opérateurs disponibles
  const operators = [
    { label: "MTN Mobile Money", value: "MTN" },
    { label: "Orange Money", value: "ORANGE" },
  ];

  return {
    // State
    currentPayment: computed(() => paymentsStore.currentPayment),
    currentStatus: computed(() => paymentsStore.currentStatus),
    myPayments: computed(() => paymentsStore.myPayments),
    loading: computed(() => paymentsStore.loading),
    error: computed(() => paymentsStore.error),

    // Getters
    isPending: computed(() => paymentsStore.isPending),
    isCompleted: computed(() => paymentsStore.isCompleted),
    isFailed: computed(() => paymentsStore.isFailed),
    accessGranted: computed(() => paymentsStore.accessGranted),

    // Actions
    pay,
    checkStatus: paymentsStore.checkStatus,
    stopPolling: paymentsStore.stopPolling,
    fetchMyPayments: paymentsStore.fetchMyPayments,
    resetPayment: paymentsStore.resetPayment,

    // Helpers
    formatStatus,
    formatAmount,
    operators,
  };
};
