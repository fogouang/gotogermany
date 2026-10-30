<!-- pages/dashboard/paiement.vue -->
<template>
  <div class="space-y-5 pb-10">
    <NuxtLink
      :to="localePath(backPath)"
      class="inline-flex items-center gap-2 text-sm text-muted hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("payment.back") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loadingData" class="grid gap-5 lg:grid-cols-5">
      <div class="h-96 animate-pulse rounded-card bg-card-2 lg:col-span-3" />
      <div class="h-96 animate-pulse rounded-card bg-card-2 lg:col-span-2" />
    </div>

    <!-- ── Niveau introuvable ── -->
    <div
      v-else-if="!targetLevel"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-14 text-center"
    >
      <span class="flex size-14 items-center justify-center rounded-full bg-red-500/10 text-red-600">
        <i class="pi pi-exclamation-triangle text-xl" />
      </span>
      <p class="font-medium text-ink">{{ t("payment.level") }}</p>
      <Button :label="t('payment.back')" outlined size="small" @click="navigateTo(localePath(backPath))" />
    </div>

    <div v-else class="grid items-start gap-5 lg:grid-cols-5">
      <!-- ══════════ Gauche : niveau, plan, inclus ══════════ -->
      <div class="space-y-5 lg:col-span-3">
        <!-- Niveau visé -->
        <section class="flex items-center gap-4 rounded-card border border-line bg-card p-5 shadow-soft">
          <span class="flex size-12 shrink-0 items-center justify-center rounded-leaf text-sm font-bold" :class="levelBg">
            {{ targetLevel.cefr_code }}
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold text-ink">{{ targetExamName }}</p>
            <p class="text-sm text-muted">
              {{ targetLevel.cefr_code }} ·
              <span class="font-medium text-primary">{{ targetLevel.subject_count }} {{ t("payment.subjet") }}</span>
            </p>
          </div>

          <!-- Start Deutsch sans niveau précisé : choix A1 / A2 -->
          <div
            v-if="isStartDeutsch && !sdLevelFromQuery"
            class="flex shrink-0 gap-1 rounded-leaf border border-line bg-card-2 p-1"
          >
            <button
              v-for="lvl in SD_LEVELS"
              :key="lvl"
              type="button"
              class="rounded-leaf px-3 py-1.5 text-sm font-semibold transition-colors"
              :class="sdLevel === lvl ? 'bg-card text-primary shadow-soft' : 'text-muted hover:text-ink'"
              :disabled="loading"
              @click="sdLevel = lvl"
            >
              {{ lvl }}
            </button>
          </div>
        </section>

        <!-- Durée -->
        <section class="space-y-3 rounded-card border border-line bg-card p-5 shadow-soft">
          <h2 class="text-sm font-semibold text-ink">{{ t("payment.choose_duration") }}</h2>
          <div class="grid gap-2 sm:grid-cols-2">
            <button
              v-for="plan in activePlans"
              :key="plan.id"
              type="button"
              class="flex items-center justify-between gap-3 rounded-leaf border-2 p-4 text-left transition-colors"
              :class="selectedPlan?.id === plan.id ? 'border-primary bg-primary/10' : 'border-line bg-card hover:border-primary/30'"
              @click="selectedPlan = plan"
            >
              <span class="flex min-w-0 items-center gap-3">
                <span
                  class="flex size-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors"
                  :class="selectedPlan?.id === plan.id ? 'border-primary bg-primary' : 'border-line'"
                >
                  <i v-if="selectedPlan?.id === plan.id" class="pi pi-check text-[10px] text-white" />
                </span>
                <span class="min-w-0">
                  <span class="block truncate text-sm font-semibold text-ink">{{ plan.name }}</span>
                  <span class="block text-xs text-muted">{{ formatDuration(plan.duration_days) }}</span>
                </span>
              </span>
              <span class="shrink-0 text-right">
                <span class="block font-bold text-ink">{{ fcfa(plan.price) }}</span>
                <span class="block text-xs text-muted">
                  {{ num(Math.round(plan.price / plan.duration_days)) }} {{ t("payment.per_day") }}
                </span>
              </span>
            </button>
          </div>
        </section>

        <!-- Inclus -->
        <section class="space-y-3 rounded-card border border-line bg-card p-5 shadow-soft">
          <h2 class="text-sm font-semibold text-ink">{{ t("payment.included") }}</h2>
          <ul class="grid gap-2 sm:grid-cols-2">
            <li v-for="key in featureKeys" :key="key" class="flex items-center gap-2 text-sm text-ink">
              <i class="pi pi-check-circle text-xs text-primary" />
              {{ t(`payment.features.${key}`) }}
            </li>
          </ul>
        </section>
      </div>

      <!-- ══════════ Droite : paiement ══════════ -->
      <aside class="space-y-5 rounded-card border border-line bg-card p-5 shadow-soft lg:sticky lg:top-0 lg:col-span-2">
        <div class="flex items-center gap-3">
          <img :src="img('orange.jpg')" alt="Orange Money" class="h-8 rounded-md object-contain" />
          <img :src="img('momo.jpg')" alt="MTN MoMo" class="h-8 rounded-md object-contain" />
          <div>
            <p class="text-sm font-semibold text-ink">{{ t("payment.mobile_money") }}</p>
            <p class="text-xs text-muted">{{ t("payment.mobile_desc") }}</p>
          </div>
        </div>

        <!-- Opérateur -->
        <div>
          <label class="mb-2 block text-sm font-medium text-ink">{{ t("payment.operator") }}</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="op in operators"
              :key="op.value"
              type="button"
              class="flex items-center gap-2.5 rounded-leaf border-2 p-3 text-left transition-colors"
              :class="form.operator === op.value ? 'border-primary bg-primary/10' : 'border-line bg-card hover:border-primary/30'"
              :disabled="loading"
              @click="form.operator = op.value"
            >
              <img
                :src="img(op.value === 'MTN' ? 'momo.jpg' : 'orange.jpg')"
                :alt="op.label"
                class="size-8 shrink-0 rounded-md object-contain"
              />
              <span class="text-sm font-medium text-ink">{{ op.label }}</span>
            </button>
          </div>
        </div>

        <!-- Numéro -->
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("payment.phone") }}</label>
          <InputText
            v-model="form.phone_number"
            inputmode="numeric"
            placeholder="690000000"
            fluid
            :disabled="loading"
            :invalid="phoneTouched && !phoneValid"
            @blur="phoneTouched = true"
          />
          <p class="mt-1.5 text-xs" :class="phoneTouched && !phoneValid ? 'text-red-600' : 'text-faint'">
            <i class="pi pi-info-circle mr-1" />
            {{ phoneTouched && !phoneValid ? t("ai_credits.phone_invalid") : t("payment.phone_hint") }}
          </p>
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

        <!-- Total + CTA -->
        <div class="space-y-4 border-t border-line pt-4">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-muted">{{ t("payment.total") }}</span>
            <span class="text-2xl font-extrabold text-ink">{{ selectedPlan ? fcfa(selectedPlan.price) : "-" }}</span>
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
          <p class="text-center text-xs text-faint">
            <i class="pi pi-shield mr-1" />{{ t("payment.secure") }}
          </p>
        </div>
      </aside>
    </div>

    <!-- ══════════ Dialogue de confirmation ══════════ -->
    <Dialog
      v-model:visible="confirmDialog"
      :header="t('payment.confirm.title')"
      modal
      :closable="false"
      :style="{ width: '30rem', maxWidth: '95vw' }"
    >
      <div class="space-y-5 text-center">
        <span
          class="mx-auto flex size-16 items-center justify-center rounded-full"
          :class="isCompleted ? 'bg-emerald-500/10 text-emerald-600' : isFailed ? 'bg-red-500/10 text-red-600' : 'bg-amber-500/15 text-amber-600'"
        >
          <i v-if="isPending" class="pi pi-spin pi-spinner text-2xl" />
          <i v-else-if="isCompleted" class="pi pi-check-circle text-3xl" />
          <i v-else class="pi pi-times-circle text-3xl" />
        </span>

        <div>
          <p class="text-lg font-bold text-ink">
            {{
              isPending
                ? t("payment.confirm.pending_title")
                : isCompleted
                  ? t("payment.confirm.success_title")
                  : t("payment.confirm.failed_title")
            }}
          </p>
          <p class="mt-1 text-sm text-muted">
            {{
              isPending
                ? t("payment.confirm.pending_desc")
                : isCompleted
                  ? t("payment.confirm.success_desc")
                  : t("payment.confirm.failed_desc")
            }}
          </p>
        </div>

        <div v-if="isPending" class="space-y-2 rounded-leaf bg-card-2 p-4 text-left text-sm">
          <p class="flex items-start gap-2 text-ink">
            <i class="pi pi-mobile mt-0.5 text-amber-600" />
            <span>{{ t("payment.message").trim() }} : <strong>{{ normalizedPhone }}</strong></span>
          </p>
          <p class="pl-6 text-muted">{{ t("payment.pin") }} ({{ operatorLabel }})</p>
          <p class="flex items-center gap-2 pt-1 text-xs text-faint">
            <i class="pi pi-clock text-[10px]" />
            {{ t("payment.polling") }}
          </p>
        </div>

        <div v-if="currentPayment?.transaction_reference" class="rounded-leaf bg-card-2 px-4 py-3 text-left">
          <p class="text-xs text-muted">{{ t("payment.ref") }}</p>
          <p class="break-all font-mono text-sm font-semibold text-ink">{{ currentPayment.transaction_reference }}</p>
        </div>
      </div>

      <template #footer>
        <Button v-if="isPending" :label="t('invoices.close')" text severity="secondary" @click="closeConfirm" />
        <Button v-if="isFailed" :label="t('payment.confirm.retry')" severity="secondary" outlined @click="closeConfirm" />
        <Button
          v-if="isCompleted"
          :label="t('payment.confirm.go_to_exams')"
          icon="pi pi-arrow-right"
          iconPos="right"
          @click="goToExams"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Zugang" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const examsStore = useExamsStore();
const startDeutschStore = useStartDeutschSessionStore();
const authStore = useAuthStore();
const learningTrack = useLearningTrack();
const { activePlans, loadPlans, formatDuration } = usePlans();
const { pay, operators, currentPayment, isPending, isCompleted, isFailed, loading, error, stopPolling, resetPayment } =
  usePayments();

const img = (name: string) => `/images/${name}`;
const featureKeys = ["unlimited", "subjects", "audio", "corrections", "progress"];

const loadingData = ref(true);
const selectedPlan = ref<PlanResponse | null>(null);
const confirmDialog = ref(false);
const form = ref({ operator: "", phone_number: "" });
const phoneTouched = ref(false);

// ── Format ──
const intlLocale = computed(() => ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ?? "en-GB");
const num = (n: number) => n.toLocaleString(intlLocale.value);
const fcfa = (n: number) => `${num(n)} FCFA`;

// ── Niveau visé ──
// Examen B : ?level_id=... ; Start Deutsch : ?sd_level=A1 ou A2.
// Sans l'un ni l'autre (venu de la page Tarifs), on suit le parcours de l'élève.
const levelId = computed(() => route.query.level_id as string | undefined);

type SdLevel = "A1" | "A2";
const SD_LEVELS: SdLevel[] = ["A1", "A2"];
const asSdLevel = (v: unknown): SdLevel | null => (v === "A1" || v === "A2" ? v : null);

const sdLevelFromQuery = asSdLevel(route.query.sd_level);
const isStartDeutsch = computed(
  () => !!sdLevelFromQuery || (!levelId.value && learningTrack.isStartDeutsch.value),
);
const sdLevel = ref<SdLevel>(
  sdLevelFromQuery ??
    asSdLevel((authStore.user as { target_sd_level?: string } | null)?.target_sd_level) ??
    "A1",
);

const targetLevel = computed(() => {
  if (isStartDeutsch.value) {
    return {
      cefr_code: sdLevel.value,
      subject_count: startDeutschStore.subjects.filter((s) => s.level === sdLevel.value).length,
    };
  }
  for (const exam of examsStore.catalog) {
    const level = exam.levels?.find((l) => l.id === levelId.value);
    if (level) return level;
  }
  return null;
});

const targetExamName = computed(() => {
  if (isStartDeutsch.value) return `Start Deutsch ${sdLevel.value}`;
  for (const exam of examsStore.catalog) {
    if (exam.levels?.some((l) => l.id === levelId.value)) return exam.name;
  }
  return "";
});

// Retour et suite selon le parcours
const backPath = computed(() =>
  isStartDeutsch.value ? "/dashboard/start-deutsch" : "/dashboard/examens",
);

const levelBg = computed(
  () =>
    ({
      B1: "bg-sky-500/10 text-sky-600",
      A1: "bg-emerald-500/10 text-emerald-600",
      A2: "bg-teal-500/10 text-teal-600",
      B2: "bg-indigo-500/10 text-indigo-600",
      C1: "bg-violet-500/10 text-violet-600",
    })[targetLevel.value?.cefr_code ?? ""] ?? "bg-primary/10 text-primary",
);

// ── Téléphone ──
const normalizedPhone = computed(() => form.value.phone_number.replace(/\s+/g, "").replace(/^(\+?237)/, ""));
const phoneValid = computed(() => /^[69]\d{8}$/.test(normalizedPhone.value));
const operatorLabel = computed(() => operators.find((o) => o.value === form.value.operator)?.label ?? form.value.operator);

// ── Init ──
onMounted(async () => {
  await Promise.all([
    loadPlans(),
    examsStore.catalog.length === 0 ? examsStore.fetchCatalog() : Promise.resolve(),
    // Nombre de sujets affiché pour Start Deutsch
    isStartDeutsch.value && startDeutschStore.subjects.length === 0
      ? startDeutschStore.fetchSubjects()
      : Promise.resolve(),
  ]);
  const planId = route.query.plan_id as string;
  if (planId) selectedPlan.value = activePlans.value.find((p) => p.id === planId) ?? null;
  if (!selectedPlan.value && activePlans.value.length > 0) {
    selectedPlan.value = activePlans.value[Math.floor(activePlans.value.length / 2)] ?? null;
  }
  loadingData.value = false;
});

// ── Validation ──
const canPay = computed(() => !!selectedPlan.value && !!targetLevel.value && !!form.value.operator && phoneValid.value);

// ── Payer ──
const handlePay = async () => {
  phoneTouched.value = true;
  if (!canPay.value || !selectedPlan.value || !targetLevel.value) return;
  resetPayment();
  confirmDialog.value = true;

  const res = await pay({
    // Niveau d'examen OU niveau Start Deutsch
    level_id: isStartDeutsch.value ? null : levelId.value ?? null,
    sd_level: isStartDeutsch.value ? sdLevel.value : null,
    plan_id: selectedPlan.value.id,
    operator: form.value.operator,
    phone_number: normalizedPhone.value,
  });

  if (!res.success) confirmDialog.value = false;
};

const closeConfirm = () => {
  stopPolling();
  confirmDialog.value = false;
};

const goToExams = () => {
  stopPolling();
  confirmDialog.value = false;
  navigateTo(localePath(backPath.value));
};

onUnmounted(() => stopPolling());
</script>