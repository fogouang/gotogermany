<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Crédits IA</h1>
      <p class="text-sm text-gray-500">Gérez vos crédits de correction IA</p>
    </div>

    <!-- Solde actuel -->
    <div
      class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 text-center"
    >
      <div
        class="w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-4"
      >
        <i class="pi pi-sparkles text-3xl text-amber-500"></i>
      </div>
      <p class="text-4xl font-extrabold text-gray-900 mb-1">
        {{ authStore.aiCredits }}
      </p>
      <p class="text-gray-500 text-sm">crédit(s) disponible(s)</p>
    </div>

    <!-- Acheter -->
    <div
      class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-5"
    >
      <div>
        <h2 class="font-semibold text-gray-900">Acheter des crédits</h2>
        <p class="text-sm text-gray-500 mt-0.5">
          {{ pricing?.price_per_credit ?? 50 }} FCFA par crédit. 1 crédit = 1
          correction complète.
        </p>
      </div>

      <!-- Step 1 : quantité + opérateur -->
      <template v-if="step === 1">
        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-gray-700"
            >Nombre de crédits</label
          >
          <InputNumber
            v-model="credits"
            :min="5"
            :max="500"
            fluid
            show-buttons
            button-layout="horizontal"
            :step="1"
          >
            <template #decrementbuttonicon><i class="pi pi-minus" /></template>
            <template #incrementbuttonicon><i class="pi pi-plus" /></template>
          </InputNumber>
        </div>

        <div class="flex gap-2 flex-wrap">
          <button
            v-for="qty in [5, 10, 20, 50]"
            :key="qty"
            class="px-3 py-1.5 rounded-lg text-sm font-semibold border transition-colors"
            :class="
              credits === qty
                ? 'bg-[#076152] text-white border-transparent'
                : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-teal-300'
            "
            @click="credits = qty"
          >
            {{ qty }} crédits
          </button>
        </div>

        <div
          class="bg-gray-50 rounded-xl p-4 flex items-center justify-between"
        >
          <div>
            <p class="text-sm text-gray-500">Total à payer</p>
            <p class="text-2xl font-extrabold text-[#076152]">
              {{ totalAmount.toLocaleString("fr-FR") }} FCFA
            </p>
          </div>
          <p class="text-xs text-gray-400">
            {{ credits }} crédit{{ credits > 1 ? "s" : "" }}
          </p>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-gray-700"
            >Opérateur Mobile Money</label
          >
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="op in operators"
              :key="op.value"
              class="flex items-center gap-2 p-3 rounded-xl border-2 transition-all text-left"
              :class="
                operator === op.value
                  ? 'border-teal-500 bg-teal-50'
                  : 'border-gray-200 bg-white hover:border-teal-300'
              "
              @click="operator = op.value"
            >
              <img
                :src="op.logo"
                :alt="op.label"
                class="h-7 w-7 object-contain rounded"
              />
              <div>
                <p
                  class="text-sm font-semibold"
                  :class="
                    operator === op.value ? 'text-teal-700' : 'text-gray-800'
                  "
                >
                  {{ op.label }}
                </p>
                <p class="text-xs text-gray-400">{{ op.desc }}</p>
              </div>
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-sm font-semibold text-gray-700"
            >Numéro Mobile Money</label
          >
          <InputText v-model="phone" placeholder="6XXXXXXXX" fluid />
        </div>

        <Message v-if="errorMessage" severity="error" :closable="false">{{
          errorMessage
        }}</Message>

        <Button
          label="Payer"
          icon="pi pi-arrow-right"
          icon-pos="right"
          :loading="purchasing"
          :disabled="!canProceed"
          class="w-full"
          style="background-color: #076152; border: none"
          @click="purchase"
        />
      </template>

      <!-- Step 2 : confirmation (polling) -->
      <template v-else-if="step === 2">
        <div
          class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center"
        >
          <i class="pi pi-mobile text-3xl text-blue-500 mb-2 block" />
          <p class="font-bold text-blue-800 mb-1">
            Confirmez sur votre téléphone
          </p>
          <p class="text-sm text-blue-700">
            Une demande a été envoyée au {{ phone }} pour
            <strong
              >{{
                purchaseResult?.total_amount.toLocaleString("fr-FR")
              }}
              FCFA</strong
            >.
          </p>
        </div>
        <div
          class="flex items-center justify-center gap-2 text-sm text-gray-400 py-2"
        >
          <ProgressSpinner style="width: 18px; height: 18px" stroke-width="6" />
          En attente de confirmation...
        </div>
      </template>

      <!-- Step 3 : succès -->
      <template v-else-if="step === 3">
        <div class="flex flex-col items-center gap-3 py-4 text-center">
          <div
            class="w-16 h-16 rounded-full bg-green-50 flex items-center justify-center"
          >
            <i class="pi pi-check-circle text-green-500 text-3xl" />
          </div>
          <p class="font-bold text-lg text-gray-900">Crédits ajoutés !</p>
          <p class="text-sm text-gray-500">
            {{ purchaseResult?.credits }} crédits ont été ajoutés à votre
            compte.
          </p>
          <Button
            label="Fermer"
            icon="pi pi-check"
            severity="success"
            @click="resetState"
          />
        </div>
      </template>

      <!-- Step erreur -->
      <template v-else-if="step === 'error'">
        <div class="flex flex-col items-center gap-3 py-4 text-center">
          <div
            class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center"
          >
            <i class="pi pi-times-circle text-red-500 text-2xl" />
          </div>
          <p class="font-bold text-gray-900">Erreur de paiement</p>
          <p class="text-sm text-gray-500">{{ errorMessage }}</p>
          <Button
            label="Réessayer"
            icon="pi pi-refresh"
            outlined
            @click="step = 1"
          />
        </div>
      </template>

      <!-- WhatsApp en secours -->
      <div class="pt-3 border-t border-gray-100">
        <p class="text-xs text-gray-400 mb-2">
          Problème avec le paiement mobile money ?
        </p>

        <a
          href="https://wa.me/237670886288?text=Bonjour, je souhaite acheter des crédits IA sur GoToGermany."
          target="_blank"
          class="inline-flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-xl text-sm font-semibold hover:bg-green-600 transition-colors"
        >
          <i class="pi pi-whatsapp"></i>
          Nous contacter via WhatsApp
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

import { AiCreditsService, PaymentsService } from "#shared/api";

const authStore = useAuthStore();

const PRICE_PER_CREDIT = 50;

const pricing = ref<{ price_per_credit: number } | null>(null);
const credits = ref(10);
const operator = ref<"MTN" | "ORANGE">("MTN");
const phone = ref("");
const purchasing = ref(false);
const errorMessage = ref("");
const step = ref<1 | 2 | 3 | "error">(1);
const purchaseResult = ref<{
  payment_id: string;
  invoice_number: string;
  credits: number;
  total_amount: number;
} | null>(null);

let pollInterval: ReturnType<typeof setInterval> | null = null;

const operators: {
  value: "MTN" | "ORANGE";
  label: string;
  desc: string;
  logo: string;
}[] = [
  {
    value: "MTN",
    label: "MTN MoMo",
    desc: "Mobile Money MTN",
    logo: "/images/momo.jpg",
  },
  {
    value: "ORANGE",
    label: "Orange Money",
    desc: "Mobile Money Orange",
    logo: "/images/orange.jpg",
  },
];

const totalAmount = computed(
  () => (pricing.value?.price_per_credit ?? PRICE_PER_CREDIT) * credits.value,
);

const canProceed = computed(() => {
  if (!credits.value || credits.value < 5) return false;
  if (!phone.value.trim()) return false;
  return true;
});

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

function resetState() {
  stopPolling();
  step.value = 1;
  purchaseResult.value = null;
  errorMessage.value = "";
  phone.value = "";
  credits.value = 10;
  operator.value = "MTN";
}

onUnmounted(() => stopPolling());

async function fetchPricing() {
  try {
    const res: any =
      await AiCreditsService.getPricingApiV1AiCreditsPricingGet();
    pricing.value = res.data ?? res ?? null;
  } catch {
    // silencieux — fallback sur PRICE_PER_CREDIT
  }
}

async function purchase() {
  purchasing.value = true;
  errorMessage.value = "";
  try {
    const res: any =
      await AiCreditsService.purchaseCreditsApiV1AiCreditsPurchasePost({
        credits: credits.value,
        phone_number: phone.value,
        operator: operator.value,
      });
    purchaseResult.value = res.data ?? res ?? null;
    step.value = 2;
    startPolling();
  } catch (err: any) {
    errorMessage.value =
      err?.body?.detail ?? "Impossible d'initier le paiement.";
    step.value = "error";
  } finally {
    purchasing.value = false;
  }
}

function startPolling() {
  const paymentId = purchaseResult.value?.payment_id;
  if (!paymentId) return;

  let attempts = 0;
  const maxAttempts = 40;

  pollInterval = setInterval(async () => {
    attempts++;
    try {
      const res: any =
        await PaymentsService.getPaymentApiV1PaymentsPaymentIdGet(paymentId);
      const status = res.payment_status;

      if (status === "COMPLETED") {
        stopPolling();
        await authStore.fetchUser();
        step.value = 3;
      } else if (status === "FAILED") {
        stopPolling();
        errorMessage.value = "Le paiement a échoué ou a été annulé.";
        step.value = "error";
      }
    } catch {
      // erreur réseau transitoire, on continue à poller
    }

    if (attempts >= maxAttempts && step.value === 2) {
      stopPolling();
      errorMessage.value =
        "Délai dépassé. Si le paiement a été confirmé, vérifiez votre solde dans quelques instants.";
      step.value = "error";
    }
  }, 3000);
}

onMounted(() => {
  fetchPricing();
});
</script>
