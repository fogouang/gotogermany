<!-- pages/centre/inscriptions/index.vue -->
<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div />
      <Button
        label="Nouveau cursus"
        icon="pi pi-plus"
        @click="navigateTo('/centre/inscriptions/nouveau')"
      />
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div
      v-else-if="cursusList.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucun cursus pour l'instant.
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Élève</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Parcours</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Statut</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Créé le</th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="cursus in enrichedCursusList"
              :key="cursus.id"
              class="border-b border-gray-100 last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="navigateTo(`/centre/inscriptions/${cursus.id}`)"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">
                {{ cursus.studentName }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ cursus.start_level }} → {{ cursus.target_level }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag :value="statusLabel(cursus.status)" :severity="statusSeverity(cursus.status)" />
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ formatDate(cursus.created_at) }}
              </td>
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

const centerStaffStore = useCenterStaffStore();
const enrollmentsStore = useEnrollmentsStore();
const authStore = useAuthStore();

const loading = ref(true);
const errorMessage = ref<string | null>(null);

const cursusList = computed(() => enrollmentsStore.cursusList);

const enrichedCursusList = computed(() =>
  cursusList.value.map((cursus) => {
    const student = centerStaffStore.students.find((s) => s.id === cursus.student_id);
    return {
      ...cursus,
      studentName: student?.full_name || "Élève inconnu",
    };
  }),
);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    in_progress: "En cours",
    completed: "Terminé",
    abandoned: "Abandonné",
  };
  return labels[status] || status;
}

function statusSeverity(status: string) {
  const severities: Record<string, string> = {
    in_progress: "info",
    completed: "success",
    abandoned: "danger",
  };
  return severities[status] || "secondary";
}

onMounted(async () => {
  loading.value = true;

  if (centerStaffStore.students.length === 0) {
    if (authStore.isDirector) {
      await centerStaffStore.fetchStudentsByCenter();
    } else {
      await centerStaffStore.fetchStudentsByBranch();
    }
  }

  const result = await enrollmentsStore.fetchCursusList();
  if (!result.success) {
    errorMessage.value = result.error || "Erreur de chargement.";
  }

  loading.value = false;
});
</script>