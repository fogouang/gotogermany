<!-- pages/enseignant/sessions.vue -->
<template>
  <div>
    <p class="text-sm text-gray-500 mb-6">
      {{ mySessions.length }} session(s) assignée(s)
    </p>

    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div
      v-else-if="mySessions.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucune session ne vous est encore assignée.
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="session in mySessions"
        :key="session.id"
        class="bg-white rounded-xl border border-gray-200 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <div>
            <h3 class="font-semibold text-gray-900">
              {{ session.level_name }}
              <span v-if="session.label" class="text-gray-400 text-sm font-normal">
                ({{ session.label }})
              </span>
            </h3>
            <p class="text-xs text-gray-400 mt-0.5">
              Début le {{ formatDate(session.start_date) }}
            </p>
          </div>
          <Tag :value="`${activeStudents(session).length} étudiant(s) actif(s)`" severity="info" />
        </div>

        <div class="divide-y divide-gray-50 border-t border-gray-100">
          <div
            v-for="s in activeStudents(session)"
            :key="s.student_id"
            class="flex items-center justify-between py-2 text-sm"
          >
            <span class="text-gray-800">{{ s.student_name }}</span>
            <div class="flex gap-2">
              <Button
                label="Détail"
                text
                size="small"
                @click="goToDetail(s.student_id)"
              />
              <Button
                label="Lancer un live"
                icon="pi pi-microphone"
                size="small"
                @click="goToLaunchLive(s.student_id)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "enseignant",
  middleware: "teacher",
});

const router = useRouter();
const teacherPortalStore = useTeacherPortalStore();

const loading = ref(true);
const mySessions = ref(teacherPortalStore.mySessions);
const errorMessage = ref<string | null>(null);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function activeStudents(session: (typeof mySessions)["value"][number]) {
  return session.students.filter((s) => !s.ended_at);
}

function goToDetail(studentId: string) {
  router.push(`/enseignant/etudiants/${studentId}`);
}

function goToLaunchLive(studentId: string) {
  // Redirige vers l'écran de lancement live (à confirmer une fois la
  // page staff équivalente partagée — probablement un paramètre
  // studentId en query pour pré-sélectionner l'étudiant).
  router.push(`/enseignant/live/nouveau?student_id=${studentId}`);
}

async function loadData() {
  loading.value = true;
  const result = await teacherPortalStore.fetchMySessions();
  mySessions.value = teacherPortalStore.mySessions;
  if (!result.success) {
    errorMessage.value = result.error || "Erreur de chargement.";
  }
  loading.value = false;
}

onMounted(loadData);
</script>