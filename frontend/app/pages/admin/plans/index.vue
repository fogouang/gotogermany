<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">Plans d'abonnement</h2>
        <p class="text-sm text-gray-500">
          Définissez les durées et tarifs d'accès
        </p>
      </div>
      <Button label="Nouveau plan" icon="pi pi-plus" @click="openCreate" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Liste plans -->
    <div
      v-else
      class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
    >
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Plan
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Durée
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Prix
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Ordre
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Statut
            </th>
            <th
              class="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="plan in plans"
            :key="plan.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <td class="px-5 py-4">
              <p class="font-medium text-gray-900">{{ plan.name }}</p>
              <p
                v-if="plan.description"
                class="text-xs text-gray-400 mt-0.5 truncate max-w-xs"
              >
                {{ plan.description }}
              </p>
            </td>
            <td class="px-5 py-4">
              <span
                class="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-1 rounded-full"
              >
                {{ formatDuration(plan.duration_days) }}
              </span>
            </td>
            <td class="px-5 py-4">
              <span class="font-bold text-gray-900">{{
                formatPrice(plan.price)
              }}</span>
            </td>
            <td class="px-5 py-4 text-gray-500">{{ plan.display_order }}</td>
            <td class="px-5 py-4">
              <Tag
                :value="plan.is_active ? 'Actif' : 'Inactif'"
                :severity="plan.is_active ? 'success' : 'danger'"
              />
            </td>
            <td class="px-5 py-4">
              <div class="flex items-center justify-end gap-1">
                <Button
                  icon="pi pi-pencil"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  v-tooltip.top="'Modifier'"
                  @click="openEdit(plan)"
                />
                <Button
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  @click="openDelete(plan)"
                />
              </div>
            </td>
          </tr>
          <tr v-if="plans.length === 0">
            <td colspan="6" class="px-5 py-12 text-center text-gray-400">
              <i class="pi pi-tag text-3xl mb-2 block"></i>
              Aucun plan — créez votre premier plan
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ─── Dialog Créer / Éditer ──────────────────────── -->
    <Dialog
      v-model:visible="formDialog"
      :header="editingPlan ? 'Modifier le plan' : 'Nouveau plan'"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '480px' }"
    >
      <div class="space-y-4 mt-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Nom <span class="text-red-500">*</span></label
          >
          <InputText
            v-model="form.name"
            class="w-full"
            placeholder="Ex: 1 mois, Accès 30 jours…"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Durée (jours) <span class="text-red-500">*</span></label
            >
            <InputNumber
              v-model="form.duration_days"
              :min="1"
              class="w-full"
              placeholder="30"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Prix (FCFA) <span class="text-red-500">*</span></label
            >
            <InputNumber
              v-model="form.price"
              :min="0"
              class="w-full"
              placeholder="5000"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >Description</label
          >
          <Textarea
            v-model="form.description"
            class="w-full"
            rows="2"
            placeholder="Décrit ce plan sur la page tarifs"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >Ordre d'affichage</label
            >
            <InputNumber
              v-model="form.display_order"
              :min="0"
              class="w-full"
              placeholder="0"
            />
          </div>
          <div class="flex items-end pb-1">
            <div class="flex items-center gap-2">
              <Checkbox
                v-model="form.is_active"
                :binary="true"
                inputId="is_active"
              />
              <label
                for="is_active"
                class="text-sm text-gray-700 cursor-pointer"
                >Plan actif</label
              >
            </div>
          </div>
        </div>
        <Message v-if="error" severity="error" :closable="false">{{
          error
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="formDialog = false" />
        <Button
          :label="editingPlan ? 'Enregistrer' : 'Créer'"
          icon="pi pi-check"
          :loading="loading"
          :disabled="!form.name || !form.duration_days || form.price === null"
          @click="handleSave"
        />
      </template>
    </Dialog>

    <!-- ─── Dialog Supprimer ──────────────────────────── -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le plan ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '400px' }"
    >
      <div class="space-y-3 mt-2">
        <Message severity="warn" :closable="false">
          Les paiements existants liés à ce plan ne seront pas affectés.
        </Message>
        <div class="bg-gray-50 rounded-lg p-3">
          <p class="font-medium text-gray-900">{{ deletingPlan?.name }}</p>
          <p class="text-sm text-gray-500">
            {{ formatDuration(deletingPlan?.duration_days ?? 0) }} —
            {{ formatPrice(deletingPlan?.price ?? 0) }}
          </p>
        </div>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button
          label="Supprimer"
          severity="danger"
          icon="pi pi-trash"
          :loading="loading"
          @click="handleDelete"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse } from "#shared/api";

definePageMeta({ layout: "admin", middleware: "admin" });

const toast = useToast();
const {
  plans,
  loading,
  error,
  loadPlans,
  createPlan,
  updatePlan,
  deletePlan,
  formatDuration,
  formatPrice,
} = usePlans();

// ── Form ──────────────────────────────────────────────
const formDialog = ref(false);
const editingPlan = ref<PlanResponse | null>(null);

const defaultForm = () => ({
  name: "",
  duration_days: null as number | null,
  price: null as number | null,
  description: "",
  display_order: 0,
  is_active: true,
});

const form = ref(defaultForm());

const openCreate = () => {
  editingPlan.value = null;
  form.value = defaultForm();
  formDialog.value = true;
};

const openEdit = (plan: PlanResponse) => {
  editingPlan.value = plan;
  form.value = {
    name: plan.name,
    duration_days: plan.duration_days,
    price: plan.price,
    description: plan.description ?? "",
    display_order: plan.display_order,
    is_active: plan.is_active,
  };
  formDialog.value = true;
};

const handleSave = async () => {
  if (
    !form.value.name ||
    !form.value.duration_days ||
    form.value.price === null
  )
    return;

  if (editingPlan.value) {
    const res = await updatePlan(editingPlan.value.id, {
      name: form.value.name,
      duration_days: form.value.duration_days,
      price: form.value.price,
      description: form.value.description || null,
      display_order: form.value.display_order,
      is_active: form.value.is_active,
    });
    if (res.success) {
      formDialog.value = false;
      toast.add({ severity: "success", summary: "Plan modifié", life: 3000 });
    }
  } else {
    const res = await createPlan({
      name: form.value.name,
      duration_days: form.value.duration_days!,
      price: form.value.price!,
      description: form.value.description || null,
      display_order: form.value.display_order,
      is_active: form.value.is_active,
    });
    if (res.success) {
      formDialog.value = false;
      toast.add({ severity: "success", summary: "Plan créé", life: 3000 });
    }
  }
};

// ── Supprimer ─────────────────────────────────────────
const deleteDialog = ref(false);
const deletingPlan = ref<PlanResponse | null>(null);

const openDelete = (plan: PlanResponse) => {
  deletingPlan.value = plan;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!deletingPlan.value) return;
  const res = await deletePlan(deletingPlan.value.id);
  if (res.success) {
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Plan supprimé", life: 3000 });
  } else {
    toast.add({
      severity: "error",
      summary: res.error || "Erreur",
      life: 4000,
    });
  }
};

onMounted(loadPlans);
</script>
