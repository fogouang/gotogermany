<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-bold text-(--text-primary)">
          Paiements manuels
        </h1>
        <p class="text-sm text-(--text-tertiary) mt-0.5">
          Accorder un accès exam ou des crédits IA hors plateforme (virement,
          espèces, etc.)
        </p>
      </div>
      <div class="flex gap-2">
        <Button
          label="Accès exam"
          icon="pi pi-book"
          outlined
          @click="openExamForm"
        />
        <Button
          label="Crédits IA"
          icon="pi pi-bolt"
          class="bg-gradient-primary border-none font-bold"
          @click="openCreditForm"
        />
      </div>
    </div>

    <Message severity="warn" :closable="false" class="mb-6">
      Utilisez cette page pour activer manuellement un accès après paiement reçu
      hors plateforme.
    </Message>

    <!-- ═══ DIALOG — Accès exam ═══════════════════════════════ -->
    <Dialog
      v-model:visible="examFormVisible"
      header="Accorder un accès exam"
      modal
      :style="{ width: '520px' }"
      :draggable="false"
    >
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-(--text-secondary)"
            >Utilisateur</label
          >
          <Select
            v-model="examForm.user_id"
            :options="userOptions"
            option-label="label"
            option-value="value"
            placeholder="Sélectionner un utilisateur"
            filter
            fluid
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-(--text-secondary)"
            >Exam</label
          >
          <Select
            v-model="examForm.exam_id"
            :options="examOptions"
            option-label="label"
            option-value="value"
            placeholder="Sélectionner un exam"
            fluid
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-(--text-secondary)"
            >Plan (durée)</label
          >
          <Select
            v-model="examForm.plan_id"
            :options="planOptions"
            option-label="label"
            option-value="value"
            placeholder="Sélectionner un plan"
            fluid
          />
          <div
            v-if="selectedPlan"
            class="bg-(--bg-ground) rounded-lg p-3 flex items-center justify-between"
          >
            <div>
              <p class="text-sm font-semibold text-(--text-primary)">
                {{ selectedPlan.name }}
              </p>
              <p class="text-xs text-(--text-tertiary)">
                {{ selectedPlan.duration_days }} jours d'accès
              </p>
            </div>
            <p class="text-lg font-bold text-primary-600">
              {{ selectedPlan.price.toLocaleString("fr-FR") }} FCFA
            </p>
          </div>
        </div>

        <div
          v-if="examForm.user_id && examForm.exam_id && examForm.plan_id"
          class="bg-green-50 border border-green-200 rounded-xl p-4"
        >
          <p class="text-sm font-semibold text-green-800 mb-1">Récapitulatif</p>
          <p class="text-sm text-green-700">
            L'accès sera activé immédiatement pour
            <strong>{{ selectedPlan?.duration_days }} jours</strong>.
          </p>
        </div>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="examFormVisible = false" />
        <Button
          label="Activer l'accès"
          icon="pi pi-check"
          :loading="savingExam"
          :disabled="
            !examForm.user_id || !examForm.exam_id || !examForm.plan_id
          "
          class="bg-gradient-primary border-none font-bold"
          @click="onActivateExam"
        />
      </template>
    </Dialog>

    <!-- ═══ DIALOG — Crédits IA ════════════════════════════════ -->
    <Dialog
      v-model:visible="creditFormVisible"
      header="Accorder des crédits IA"
      modal
      :style="{ width: '480px' }"
      :draggable="false"
    >
      <div class="flex flex-col gap-4 pt-2">
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-(--text-secondary)"
            >Utilisateur</label
          >
          <Select
            v-model="creditForm.user_id"
            :options="userOptions"
            option-label="label"
            option-value="value"
            placeholder="Sélectionner un utilisateur"
            filter
            fluid
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-(--text-secondary)"
            >Nombre de crédits</label
          >
          <InputNumber
            v-model="creditForm.credits"
            :min="1"
            :max="500"
            fluid
            show-buttons
          />
          <small class="text-(--text-tertiary)">
            Valeur :
            {{
              (creditForm.credits * pricePerCredit).toLocaleString("fr-FR")
            }}
            FCFA ({{ pricePerCredit }} FCFA / crédit)
          </small>
        </div>

        <div
          v-if="creditForm.user_id && creditForm.credits"
          class="bg-blue-50 border border-blue-200 rounded-xl p-4"
        >
          <p class="text-sm font-semibold text-blue-800 mb-1">Récapitulatif</p>
          <p class="text-sm text-blue-700">
            <strong>{{ creditForm.credits }} crédits IA</strong> seront ajoutés
            immédiatement au solde de l'utilisateur.
          </p>
        </div>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="creditFormVisible = false" />
        <Button
          label="Accorder les crédits"
          icon="pi pi-bolt"
          :loading="savingCredit"
          :disabled="!creditForm.user_id || !creditForm.credits"
          class="bg-gradient-primary border-none font-bold"
          @click="onGrantCredits"
        />
      </template>
    </Dialog>

    <!-- ═══ HISTORIQUE — Accès exam ════════════════════════════ -->
    <div
      class="bg-(--bg-card) border border-(--border-color) rounded-xl p-5 mb-5"
    >
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-base font-bold text-(--text-primary)">
          Accès exam récents
        </h2>
        <Button
          icon="pi pi-refresh"
          text
          rounded
          :loading="loadingAccess"
          @click="fetchRecentAccess"
        />
      </div>
      <div v-if="loadingAccess" class="flex justify-center py-8">
        <i class="pi pi-spin pi-spinner text-2xl text-(--text-tertiary)" />
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="access in recentAccess"
          :key="access.id"
          class="flex items-center justify-between p-4 bg-(--bg-ground) rounded-xl"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-9 h-9 rounded-full bg-green-50 flex items-center justify-center"
            >
              <i class="pi pi-book text-green-600 text-sm" />
            </div>
            <div>
              <p class="text-sm font-semibold text-(--text-primary)">
                {{ access.user_email }}
              </p>
              <p class="text-xs text-(--text-tertiary)">
                {{ access.exam_name }} · Expire le
                {{ formatDate(access.expires_at) }}
              </p>
            </div>
          </div>
          <Tag
            :value="access.is_active ? 'Actif' : 'Expiré'"
            :severity="access.is_active ? 'success' : 'secondary'"
          />
        </div>
        <p
          v-if="!recentAccess.length"
          class="text-sm text-(--text-tertiary) text-center py-4"
        >
          Aucun accès accordé récemment.
        </p>
      </div>
    </div>

    <!-- ═══ HISTORIQUE — Crédits IA ════════════════════════════ -->
    <div class="bg-(--bg-card) border border-(--border-color) rounded-xl p-5">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-base font-bold text-(--text-primary)">
          Crédits IA accordés
        </h2>
        <Button
          icon="pi pi-refresh"
          text
          rounded
          :loading="loadingCredits"
          @click="fetchCreditGrants"
        />
      </div>
      <div v-if="loadingCredits" class="flex justify-center py-8">
        <i class="pi pi-spin pi-spinner text-2xl text-(--text-tertiary)" />
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="grant in creditGrants"
          :key="grant.id"
          class="flex items-center justify-between p-4 bg-(--bg-ground) rounded-xl"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center"
            >
              <i class="pi pi-bolt text-blue-600 text-sm" />
            </div>
            <div>
              <p class="text-sm font-semibold text-(--text-primary)">
                {{ grant.user_email }}
              </p>
              <p class="text-xs text-(--text-tertiary)">
                {{ grant.credits_purchased }} crédits ·
                {{ formatDate(grant.created_at) }}
              </p>
            </div>
          </div>
          <Tag
            :value="statusLabel(grant.payment_status)"
            :severity="statusSeverity(grant.payment_status)"
          />
        </div>
        <p
          v-if="!creditGrants.length"
          class="text-sm text-(--text-tertiary) text-center py-4"
        >
          Aucun crédit accordé manuellement.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "admin" });

const toast = useToast();

// ── Stores & composables ───────────────────────────────────────
const adminUsersStore = useAdminUsersStore();
const { loadCatalog, catalog } = useExams();
const { loadPlans, activePlans } = usePlans();
const { adminGrantExamAccess } = usePayments();
const {
  adminGrantCredits,
  pricePerCredit,
  statusLabel,
  statusSeverity,
  formatDate,
} = useAiCredits();

// ── State ──────────────────────────────────────────────────────
const examFormVisible = ref(false);
const creditFormVisible = ref(false);
const savingExam = ref(false);
const savingCredit = ref(false);
const loadingAccess = ref(false);
const loadingCredits = ref(false);
const recentAccess = ref<any[]>([]);
const creditGrants = ref<any[]>([]);

// ── Options selects ────────────────────────────────────────────
const userOptions = computed(() =>
  adminUsersStore.users.map((u) => ({
    label: `${u.full_name} (${u.email})`,
    value: u.id,
  })),
);

const examOptions = computed(() =>
  catalog.value.map((e) => ({
    label: e.name,
    value: e.id,
  })),
);

const planOptions = computed(() =>
  activePlans.value.map((p) => ({
    label: `${p.name} — ${p.price.toLocaleString("fr-FR")} FCFA (${p.duration_days}j)`,
    value: p.id,
  })),
);

const selectedPlan = computed(
  () => activePlans.value.find((p) => p.id === examForm.plan_id) ?? null,
);

// ── Formulaires ────────────────────────────────────────────────
const examForm = reactive({ user_id: "", exam_id: "", plan_id: "" });
const creditForm = reactive({ user_id: "", credits: 10 });

// ── Init ───────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    adminUsersStore.fetchUsers(),
    loadCatalog(),
    loadPlans(),
    fetchRecentAccess(),
    fetchCreditGrants(),
  ]);
});

// ── Fetch historiques (ExamAccess + CreditGrants MANUAL) ───────
async function fetchRecentAccess() {
  loadingAccess.value = true;
  try {
    const { PaymentsService } = await import("#shared/api");
    const res =
      await PaymentsService.listManualPaymentsApiV1PaymentsAdminManualListGet();
    recentAccess.value = res ?? [];
  } catch {
    recentAccess.value = [];
  } finally {
    loadingAccess.value = false;
  }
}

async function fetchCreditGrants() {
  loadingCredits.value = true;
  try {
    const { AiCreditsService } = await import("#shared/api");
    const res =
      await AiCreditsService.adminHistoryApiV1AiCreditsAdminHistoryGet();
    creditGrants.value = res.data ?? [];
  } catch {
    creditGrants.value = [];
  } finally {
    loadingCredits.value = false;
  }
}

// ── Open/close ─────────────────────────────────────────────────
function openExamForm() {
  Object.assign(examForm, { user_id: "", exam_id: "", plan_id: "" });
  examFormVisible.value = true;
}
function openCreditForm() {
  Object.assign(creditForm, { user_id: "", credits: 10 });
  creditFormVisible.value = true;
}

// ── Actions ────────────────────────────────────────────────────
async function onActivateExam() {
  savingExam.value = true;
  try {
    const res = await adminGrantExamAccess({
      user_id: examForm.user_id,
      exam_id: examForm.exam_id,
      plan_id: examForm.plan_id,
    });
    if (!res.success) throw new Error(res.message);
    toast.add({
      severity: "success",
      summary: "Accès activé avec succès",
      life: 4000,
    });
    examFormVisible.value = false;
    await fetchRecentAccess();
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: err?.message ?? "Impossible d'activer l'accès",
      life: 4000,
    });
  } finally {
    savingExam.value = false;
  }
}

async function onGrantCredits() {
  savingCredit.value = true;
  try {
    const res = await adminGrantCredits({
      user_id: creditForm.user_id,
      credits: creditForm.credits,
    });
    if (!res.success) throw new Error(res.message);
    toast.add({
      severity: "success",
      summary: `${creditForm.credits} crédits accordés`,
      life: 4000,
    });
    creditFormVisible.value = false;
    await fetchCreditGrants();
  } catch (err: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: err?.message ?? "Impossible d'accorder les crédits",
      life: 4000,
    });
  } finally {
    savingCredit.value = false;
  }
}

useHead({ title: "Paiements manuels | Admin GoToGermany" });
</script>
