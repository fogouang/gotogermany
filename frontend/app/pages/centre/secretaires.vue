<!-- pages/centre/secretaires.vue -->
<template>
  <div>
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6"
    >
      <p class="text-sm text-gray-500">
        {{ secretaries.length }} secrétaire(s)
      </p>
      <Button
        label="Nouvelle secrétaire"
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
      v-else-if="secretaries.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucune secrétaire pour l'instant.
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
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Succursale
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Statut
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="sec in secretaries"
              :key="sec.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">
                {{ sec.full_name }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ sec.email }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ branchName(sec.branch_id) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag
                  :value="sec.is_active ? 'Active' : 'Désactivée'"
                  :severity="sec.is_active ? 'success' : 'danger'"
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
      header="Nouvelle secrétaire"
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
            placeholder="ex: Marie Talla"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Email</label
          >
          <InputText
            v-model="form.email"
            class="w-full"
            placeholder="marie@centre-alpha.cm"
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
        <div>
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
  middleware: "director",
});

import type { UserAdminResponse, BranchResponse } from "#shared/api";

const centerStaffStore = useCenterStaffStore();

const loading = ref(true);
const secretaries = ref<UserAdminResponse[]>([]);
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
  const [secResult, branchResult] = await Promise.all([
    centerStaffStore.fetchSecretaries(),
    centerStaffStore.fetchMyBranches(),
  ]);

  if (secResult.success) {
    secretaries.value = secResult.secretaries ?? [];
  } else {
    errorMessage.value = secResult.error || "Erreur de chargement.";
  }

  if (branchResult.success) {
    branches.value = branchResult.branches ?? [];
  }

  loading.value = false;
}

async function handleCreate() {
  if (
    !form.value.full_name.trim() ||
    !form.value.email.trim() ||
    !form.value.password ||
    !form.value.branch_id
  ) {
    createError.value = "Tous les champs obligatoires doivent être remplis.";
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await centerStaffStore.createSecretary({
    email: form.value.email.trim(),
    password: form.value.password,
    full_name: form.value.full_name.trim(),
    phone: form.value.phone.trim() || null,
    branch_id: form.value.branch_id,
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
