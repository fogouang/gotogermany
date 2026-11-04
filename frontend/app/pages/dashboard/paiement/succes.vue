<!-- pages/dashboard/paiement/succes.vue -->
<template>
  <div class="mx-auto max-w-xl space-y-5 py-6">
    <section class="rounded-card border border-line bg-card p-6 text-center shadow-soft sm:p-8">
      <!-- Icône d'état -->
      <span
        class="mx-auto flex size-20 items-center justify-center rounded-full"
        :class="
          state === 'completed'
            ? 'bg-emerald-500/10 text-emerald-600'
            : state === 'failed' || state === 'missing'
              ? 'bg-red-500/10 text-red-600'
              : 'bg-amber-500/15 text-amber-600'
        "
      >
        <i v-if="state === 'loading' || state === 'pending'" class="pi pi-spin pi-spinner text-3xl" />
        <i v-else-if="state === 'completed'" class="pi pi-check-circle text-4xl" />
        <i v-else class="pi pi-times-circle text-4xl" />
      </span>

      <h1 class="mt-5 text-2xl font-bold text-ink">{{ title }}</h1>
      <p class="mx-auto mt-2 max-w-sm text-sm text-muted">{{ description }}</p>

      <!-- Détails du paiement -->
      <dl
        v-if="status"
        class="mt-6 grid grid-cols-1 gap-x-4 gap-y-2 rounded-leaf bg-card-2 px-5 py-4 text-left text-sm sm:grid-cols-[auto_1fr]"
      >
        <dt class="text-muted">{{ t("payment.success.amount") }}</dt>
        <dd class="font-semibold text-ink">{{ amountLabel }}</dd>
        <template v-if="status.operator">
          <dt class="text-muted">{{ t("payment.success.method") }}</dt>
          <dd class="text-ink">{{ methodLabel }}</dd>
        </template>
        <template v-if="status.completed_at">
          <dt class="text-muted">{{ t("payment.success.date") }}</dt>
          <dd class="text-ink">{{ formatDateTime(status.completed_at) }}</dd>
        </template>
        <dt class="text-muted">{{ t("payment.ref") }}</dt>
        <dd class="break-all font-mono text-xs font-semibold text-ink">{{ status.transaction_reference }}</dd>
      </dl>

      <!-- Redirection automatique -->
      <p v-if="state === 'completed' && countdown > 0" class="mt-5 text-xs text-faint">
        {{ t("payment.success.redirect", { n: countdown }) }}
      </p>

      <!-- Actions -->
      <div class="mt-6 flex flex-col justify-center gap-2 sm:flex-row">
        <Button
          v-if="state === 'completed'"
          :label="nextLabel"
          icon="pi pi-arrow-right"
          iconPos="right"
          @click="goNext"
        />
        <Button
          v-if="state === 'completed'"
          :label="t('payment.success.invoices')"
          icon="pi pi-file"
          outlined
          @click="navigateTo(localePath('/dashboard/factures'))"
        />
        <Button
          v-if="state === 'failed' || state === 'missing'"
          :label="t('payment.confirm.retry')"
          icon="pi pi-refresh"
          @click="navigateTo(localePath('/dashboard/paiement'))"
        />
        <Button
          v-if="state === 'pending'"
          :label="t('payment.success.later')"
          text
          severity="secondary"
          @click="goNext"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { PaymentStatusResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Danke" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const paymentsStore = usePaymentsStore();

type State = "loading" | "pending" | "completed" | "failed" | "missing";

const reference = computed(() => (route.query.ref as string | undefined) ?? "");
// Où aller ensuite : Start Deutsch ou examens B (transmis par la page de paiement)
const nextPath = computed(() =>
  route.query.next === "start-deutsch" ? "/dashboard/start-deutsch" : "/dashboard/examens",
);

const state = ref<State>("loading");
const status = ref<PaymentStatusResponse | null>(null);
const countdown = ref(0);

const POLL_MS = 5000;
const MAX_WAIT_MS = 10 * 60 * 1000; // un paiement Mobile Money ou carte peut prendre quelques minutes

let pollTimer: ReturnType<typeof setInterval> | null = null;
let countdownTimer: ReturnType<typeof setInterval> | null = null;
let startedAt = 0;

// ── Libellés ──
const title = computed(() => {
  switch (state.value) {
    case "completed": return t("payment.confirm.success_title");
    case "failed": return t("payment.confirm.failed_title");
    case "missing": return t("payment.success.missing_title");
    default: return t("payment.confirm.pending_title");
  }
});

const description = computed(() => {
  switch (state.value) {
    case "completed":
      return status.value?.exam_access_granted
        ? t("payment.success.access_active")
        : t("payment.confirm.success_desc");
    case "failed": return t("payment.confirm.failed_desc");
    case "missing": return t("payment.success.missing_desc");
    default: return t("payment.success.pending_desc");
  }
});

const nextLabel = computed(() =>
  nextPath.value === "/dashboard/start-deutsch"
    ? t("payment.success.go_start_deutsch")
    : t("payment.confirm.go_to_exams"),
);

const intlLocale = computed(() => ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ?? "en-GB");

const amountLabel = computed(() => {
  const s = status.value;
  if (!s) return "-";
  if (s.charged_amount != null && s.charged_currency) {
    return Number(s.charged_amount).toLocaleString(intlLocale.value, {
      style: "currency",
      currency: s.charged_currency,
    });
  }
  const n = Number(s.amount_paid).toLocaleString(intlLocale.value);
  return s.currency === "XAF" ? `${n} FCFA` : `${n} ${s.currency}`;
});

const methodLabel = computed(() => {
  const map: Record<string, string> = {
    MTN: "MTN Mobile Money",
    ORANGE: "Orange Money",
    STRIPE: t("payment.success.card"),
  };
  return map[status.value?.operator ?? ""] ?? status.value?.operator ?? "";
});

const formatDateTime = (d: string) =>
  new Date(d).toLocaleString(intlLocale.value, {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

// ── Suivi du paiement ──
function stopTimers() {
  if (pollTimer) clearInterval(pollTimer);
  if (countdownTimer) clearInterval(countdownTimer);
  pollTimer = null;
  countdownTimer = null;
}

/** Recharge ce qui dépend de l'accès payé, pour que tout s'ouvre sans rafraîchir. */
async function refreshAfterPayment() {
  await Promise.allSettled([
    useAuthStore().fetchUser(),
    useExamsStore().fetchCatalog(),
    useStartDeutschSessionStore().fetchSubjects(),
  ]);
}

async function onCompleted() {
  stopTimers();
  state.value = "completed";
  await refreshAfterPayment();

  // Redirection automatique quand l'accès est actif
  if (status.value?.exam_access_granted) {
    countdown.value = 5;
    countdownTimer = setInterval(() => {
      countdown.value -= 1;
      if (countdown.value <= 0) goNext();
    }, 1000);
  }
}

async function check() {
  const res = await paymentsStore.checkStatus(reference.value);
  if (!res.success || !res.data) {
    // Référence inconnue ou pas à cet élève
    if (state.value === "loading") {
      stopTimers();
      state.value = "missing";
    }
    return;
  }

  status.value = res.data;
  const s = res.data.payment_status;

  if (s === "COMPLETED") {
    await onCompleted();
  } else if (s === "FAILED") {
    stopTimers();
    state.value = "failed";
  } else {
    state.value = "pending";
    if (Date.now() - startedAt > MAX_WAIT_MS) stopTimers();
  }
}

function goNext() {
  stopTimers();
  navigateTo(localePath(nextPath.value));
}

onMounted(async () => {
  paymentsStore.stopPolling();
  if (!reference.value) {
    state.value = "missing";
    return;
  }
  startedAt = Date.now();
  await check();
  if (state.value === "pending") pollTimer = setInterval(check, POLL_MS);
});

onBeforeUnmount(stopTimers);
</script>