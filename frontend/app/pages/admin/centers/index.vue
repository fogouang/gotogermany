<!-- pages/admin/centers/index.vue -->
<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <p class="text-sm text-gray-500">
        {{ adminCenters.centers.length }} centre(s)
      </p>
      <Button
        label="Nouveau centre"
        icon="pi pi-plus"
        size="small"
        @click="openCreateCenterDialog"
      />
    </div>

    <div v-if="loadingCenters" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-teal-600"></i>
    </div>

    <div
      v-else-if="adminCenters.centers.length === 0"
      class="text-center py-12 text-gray-400"
    >
      Aucun centre pour l'instant.
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
                Contact
              </th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">
                Pool crédits IA
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
              v-for="center in paginatedCenters"
              :key="center.id"
              class="border-b border-gray-100 last:border-0"
            >
              <td
                class="px-4 py-3 text-gray-900 font-medium whitespace-nowrap"
              >
                {{ center.name }}
              </td>
              <td class="px-4 py-3 text-gray-500 whitespace-nowrap">
                <div>{{ center.contact_email || "—" }}</div>
                <div class="text-xs text-gray-400">
                  {{ center.contact_phone || "" }}
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span
                  class="font-semibold"
                  :class="
                    center.ai_credit_pool_balance <
                    center.default_credits_per_student
                      ? 'text-red-600'
                      : 'text-gray-900'
                  "
                >
                  {{ center.ai_credit_pool_balance }}
                </span>
                <span class="text-xs text-gray-400 ml-1">
                  (défaut: {{ center.default_credits_per_student }}/étudiant)
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <Tag
                  :value="center.is_active ? 'Actif' : 'Inactif'"
                  :severity="center.is_active ? 'success' : 'danger'"
                />
              </td>
              <td class="px-4 py-3 text-right whitespace-nowrap">
                <Button
                  label="Directeur"
                  icon="pi pi-user-plus"
                  text
                  size="small"
                  @click="openDirectorDialog(center)"
                />
                <Button
                  label="Recharger crédits"
                  icon="pi pi-sparkles"
                  text
                  size="small"
                  @click="openRechargeDialog(center)"
                />
                <Button
                  :label="center.is_active ? 'Désactiver' : 'Réactiver'"
                  :icon="center.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
                  text
                  size="small"
                  :severity="center.is_active ? 'danger' : 'success'"
                  @click="confirmToggleActive(center)"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Paginator
        v-model:first="centersFirst"
        v-model:rows="centersRows"
        :totalRecords="adminCenters.centers.length"
        :rowsPerPageOptions="[10, 20, 50]"
        class="border-t border-gray-200"
      />
    </div>

    <!-- Dialog création centre -->
    <Dialog
      v-model:visible="showCreateCenterDialog"
      header="Nouveau centre"
      modal
      :style="{ width: '28rem' }"
    >
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nom du centre</label
          >
          <InputText
            v-model="centerForm.name"
            class="w-full"
            placeholder="ex: Centre Alpha Formation"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Email de contact (optionnel)</label
          >
          <InputText
            v-model="centerForm.contact_email"
            class="w-full"
            placeholder="contact@centre-alpha.cm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Téléphone (optionnel)</label
          >
          <InputText
            v-model="centerForm.contact_phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
        </div>
        <Message v-if="centerFormError" severity="error" :closable="false">{{
          centerFormError
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="showCreateCenterDialog = false" />
        <Button
          label="Créer"
          :loading="creatingCenter"
          @click="handleCreateCenter"
        />
      </template>
    </Dialog>

    <!-- Dialog création directeur -->
    <Dialog
      v-model:visible="showDirectorDialog"
      header="Créer le directeur"
      modal
      :style="{ width: '28rem' }"
    >
      <div v-if="selectedCenter" class="space-y-4">
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="font-semibold text-gray-900">{{ selectedCenter.name }}</p>
        </div>

        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Nom complet</label
          >
          <InputText
            v-model="directorForm.full_name"
            class="w-full"
            placeholder="ex: M. Jean Talla"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Email</label
          >
          <InputText
            v-model="directorForm.email"
            class="w-full"
            placeholder="directeur@cfm.cm"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Téléphone (optionnel)</label
          >
          <InputText
            v-model="directorForm.phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Mot de passe provisoire</label
          >
          <Password
            v-model="directorForm.password"
            class="w-full"
            inputClass="w-full"
            toggleMask
            :feedback="false"
            placeholder="Min. 8 caractères"
          />
        </div>

        <Message v-if="directorFormError" severity="error" :closable="false">{{
          directorFormError
        }}</Message>
        <Message v-if="directorSuccess" severity="success" :closable="false">{{
          directorSuccess
        }}</Message>
      </div>
      <template #footer>
        <Button label="Fermer" text @click="showDirectorDialog = false" />
        <Button
          v-if="!directorSuccess"
          label="Créer"
          icon="pi pi-user-plus"
          :loading="creatingDirector"
          @click="handleCreateDirector"
        />
      </template>
    </Dialog>

    <!-- Dialog rechargement du pool de crédits IA -->
    <Dialog
      v-model:visible="showRechargeDialog"
      header="Recharger le pool de crédits IA"
      modal
      :style="{ width: '28rem' }"
    >
      <div v-if="selectedCenter" class="space-y-4">
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="font-semibold text-gray-900">{{ selectedCenter.name }}</p>
          <p class="text-xs text-gray-500 mt-1">
            Solde actuel :
            <strong>{{ selectedCenter.ai_credit_pool_balance }}</strong> crédits
          </p>
        </div>

        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Quantité à ajouter</label
          >
          <InputNumber
            v-model="rechargeForm.amount"
            class="w-full"
            :min="1"
            showButtons
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Motif / référence (optionnel)</label
          >
          <InputText
            v-model="rechargeForm.reason"
            class="w-full"
            placeholder="ex: Rechargement négocié le 09/07, 20000 FCFA"
          />
        </div>

        <Message v-if="rechargeFormError" severity="error" :closable="false">{{
          rechargeFormError
        }}</Message>
        <Message v-if="rechargeSuccess" severity="success" :closable="false">{{
          rechargeSuccess
        }}</Message>
      </div>
      <template #footer>
        <Button label="Fermer" text @click="showRechargeDialog = false" />
        <Button
          v-if="!rechargeSuccess"
          label="Recharger"
          icon="pi pi-sparkles"
          :loading="recharging"
          @click="handleRechargePool"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin" });

import type { CenterResponse } from "#shared/api";

const adminCenters = useAdminCentersStore();
const adminUsers = useAdminUsersStore();
const toast = useToast();
const confirm = useConfirm();

const loadingCenters = ref(true);
const selectedCenter = ref<CenterResponse | null>(null);

// ── Pagination (client) ──
const centersFirst = ref(0);
const centersRows = ref(10);
const paginatedCenters = computed(() =>
  adminCenters.centers.slice(
    centersFirst.value,
    centersFirst.value + centersRows.value,
  ),
);

// ── Activation / désactivation ──
function confirmToggleActive(center: CenterResponse) {
  confirm.require({
    message: center.is_active
      ? `Désactiver "${center.name}" ? Tout le personnel et les étudiants de ce centre perdront l'accès immédiatement.`
      : `Réactiver "${center.name}" ? Le personnel et les étudiants retrouveront l'accès.`,
    header: center.is_active ? "Désactiver le centre" : "Réactiver le centre",
    icon: "pi pi-exclamation-triangle",
    acceptClass: center.is_active ? "p-button-danger" : undefined,
    accept: async () => {
      const result = await adminCenters.toggleCenterActive(center.id);
      if (result.success) {
        toast.add({
          severity: "success",
          summary: center.is_active ? "Centre désactivé" : "Centre réactivé",
          life: 3000,
        });
      } else {
        toast.add({
          severity: "error",
          summary: result.error || "Erreur",
          life: 4000,
        });
      }
    },
  });
}

// ── Création centre ──
const showCreateCenterDialog = ref(false);
const creatingCenter = ref(false);
const centerFormError = ref<string | null>(null);
const centerForm = ref({ name: "", contact_email: "", contact_phone: "" });

function openCreateCenterDialog() {
  centerForm.value = { name: "", contact_email: "", contact_phone: "" };
  centerFormError.value = null;
  showCreateCenterDialog.value = true;
}

async function handleCreateCenter() {
  if (!centerForm.value.name.trim()) {
    centerFormError.value = "Le nom du centre est requis.";
    return;
  }
  creatingCenter.value = true;
  centerFormError.value = null;
  const result = await adminCenters.createCenter({
    name: centerForm.value.name.trim(),
    contact_email: centerForm.value.contact_email.trim() || null,
    contact_phone: centerForm.value.contact_phone.trim() || null,
  });
  creatingCenter.value = false;
  if (result.success) {
    showCreateCenterDialog.value = false;
    // Le nouveau centre est ajouté en fin de liste : on saute à la
    // dernière page pour qu'il soit visible immédiatement.
    centersFirst.value =
      Math.floor((adminCenters.centers.length - 1) / centersRows.value) *
      centersRows.value;
    toast.add({ severity: "success", summary: "Centre créé", life: 3000 });
  } else {
    centerFormError.value = result.error || "Erreur lors de la création.";
  }
}

// ── Création directeur ──
const showDirectorDialog = ref(false);
const creatingDirector = ref(false);
const directorFormError = ref<string | null>(null);
const directorSuccess = ref<string | null>(null);
const directorForm = ref({ full_name: "", email: "", phone: "", password: "" });

function openDirectorDialog(center: CenterResponse) {
  selectedCenter.value = center;
  directorForm.value = { full_name: "", email: "", phone: "", password: "" };
  directorFormError.value = null;
  directorSuccess.value = null;
  showDirectorDialog.value = true;
}

async function handleCreateDirector() {
  if (!selectedCenter.value) return;
  if (
    !directorForm.value.full_name.trim() ||
    !directorForm.value.email.trim() ||
    !directorForm.value.password
  ) {
    directorFormError.value = "Nom, email et mot de passe sont requis.";
    return;
  }

  creatingDirector.value = true;
  directorFormError.value = null;

  const result = await adminUsers.createDirector({
    email: directorForm.value.email.trim(),
    password: directorForm.value.password,
    full_name: directorForm.value.full_name.trim(),
    phone: directorForm.value.phone.trim() || null,
    center_id: selectedCenter.value.id,
  });

  creatingDirector.value = false;

  if (result.success) {
    directorSuccess.value = `Compte créé. Transmettez ces identifiants à ${directorForm.value.full_name} : ${directorForm.value.email} / ${directorForm.value.password}`;
  } else {
    directorFormError.value =
      result.error || "Erreur lors de la création du directeur.";
  }
}

// ── Rechargement du pool de crédits IA ──
const showRechargeDialog = ref(false);
const recharging = ref(false);
const rechargeFormError = ref<string | null>(null);
const rechargeSuccess = ref<string | null>(null);
const rechargeForm = ref({ amount: 50, reason: "" });

function openRechargeDialog(center: CenterResponse) {
  selectedCenter.value = center;
  rechargeForm.value = { amount: 50, reason: "" };
  rechargeFormError.value = null;
  rechargeSuccess.value = null;
  showRechargeDialog.value = true;
}

async function handleRechargePool() {
  if (!selectedCenter.value || !rechargeForm.value.amount) {
    rechargeFormError.value = "La quantité est requise.";
    return;
  }

  const center = selectedCenter.value;

  recharging.value = true;
  rechargeFormError.value = null;

  const result = await adminCenters.rechargeCreditPool(center.id, {
    amount: rechargeForm.value.amount,
    reason: rechargeForm.value.reason.trim() || null,
  });

  recharging.value = false;

  if (result.success && result.pool) {
    rechargeSuccess.value = `Pool rechargé avec succès. Nouveau solde : ${result.pool.ai_credit_pool_balance} crédits.`;

    const index = adminCenters.centers.findIndex((c) => c.id === center.id);
    if (index !== -1) {
      adminCenters.centers[index] = {
        ...center,
        ai_credit_pool_balance: result.pool.ai_credit_pool_balance,
      };
    }

    selectedCenter.value = {
      ...center,
      ai_credit_pool_balance: result.pool.ai_credit_pool_balance,
    };
  } else {
    rechargeFormError.value = result.error || "Erreur lors du rechargement.";
  }
}

onMounted(async () => {
  loadingCenters.value = true;
  await adminCenters.fetchCenters();
  loadingCenters.value = false;
});
</script>