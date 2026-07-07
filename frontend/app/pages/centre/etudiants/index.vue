<!-- pages/centre/etudiants.vue -->
<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <p class="text-sm text-gray-500">{{ students.length }} étudiant(s)</p>
      <Button
        v-if="authStore.isSecretary"
        label="Nouvel étudiant"
        icon="pi pi-user-plus"
        size="small"
        @click="navigateTo('/centre/etudiants/nouveau')"
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
      v-else-if="students.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucun étudiant pour l'instant.
    </div>

    <div
      v-else
      class="bg-white rounded-xl border border-gray-200 overflow-hidden"
    >
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">Nom</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Email
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Examen visé
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Statut
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Première connexion
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Accès expire le
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="student in students"
              :key="student.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">{{ student.full_name }}</td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ student.email }}</td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ levelLabel(student.target_level_id) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag
                  :value="student.is_active ? 'Actif' : 'Désactivé'"
                  :severity="student.is_active ? 'success' : 'danger'"
                />
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{
                  student.first_login_at
                    ? formatDate(student.first_login_at)
                    : "Jamais connecté"
                }}
              </td>
              <td
                class="px-4 py-3 whitespace-nowrap"
                :class="expiryClass(student.access_expires_at)"
              >
                {{
                  student.access_expires_at
                    ? formatDate(student.access_expires_at)
                    : "—"
                }}
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
  middleware: "centre-staff", // accessible director OU secretary — cf. note ci-dessous
});

import type { StudentResponse } from "#shared/api";

const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const examsStore = useExamsStore();

const loading = ref(true);
const students = ref<StudentResponse[]>([]);
const errorMessage = ref<string | null>(null);

const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

function levelLabel(targetLevelId: string | null) {
  if (!targetLevelId) return "—";
  return allLevels.value.find((l) => l.value === targetLevelId)?.label ?? "—";
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function expiryClass(dateStr: string | null) {
  if (!dateStr) return "text-gray-400";
  const daysLeft =
    (new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24);
  if (daysLeft < 0) return "text-red-600 font-medium";
  if (daysLeft <= 7) return "text-amber-600 font-medium";
  return "text-gray-500";
}

async function loadStudents() {
  loading.value = true;

  if (examsStore.catalog.length === 0) {
    await examsStore.fetchCatalog();
  }

  const result = authStore.isDirector
    ? await centerStaffStore.fetchStudentsByCenter()
    : await centerStaffStore.fetchStudentsByBranch();

  if (result.success) {
    students.value = result.students ?? [];
  } else {
    errorMessage.value = result.error || "Erreur de chargement.";
  }
  loading.value = false;
}

onMounted(loadStudents);
</script>