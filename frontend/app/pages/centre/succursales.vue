<!-- pages/centre/succursales.vue -->
<template>
  <div>
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6"
    >
      <p class="text-sm text-gray-500">{{ branches.length }} succursale(s)</p>
      <Button
        label="Nouvelle succursale"
        icon="pi pi-plus"
        size="small"
        class="w-full sm:w-auto"
        @click="showCreateDialog = true"
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
      v-else-if="branches.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucune succursale pour l'instant.
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
                Type
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Étudiants inscrits
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Créée le
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="branch in branches"
              :key="branch.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td class="px-4 py-3 text-gray-900 whitespace-nowrap">
                {{ branch.name }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag
                  v-if="branch.is_main"
                  value="Principale"
                  severity="success"
                />
                <span v-else class="text-gray-400">Secondaire</span>
              </td>
              <td class="px-4 py-3 text-gray-700 font-medium whitespace-nowrap">
                {{ studentCount(branch.name) }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                {{ formatDate(branch.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Dialog création -->
    <Dialog
      v-model:visible="showCreateDialog"
      header="Nouvelle succursale"
      modal
      :style="{ width: '90vw', maxWidth: '28rem' }"
    >
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nom de la succursale</label
          >
          <InputText
            v-model="newBranchName"
            class="w-full"
            placeholder="ex: Centre Alpha - Yaoundé"
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

import type { BranchResponse } from "#shared/api";

const centerStaffStore = useCenterStaffStore();

const loading = ref(true);
const branches = ref<BranchResponse[]>([]);
const branchesBreakdown = ref<Record<string, number>>({});
const errorMessage = ref<string | null>(null);

const showCreateDialog = ref(false);
const newBranchName = ref("");
const creating = ref(false);
const createError = ref<string | null>(null);

function studentCount(branchName: string) {
  return branchesBreakdown.value[branchName] ?? 0;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

async function loadBranches() {
  loading.value = true;

  const [branchResult, usageResult] = await Promise.all([
    centerStaffStore.fetchMyBranches(),
    centerStaffStore.fetchMyUsage(),
  ]);

  if (branchResult.success) {
    branches.value = branchResult.branches ?? [];
  } else {
    errorMessage.value = branchResult.error || "Erreur de chargement.";
  }

  if (usageResult.success && usageResult.usage) {
    branchesBreakdown.value = usageResult.usage.branches_breakdown ?? {};
  }

  loading.value = false;
}

async function handleCreate() {
  if (!newBranchName.value.trim()) {
    createError.value = "Le nom est requis.";
    return;
  }
  creating.value = true;
  createError.value = null;
  const result = await centerStaffStore.createMyBranch({
    name: newBranchName.value.trim(),
  });
  creating.value = false;
  if (result.success) {
    showCreateDialog.value = false;
    newBranchName.value = "";
    await loadBranches();
  } else {
    createError.value = result.error || "Erreur lors de la création.";
  }
}

onMounted(loadBranches);
</script>
