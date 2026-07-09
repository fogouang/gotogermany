<!-- pages/centre/progression.vue -->
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
      v-else-if="progress.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucune donnée de progression pour l'instant.
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Étudiant</th>
              <th v-if="authStore.isDirector" class="text-left px-4 py-3 font-semibold text-gray-600">
                Succursale
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Sessions</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Score moyen</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Dernière session</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Crédits IA restants</th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in progress"
              :key="row.student_id"
              class="border-b border-gray-100 last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="goToDetail(row.student_id)"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">{{ row.student_name }}</td>
              <td v-if="authStore.isDirector" class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ row.branch_name }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">{{ row.total_sessions }}</td>
              <td class="px-4 py-3 whitespace-nowrap" :class="scoreClass(row.average_score)">
                {{ row.average_score !== null ? row.average_score.toFixed(0) + '/100' : '—' }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ row.last_session_at ? formatDate(row.last_session_at) : 'Aucune session' }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">{{ row.ai_credits_remaining }}</td>
              <td class="px-4 py-3 text-right whitespace-nowrap">
                <i class="pi pi-chevron-right text-gray-300"></i>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import type { StudentProgressResponse } from "#shared/api";

const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const router = useRouter();

const loading = ref(true);
const progress = ref<StudentProgressResponse[]>([]);
const errorMessage = ref<string | null>(null);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function scoreClass(score: number | null) {
  if (score === null) return "text-gray-400";
  if (score >= 60) return "text-emerald-600 font-medium";
  return "text-amber-600 font-medium";
}

function goToDetail(studentId: string) {
  router.push(`/centre/progression/${studentId}`);
}

async function loadProgress() {
  loading.value = true;
  const result = await centerStaffStore.fetchStudentProgress();
  if (result.success) {
    progress.value = result.progress ?? [];
  } else {
    errorMessage.value = result.error || "Erreur de chargement.";
  }
  loading.value = false;
}

onMounted(loadProgress);
</script>