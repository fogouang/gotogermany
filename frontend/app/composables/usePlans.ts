/**
 * composables/usePlans.ts
 */
import { usePlansStore } from "~/stores/plans";

export const usePlans = () => {
  const plansStore = usePlansStore();

  // Charger les plans si pas encore chargés
  const loadPlans = async () => {
    if (plansStore.plans.length === 0) {
      await plansStore.fetchPlans();
    }
  };

  // Formater la durée en texte lisible
  const formatDuration = (days: number): string => {
    if (days === 7) return "7 jours";
    if (days === 15) return "15 jours";
    if (days === 30) return "1 mois";
    if (days === 60) return "2 mois";
    if (days === 90) return "3 mois";
    if (days === 180) return "6 mois";
    if (days === 365) return "1 an";
    return `${days} jours`;
  };

  // Formater le prix
  const formatPrice = (price: number): string => {
    return `${price.toLocaleString("fr-FR")} FCFA`;
  };

  // Trouver un plan par ID
  const getPlanById = (planId: string) => {
    return plansStore.plans.find((p) => p.id === planId) ?? null;
  };

  return {
    // State
    plans: computed(() => plansStore.sortedPlans),
    activePlans: computed(() => plansStore.activePlans),
    loading: computed(() => plansStore.loading),
    error: computed(() => plansStore.error),

    // Actions
    loadPlans,
    createPlan: plansStore.createPlan,
    updatePlan: plansStore.updatePlan,
    deletePlan: plansStore.deletePlan,
    fetchPlans: plansStore.fetchPlans,

    // Helpers
    formatDuration,
    formatPrice,
    getPlanById,
  };
};
