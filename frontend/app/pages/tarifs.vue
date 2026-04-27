<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-gradient-primary text-white py-16 px-4 text-center">
      <h1 class="text-4xl font-bold mb-3">Tarifs GoToGermany</h1>
      <p class="text-lg text-white/80 max-w-xl mx-auto">
        Choisissez la durée qui vous convient et accédez à tous les examens
        disponibles.
      </p>
    </div>
    <!-- Note paiement -->
    <div class="mt-12 text-center space-y-4">
      <p class="text-md text-gray-900">Moyens de paiement acceptés</p>
      <div class="flex items-center justify-center gap-4 flex-wrap">
        <img
          src="/images/orange.jpg"
          alt="Orange Money"
          class="h-10 rounded-lg object-contain"
        />
        <img
          src="/images/momo.jpg"
          alt="MTN MoMo"
          class="h-10 rounded-lg object-contain"
        />
        <img
          src="/images/visa.png"
          alt="Visa"
          class="h-10 rounded-lg object-contain"
        />
        <img
          src="/images/master.png"
          alt="Mastercard"
          class="h-10 rounded-lg object-contain"
        />
        <img
          src="/images/paypal.png"
          alt="PayPal"
          class="h-10 rounded-lg object-contain"
        />
      </div>
      <div
        class="flex items-center justify-center gap-6 flex-wrap text-sm text-gray-400"
      >
        <span class="flex items-center gap-1">
          <i class="pi pi-refresh text-green-500"></i>
          Accès immédiat après paiement
        </span>
      </div>
    </div>

    <!-- Plans -->
    <div class="max-w-5xl mx-auto px-4 py-16 mb-16">
      <div v-if="loading" class="flex justify-center py-12">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <div
        v-else-if="activePlans.length === 0"
        class="text-center text-gray-400 py-12"
      >
        <i class="pi pi-tag text-4xl mb-3 block"></i>
        Aucun plan disponible pour le moment.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(plan, index) in activePlans"
          :key="plan.id"
          :class="[
            'bg-white rounded-2xl border-2 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col',
            index === recommendedIndex
              ? 'border-green-600 scale-105 shadow-lg'
              : 'border-gray-100 hover:border-green-300',
          ]"
        >
          <!-- Badge recommandé -->
          <div
            v-if="index === recommendedIndex"
            class="bg-gradient-primary text-white text-xs font-bold text-center py-2 tracking-wide uppercase"
          >
            ⭐ Le plus populaire
          </div>

          <div class="p-6 flex flex-col flex-1">
            <!-- Durée -->
            <div class="mb-4">
              <span
                class="text-sm font-semibold text-green-700 bg-green-50 px-3 py-1 rounded-full"
              >
                {{ formatDuration(plan.duration_days) }}
              </span>
            </div>

            <!-- Nom -->
            <h3 class="text-xl font-bold text-gray-900 mb-2">
              {{ plan.name }}
            </h3>

            <!-- Description -->
            <p class="text-sm text-gray-500 mb-6 flex-1">
              {{
                plan.description ||
                `Accès complet à tous les examens pendant ${formatDuration(plan.duration_days)}`
              }}
            </p>

            <!-- Prix -->
            <div class="mb-6">
              <span class="text-4xl font-extrabold text-gray-900">
                {{ plan.price.toLocaleString("fr-FR") }}
              </span>
              <span class="text-gray-400 text-sm ml-1">FCFA</span>
              <p class="text-xs text-gray-400 mt-1">
                soit
                {{
                  Math.round(plan.price / plan.duration_days).toLocaleString(
                    "fr-FR",
                  )
                }}
                FCFA/jour
              </p>
            </div>

            <!-- Features incluses -->
            <ul class="space-y-2 mb-6 text-sm text-gray-600">
              <li class="flex items-center gap-2">
                <i class="pi pi-check-circle text-green-500"></i>
                Accès illimité à tous les examens
              </li>
              <li class="flex items-center gap-2">
                <i class="pi pi-check-circle text-green-500"></i>
                Tous les sujets disponibles
              </li>
              <li class="flex items-center gap-2">
                <i class="pi pi-check-circle text-green-500"></i>
                Corrections automatiques
              </li>
              <li class="flex items-center gap-2">
                <i class="pi pi-check-circle text-green-500"></i>
                Suivi de progression
              </li>
            </ul>

            <!-- CTA -->
            <Button
              label="Choisir ce plan"
              icon="pi pi-arrow-right"
              iconPos="right"
              :class="[
                'w-full',
                index === recommendedIndex
                  ? 'bg-gradient-primary! border-transparent!'
                  : '',
              ]"
              :severity="index === recommendedIndex ? 'primary' : 'secondary'"
              @click="selectPlan(plan)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse } from "#shared/api";

definePageMeta({ layout: "default" });

const { activePlans, loading, loadPlans, formatDuration } = usePlans();

// Plan recommandé — le milieu de la liste
const recommendedIndex = computed(() => {
  const len = activePlans.value.length;
  if (len === 0) return -1;
  return Math.floor(len / 2);
});

const selectPlan = (plan: PlanResponse) => {
  const authStore = useAuthStore();
  if (!authStore.isAuthenticated) {
    // Rediriger vers login avec redirect après
    navigateTo(`/?redirect=/dashboard/paiement?plan_id=${plan.id}`);
    return;
  }
  navigateTo(`/dashboard/paiement?plan_id=${plan.id}`);
};

onMounted(loadPlans);
</script>
