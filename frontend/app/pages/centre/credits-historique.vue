<!-- pages/centre/credits-historique.vue -->
<template>
  <div>
    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div
      v-else-if="transactions.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucune transaction pour l'instant.
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Date</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Étudiant</th>
              <th v-if="authStore.isDirector" class="text-left px-4 py-3 font-semibold text-gray-600">
                Effectué par
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Crédits</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Solde pool après</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Motif</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="txn in transactions"
              :key="txn.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ formatDate(txn.created_at) }}</td>
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">{{ txn.student_name }}</td>
              <td v-if="authStore.isDirector" class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ txn.performer_name }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap" :class="txn.amount >= 0 ? 'text-emerald-600' : 'text-red-600'">
                {{ txn.amount >= 0 ? '+' : '' }}{{ txn.amount }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ txn.pool_balance_after }}</td>
              <td class="px-4 py-3 text-gray-400 whitespace-nowrap">{{ txn.reason || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p v-if="!authStore.isDirector" class="text-xs text-gray-400 mt-4">
      Cet historique n'affiche que vos propres actions. Le directeur peut consulter l'audit complet du centre.
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import type { CenterCreditTransactionResponse } from "#shared/api";

const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();

const loading = ref(true);
const transactions = ref<CenterCreditTransactionResponse[]>([]);
const errorMessage = ref<string | null>(null);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function loadTransactions() {
  loading.value = true;
  const result = authStore.isDirector
    ? await centerStaffStore.fetchCreditTransactions()
    : await centerStaffStore.fetchMyCreditTransactions();

  if (result.success) {
    transactions.value = result.transactions ?? [];
  } else {
    errorMessage.value = result.error || "Erreur de chargement.";
  }
  loading.value = false;
}

onMounted(loadTransactions);
</script>