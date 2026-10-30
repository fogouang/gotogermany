/**
 * composables/usePayments.ts
 */
import { usePaymentsStore } from "~/stores/payments";
import type { PaymentStatusResponse } from "#shared/api";
import { PaymentsService } from "#shared/api";

export const usePayments = () => {
  const paymentsStore = usePaymentsStore();
  const router = useRouter();
  const toast = useToast();

  // ── User : initier un paiement + polling ────────────────────
  const pay = async (data: {
    // Niveau d'examen OU niveau Start Deutsch
    level_id?: string | null;
    sd_level?: "A1" | "A2" | null;
    plan_id: string;
    operator: string;
    phone_number: string;
  }) => {
    const res = await paymentsStore.initiatePayment(data);
    if (!res.success) return res;

    paymentsStore.startPolling(
      res.data!.transaction_reference,
      (status: PaymentStatusResponse) => {
        if (
          status.payment_status === "COMPLETED" &&
          status.exam_access_granted
        ) {
          router.push({
            path: "/dashboard/paiement/succes",
            query: { ref: res.data!.transaction_reference },
          });
        }
      },
    );
    return res;
  };

  // ── Admin : accorder un accès exam manuellement ─────────────
  const adminGrantExamAccess = async (data: {
    user_id: string;
    // Niveau d'examen OU niveau Start Deutsch
    level_id?: string | null;
    sd_level?: "A1" | "A2" | null;
    // Formule OU pass journalier (days)
    plan_id?: string | null;
    days?: number | null;
    note?: string | null;
  }) => {
    try {
      const res =
        await PaymentsService.createManualPaymentApiV1PaymentsAdminManualPost({
          user_id: data.user_id,
          level_id: data.level_id ?? null,
          sd_level: data.sd_level ?? null,
          plan_id: data.plan_id ?? null,
          days: data.days ?? null,
          note: data.note ?? null,
        });
      return { success: true, data: res };
    } catch (err: any) {
      return {
        success: false,
        message:
          err?.body?.detail ??
          err?.body?.message ??
          "Erreur lors de l'activation manuelle",
      };
    }
  };

  // ── Helpers ─────────────────────────────────────────────────
  const formatStatus = (status: string): string => {
    const map: Record<string, string> = {
      PENDING: "En attente",
      COMPLETED: "Payé",
      FAILED: "Échoué",
    };
    return map[status] || status;
  };

  const formatAmount = (amount: number): string =>
    `${amount.toLocaleString("fr-FR")} FCFA`;

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
    // Actions user
    pay,
    checkStatus: paymentsStore.checkStatus,
    stopPolling: paymentsStore.stopPolling,
    fetchMyPayments: paymentsStore.fetchMyPayments,
    resetPayment: paymentsStore.resetPayment,
    // Actions admin
    adminGrantExamAccess,
    // Helpers
    formatStatus,
    formatAmount,
    operators,
  };
};
