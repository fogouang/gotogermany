<!-- pages/centre/enseignants.vue -->
<template>
  <div>
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6"
    >
      <p class="text-sm text-gray-500">{{ teachers.length }} enseignant(s)</p>
      <Button
        label="Nouvel enseignant"
        icon="pi pi-user-plus"
        size="small"
        class="w-full sm:w-auto"
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
      v-else-if="teachers.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucun enseignant pour l'instant.
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
                Email
              </th>
              <th
                v-if="authStore.isDirector"
                class="text-left px-4 py-3 font-semibold text-gray-600"
              >
                Succursale
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Statut
              </th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="teacher in teachers"
              :key="teacher.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">
                {{ teacher.full_name }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ teacher.email }}
              </td>
              <td
                v-if="authStore.isDirector"
                class="px-4 py-3 text-gray-500 whitespace-nowrap"
              >
                {{ branchName(teacher.branch_id) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag
                  :value="teacher.is_active ? 'Active' : 'Désactivée'"
                  :severity="teacher.is_active ? 'success' : 'danger'"
                />
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag
                  :value="teacher.is_active ? 'Active' : 'Désactivée'"
                  :severity="teacher.is_active ? 'success' : 'danger'"
                />
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-right">
                <Button
                  :label="teacher.is_active ? 'Désactiver' : 'Réactiver'"
                  :icon="teacher.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
                  text
                  size="small"
                  :severity="teacher.is_active ? 'danger' : 'success'"
                  @click="confirmToggleActive(teacher)"
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
      header="Nouvel enseignant"
      modal
      :style="{ width: '90vw', maxWidth: '28rem' }"
    >
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nom complet</label
          >
          <InputText
            v-model="form.full_name"
            class="w-full"
            placeholder="ex: Paul Nkeng"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Email</label
          >
          <InputText
            v-model="form.email"
            class="w-full"
            placeholder="paul@centre-alpha.cm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Téléphone (optionnel)</label
          >
          <InputText
            v-model="form.phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Mot de passe provisoire</label
          >
          <Password
            v-model="form.password"
            class="w-full"
            inputClass="w-full"
            :feedback="false"
            toggleMask
            placeholder="Min. 8 caractères"
          />
        </div>
        <!-- Succursale : uniquement pour le directeur — la secrétaire
             crée toujours dans sa propre succursale (géré côté backend) -->
        <div v-if="authStore.isDirector">
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Succursale</label
          >
          <Select
            v-model="form.branch_id"
            :options="branches"
            optionLabel="name"
            optionValue="id"
            placeholder="Choisir une succursale"
            class="w-full"
          />
        </div>
        <p v-if="createError" class="text-sm text-red-600">{{ createError }}</p>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="showCreateDialog = false" />
        <Button label="Créer" :loading="creating" @click="handleCreate" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

import type { UserAdminResponse, BranchResponse } from "#shared/api";

const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();

const loading = ref(true);
const teachers = ref<UserAdminResponse[]>([]);
const branches = ref<BranchResponse[]>([]);
const errorMessage = ref<string | null>(null);

const showCreateDialog = ref(false);
const creating = ref(false);
const createError = ref<string | null>(null);
const form = ref({
  full_name: "",
  email: "",
  phone: "",
  password: "",
  branch_id: "",
});

const confirm = useConfirm();

function confirmToggleActive(teacher: UserAdminResponse) {
  confirm.require({
    message: teacher.is_active
      ? `Désactiver "${teacher.full_name}" ? Il/elle ne pourra plus se connecter.`
      : `Réactiver "${teacher.full_name}" ? Il/elle retrouvera l'accès.`,
    header: teacher.is_active
      ? "Désactiver l'enseignant"
      : "Réactiver l'enseignant",
    icon: "pi pi-exclamation-triangle",
    acceptClass: teacher.is_active ? "p-button-danger" : undefined,
    accept: async () => {
      const result = await centerStaffStore.toggleTeacherActive(teacher.id);
      if (result.success) {
        await loadData();
      } else {
        errorMessage.value =
          result.error || "Erreur lors du changement de statut.";
      }
    },
  });
}

function branchName(branchId: string | null) {
  if (!branchId) return "—";
  return branches.value.find((b) => b.id === branchId)?.name ?? "—";
}

function resetForm() {
  form.value = {
    full_name: "",
    email: "",
    phone: "",
    password: "",
    branch_id: "",
  };
  createError.value = null;
}

function openCreateDialog() {
  resetForm();
  showCreateDialog.value = true;
}

async function loadData() {
  loading.value = true;
  const promises: Promise<any>[] = [centerStaffStore.fetchTeachers()];
  // Les succursales ne sont utiles que pour le directeur (filtre colonne + select du dialog)
  if (authStore.isDirector) {
    promises.push(centerStaffStore.fetchMyBranches());
  }
  const [teacherResult, branchResult] = await Promise.all(promises);

  if (teacherResult.success) {
    teachers.value = teacherResult.teachers ?? [];
  } else {
    errorMessage.value = teacherResult.error || "Erreur de chargement.";
  }

  if (branchResult?.success) {
    branches.value = branchResult.branches ?? [];
  }

  loading.value = false;
}

async function handleCreate() {
  if (
    !form.value.full_name.trim() ||
    !form.value.email.trim() ||
    !form.value.password ||
    (authStore.isDirector && !form.value.branch_id)
  ) {
    createError.value = "Tous les champs obligatoires doivent être remplis.";
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await centerStaffStore.createTeacher({
    email: form.value.email.trim(),
    password: form.value.password,
    full_name: form.value.full_name.trim(),
    phone: form.value.phone.trim() || null,
    branch_id: authStore.isDirector ? form.value.branch_id : null,
  });

  creating.value = false;

  if (result.success) {
    showCreateDialog.value = false;
    await loadData();
  } else {
    createError.value = result.error || "Erreur lors de la création.";
  }
}

onMounted(loadData);
</script>
