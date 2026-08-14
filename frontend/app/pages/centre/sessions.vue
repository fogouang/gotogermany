<!-- pages/centre/sessions.vue -->
<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <p class="text-sm text-gray-500">{{ sessions.length }} session(s)</p>
      <Button
        label="Nouvelle session"
        icon="pi pi-plus"
        size="small"
        @click="openCreateDialog"
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
      v-else-if="sessions.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucune session pour l'instant.
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
                Niveau
              </th>
              <th
                v-if="authStore.isDirector"
                class="text-left px-4 py-3 font-semibold text-gray-600"
              >
                Succursale
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Début
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Fin prévue
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Enseignants
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Étudiants
              </th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="session in sessions"
              :key="session.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">
                {{ session.level_name }}
                <span v-if="session.label" class="text-gray-400 text-xs">
                  ({{ session.label }})
                </span>
              </td>
              <td
                v-if="authStore.isDirector"
                class="px-4 py-3 text-gray-500 whitespace-nowrap"
              >
                {{ session.branch_name }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ formatDate(session.start_date) }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ session.end_date ? formatDate(session.end_date) : "—" }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ session.teachers.length }}
              </td>
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ activeStudentCount(session) }} actif(s) /
                {{ session.students.length }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-right">
                <Button
                  label="Gérer"
                  text
                  size="small"
                  @click="openManageDialog(session)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Dialog création -->
    <Dialog
      v-model:visible="showCreateDialog"
      header="Nouvelle session"
      modal
      :style="{ width: '90vw', maxWidth: '28rem' }"
    >
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Niveau</label
          >
          <Select
            v-model="createForm.level_id"
            :options="allLevels"
            optionLabel="label"
            optionValue="value"
            placeholder="Choisir un niveau"
            class="w-full"
          />
        </div>
        <div v-if="authStore.isDirector">
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Succursale</label
          >
          <Select
            v-model="createForm.branch_id"
            :options="branches"
            optionLabel="name"
            optionValue="id"
            placeholder="Choisir une succursale"
            class="w-full"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Libellé (optionnel)</label
          >
          <InputText
            v-model="createForm.label"
            class="w-full"
            placeholder="ex: Rentrée Août"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Date de début</label
          >
          <DatePicker
            v-model="createForm.start_date"
            class="w-full"
            dateFormat="dd/mm/yy"
            showIcon
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Date de fin prévue (optionnel)</label
          >
          <DatePicker
            v-model="createForm.end_date"
            class="w-full"
            dateFormat="dd/mm/yy"
            showIcon
          />
        </div>
        <p v-if="createError" class="text-sm text-red-600">
          {{ createError }}
        </p>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="showCreateDialog = false" />
        <Button
          label="Créer"
          :loading="creating"
          @click="handleCreateSession"
        />
      </template>
    </Dialog>

    <!-- Dialog gestion (enseignants + étudiants) -->
    <Dialog
      v-model:visible="showManageDialog"
      :header="manageHeader"
      modal
      :style="{ width: '90vw', maxWidth: '40rem' }"
    >
      <div v-if="selectedSession" class="space-y-6">
        <!-- Enseignants -->
        <div>
          <h4 class="text-sm font-semibold text-gray-700 mb-2">
            Enseignants assignés
          </h4>
          <div class="flex flex-wrap gap-2 mb-3">
            <Tag
              v-for="t in selectedSession.teachers"
              :key="t.teacher_id"
              :value="t.teacher_name"
              severity="info"
              class="cursor-pointer"
              @click="handleRemoveTeacher(t.teacher_id)"
            >
              {{ t.teacher_name }} <i class="pi pi-times ml-1"></i>
            </Tag>
            <span
              v-if="selectedSession.teachers.length === 0"
              class="text-sm text-gray-400"
              >Aucun enseignant assigné.</span
            >
          </div>
          <div class="flex gap-2">
            <Select
              v-model="teacherToAdd"
              :options="availableTeachers"
              optionLabel="full_name"
              optionValue="id"
              placeholder="Ajouter un enseignant"
              class="flex-1"
            />
            <Button
              label="Ajouter"
              size="small"
              :disabled="!teacherToAdd"
              @click="handleAssignTeacher"
            />
          </div>
        </div>

        <!-- Étudiants -->
        <div>
          <h4 class="text-sm font-semibold text-gray-700 mb-2">
            Étudiants inscrits
          </h4>
          <div class="max-h-48 overflow-y-auto border border-gray-100 rounded-lg mb-3">
            <div
              v-for="s in selectedSession.students"
              :key="s.student_id"
              class="flex items-center justify-between px-3 py-2 border-b border-gray-50 last:border-0 text-sm"
            >
              <span>{{ s.student_name }}</span>
              <Tag
                v-if="s.ended_at"
                value="Terminé"
                severity="secondary"
              />
              <Button
                v-else
                label="Marquer terminé"
                text
                size="small"
                @click="handleEndStudent(s.student_id)"
              />
            </div>
            <p
              v-if="selectedSession.students.length === 0"
              class="text-sm text-gray-400 px-3 py-2"
            >
              Aucun étudiant inscrit.
            </p>
          </div>
          <div class="flex gap-2">
            <Select
              v-model="studentToAdd"
              :options="availableStudents"
              optionLabel="full_name"
              optionValue="id"
              placeholder="Inscrire un étudiant"
              class="flex-1"
            />
            <Button
              label="Inscrire"
              size="small"
              :disabled="!studentToAdd"
              @click="handleEnrollStudent"
            />
          </div>
        </div>

        <p v-if="manageError" class="text-sm text-red-600">
          {{ manageError }}
        </p>
      </div>
      <template #footer>
        <Button label="Fermer" text @click="showManageDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import type {
  TrainingSessionResponse,
  BranchResponse,
  UserAdminResponse,
  StudentResponse,
} from "#shared/api";
import type { NormalizedTrainingSession } from "~/stores/trainingSessions";

const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const trainingSessionsStore = useTrainingSessionsStore();
const examsStore = useExamsStore();


const loading = ref(true);
const sessions = ref<NormalizedTrainingSession[]>([]);
const errorMessage = ref<string | null>(null);
const branches = ref<BranchResponse[]>([]);
const teachers = ref<UserAdminResponse[]>([]);
const students = ref<StudentResponse[]>([]);



const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function activeStudentCount(session: NormalizedTrainingSession) {
  return session.students.filter((s) => !s.ended_at).length;
}

async function loadData() {
  loading.value = true;

  const tasks: Promise<any>[] = [
    authStore.isDirector
      ? trainingSessionsStore.fetchByCenter()
      : trainingSessionsStore.fetchByBranch(),
    centerStaffStore.fetchTeachers(),
    authStore.isDirector
      ? centerStaffStore.fetchStudentsByCenter()
      : centerStaffStore.fetchStudentsByBranch(),
  ];
  if (examsStore.catalog.length === 0) {
    tasks.push(examsStore.fetchCatalog());
  }
  if (authStore.isDirector) {
    tasks.push(centerStaffStore.fetchMyBranches());
  }

  const results = await Promise.all(tasks);

  sessions.value = trainingSessionsStore.sessions;
  if (!results[0]?.success) {
    errorMessage.value =
      trainingSessionsStore.error || "Erreur de chargement.";
  }

  const teacherResult = results[1];
  teachers.value = teacherResult?.teachers ?? [];

  const studentResult = results[2];
  students.value = studentResult?.students ?? [];

  if (authStore.isDirector) {
    const branchResult = results[results.length - 1];
    branches.value = branchResult?.branches ?? [];
  }

  loading.value = false;
}

// ── Création ──────────────────────────
const showCreateDialog = ref(false);
const creating = ref(false);
const createError = ref<string | null>(null);
const createForm = ref<{
  level_id: string;
  branch_id: string;
  label: string;
  start_date: Date | null;
  end_date: Date | null;
}>({
  level_id: "",
  branch_id: "",
  label: "",
  start_date: null,
  end_date: null,
});

function openCreateDialog() {
  createForm.value = {
    level_id: "",
    branch_id: "",
    label: "",
    start_date: new Date(),
    end_date: null,
  };
  createError.value = null;
  showCreateDialog.value = true;
}

async function handleCreateSession() {
  if (
    !createForm.value.level_id ||
    !createForm.value.start_date ||
    (authStore.isDirector && !createForm.value.branch_id)
  ) {
    createError.value = "Tous les champs obligatoires doivent être remplis.";
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await trainingSessionsStore.createSession({
    level_id: createForm.value.level_id,
    branch_id: authStore.isDirector ? createForm.value.branch_id : null,
    label: createForm.value.label.trim() || null,
    start_date: createForm.value.start_date.toISOString(),
    end_date: createForm.value.end_date
      ? createForm.value.end_date.toISOString()
      : null,
  });

  creating.value = false;

  if (result.success) {
    showCreateDialog.value = false;
    sessions.value = trainingSessionsStore.sessions;
  } else {
    createError.value = result.error || "Erreur lors de la création.";
  }
}

// ── Gestion (enseignants + étudiants) ──
const showManageDialog = ref(false);
const selectedSession = ref<NormalizedTrainingSession | null>(null);
const manageError = ref<string | null>(null);
const teacherToAdd = ref("");
const studentToAdd = ref("");

const manageHeader = computed(() =>
  selectedSession.value ? `Gérer — ${selectedSession.value.level_name}` : "",
);

const availableTeachers = computed(() => {
  if (!selectedSession.value) return [];
  const assignedIds = new Set(
    selectedSession.value.teachers.map((t) => t.teacher_id),
  );
  return teachers.value.filter((t) => !assignedIds.has(t.id));
});

const availableStudents = computed(() => {
  if (!selectedSession.value) return [];
  const enrolledIds = new Set(
    selectedSession.value.students.map((s) => s.student_id),
  );
  return students.value.filter((s) => !enrolledIds.has(s.id));
});

function openManageDialog(session: NormalizedTrainingSession) {
  selectedSession.value = session;
  teacherToAdd.value = "";
  studentToAdd.value = "";
  manageError.value = null;
  showManageDialog.value = true;
}

async function refreshSelectedSession() {
  // Recharge toute la liste pour resynchroniser le détail (teachers/students)
  // de la session ouverte — évite de dupliquer une méthode get-by-id.
  const result = authStore.isDirector
    ? await trainingSessionsStore.fetchByCenter()
    : await trainingSessionsStore.fetchByBranch();
  if (result.success && selectedSession.value) {
    sessions.value = trainingSessionsStore.sessions;
    selectedSession.value =
      sessions.value.find((s) => s.id === selectedSession.value!.id) ?? null;
  }
}

async function handleAssignTeacher() {
  if (!selectedSession.value || !teacherToAdd.value) return;
  manageError.value = null;
  const result = await trainingSessionsStore.assignTeacher(
    selectedSession.value.id,
    { teacher_id: teacherToAdd.value },
  );
  if (result.success) {
    teacherToAdd.value = "";
    await refreshSelectedSession();
  } else {
    manageError.value = result.error || "Erreur lors de l'affectation.";
  }
}

async function handleRemoveTeacher(teacherId: string) {
  if (!selectedSession.value) return;
  manageError.value = null;
  const result = await trainingSessionsStore.removeTeacher(
    selectedSession.value.id,
    teacherId,
  );
  if (result.success) {
    await refreshSelectedSession();
  } else {
    manageError.value = result.error || "Erreur lors du retrait.";
  }
}

async function handleEnrollStudent() {
  if (!selectedSession.value || !studentToAdd.value) return;
  manageError.value = null;
  const result = await trainingSessionsStore.enrollStudent(
    selectedSession.value.id,
    { student_id: studentToAdd.value },
  );
  if (result.success) {
    studentToAdd.value = "";
    await refreshSelectedSession();
  } else {
    manageError.value = result.error || "Erreur lors de l'inscription.";
  }
}

async function handleEndStudent(studentId: string) {
  if (!selectedSession.value) return;
  manageError.value = null;
  const result = await trainingSessionsStore.endStudent(
    selectedSession.value.id,
    studentId,
    { ended_at: null },
  );
  if (result.success) {
    await refreshSelectedSession();
  } else {
    manageError.value = result.error || "Erreur lors de la clôture.";
  }
}

onMounted(loadData);
</script>