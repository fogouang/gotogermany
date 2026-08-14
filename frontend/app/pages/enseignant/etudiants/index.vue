<!-- pages/enseignant/etudiants/index.vue -->
<template>
  <div>
    <p class="text-sm text-gray-500 mb-6">{{ students.length }} étudiant(s)</p>

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
      Aucun étudiant assigné pour l'instant.
    </div>

    <div
      v-else
      class="bg-white rounded-xl border border-gray-200 overflow-hidden"
    >
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Nom
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Cohorte(s)
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Sessions
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Score moyen
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Dernière session
              </th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in students"
              :key="s.student_id"
              class="border-b border-gray-100 last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
              @click="goToDetail(s.student_id)"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">
                {{ s.student_name }}
              </td>
              <td class="px-4 py-3 text-gray-500">
                <span class="flex flex-wrap gap-1">
                  <Tag
                    v-for="label in s.cohortLabels"
                    :key="label"
                    :value="label"
                    severity="info"
                  />
                </span>
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ s.total_sessions ?? "—" }}
              </td>
              <td
                class="px-4 py-3 whitespace-nowrap"
                :class="scoreClass(s.average_score)"
              >
                {{
                  s.average_score !== null && s.average_score !== undefined
                    ? s.average_score.toFixed(0) + "/100"
                    : "—"
                }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{
                  s.last_session_at ? formatDate(s.last_session_at) : "Aucune session"
                }}
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
  layout: "enseignant",
  middleware: "teacher",
});

import type { StudentProgressResponse } from "#shared/api";

const router = useRouter();
const teacherPortalStore = useTeacherPortalStore();

const loading = ref(true);
const errorMessage = ref<string | null>(null);
const progressByStudent = ref<Map<string, StudentProgressResponse>>(new Map());

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function scoreClass(score: number | null | undefined) {
  if (score === null || score === undefined) return "text-gray-400";
  if (score >= 60) return "text-emerald-600 font-medium";
  return "text-amber-600 font-medium";
}

// Dédoublonne les étudiants actifs à travers toutes les sessions de
// l'enseignant, en gardant la liste des cohortes, et fusionne les
// stats agrégées (score moyen, dernière session) récupérées séparément.
const students = computed(() => {
  const map = new Map<
    string,
    {
      student_id: string;
      student_name: string;
      cohortLabels: string[];
      average_score: number | null | undefined;
      total_sessions: number | undefined;
      last_session_at: string | null | undefined;
    }
  >();
  for (const session of teacherPortalStore.mySessions) {
    const cohortLabel = session.label
      ? `${session.level_name} — ${session.label}`
      : session.level_name;
    for (const s of session.students) {
      if (s.ended_at) continue;
      const progress = progressByStudent.value.get(s.student_id);
      const existing = map.get(s.student_id);
      if (existing) {
        if (!existing.cohortLabels.includes(cohortLabel)) {
          existing.cohortLabels.push(cohortLabel);
        }
      } else {
        map.set(s.student_id, {
          student_id: s.student_id,
          student_name: s.student_name,
          cohortLabels: [cohortLabel],
          average_score: progress?.average_score,
          total_sessions: progress?.total_sessions,
          last_session_at: progress?.last_session_at,
        });
      }
    }
  }
  return [...map.values()];
});

function goToDetail(studentId: string) {
  router.push(`/enseignant/etudiants/${studentId}`);
}

async function loadData() {
  loading.value = true;
  const [sessionsResult, progressResult] = await Promise.all([
    teacherPortalStore.fetchMySessions(),
    teacherPortalStore.fetchStudentsProgress(),
  ]);

  if (!sessionsResult.success) {
    errorMessage.value = sessionsResult.error || "Erreur de chargement.";
  }

  if (progressResult.success) {
    progressByStudent.value = new Map(
      (progressResult.progress ?? []).map((p) => [p.student_id, p]),
    );
  }

  loading.value = false;
}

onMounted(loadData);
</script>