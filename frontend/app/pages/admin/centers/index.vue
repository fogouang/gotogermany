<!-- pages/admin/centers.vue -->
<template>
  <div>
    <Tabs value="0">
      <TabList>
        <Tab value="0">Centres</Tab>
        <Tab value="1">Formules de licence</Tab>
      </TabList>

      <TabPanels>
        <!-- ── Onglet Centres ── -->
        <TabPanel value="0">
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
                    <th
                      class="text-right px-4 py-3 font-semibold text-gray-600"
                    >
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="center in adminCenters.centers"
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
                        (défaut:
                        {{ center.default_credits_per_student }}/étudiant)
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
                        label="Licence"
                        icon="pi pi-verified"
                        text
                        size="small"
                        @click="openLicenseDialog(center)"
                      />
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
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </TabPanel>

        <!-- ── Onglet Formules ── -->
        <TabPanel value="1">
          <div class="flex items-center justify-between mb-6">
            <p class="text-sm text-gray-500">
              {{ adminCenters.formulas.length }} formule(s)
            </p>
            <Button
              label="Nouvelle formule"
              icon="pi pi-plus"
              size="small"
              @click="openCreateFormulaDialog"
            />
          </div>

          <div v-if="loadingFormulas" class="flex justify-center py-12">
            <i class="pi pi-spin pi-spinner text-3xl text-teal-600"></i>
          </div>

          <div
            v-else-if="adminCenters.formulas.length === 0"
            class="text-center py-12 text-gray-400"
          >
            Aucune formule pour l'instant.
          </div>

          <div
            v-else
            class="bg-white rounded-xl border border-gray-200 overflow-hidden"
          >
            <table class="w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="text-left px-4 py-3 font-semibold text-gray-600">
                    Label
                  </th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-600">
                    Durée
                  </th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-600">
                    Plafond
                  </th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-600">
                    Statut
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="formula in adminCenters.formulas"
                  :key="formula.id"
                  class="border-b border-gray-100 last:border-0"
                >
                  <td class="px-4 py-3 text-gray-900 font-medium">
                    {{ formula.label }}
                  </td>
                  <td class="px-4 py-3 text-gray-500">
                    {{ formula.duration_months }} mois
                  </td>
                  <td class="px-4 py-3 text-gray-500">
                    {{ formula.max_students }} étudiants
                  </td>
                  <td class="px-4 py-3">
                    <Tag
                      :value="formula.is_active ? 'Active' : 'Inactive'"
                      :severity="formula.is_active ? 'success' : 'secondary'"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>

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

    <!-- Dialog création formule -->
    <Dialog
      v-model:visible="showCreateFormulaDialog"
      header="Nouvelle formule"
      modal
      :style="{ width: '28rem' }"
    >
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Label</label
          >
          <InputText
            v-model="formulaForm.label"
            class="w-full"
            placeholder="ex: 6 mois — 100 étudiants"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Durée (mois)</label
          >
          <InputNumber
            v-model="formulaForm.duration_months"
            class="w-full"
            :min="1"
            :max="24"
          />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-700 mb-1 block"
            >Plafond d'étudiants</label
          >
          <InputNumber
            v-model="formulaForm.max_students"
            class="w-full"
            :min="1"
          />
        </div>
        <Message v-if="formulaFormError" severity="error" :closable="false">{{
          formulaFormError
        }}</Message>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="showCreateFormulaDialog = false" />
        <Button
          label="Créer"
          :loading="creatingFormula"
          @click="handleCreateFormula"
        />
      </template>
    </Dialog>

    <!-- Dialog gestion licence -->
    <Dialog
      v-model:visible="showLicenseDialog"
      header="Gérer la licence"
      modal
      :style="{ width: '30rem' }"
    >
      <div v-if="selectedCenter" class="space-y-4">
        <div class="p-3 bg-gray-50 rounded-lg">
          <p class="font-semibold text-gray-900">{{ selectedCenter.name }}</p>
        </div>

        <!-- Formulaire activation licence — masqué une fois activée avec succès -->
        <template v-if="!licenseSuccess">
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block"
              >Formule</label
            >
            <Select
              v-model="licenseForm.formula_id"
              :options="adminCenters.formulas"
              optionLabel="label"
              optionValue="id"
              placeholder="Choisir une formule"
              class="w-full"
            />
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block"
              >Mode de paiement</label
            >
            <Select
              v-model="licenseForm.payment_method"
              :options="paymentMethodOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Choisir un mode de paiement"
              class="w-full"
            />
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 mb-1 block"
              >Référence de paiement (optionnel)</label
            >
            <InputText
              v-model="licenseForm.payment_reference"
              class="w-full"
              placeholder="ex: VIR-2026-0042"
            />
          </div>

          <Message v-if="licenseFormError" severity="error" :closable="false">{{
            licenseFormError
          }}</Message>
        </template>

        <!-- Bloc création directeur — apparaît après activation réussie -->
        <template v-else>
          <Message severity="success" :closable="false">{{
            licenseSuccess
          }}</Message>

          <div class="border-t border-gray-100 pt-4 mt-2">
            <p class="text-sm font-semibold text-gray-700 mb-3">
              Créer le compte directeur
            </p>

            <div class="space-y-3">
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
                <InputText
                  v-model="directorForm.password"
                  type="password"
                  class="w-full"
                  placeholder="Min. 8 caractères"
                />
              </div>
            </div>

            <Message
              v-if="directorFormError"
              severity="error"
              :closable="false"
              class="mt-3"
              >{{ directorFormError }}</Message
            >
            <Message
              v-if="directorSuccess"
              severity="success"
              :closable="false"
              class="mt-3"
              >{{ directorSuccess }}</Message
            >
          </div>
        </template>
      </div>

      <template #footer>
        <Button label="Fermer" text @click="showLicenseDialog = false" />
        <Button
          v-if="!licenseSuccess"
          label="Activer la licence"
          :loading="activatingLicense"
          @click="handleActivateLicense"
        />
        <Button
          v-else-if="!directorSuccess"
          label="Créer le directeur"
          icon="pi pi-user-plus"
          :loading="creatingDirector"
          @click="handleCreateDirector"
        />
      </template>
    </Dialog>

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
          <InputText
            v-model="directorForm.password"
            type="password"
            class="w-full"
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
            placeholder="ex: Rechargement négocié le 09/07 — 20000 FCFA"
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
definePageMeta({ layout: "admin", middleware: "admin" });

import type { CenterResponse } from "#shared/api";
import { PaymentMethod } from "#shared/api";

const adminCenters = useAdminCentersStore();
const adminUsers = useAdminUsersStore();
const toast = useToast();

const loadingCenters = ref(true);
const loadingFormulas = ref(true);
const showDirectorDialog = ref(false);

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

function openDirectorDialog(center: CenterResponse) {
  selectedCenter.value = center;
  directorForm.value = { full_name: "", email: "", phone: "", password: "" };
  directorFormError.value = null;
  directorSuccess.value = null;
  showDirectorDialog.value = true;
}

// ── Création directeur ──
const creatingDirector = ref(false);
const directorFormError = ref<string | null>(null);
const directorSuccess = ref<string | null>(null);
const directorForm = ref({ full_name: "", email: "", phone: "", password: "" });

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
    toast.add({ severity: "success", summary: "Centre créé", life: 3000 });
  } else {
    centerFormError.value = result.error || "Erreur lors de la création.";
  }
}

// ── Création formule ──
const showCreateFormulaDialog = ref(false);
const creatingFormula = ref(false);
const formulaFormError = ref<string | null>(null);
const formulaForm = ref({ label: "", duration_months: 6, max_students: 100 });

function openCreateFormulaDialog() {
  formulaForm.value = { label: "", duration_months: 6, max_students: 100 };
  formulaFormError.value = null;
  showCreateFormulaDialog.value = true;
}

async function handleCreateFormula() {
  if (
    !formulaForm.value.label.trim() ||
    !formulaForm.value.duration_months ||
    !formulaForm.value.max_students
  ) {
    formulaFormError.value = "Tous les champs sont requis.";
    return;
  }
  creatingFormula.value = true;
  formulaFormError.value = null;
  const result = await adminCenters.createFormula({
    label: formulaForm.value.label.trim(),
    duration_months: formulaForm.value.duration_months,
    max_students: formulaForm.value.max_students,
  });
  creatingFormula.value = false;
  if (result.success) {
    showCreateFormulaDialog.value = false;
    toast.add({ severity: "success", summary: "Formule créée", life: 3000 });
  } else {
    formulaFormError.value = result.error || "Erreur lors de la création.";
  }
}

// ── Gestion licence ──
const showLicenseDialog = ref(false);
const activatingLicense = ref(false);
const licenseFormError = ref<string | null>(null);
const licenseSuccess = ref<string | null>(null);
const selectedCenter = ref<CenterResponse | null>(null);
const licenseForm = ref({
  formula_id: "",
  payment_method: "" as PaymentMethod | "",
  payment_reference: "",
});

const paymentMethodOptions = [
  { label: "Mobile Money", value: PaymentMethod.MOBILE_MONEY },
  { label: "Virement bancaire", value: PaymentMethod.BANK_TRANSFER },
];

function openLicenseDialog(center: CenterResponse) {
  selectedCenter.value = center;
  licenseForm.value = {
    formula_id: "",
    payment_method: "",
    payment_reference: "",
  };
  licenseFormError.value = null;
  licenseSuccess.value = null;
  directorForm.value = { full_name: "", email: "", phone: "", password: "" };
  directorFormError.value = null;
  directorSuccess.value = null;
  showLicenseDialog.value = true;
}

async function handleActivateLicense() {
  if (
    !selectedCenter.value ||
    !licenseForm.value.formula_id ||
    !licenseForm.value.payment_method
  ) {
    licenseFormError.value = "Formule et mode de paiement sont requis.";
    return;
  }
  activatingLicense.value = true;
  licenseFormError.value = null;
  const result = await adminCenters.activateLicense(selectedCenter.value.id, {
    formula_id: licenseForm.value.formula_id,
    payment_method: licenseForm.value.payment_method as PaymentMethod,
    payment_reference: licenseForm.value.payment_reference.trim() || null,
  });
  activatingLicense.value = false;
  if (result.success) {
    licenseSuccess.value =
      "Licence activée avec succès. Vous pouvez maintenant créer le compte directeur.";
  } else {
    licenseFormError.value = result.error || "Erreur lors de l'activation.";
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

  loadingFormulas.value = true;
  await adminCenters.fetchFormulas();
  loadingFormulas.value = false;
});
</script>
