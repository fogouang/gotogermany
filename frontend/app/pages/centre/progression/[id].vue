<!-- pages/centre/progression/[id].vue -->
<template>
  <div>
    <Button
      icon="pi pi-arrow-left"
      label="Retour à la progression"
      text
      size="small"
      class="mb-4"
      @click="router.push('/centre/progression')"
    />

    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div v-else-if="detail" class="space-y-6">
      <!-- En-tête étudiant -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 class="text-lg font-bold text-gray-900">{{ detail.student_name }}</h2>
            <p class="text-sm text-gray-400 mt-0.5">{{ detail.branch_name }}</p>
          </div>
          <div class="flex gap-6 text-sm">
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">{{ detail.total_sessions }}</p>
              <p class="text-xs text-gray-400">sessions</p>
            </div>
            <div class="text-center">
              <p
                class="text-2xl font-bold"
                :class="scoreClass(detail.overall_average_score)"
              >
                {{ detail.overall_average_score !== null ? detail.overall_average_score.toFixed(0) : '—' }}
              </p>
              <p class="text-xs text-gray-400">score moyen</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">{{ detail.ai_credits_remaining }}</p>
              <p class="text-xs text-gray-400">crédits IA</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Graphique évolution des scores -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="text-sm font-semibold text-gray-700 mb-4">Évolution des scores</h3>
        <ScoreEvolutionChart :data="detail.score_history" />
      </div>

      <!-- Ventilation par examen -->
      <div
        v-for="exam in detail.exams"
        :key="exam.exam_id"
        class="bg-white rounded-xl border border-gray-200 p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-semibold text-gray-900">{{ exam.exam_name }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">
              {{ exam.total_sessions }} session(s)
              <span v-if="exam.last_session_at">
                · dernière le {{ formatDate(exam.last_session_at) }}
              </span>
            </p>
          </div>
          <p class="text-xl font-bold" :class="scoreClass(exam.average_score)">
            {{ exam.average_score !== null ? exam.average_score.toFixed(0) + '/100' : '—' }}
          </p>
        </div>

        <ModuleBarChart :modules="exam.modules" />
      </div>

      <div v-if="detail.exams.length === 0" class="text-center py-8 text-gray-400 text-sm">
        Aucune session complétée pour l'instant.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import type { StudentDetailedProgressResponse } from "#shared/api";
import ScoreEvolutionChart from "~/components/centre/ScoreEvolutionChart.vue";
import ModuleBarChart from "~/components/centre/ModuleBarChart.vue";

const route = useRoute();
const router = useRouter();
const centerStaffStore = useCenterStaffStore();

const loading = ref(true);
const detail = ref<StudentDetailedProgressResponse | null>(null);
const errorMessage = ref<string | null>(null);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function scoreClass(score: number | null) {
  if (score === null) return "text-gray-400";
  if (score >= 60) return "text-emerald-600";
  return "text-amber-600";
}

async function loadDetail() {
  loading.value = true;
  const studentId = route.params.id as string;
  const result = await centerStaffStore.fetchStudentProgressDetail(studentId);
  if (result.success && result.detail) {
    detail.value = result.detail;
  } else {
    errorMessage.value = result.error || "Erreur de chargement.";
  }
  loading.value = false;
}

onMounted(loadDetail);
</script>