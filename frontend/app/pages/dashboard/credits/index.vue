<template>
  <div class="space-y-5 pb-10">
    <p class="text-sm text-muted">{{ t("ai_credits.subtitle") }}</p>

    <div class="grid items-start gap-5 lg:grid-cols-3">
      <!-- ══════════ Colonne droite : solde ══════════ -->
      <aside class="space-y-4 lg:sticky lg:top-0 lg:order-last">
        <section class="relative isolate overflow-hidden rounded-card border border-line bg-card p-6 text-center shadow-soft">
          <span class="mx-auto mb-3 flex size-14 items-center justify-center rounded-full bg-amber-500/15 text-amber-600">
            <i class="pi pi-sparkles text-2xl" />
          </span>
          <div v-if="loading && !balance" class="mx-auto h-10 w-20 animate-pulse rounded-leaf bg-card-2" />
          <p v-else class="text-4xl font-extrabold leading-none text-ink">{{ aiCredits }}</p>
          <p class="mt-2 text-sm text-muted">{{ t("ai_credits.available", { n: aiCredits }, aiCredits) }}</p>
        </section>

        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-card border border-line bg-card p-4 shadow-soft">
            <p class="text-lg font-bold leading-none text-ink">{{ totalPurchased }}</p>
            <p class="mt-1.5 text-xs text-muted">{{ t("ai_credits.total_purchased") }}</p>
          </div>
          <div class="rounded-card border border-line bg-card p-4 shadow-soft">
            <p class="text-lg font-bold leading-none text-ink">{{ fcfa(totalSpent) }}</p>
            <p class="mt-1.5 text-xs text-muted">{{ t("ai_credits.total_spent") }}</p>
          </div>
        </div>

        <section class="space-y-3 rounded-card border border-line bg-card p-5 shadow-soft">
          <p class="text-sm font-medium text-ink">{{ t("ai_credits.help_title") }}</p>
          <a
            :href="whatsappUrl"
            target="_blank"
            rel="noopener"
            class="inline-flex w-full items-center justify-center gap-2 rounded-leaf bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
          >
            <i class="pi pi-whatsapp" />
            {{ t("ai_credits.help_whatsapp") }}
          </a>
        </section>
      </aside>

      <!-- ══════════ Colonne gauche : achat + historique ══════════ -->
      <div class="space-y-5 lg:col-span-2">
        <section class="space-y-5 rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
          <header>
            <h2 class="font-semibold text-ink">{{ t("ai_credits.buy_title") }}</h2>
            <p v-if="pricing" class="mt-0.5 text-sm text-muted">
              {{ t("ai_credits.per_credit", { price: fcfa(pricePerCredit) }) }}
            </p>
            <div v-else class="mt-1.5 h-4 w-64 animate-pulse rounded bg-card-2" />
          </header>

          <!-- ── Étape : formulaire ── -->
          <template v-if="step === 'form'">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("ai_credits.quantity") }}</label>
              <InputNumber
                v-model="credits"
                :min="minPurchase"
                :max="maxPurchase"
                fluid
                showButtons
                buttonLayout="horizontal"
                :step="1"
              >
                <template #decrementbuttonicon><i class="pi pi-minus" /></template>
                <template #incrementbuttonicon><i class="pi pi-plus" /></template>
              </InputNumber>
              <p class="mt-1 text-xs text-faint">{{ t("ai_credits.range", { min: minPurchase, max: maxPurchase }) }}</p>

              <div class="mt-3 flex flex-wrap gap-2">
                <button
                  v-for="qty in presets"
                  :key="qty"
                  type="button"
                  class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
                  :class="credits === qty ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
                  @click="credits = qty"
                >
                  {{ t("ai_credits.preset", { n: qty }) }}
                </button>
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("payment.operator") }}</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="op in operators"
                  :key="op.value"
                  type="button"
                  class="flex items-center gap-3 rounded-leaf border-2 p-3 text-left transition-colors"
                  :class="operator === op.value ? 'border-primary bg-primary/10' : 'border-line bg-card hover:border-primary/30'"
                  @click="operator = op.value"
                >
                  <span class="flex size-9 shrink-0 items-center justify-center rounded-leaf text-xs font-black" :class="op.badge">
                    {{ op.short }}
                  </span>
                  <span class="text-sm font-medium text-ink">{{ op.label }}</span>
                </button>
              </div>
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("payment.phone") }}</label>
              <InputText
                v-model="phone"
                inputmode="numeric"
                placeholder="6XXXXXXXX"
                fluid
                :invalid="phoneTouched && !phoneValid"
                @blur="phoneTouched = true"
              />
              <p class="mt-1 text-xs" :class="phoneTouched && !phoneValid ? 'text-red-600' : 'text-faint'">
                {{ phoneTouched && !phoneValid ? t("ai_credits.phone_invalid") : t("payment.phone_hint") }}
              </p>
            </div>

            <div class="flex items-center justify-between rounded-leaf bg-card-2 px-4 py-3">
              <div>
                <p class="text-xs text-muted">{{ t("payment.total") }}</p>
                <p class="text-2xl font-extrabold text-primary">{{ pricing ? fcfa(totalAmount) : "..." }}</p>
              </div>
              <p class="text-xs text-muted">{{ t("ai_credits.preset", { n: credits ?? 0 }) }}</p>
            </div>

            <Message v-if="errorMessage" severity="error" :closable="false">{{ errorMessage }}</Message>

            <Button
              :label="t('ai_credits.pay', { amount: pricing ? fcfa(totalAmount) : '' })"
              icon="pi pi-arrow-right"
              iconPos="right"
              class="w-full"
              :loading="loadingPurchase"
              :disabled="!canProceed"
              @click="purchase"
            />
          </template>

          <!-- ── Étape : attente de confirmation ── -->
          <div v-else-if="step === 'waiting'" class="space-y-4">
            <div class="flex flex-col items-center gap-2 rounded-leaf bg-sky-500/10 px-4 py-6 text-center">
              <i class="pi pi-mobile text-3xl text-sky-600" />
              <p class="font-semibold text-ink">{{ t("payment.pin") }}</p>
              <p class="text-sm text-muted">{{ t("payment.message") }}</p>
              <p v-if="lastPurchase" class="text-lg font-bold text-ink">{{ fcfa(lastPurchase.total_amount) }}</p>
              <p v-if="lastPurchase?.transaction_reference" class="break-all text-xs text-faint">
                {{ t("payment.ref") }} : {{ lastPurchase.transaction_reference }}
              </p>
            </div>
            <div class="flex items-center justify-center gap-2 text-sm text-muted">
              <i class="pi pi-spin pi-spinner text-xs" />
              {{ t("payment.polling") }}
            </div>
          </div>

          <!-- ── Étape : succès ── -->
          <div v-else-if="step === 'success'" class="flex flex-col items-center gap-3 py-4 text-center">
            <span class="flex size-16 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600">
              <i class="pi pi-check-circle text-3xl" />
            </span>
            <p class="text-lg font-bold text-ink">{{ t("ai_credits.success_title") }}</p>
            <p class="text-sm text-muted">
              {{ t("ai_credits.success_text", { n: lastPurchase?.credits ?? 0 }, lastPurchase?.credits ?? 0) }}
            </p>
            <Button :label="t('ai_credits.buy_more')" icon="pi pi-plus" outlined @click="resetState" />
          </div>

          <!-- ── Étape : échec ou délai dépassé ── -->
          <div v-else class="flex flex-col items-center gap-3 py-4 text-center">
            <span
              class="flex size-16 items-center justify-center rounded-full"
              :class="step === 'failed' ? 'bg-red-500/10 text-red-600' : 'bg-amber-500/15 text-amber-600'"
            >
              <i class="pi text-3xl" :class="step === 'failed' ? 'pi-times-circle' : 'pi-clock'" />
            </span>
            <p class="text-lg font-bold text-ink">
              {{ step === "failed" ? t("ai_credits.failed_title") : t("ai_credits.timeout_title") }}
            </p>
            <p class="max-w-md text-sm text-muted">
              {{ step === "failed" ? t("ai_credits.failed_text") : t("ai_credits.timeout_text") }}
            </p>
            <Button :label="t('ai_credits.retry')" icon="pi pi-refresh" outlined @click="resetState" />
          </div>
        </section>

        <!-- ── Historique ── -->
        <section class="space-y-2">
          <h3 class="text-sm font-semibold text-ink">
            {{ t("ai_credits.history_title") }}
            <span v-if="history.length" class="font-normal text-muted">· {{ history.length }}</span>
          </h3>

          <div v-if="historyLoading" class="space-y-2">
            <div v-for="n in 3" :key="n" class="h-14 animate-pulse rounded-card bg-card-2" />
          </div>

          <p v-else-if="history.length === 0" class="rounded-card border border-dashed border-line bg-card px-4 py-8 text-center text-sm text-muted">
            {{ t("ai_credits.history_empty") }}
          </p>

          <ul v-else class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft">
            <li v-for="item in sortedHistory" :key="item.id" class="flex flex-wrap items-center gap-x-4 gap-y-1 px-4 py-3 sm:px-5">
              <span class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-amber-500/15 text-xs font-bold text-amber-600">
                +{{ item.credits_purchased }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-ink">{{ fcfa(item.total_amount) }}</p>
                <p class="truncate text-xs text-muted">
                  {{ formatDate(item.created_at) }}
                  <span v-if="item.transaction_reference"> · {{ item.transaction_reference }}</span>
                </p>
              </div>
              <span class="rounded-full px-2 py-0.5 text-[11px] font-semibold" :class="statusBadge(item.payment_status)">
                {{ formatStatus(item.payment_status) }}
              </span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", watermark: "KI-Guthaben" });

const { t, te, locale } = useI18n();
const {
  balance,
  pricing,
  history,
  totalSpent,
  totalPurchased,
  loading,
  loadingPurchase,
  lastPurchase,
  aiCredits,
  pricePerCredit,
  minPurchase,
  maxPurchase,
  fetchPricing,
  fetchBalance,
  fetchHistory,
  purchaseCredits,
} = useAiCredits();

// ── Format ──
const intlLocale = computed(() => ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ?? "en-GB");
const fcfa = (n: number) => `${Math.round(n).toLocaleString(intlLocale.value)} FCFA`;
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(intlLocale.value, { day: "2-digit", month: "short", year: "numeric" });

const formatStatus = (s: string) => (te(`invoices.status.${s}`) ? t(`invoices.status.${s}`) : s);
const statusBadge = (s: string) =>
  ({
    COMPLETED: "bg-emerald-500/10 text-emerald-600",
    FAILED: "bg-red-500/10 text-red-600",
    PENDING: "bg-amber-500/15 text-amber-600",
    MANUAL: "bg-sky-500/10 text-sky-600",
  })[s] ?? "bg-card-2 text-muted";

// ── Formulaire ──
type Step = "form" | "waiting" | "success" | "failed" | "timeout";
const step = ref<Step>("form");
const credits = ref<number | null>(10);
const operator = ref<"MTN" | "ORANGE" | null>(null);
const phone = ref("");
const phoneTouched = ref(false);
const errorMessage = ref("");

const operators = [
  { value: "MTN" as const, label: "MTN Mobile Money", short: "MTN", badge: "bg-yellow-400 text-black" },
  { value: "ORANGE" as const, label: "Orange Money", short: "OM", badge: "bg-orange-500 text-white" },
];

const presets = computed(() => [5, 10, 20, 50].filter((n) => n >= minPurchase.value && n <= maxPurchase.value));

const normalizedPhone = computed(() => phone.value.replace(/\s+/g, "").replace(/^(\+?237)/, ""));
const phoneValid = computed(() => /^[69]\d{8}$/.test(normalizedPhone.value));

const totalAmount = computed(() => (credits.value ?? 0) * pricePerCredit.value);

const canProceed = computed(
  () =>
    !!pricing.value &&
    !!operator.value &&
    phoneValid.value &&
    !!credits.value &&
    credits.value >= minPurchase.value &&
    credits.value <= maxPurchase.value,
);

// ── Achat + vérification ──
const POLL_MS = 5000;
const MAX_ATTEMPTS = 36; // 3 minutes
let pollTimer: ReturnType<typeof setInterval> | null = null;
let attempts = 0;

const stopPolling = () => {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = null;
};

const finish = async (result: Step) => {
  stopPolling();
  step.value = result;
  if (result === "success") await fetchBalance();
};

const startPolling = (paymentId: string) => {
  stopPolling();
  attempts = 0;
  pollTimer = setInterval(async () => {
    attempts++;
    await fetchHistory();
    const status = history.value.find((h) => h.payment_id === paymentId)?.payment_status;
    if (status === "COMPLETED") finish("success");
    else if (status === "FAILED") finish("failed");
    else if (attempts >= MAX_ATTEMPTS) finish("timeout");
  }, POLL_MS);
};

const purchase = async () => {
  phoneTouched.value = true;
  if (!canProceed.value) return;
  errorMessage.value = "";

  const result = await purchaseCredits({
    credits: credits.value!,
    phone_number: normalizedPhone.value,
    operator: operator.value!,
  });

  if (!result.success || !result.data) {
    errorMessage.value = result.message || t("ai_credits.error");
    return;
  }

  if (result.data.payment_status === "COMPLETED") return finish("success");
  if (result.data.payment_status === "FAILED") return finish("failed");

  step.value = "waiting";
  startPolling(result.data.payment_id);
};

const resetState = () => {
  stopPolling();
  step.value = "form";
  errorMessage.value = "";
};

// ── Historique ──
const historyLoaded = ref(false);
const historyLoading = computed(() => !historyLoaded.value);
const sortedHistory = computed(() => [...history.value].sort((a, b) => b.created_at.localeCompare(a.created_at)));

// ── WhatsApp ──
const whatsappUrl = computed(
  () => `https://wa.me/237670886288?text=${encodeURIComponent(t("ai_credits.whatsapp_message"))}`,
);

onMounted(async () => {
  await Promise.all([fetchPricing(), fetchBalance(), fetchHistory()]);
  historyLoaded.value = true;
  if (credits.value! < minPurchase.value) credits.value = minPurchase.value;
});

onBeforeUnmount(stopPolling);
</script>