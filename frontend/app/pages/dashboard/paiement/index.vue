<template>
  <div class="min-h-screen bg-gray-50 py-10 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="mb-8 text-center">
        <button
          class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-4 mx-auto transition-colors"
          @click="navigateTo('/dashboard/examens')"
        >
          <i class="pi pi-arrow-left"></i> {{ t("payment.back") }}
        </button>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ t("payment.title") }}
        </h1>
        <p class="text-gray-500 text-sm mt-1">{{ t("payment.subtitle") }}</p>
      </div>

      <!-- Loading -->
      <div v-if="loadingData" class="flex justify-center py-20">
        <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
      </div>

      <!-- Niveau introuvable -->
      <div
        v-else-if="!targetLevel"
        class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-gray-100"
      >
        <div
          class="w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mb-4"
        >
          <i class="pi pi-exclamation-triangle text-2xl text-red-400"></i>
        </div>
        <p class="font-semibold text-gray-700 mb-4">{{ t("payment.level") }}</p>
        <Button
          label="Retour aux examens"
          outlined
          size="small"
          @click="navigateTo('/dashboard/examens')"
        />
      </div>

      <!-- Contenu 2 colonnes -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <!-- ── Colonne gauche : Récapitulatif ── -->
        <div
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-7 space-y-6"
        >
          <!-- Niveau cible -->
          <div class="flex items-center gap-4 pb-6 border-b border-gray-100">
            <div
              :class="[
                'w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-sm shrink-0',
                levelBg,
              ]"
            >
              {{ targetLevel.cefr_code }}
            </div>
            <div>
              <p class="font-bold text-gray-900">{{ targetExamName }}</p>
              <p class="text-sm text-gray-500">
                Niveau {{ targetLevel.cefr_code }} -
                <span class="text-teal-600 font-medium"
                  >{{ targetLevel.subject_count }} {{ t("payment.subjet") }}</span
                >
              </p>
            </div>
          </div>

          <!-- Sélecteur plan -->
          <div>
            <p
              class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3"
            >
              {{ t("payment.choose_duration") }}
            </p>
            <div class="space-y-2">
              <button
                v-for="plan in activePlans"
                :key="plan.id"
                :class="[
                  'w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all text-left',
                  selectedPlan?.id === plan.id
                    ? 'border-teal-600 bg-teal-50'
                    : 'border-gray-200 hover:border-teal-300',
                ]"
                @click="selectedPlan = plan"
              >
                <div class="flex items-center gap-3">
                  <div
                    :class="[
                      'w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors',
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
                    {{ t("payment.per_day") }}
                  </p>
                </div>
              </button>
            </div>
          </div>

          <!-- Ce qui est inclus -->
          <div class="pb-6 border-b border-gray-100">
            <p
              class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-3"
            >
              {{ t("payment.included") }}
            </p>
            <ul class="space-y-2">
              <li
                v-for="key in featureKeys"
                :key="key"
                class="flex items-center gap-2 text-sm text-gray-700"
              >
                <i class="pi pi-check-circle text-teal-500 text-xs"></i>
                {{ t(`payment.features.${key}`) }}
              </li>
            </ul>
          </div>

          <!-- Code promo -->
          <div>
            <p
              class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2"
            >
              {{ t("payment.promo_code") }}
            </p>
            <div v-if="!promoApplied" class="flex gap-2">
              <InputText
                v-model="promoCode"
                :placeholder="t('payment.promo_placeholder')"
                class="flex-1 text-sm"
                @keyup.enter="applyPromo"
              />
              <Button
                :label="t('payment.apply')"
                size="small"
                outlined
                :disabled="!promoCode"
                @click="applyPromo"
              />
            </div>
            <div
              v-else
              class="flex items-center justify-between text-sm bg-green-50 border border-green-200 rounded-xl px-4 py-2.5"
            >
              <span class="text-green-700 flex items-center gap-1.5">
                <i class="pi pi-check-circle"></i>
                Code <strong>{{ promoCode.toUpperCase() }}</strong> appliqué
              </span>
              <button
                class="text-xs text-gray-400 hover:text-red-500 transition-colors"
                @click="removePromo"
              >
                {{ t("payment.remove") }}
              </button>
            </div>
          </div>
        </div>

        <!-- ── Colonne droite : Paiement ── -->
        <div
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-7 space-y-6"
        >
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wide">
            {{ t("payment.payment_method") }}
          </p>

          <!-- Méthodes -->
          <div class="space-y-2">
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
                    {{ t("payment.mobile_money") }}
                  </p>
                  <p class="text-xs text-gray-400">
                    {{ t("payment.mobile_desc") }}
                  </p>
                </div>
              </div>
            </button>
          </div>

          <!-- Formulaire Mobile Money -->
          <div class="space-y-4">
            <!-- Opérateur -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">{{
                t("payment.operator")
              }}</label>
              <div class="grid grid-cols-2 gap-3">
                <button
                  v-for="op in operators"
                  :key="op.value"
                  :class="[
                    'flex items-center gap-2.5 p-3.5 rounded-xl border-2 transition-all',
                    form.operator === op.value
                      ? 'border-teal-600 bg-teal-50'
                      : 'border-gray-200 hover:border-gray-300',
                  ]"
                  @click="form.operator = op.value"
                >
                  <div
                    :class="[
                      'w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0',
                      op.value === 'MTN' ? 'bg-yellow-400' : 'bg-orange-500',
                    ]"
                  >
                    {{ op.value === "MTN" ? "M" : "O" }}
                  </div>
                  <span class="text-sm font-semibold text-gray-900">{{
                    op.label
                  }}</span>
                </button>
              </div>
            </div>

            <!-- Numéro -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{
                t("payment.phone")
              }}</label>
              <InputText
                v-model="form.phone_number"
                class="w-full"
                placeholder="Ex: 690000000"
                :disabled="loading"
              />
              <p class="text-xs text-gray-400 mt-1.5">
                <i class="pi pi-info-circle mr-1"></i
                >{{ t("payment.phone_hint") }}
              </p>
            </div>
          </div>

          <!-- Erreur -->
          <Message v-if="error" severity="error" :closable="false">{{
            error
          }}</Message>

          <!-- Total + CTA -->
          <div>
            <Divider />
            <div class="flex items-center justify-between mb-5">
              <span class="font-bold text-gray-900">{{
                t("payment.total")
              }}</span>
              <span class="font-bold text-xl text-gray-900">
                {{
                  selectedPlan
                    ? selectedPlan.price.toLocaleString("fr-FR")
                    : "-"
                }}
                FCFA
              </span>
            </div>

            <Button
              :label="t('payment.pay_now')"
              icon="pi pi-lock"
              class="w-full"
              size="large"
              :loading="loading"
              :disabled="!canPay"
              @click="handlePay"
            />
          </div>

          <!-- Logos sécurité -->
          <div class="flex items-center justify-center gap-3 flex-wrap pt-2">
            <img
              :src="img('orange.jpg')"
              alt="Orange Money"
              class="h-7 rounded-md object-contain opacity-70"
            />
            <img
              :src="img('momo.jpg')"
              alt="MTN MoMo"
              class="h-7 rounded-md object-contain opacity-70"
            />
            <img
              :src="img('visa.png')"
              alt="Visa"
              class="h-5 object-contain opacity-50"
            />
            <img
              :src="img('master.png')"
              alt="Mastercard"
              class="h-5 object-contain opacity-50"
            />
          </div>
          <p class="text-xs text-center text-gray-400">
            <i class="pi pi-shield mr-1"></i>{{ t("payment.secure") }}
          </p>
        </div>
      </div>
    </div>

    <!-- ── Dialog confirmation pawaPay ── -->
    <Dialog
      v-model:visible="confirmDialog"
      :header="t('payment.confirm.title')"
      :modal="true"
      :closable="false"
      :style="{ width: '90vw', maxWidth: '460px' }"
    >
      <div class="space-y-5 mt-2 text-center">
        <!-- Icône statut -->
        <div
          :class="[
            'w-16 h-16 rounded-2xl flex items-center justify-center mx-auto',
            isCompleted
              ? 'bg-green-50'
              : isFailed
                ? 'bg-red-50'
                : 'bg-amber-50',
          ]"
        >
          <ProgressSpinner
            v-if="isPending"
            style="width: 32px; height: 32px"
            strokeWidth="3"
          />
          <i
            v-else-if="isCompleted"
            class="pi pi-check-circle text-3xl text-green-500"
          ></i>
          <i
            v-else-if="isFailed"
            class="pi pi-times-circle text-3xl text-red-500"
          ></i>
        </div>

        <!-- Message -->
        <div>
          <p
            :class="[
              'font-bold text-lg',
              isCompleted
                ? 'text-green-700'
                : isFailed
                  ? 'text-red-600'
                  : 'text-amber-700',
            ]"
          >
            {{
              isPending
                ? t("payment.confirm.pending_title")
                : isCompleted
                  ? t("payment.confirm.success_title")
                  : t("payment.confirm.failed_title")
            }}
          </p>
          <p class="text-sm text-gray-500 mt-1">
            {{
              isPending
                ? t("payment.confirm.pending_desc")
                : isCompleted
                  ? t("payment.confirm.success_desc")
                  : t("payment.confirm.failed_desc")
            }}
          </p>
        </div>

        <!-- Info paiement en attente -->
        <div
          v-if="isPending"
          class="bg-amber-50 border border-amber-100 rounded-xl p-4 text-left space-y-2"
        >
          <div class="flex items-start gap-2">
            <i class="pi pi-mobile text-amber-500 mt-0.5"></i>
            <p class="text-sm text-amber-800">
             {{ t("payment.message") }}
              <strong>{{ form.phone_number }}</strong
              >. {{ t("payment.pin") }} {{ form.operator }} Mobile Money.
            </p>
          </div>
          <div class="flex items-center gap-2 pt-1">
            <i class="pi pi-clock text-amber-400 text-xs"></i>
            <p class="text-xs text-amber-600">
              {{ t("payment.polling") }}
            </p>
          </div>
        </div>

        <!-- Référence -->
        <div class="bg-gray-50 rounded-xl px-4 py-3 text-left">
          <p class="text-xs text-gray-400 mb-0.5">{{ t("payment.ref") }}</p>
          <p class="text-sm font-mono font-semibold text-gray-700">
            {{ currentPayment?.transaction_reference }}
          </p>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-2 justify-end">
          <Button
            v-if="isFailed"
            :label="t('payment.confirm.retry')"
            severity="secondary"
            outlined
            @click="closeConfirm"
          />
          <Button
            v-if="isCompleted"
            :label="t('payment.confirm.go_to_exams')"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="goToExams"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const route = useRoute();
const examsStore = useExamsStore();
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

const img = (name: string) => `/images/${name}`;
const featureKeys = [
  "unlimited",
  "subjects",
  "audio",
  "corrections",
  "progress",
];
const loadingData = ref(true);
const selectedPlan = ref<PlanResponse | null>(null);
const paymentMethod = ref<"mobile">("mobile");
const confirmDialog = ref(false);
const promoCode = ref("");
const promoApplied = ref(false);

const form = ref({ operator: "", phone_number: "" });

// ── Trouver le level + exam depuis level_id ───────────────────
const levelId = computed(() => route.query.level_id as string);

const targetLevel = computed(() => {
  for (const exam of examsStore.catalog) {
    const level = exam.levels?.find((l) => l.id === levelId.value);
    if (level) return level;
  }
  return null;
});

const targetExamName = computed(() => {
  for (const exam of examsStore.catalog) {
    if (exam.levels?.some((l) => l.id === levelId.value)) return exam.name;
  }
  return "";
});

const levelBg = computed(
  () =>
    ({
      B1: "bg-blue-100 text-blue-700",
      B2: "bg-indigo-100 text-indigo-700",
      C1: "bg-purple-100 text-purple-700",
    })[targetLevel.value?.cefr_code ?? ""] ?? "bg-gray-100 text-gray-700",
);

// ── Init ─────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    loadPlans(),
    examsStore.catalog.length === 0
      ? examsStore.fetchCatalog()
      : Promise.resolve(),
  ]);
  // Plan présélectionné depuis query ou plan médian
  const planId = route.query.plan_id as string;
  if (planId) {
    selectedPlan.value = activePlans.value.find((p) => p.id === planId) ?? null;
  }
  if (!selectedPlan.value && activePlans.value.length > 0) {
    selectedPlan.value =
      activePlans.value[Math.floor(activePlans.value.length / 2)] ?? null;
  }
  loadingData.value = false;
});

// ── Validation ───────────────────────────────────────────────
const canPay = computed(
  () =>
    !!selectedPlan.value &&
    !!targetLevel.value &&
    !!form.value.operator &&
    !!form.value.phone_number,
);

// ── Payer ────────────────────────────────────────────────────
const handlePay = async () => {
  if (!canPay.value || !selectedPlan.value || !targetLevel.value) return;
  resetPayment();
  confirmDialog.value = true;

  const res = await pay({
    level_id: targetLevel.value.id,
    plan_id: selectedPlan.value.id,
    operator: form.value.operator,
    phone_number: form.value.phone_number,
    promo_code: promoApplied.value ? promoCode.value : null,
  });

  if (!res.success) {
    confirmDialog.value = false;
  }
};

const closeConfirm = () => {
  stopPolling();
  confirmDialog.value = false;
};

const goToExams = () => {
  stopPolling();
  confirmDialog.value = false;
  navigateTo("/dashboard/examens");
};

const applyPromo = () => {
  if (promoCode.value.trim()) promoApplied.value = true;
};
const removePromo = () => {
  promoApplied.value = false;
  promoCode.value = "";
};

onUnmounted(() => stopPolling());
</script>
