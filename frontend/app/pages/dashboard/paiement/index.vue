<template>
  <div class="min-h-screen bg-gray-50 py-10 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="mb-8 text-center">
        <button
          @click="navigateTo('/dashboard/examens')"
          class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-4 mx-auto"
        >
          <i class="pi pi-arrow-left"></i> Retour aux examens
        </button>
        <h1 class="text-3xl font-bold text-gray-900">Finaliser votre accès</h1>
        <p class="text-gray-500 text-sm mt-1">
          Accédez à tous les examens GoToGermany
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loadingData" class="flex justify-center py-20">
        <ProgressSpinner style="width: 50px; height: 50px" />
      </div>

      <!-- Contenu 2 colonnes -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <!-- ── Colonne gauche : Récapitulatif ─────────── -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-7">
          <!-- Exam cible -->
          <div
            v-if="targetExam"
            class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-100"
          >
            <div
              class="w-10 h-10 bg-teal-600 rounded-lg flex items-center justify-center shrink-0"
            >
              <i class="pi pi-book text-white"></i>
            </div>
            <div>
              <p class="font-semibold text-gray-900">{{ targetExam.name }}</p>
              <p class="text-xs text-gray-400">{{ targetExam.provider }}</p>
            </div>
          </div>

          <!-- Sélecteur plan -->
          <div class="mb-6">
            <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
              Choisissez votre durée
            </p>
            <div class="space-y-2">
              <button
                v-for="plan in activePlans"
                :key="plan.id"
                :class="[
                  'w-full flex items-center justify-between p-3.5 rounded-xl border-2 transition-all text-left',
                  selectedPlan?.id === plan.id
                    ? 'border-teal-600 bg-teal-50'
                    : 'border-gray-200 hover:border-teal-300',
                ]"
                @click="selectedPlan = plan"
              >
                <div class="flex items-center gap-3">
                  <div
                    :class="[
                      'w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0',
                      selectedPlan?.id === plan.id
                        ? 'border-teal-600 bg-teal-600'
                        : 'border-gray-300',
                    ]"
                  >
                    <i
                      v-if="selectedPlan?.id === plan.id"
                      class="pi pi-check text-white text-xs"
                    ></i>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">
                      {{ plan.name }}
                    </p>
                    <p class="text-xs text-gray-400">
                      {{ formatDuration(plan.duration_days) }}
                    </p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="font-bold text-gray-900">
                    {{ plan.price.toLocaleString("fr-FR") }} FCFA
                  </p>
                  <p class="text-xs text-gray-400">
                    {{
                      Math.round(
                        plan.price / plan.duration_days,
                      ).toLocaleString("fr-FR")
                    }}
                    FCFA/j
                  </p>
                </div>
              </button>
            </div>
          </div>

          <!-- Ce qui est inclus -->
          <div class="mb-6 pb-6 border-b border-gray-100">
            <p class="text-xs font-semibold text-gray-500 uppercase mb-3">
              Inclus dans votre accès
            </p>
            <ul class="space-y-2">
              <li
                v-for="feature in features"
                :key="feature"
                class="flex items-center gap-2 text-sm text-gray-700"
              >
                <i class="pi pi-check text-teal-500 text-xs"></i>
                {{ feature }}
              </li>
            </ul>
          </div>

          <!-- Code promo -->
          <div>
            <p class="text-xs font-semibold text-gray-500 uppercase mb-2">
              Code partenaire (optionnel)
            </p>
            <div v-if="!promoApplied" class="flex gap-2">
              <InputText
                v-model="promoCode"
                placeholder="PARTNER2024"
                class="flex-1 text-sm"
                @keyup.enter="applyPromo"
              />
              <Button
                label="Appliquer"
                size="small"
                outlined
                :disabled="!promoCode"
                @click="applyPromo"
              />
            </div>
            <div
              v-else
              class="flex items-center justify-between text-sm bg-green-50 border border-green-200 rounded-lg px-3 py-2"
            >
              <span class="text-green-700 flex items-center gap-1">
                <i class="pi pi-check-circle"></i> Code
                <strong>{{ promoCode.toUpperCase() }}</strong>
              </span>
              <button
                class="text-xs text-gray-400 hover:text-red-500"
                @click="removePromo"
              >
                Retirer
              </button>
            </div>
          </div>
        </div>

        <!-- ── Colonne droite : Paiement ──────────────── -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-7">
          <!-- Méthode de paiement -->
          <p class="text-xs font-semibold text-gray-500 uppercase mb-4">
            Méthode de paiement
          </p>

          <div class="space-y-2 mb-6">
            <button
              :class="[
                'w-full flex items-center gap-3 p-4 rounded-xl border-2 transition-all text-left',
                paymentMethod === 'mobile'
                  ? 'border-teal-600 bg-teal-50'
                  : 'border-gray-200 hover:border-gray-300',
              ]"
              @click="paymentMethod = 'mobile'"
            >
              <div
                :class="[
                  'w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0',
                  paymentMethod === 'mobile'
                    ? 'border-teal-600 bg-teal-600'
                    : 'border-gray-300',
                ]"
              >
                <i
                  v-if="paymentMethod === 'mobile'"
                  class="pi pi-check text-white text-xs"
                ></i>
              </div>
              <div class="flex items-center gap-3 flex-1">
                <div class="flex items-center gap-2">
                  <img
                    :src="img('orange.jpg')"
                    alt="Orange Money"
                    class="h-8 rounded-md object-contain"
                  />
                  <img
                    :src="img('momo.jpg')"
                    alt="MTN MoMo"
                    class="h-8 rounded-md object-contain"
                  />
                </div>
                <div>
                  <p class="font-semibold text-gray-900 text-sm">
                    Mobile Money
                  </p>
                  <p class="text-xs text-gray-400">Orange, MTN</p>
                </div>
              </div>
            </button>

            <button
              :class="[
                'w-full flex items-center gap-3 p-4 rounded-xl border-2 transition-all text-left',
                paymentMethod === 'card'
                  ? 'border-teal-600 bg-teal-50'
                  : 'border-gray-200 hover:border-gray-300',
              ]"
              @click="paymentMethod = 'card'"
            >
              <div
                :class="[
                  'w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0',
                  paymentMethod === 'card'
                    ? 'border-teal-600 bg-teal-600'
                    : 'border-gray-300',
                ]"
              >
                <i
                  v-if="paymentMethod === 'card'"
                  class="pi pi-check text-white text-xs"
                ></i>
              </div>
              <div class="flex items-center gap-3 flex-1">
                <div class="flex items-center gap-2">
                  <img
                    :src="img('visa.png')"
                    alt="Visa"
                    class="h-6 object-contain"
                  />
                  <img
                    :src="img('master.png')"
                    alt="Mastercard"
                    class="h-6 object-contain"
                  />
                  <img
                    :src="img('paypal.png')"
                    alt="PayPal"
                    class="h-5 object-contain opacity-60"
                  />
                </div>
                <div>
                  <p class="font-semibold text-gray-900 text-sm">
                    Carte bancaire
                  </p>
                  <p class="text-xs text-gray-400">Visa, Mastercard</p>
                </div>
              </div>
            </button>
          </div>

          <!-- Formulaire Mobile Money -->
          <div v-if="paymentMethod === 'mobile'" class="space-y-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Opérateur *</label
              >
              <div class="grid grid-cols-2 gap-3">
                <button
                  v-for="op in operators"
                  :key="op.value"
                  :class="[
                    'flex items-center gap-2 p-3 rounded-lg border-2 transition-all',
                    form.operator === op.value
                      ? 'border-teal-600 bg-teal-50'
                      : 'border-gray-200 hover:border-gray-300',
                  ]"
                  @click="form.operator = op.value"
                >
                  <div
                    :class="[
                      'w-7 h-7 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0',
                      op.value === 'MTN' ? 'bg-yellow-400' : 'bg-orange-500',
                    ]"
                  >
                    {{ op.value[0] }}
                  </div>
                  <span class="text-sm font-medium text-gray-900">{{
                    op.label
                  }}</span>
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >Numéro de téléphone *</label
              >
              <InputText
                v-model="form.phone_number"
                class="w-full"
                placeholder="Ex: 690000000"
                :disabled="loading"
              />
              <p class="text-xs text-gray-400 mt-1">
                Sans indicatif, commencez par 6 ou 9
              </p>
            </div>
          </div>

          <!-- Formulaire Carte bancaire -->
          <div v-else class="space-y-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >Numéro de carte *</label
              >
              <InputText
                v-model="cardForm.number"
                class="w-full"
                placeholder="1234 5678 9012 3456"
                :disabled="loading"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1"
                  >Expiration (MM/AA) *</label
                >
                <InputText
                  v-model="cardForm.expiry"
                  class="w-full"
                  placeholder="MM / AA"
                  :disabled="loading"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1"
                  >CVC *</label
                >
                <InputText
                  v-model="cardForm.cvc"
                  class="w-full"
                  placeholder="123"
                  :disabled="loading"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >Titulaire de la carte *</label
              >
              <InputText
                v-model="cardForm.holder"
                class="w-full"
                placeholder="Jean Dupont"
                :disabled="loading"
              />
            </div>
          </div>

          <Message
            v-if="error"
            severity="error"
            :closable="false"
            class="mb-4"
            >{{ error }}</Message
          >

          <!-- Total + bouton -->
          <Divider />
          <div class="flex items-center justify-between mb-4">
            <span class="font-bold text-gray-900">Total à payer</span>
            <span class="font-bold text-gray-900 text-lg">
              {{
                selectedPlan ? selectedPlan.price.toLocaleString("fr-FR") : "—"
              }}
              FCFA
            </span>
          </div>

          <Button
            label="Payer maintenant"
            icon="pi pi-lock"
            class="w-full bg-gradient-primary! border-transparent! py-3!"
            :loading="loading"
            :disabled="!canPay"
            @click="handlePay"
          />

          <!-- Logos sécurité -->
          <div class="flex items-center justify-center gap-3 mt-5 flex-wrap">
            <img
              :src="img('orange.jpg')"
              alt="Orange Money"
              class="h-8 rounded-md object-contain"
            />
            <img
              :src="img('momo.jpg')"
              alt="MTN MoMo"
              class="h-8 rounded-md object-contain"
            />
            <img :src="img('visa.png')" alt="Visa" class="h-6 object-contain" />
            <img
              :src="img('master.png')"
              alt="Mastercard"
              class="h-6 object-contain"
            />
            <img
              :src="img('paypal.png')"
              alt="PayPal"
              class="h-5 object-contain opacity-60"
            />
          </div>
          <p class="text-xs text-center text-gray-400 mt-2">
            <i class="pi pi-shield mr-1"></i>Paiement sécurisé My-CoolPay
          </p>
        </div>
      </div>
    </div>

    <!-- ─── Dialog USSD ──────────────────────────────── -->
    <Dialog
      v-model:visible="ussdDialog"
      header="Confirmez votre paiement"
      :modal="true"
      :closable="false"
      :style="{ width: '90vw', maxWidth: '440px' }"
    >
      <div class="space-y-4 mt-2 text-center">
        <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <i class="pi pi-mobile text-3xl text-amber-500 mb-2 block"></i>
          <p class="text-sm text-amber-800 font-medium">
            {{ currentPayment?.message }}
          </p>
        </div>
        <div
          v-if="currentPayment?.ussd_code"
          class="bg-gray-900 rounded-xl p-5"
        >
          <p class="text-xs text-gray-400 mb-2">
            Composez ce code sur votre téléphone
          </p>
          <p class="text-3xl font-mono font-bold text-white tracking-widest">
            {{ currentPayment.ussd_code }}
          </p>
        </div>
        <div class="flex items-center justify-center gap-3 py-2">
          <ProgressSpinner v-if="isPending" style="width: 24px; height: 24px" />
          <i
            v-else-if="isCompleted"
            class="pi pi-check-circle text-2xl text-green-500"
          ></i>
          <i
            v-else-if="isFailed"
            class="pi pi-times-circle text-2xl text-red-500"
          ></i>
          <span
            :class="[
              'text-sm font-medium',
              isCompleted
                ? 'text-green-600'
                : isFailed
                  ? 'text-red-600'
                  : 'text-gray-500',
            ]"
          >
            {{
              isPending
                ? "En attente de confirmation..."
                : isCompleted
                  ? "Paiement confirmé !"
                  : "Paiement échoué"
            }}
          </span>
        </div>
        <p class="text-xs text-gray-400">
          Réf. <strong>{{ currentPayment?.transaction_reference }}</strong>
        </p>
      </div>
      <template #footer>
        <Button
          v-if="isFailed"
          label="Réessayer"
          severity="secondary"
          @click="closeUssd"
        />
        <Button
          v-if="isCompleted"
          label="Accéder aux examens"
          icon="pi pi-arrow-right"
          iconPos="right"
          @click="goToExams"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse, ExamCatalogResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const route = useRoute();
const { activePlans, loadPlans, formatDuration } = usePlans();
const {
  pay,
  operators,
  currentPayment,
  isPending,
  isCompleted,
  isFailed,
  loading,
  error,
  stopPolling,
  resetPayment,
} = usePayments();
const examsStore = useExamsStore();

// ── Données ───────────────────────────────────────────
const loadingData = ref(true);
const targetExam = ref<ExamCatalogResponse | null>(null);
const selectedPlan = ref<PlanResponse | null>(null);
const img = (name: string) => `/images/${name}`;

const features = [
  "Accès illimité à tous les examens",
  "Tous les sujets disponibles",
  "Hörverstehen avec audio",
  "Corrections automatiques",
  "Suivi de progression",
];

onMounted(async () => {
  await Promise.all([loadPlans(), examsStore.fetchCatalog()]);
  const examId = route.query.exam_id as string;
  if (examId)
    targetExam.value = examsStore.catalog.find((e) => e.id === examId) ?? null;
  const planId = route.query.plan_id as string;
  if (planId)
    selectedPlan.value = activePlans.value.find((p) => p.id === planId) ?? null;
  // Auto-sélectionner le premier plan si aucun
  if (!selectedPlan.value && activePlans.value.length > 0) {
    selectedPlan.value =
      activePlans.value[Math.floor(activePlans.value.length / 2)] ?? null;
  }
  loadingData.value = false;
});

// ── Méthode de paiement ───────────────────────────────
const paymentMethod = ref<"mobile" | "card">("mobile");

// ── Formulaires ───────────────────────────────────────
const form = ref({ operator: "", phone_number: "" });
const cardForm = ref({ number: "", expiry: "", cvc: "", holder: "" });

// ── Code promo ────────────────────────────────────────
const promoCode = ref("");
const promoApplied = ref(false);
const applyPromo = () => {
  if (promoCode.value.trim()) promoApplied.value = true;
};
const removePromo = () => {
  promoApplied.value = false;
  promoCode.value = "";
};

// ── Validation ────────────────────────────────────────
const canPay = computed(() => {
  if (!selectedPlan.value || !targetExam.value) return false;
  if (paymentMethod.value === "mobile")
    return !!form.value.operator && !!form.value.phone_number;
  return (
    !!cardForm.value.number &&
    !!cardForm.value.expiry &&
    !!cardForm.value.cvc &&
    !!cardForm.value.holder
  );
});

// ── Paiement ──────────────────────────────────────────
const ussdDialog = ref(false);

const handlePay = async () => {
  if (!canPay.value || !selectedPlan.value || !targetExam.value) return;
  resetPayment();

  // Pour la carte — on passe le numéro comme phone (My-CoolPay gère)
  const phoneOrCard =
    paymentMethod.value === "mobile"
      ? form.value.phone_number
      : cardForm.value.number;
  const operator =
    paymentMethod.value === "mobile" ? form.value.operator : "CARD";

  const res = await pay({
    exam_id: targetExam.value.id,
    plan_id: selectedPlan.value.id,
    operator,
    phone_number: phoneOrCard,
    promo_code: promoApplied.value ? promoCode.value : null,
  });

  if (res.success) ussdDialog.value = true;
};

const closeUssd = () => {
  stopPolling();
  ussdDialog.value = false;
};
const goToExams = () => {
  stopPolling();
  ussdDialog.value = false;
  navigateTo("/dashboard/examens");
};
onUnmounted(() => stopPolling());
</script>
