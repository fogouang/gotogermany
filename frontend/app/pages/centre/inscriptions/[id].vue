<!-- pages/centre/inscriptions/[id].vue -->
<template>
  <div class="space-y-6">
    <Button
      icon="pi pi-arrow-left"
      label="Retour aux inscriptions"
      text
      size="small"
      @click="navigateTo('/centre/inscriptions')"
    />

    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <template v-else-if="cursus">
      <!-- En-tête -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-lg font-bold text-gray-900">{{ studentName }}</h2>
        <p class="text-sm text-gray-400 mt-0.5">
          Parcours {{ cursus.start_level }} → {{ cursus.target_level }}
        </p>
      </div>

      <!-- Ajout d'un niveau -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="text-sm font-semibold text-gray-700 mb-4">
          Ajouter un niveau
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <Select
            v-model="newLevel.level"
            :options="levelOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Niveau"
          />
          <InputNumber
            v-model="newLevel.inscription_fee_amount"
            placeholder="Frais d'inscription"
            :min="0"
          />
          <InputNumber
            v-model="newLevel.formation_fee_amount"
            placeholder="Frais de formation"
            :min="0"
          />
          <Button
            label="Ajouter"
            icon="pi pi-plus"
            :loading="addingLevel"
            @click="handleAddLevel"
          />
        </div>
        <Message
          v-if="addLevelError"
          severity="error"
          :closable="false"
          class="mt-3"
        >
          {{ addLevelError }}
        </Message>
      </div>

      <!-- Niveaux existants -->
      <div
        v-for="enrollment in cursus.level_enrollments"
        :key="enrollment.id"
        class="bg-white rounded-xl border border-gray-200 p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-semibold text-gray-900">
              Niveau {{ enrollment.level }}
            </h3>
            <Tag
              :value="enrollmentStatusLabel(enrollment.status)"
              :severity="enrollmentStatusSeverity(enrollment.status)"
              class="mt-1"
            />
          </div>
        </div>

        <div
          v-if="getBalance(enrollment.id)"
          class="grid grid-cols-2 gap-4 mb-4 text-sm"
        >
          <div>
            <p class="text-gray-400">Frais d'inscription</p>
            <p class="font-semibold">
              {{ getBalance(enrollment.id)!.inscription_paid.toLocaleString() }}
              /
              {{ getBalance(enrollment.id)!.inscription_due.toLocaleString() }}
              FCFA
            </p>
          </div>
          <div>
            <p class="text-gray-400">Frais de formation</p>
            <p class="font-semibold">
              {{ getBalance(enrollment.id)!.formation_paid.toLocaleString() }} /
              {{ getBalance(enrollment.id)!.formation_due.toLocaleString() }}
              FCFA
            </p>
          </div>
        </div>

        <div class="flex gap-2 items-end border-t border-gray-100 pt-4">
          <Select
            v-model="getPaymentForm(enrollment.id).payment_type"
            :options="paymentTypeOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Type"
            class="w-40"
          />
          <InputNumber
            v-model="getPaymentForm(enrollment.id).amount"
            placeholder="Montant"
            :min="1"
            :max="
              getRemainingFor(
                enrollment.id,
                getPaymentForm(enrollment.id).payment_type,
              ) ?? undefined
            "
            class="flex-1"
          />
          <Button
            label="Encaisser"
            icon="pi pi-check"
            :loading="paying === enrollment.id"
            @click="handleRecordPayment(enrollment.id)"
          />
        </div>
        <p
          v-if="getPaymentForm(enrollment.id).payment_type"
          class="text-xs text-gray-400 mt-2"
        >
          Reste à payer :
          {{
            (
              getRemainingFor(
                enrollment.id,
                getPaymentForm(enrollment.id).payment_type,
              ) ?? 0
            ).toLocaleString()
          }}
          FCFA
        </p>

        <!-- Historique des paiements, avec reçu téléchargeable à tout moment -->
        <div
          v-if="getPayments(enrollment.id).length > 0"
          class="border-t border-gray-100 mt-4 pt-4 space-y-2"
        >
          <p class="text-xs font-semibold text-gray-500 mb-1">
            Paiements enregistrés
          </p>
          <div
            v-for="payment in getPayments(enrollment.id)"
            :key="payment.id"
            class="flex items-center justify-between text-sm"
          >
            <span class="text-gray-600">
              {{
                payment.payment_type === "inscription"
                  ? "Inscription"
                  : "Formation"
              }}
              — {{ payment.amount.toLocaleString() }} FCFA
              <span class="text-gray-400 text-xs ml-1">
                ({{ formatDate(payment.paid_at) }})
              </span>
            </span>
            <Button
              label="Reçu"
              icon="pi pi-file-pdf"
              text
              size="small"
              :loading="generatingInvoice === payment.id"
              @click="handleGenerateInvoice(enrollment.id, payment.id)"
            />
          </div>
        </div>
        <Message
          v-if="paymentErrors[enrollment.id]"
          severity="error"
          :closable="false"
          class="mt-3"
        >
          {{ paymentErrors[enrollment.id] }}
        </Message>
      </div>
    </template>

    <div v-else class="text-center py-12 text-gray-400">
      Cursus introuvable.
    </div>
  </div>
</template>

<script setup lang="ts">
import type {
  CursusLevel,
  FormationPaymentType,
  CursusResponse,
  BalanceSummaryResponse,
  app__modules__enrollments__schemas__PaymentResponse as FormationPaymentResponse,
} from "#shared/api";

definePageMeta({
  layout: "centre",
  middleware: "centre-staff",
});

const route = useRoute();
const centerStaffStore = useCenterStaffStore();
const enrollmentsStore = useEnrollmentsStore();
const authStore = useAuthStore();
const toast = useToast();

const loading = ref(true);
const addingLevel = ref(false);
const addLevelError = ref<string | null>(null);
const paying = ref<string | null>(null);
const paymentErrors = ref<Record<string, string>>({});
const balances = ref<Record<string, BalanceSummaryResponse>>({});

const generatingInvoice = ref<string | null>(null);
const payments = ref<Record<string, FormationPaymentResponse[]>>({});

const cursus = computed(
  () =>
    enrollmentsStore.cursusList.find((c) => c.id === route.params.id) as
      | CursusResponse
      | undefined,
);

const studentName = computed(() => {
  const student = centerStaffStore.students.find(
    (s) => s.id === cursus.value?.student_id,
  );
  return student?.full_name || "Élève inconnu";
});

const levelOptions = [
  { label: "A1", value: "A1" },
  { label: "A2", value: "A2" },
  { label: "B1", value: "B1" },
  { label: "B2", value: "B2" },
];

const paymentTypeOptions = [
  { label: "Inscription", value: "inscription" },
  { label: "Formation", value: "formation" },
];

const newLevel = ref({
  level: "" as CursusLevel | "",
  inscription_fee_amount: null as number | null,
  formation_fee_amount: null as number | null,
});

const paymentForms = ref<
  Record<
    string,
    { payment_type: FormationPaymentType | ""; amount: number | null }
  >
>({});

function enrollmentStatusLabel(status: string) {
  const labels: Record<string, string> = {
    pending_inscription: "Inscription à régler",
    active: "En cours",
    completed: "Terminé",
    abandoned: "Abandonné",
  };
  return labels[status] || status;
}

function enrollmentStatusSeverity(status: string) {
  const severities: Record<string, string> = {
    pending_inscription: "warning",
    active: "info",
    completed: "success",
    abandoned: "danger",
  };
  return severities[status] || "secondary";
}

function getPaymentForm(enrollmentId: string) {
  if (!paymentForms.value[enrollmentId]) {
    paymentForms.value[enrollmentId] = { payment_type: "", amount: null };
  }
  return paymentForms.value[enrollmentId]!;
}

function getBalance(enrollmentId: string) {
  return balances.value[enrollmentId];
}

// Reste à payer pour un type précis (inscription ou formation) sur un niveau —
// utilisé pour plafonner la saisie et empêcher tout dépassement.
function getRemainingFor(
  enrollmentId: string,
  paymentType: FormationPaymentType | "",
): number | null {
  const balance = getBalance(enrollmentId);
  if (!balance || !paymentType) return null;
  return paymentType === "inscription"
    ? balance.inscription_remaining
    : balance.formation_remaining;
}

function getPayments(enrollmentId: string) {
  return payments.value[enrollmentId] ?? [];
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

async function loadPayments(enrollmentId: string) {
  const result = await enrollmentsStore.fetchPayments(enrollmentId);
  if (result.success && result.payments) {
    payments.value[enrollmentId] = result.payments;
  }
}

async function loadBalances() {
  if (!cursus.value) return;
  for (const enrollment of cursus.value.level_enrollments ?? []) {
    const result = await enrollmentsStore.fetchBalance(enrollment.id);
    if (result.success && result.balance) {
      balances.value[enrollment.id] = result.balance;
    }
    if (!paymentForms.value[enrollment.id]) {
      paymentForms.value[enrollment.id] = { payment_type: "", amount: null };
    }
    await loadPayments(enrollment.id);
  }
}

async function handleGenerateInvoice(enrollmentId: string, paymentId: string) {
  generatingInvoice.value = paymentId;
  const result = await enrollmentsStore.generateInvoice(paymentId);
  generatingInvoice.value = null;

  if (result.success && result.invoiceUrl) {
    window.open(result.invoiceUrl, "_blank");
  } else {
    paymentErrors.value[enrollmentId] =
      result.error || "Erreur génération du reçu.";
  }
}

async function handleAddLevel() {
  if (
    !newLevel.value.level ||
    !newLevel.value.inscription_fee_amount ||
    !newLevel.value.formation_fee_amount
  ) {
    addLevelError.value = "Tous les champs sont obligatoires.";
    return;
  }
  if (!cursus.value) return;

  addingLevel.value = true;
  addLevelError.value = null;

  const result = await enrollmentsStore.createLevelEnrollment(cursus.value.id, {
    level: newLevel.value.level as CursusLevel,
    inscription_fee_amount: newLevel.value.inscription_fee_amount,
    formation_fee_amount: newLevel.value.formation_fee_amount,
  });

  addingLevel.value = false;

  if (result.success) {
    toast.add({ severity: "success", summary: "Niveau ajouté", life: 3000 });
    newLevel.value = {
      level: "",
      inscription_fee_amount: null,
      formation_fee_amount: null,
    };
    await refreshCursus();
  } else {
    addLevelError.value = result.error || "Erreur lors de l'ajout.";
  }
}

async function handleRecordPayment(enrollmentId: string) {
  const form = paymentForms.value[enrollmentId];
  if (!form || !form.payment_type || !form.amount) {
    paymentErrors.value[enrollmentId] = "Type et montant obligatoires.";
    return;
  }

  // Garde-fou frontend — la vraie règle est appliquée côté backend, mais on
  // évite un aller-retour réseau inutile pour une erreur évidente.
  const remaining = getRemainingFor(enrollmentId, form.payment_type);
  if (remaining !== null && form.amount > remaining) {
    paymentErrors.value[enrollmentId] =
      `Le montant dépasse le reste à payer (${remaining.toLocaleString()} FCFA).`;
    return;
  }

  paying.value = enrollmentId;
  paymentErrors.value[enrollmentId] = "";

  const result = await enrollmentsStore.recordPayment(enrollmentId, {
    payment_type: form.payment_type as FormationPaymentType,
    amount: form.amount,
  });

  paying.value = null;

  if (result.success && result.payment) {
    toast.add({
      severity: "success",
      summary: "Paiement enregistré",
      life: 3000,
    });
    paymentForms.value[enrollmentId] = { payment_type: "", amount: null };
    await refreshCursus();
  } else {
    paymentErrors.value[enrollmentId] =
      result.error || "Erreur lors de l'encaissement.";
  }
}

async function refreshCursus() {
  await enrollmentsStore.fetchCursusList();
  await loadBalances();
}

onMounted(async () => {
  loading.value = true;

  if (centerStaffStore.students.length === 0) {
    if (authStore.isDirector) {
      await centerStaffStore.fetchStudentsByCenter();
    } else {
      await centerStaffStore.fetchStudentsByBranch();
    }
  }

  if (enrollmentsStore.cursusList.length === 0) {
    await enrollmentsStore.fetchCursusList();
  }

  await loadBalances();

  loading.value = false;
});
</script>
