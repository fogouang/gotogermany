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
                Crédits IA
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Première connexion
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Accès expire le
              </th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600">
                Actions
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
              <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
                {{ student.ai_credits }}
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
              <td class="px-4 py-3 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-1">
                  <Button
                    icon="pi pi-sparkles"
                    text
                    rounded
                    size="small"
                    v-tooltip.top="'Ajuster les crédits IA'"
                    @click="openCreditsDialog(student)"
                  />
                  <template v-if="authStore.isDirector">
                    <Button
                      icon="pi pi-calendar"
                      text
                      rounded
                      size="small"
                      v-tooltip.top="'Ajuster la fenêtre d\'accès'"
                      @click="openDatesDialog(student)"
                    />
                    <Button
                      :icon="student.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
                      text
                      rounded
                      size="small"
                      :severity="student.is_active ? 'danger' : 'success'"
                      v-tooltip.top="student.is_active ? 'Désactiver' : 'Activer'"
                      @click="handleToggleActivation(student)"
                    />
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Dialog crédits -->
    <Dialog
      v-model:visible="showCreditsDialog"
      header="Ajuster les crédits IA"
      modal
      :style="{ width: '90vw', maxWidth: '24rem' }"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-500">
          Étudiant : <strong>{{ selectedStudent?.full_name }}</strong>
          — solde actuel : <strong>{{ selectedStudent?.ai_credits }}</strong>
        </p>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nombre de crédits à ajouter</label
          >
          <InputNumber
            v-model="creditsForm.amount"
            class="w-full"
            :min="1"
            :max="100"
            showButtons
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Motif (optionnel)</label
          >
          <InputText
            v-model="creditsForm.reason"
            class="w-full"
            placeholder="ex: Rechargement payé par l'étudiant"
          />
        </div>
        <p v-if="creditsError" class="text-sm text-red-600">{{ creditsError }}</p>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="showCreditsDialog = false" />
        <Button label="Valider" :loading="savingCredits" @click="handleAdjustCredits" />
      </template>
    </Dialog>

    <!-- Dialog dates (directeur uniquement) -->
    <Dialog
      v-model:visible="showDatesDialog"
      header="Ajuster la fenêtre d'accès"
      modal
      :style="{ width: '90vw', maxWidth: '24rem' }"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-500">
          Étudiant : <strong>{{ selectedStudent?.full_name }}</strong>
        </p>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nouvelle date d'expiration</label
          >
          <DatePicker
            v-model="datesForm.access_expires_at"
            class="w-full"
            dateFormat="dd/mm/yy"
            showIcon
          />
        </div>
        <p class="text-xs text-gray-400">
          Laisser vide pour ne modifier que la durée par défaut des futurs accès.
        </p>
        <p v-if="datesError" class="text-sm text-red-600">{{ datesError }}</p>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="showDatesDialog = false" />
        <Button label="Valider" :loading="savingDates" @click="handleUpdateDates" />
      </template>
    </Dialog>
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

// ── Ajustement des crédits (directeur + secrétaire) ────────
const showCreditsDialog = ref(false);
const selectedStudent = ref<StudentResponse | null>(null);
const savingCredits = ref(false);
const creditsError = ref<string | null>(null);
const creditsForm = ref({ amount: 5, reason: "" });

function openCreditsDialog(student: StudentResponse) {
  selectedStudent.value = student;
  creditsForm.value = { amount: 5, reason: "" };
  creditsError.value = null;
  showCreditsDialog.value = true;
}

async function handleAdjustCredits() {
  if (!selectedStudent.value || !creditsForm.value.amount) return;
  savingCredits.value = true;
  creditsError.value = null;

  const result = await centerStaffStore.adjustStudentCredits(
    selectedStudent.value.id,
    {
      amount: creditsForm.value.amount,
      reason: creditsForm.value.reason || null,
    },
  );

  savingCredits.value = false;

  if (result.success) {
    showCreditsDialog.value = false;
    await loadStudents();
  } else {
    creditsError.value = result.error || "Erreur lors de l'ajustement.";
  }
}

// ── Ajustement des dates d'accès (directeur uniquement) ────
const showDatesDialog = ref(false);
const savingDates = ref(false);
const datesError = ref<string | null>(null);
const datesForm = ref<{ access_expires_at: Date | null }>({
  access_expires_at: null,
});

function openDatesDialog(student: StudentResponse) {
  selectedStudent.value = student;
  datesForm.value = {
    access_expires_at: student.access_expires_at
      ? new Date(student.access_expires_at)
      : null,
  };
  datesError.value = null;
  showDatesDialog.value = true;
}

async function handleUpdateDates() {
  if (!selectedStudent.value) return;
  savingDates.value = true;
  datesError.value = null;

  const result = await centerStaffStore.updateStudentAccessDates(
    selectedStudent.value.id,
    {
      access_expires_at: datesForm.value.access_expires_at
        ? datesForm.value.access_expires_at.toISOString()
        : null,
    },
  );

  savingDates.value = false;

  if (result.success) {
    showDatesDialog.value = false;
    await loadStudents();
  } else {
    datesError.value = result.error || "Erreur lors de la mise à jour.";
  }
}

// ── Activation / désactivation (directeur uniquement) ──────
async function handleToggleActivation(student: StudentResponse) {
  const result = await centerStaffStore.toggleStudentActivation(student.id);
  if (result.success) {
    await loadStudents();
  } else {
    errorMessage.value = result.error || "Erreur lors du changement de statut.";
  }
}

onMounted(loadStudents);
</script>