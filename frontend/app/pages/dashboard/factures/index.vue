<template>
  <div class="space-y-5 pb-10">
    <p class="text-sm text-muted">{{ t("invoices.subtitle") }}</p>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div class="h-24 animate-pulse rounded-card bg-card-2" />
      <div
        v-for="n in 3"
        :key="n"
        class="h-20 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="myPayments.length === 0"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-14 text-center"
    >
      <span
        class="flex size-14 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-receipt text-xl" />
      </span>
      <div>
        <p class="font-medium text-ink">{{ t("invoices.empty_title") }}</p>
        <p class="mt-1 text-sm text-muted">
          {{ t("invoices.empty_subtitle") }}
        </p>
      </div>
      <Button
        :label="t('invoices.see_pricing')"
        icon="pi pi-tag"
        @click="navigateTo(localePath('/tarifs'))"
      />
    </div>

    <template v-else>
      <!-- ── Résumé ── -->
      <div
        class="flex flex-wrap items-center justify-between gap-4 rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <div class="flex items-center gap-4">
          <span
            class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary"
          >
            <i class="pi pi-wallet" />
          </span>
          <div>
            <p class="text-xs text-muted">{{ t("invoices.total") }}</p>
            <p class="text-2xl font-bold leading-tight text-ink">
              {{ fcfa(totalPaid) }}
            </p>
          </div>
        </div>
        <p class="text-sm text-muted">
          {{ t("invoices.count", { n: myPayments.length }, myPayments.length) }}
        </p>
      </div>

      <!-- ── Filtres ── -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="f in filters"
          :key="f.key"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            statusFilter === f.key
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30'
          "
          @click="statusFilter = f.key"
        >
          {{ f.label }} · {{ f.count }}
        </button>
      </div>

      <!-- ── Liste ── -->
      <ul
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="payment in pagedPayments"
          :key="payment.id"
          class="flex flex-wrap items-center gap-x-4 gap-y-3 px-4 py-4 sm:px-5"
        >
          <span
            class="flex size-10 shrink-0 items-center justify-center rounded-full"
            :class="statusStyle(payment.payment_status).bubble"
          >
            <i
              class="pi text-sm"
              :class="statusStyle(payment.payment_status).icon"
            />
          </span>

          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <p class="font-semibold text-ink">
                {{ fcfa(payment.amount_paid) }}
              </p>
              <span
                class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="statusStyle(payment.payment_status).badge"
              >
                {{ formatStatus(payment.payment_status) }}
              </span>
            </div>
            <p class="mt-0.5 truncate text-xs text-muted">
              {{ formatDate(payment.created_at) }}
              <span v-if="payment.operator"> · {{ payment.operator }}</span>
            </p>
            <p class="truncate text-xs text-faint">
              {{ t("invoices.ref") }} {{ payment.transaction_reference }}
            </p>
          </div>

          <template v-if="payment.payment_status === 'COMPLETED'">
            <Button
              icon="pi pi-file-pdf"
              :label="t('invoices.invoice_btn')"
              size="small"
              outlined
              severity="secondary"
              class="hidden! sm:inline-flex!"
              :loading="loadingInvoice === payment.id"
              @click="openInvoice(payment.id)"
            />
            <Button
              icon="pi pi-file-pdf"
              size="small"
              text
              rounded
              severity="secondary"
              class="sm:hidden!"
              :aria-label="t('invoices.invoice_btn')"
              :loading="loadingInvoice === payment.id"
              @click="openInvoice(payment.id)"
            />
          </template>
        </li>
      </ul>

      <Paginator
        v-if="filteredPayments.length > rowsPerPage"
        v-model:first="first"
        :rows="rowsPerPage"
        :totalRecords="filteredPayments.length"
        class="rounded-card border border-line bg-card"
      />
    </template>

    <!-- ══════════ Dialogue facture ══════════ -->
    <Dialog
      v-model:visible="invoiceDialog"
      :header="t('invoices.dialog_title')"
      modal
      :style="{ width: '32rem', maxWidth: '95vw' }"
    >
      <div v-if="invoiceLoading" class="space-y-3">
        <div class="h-24 animate-pulse rounded-leaf bg-card-2" />
        <div class="h-40 animate-pulse rounded-leaf bg-card-2" />
      </div>

      <div v-else-if="currentInvoice" class="space-y-4">
        <div
          class="flex flex-col items-center gap-1 rounded-leaf bg-primary/10 px-4 py-5 text-center"
        >
          <i class="pi pi-check-circle text-2xl text-primary" />
          <p class="font-semibold text-ink">
            {{ t("invoices.payment_confirmed") }}
          </p>
          <p class="break-all text-xs text-muted">
            {{ currentInvoice.transaction_reference }}
          </p>
        </div>

        <dl class="space-y-2.5 text-sm">
          <div class="flex justify-between gap-4">
            <dt class="text-muted">{{ t("invoices.client") }}</dt>
            <dd class="text-right font-medium text-ink">
              {{ currentInvoice.customer_name }}
            </dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-muted">{{ t("invoices.product") }}</dt>
            <dd class="max-w-56 text-right font-medium text-ink">
              {{ currentInvoice.product_description }}
            </dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-muted">{{ t("invoices.date") }}</dt>
            <dd class="text-right font-medium text-ink">
              {{ formatDate(currentInvoice.payment_date) }}
            </dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-muted">{{ t("invoices.operator") }}</dt>
            <dd class="text-right font-medium text-ink">
              {{ currentInvoice.operator || "-" }}
            </dd>
          </div>
        </dl>

        <div class="space-y-2 border-t border-line pt-3 text-sm">
          <div
            v-if="currentInvoice.discount_amount > 0"
            class="flex justify-between text-emerald-600"
          >
            <span>{{ t("invoices.discount") }}</span>
            <span>- {{ fcfa(currentInvoice.discount_amount) }}</span>
          </div>
          <div class="flex justify-between text-base font-bold">
            <span class="text-ink">{{ t("invoices.total") }}</span>
            <span class="text-primary">{{
              fcfa(currentInvoice.amount_paid)
            }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          :label="t('invoices.close')"
          text
          severity="secondary"
          @click="invoiceDialog = false"
        />
        <Button
          v-if="currentInvoice?.invoice_url"
          :label="t('invoices.download_pdf')"
          icon="pi pi-download"
          @click="
            downloadInvoice(
              currentInvoice.invoice_url!,
              `facture-${currentInvoice.transaction_reference}.pdf`,
            )
          "
        />
        <Button
          v-else-if="currentInvoice"
          :label="t('invoices.generate_pdf')"
          icon="pi pi-refresh"
          outlined
          :loading="invoiceLoading"
          @click="handleGenerate"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", watermark: "Rechnungen" });

const { t, te, locale } = useI18n();
const localePath = useLocalePath();
const { myPayments, loading, fetchMyPayments } = usePayments();
const {
  currentInvoice,
  fetchInvoice,
  generateInvoice,
  downloadInvoice,
  formatDate,
} = useInvoices();

const invoiceDialog = ref(false);
const invoiceLoading = ref(false);
const loadingInvoice = ref<string | null>(null);

// ── Format ──
const numberLocale = computed(
  () =>
    (({ fr: "fr-FR", de: "de-DE" }) as Record<string, string>)[locale.value] ??
    "en-GB",
);
const fcfa = (n: number) =>
  `${Math.round(n).toLocaleString(numberLocale.value)} FCFA`;

const formatStatus = (status: string) =>
  te(`invoices.status.${status}`) ? t(`invoices.status.${status}`) : status;

const statusStyle = (status: string) =>
  status === "COMPLETED"
    ? {
        bubble: "bg-emerald-500/10",
        icon: "pi-check text-emerald-600",
        badge: "bg-emerald-500/10 text-emerald-600",
      }
    : status === "FAILED"
      ? {
          bubble: "bg-red-500/10",
          icon: "pi-times text-red-600",
          badge: "bg-red-500/10 text-red-600",
        }
      : {
          bubble: "bg-amber-500/15",
          icon: "pi-clock text-amber-600",
          badge: "bg-amber-500/15 text-amber-600",
        };

// ── Résumé ──
const totalPaid = computed(() =>
  myPayments.value
    .filter((p) => p.payment_status === "COMPLETED")
    .reduce((s, p) => s + (p.amount_paid ?? 0), 0),
);

// ── Filtres ──
type StatusFilter = "all" | "COMPLETED" | "PENDING" | "FAILED";
const statusFilter = ref<StatusFilter>("all");

const countStatus = (s: string) =>
  myPayments.value.filter((p) => p.payment_status === s).length;

const filters = computed(() =>
  [
    {
      key: "all" as const,
      label: t("invoices.all"),
      count: myPayments.value.length,
    },
    {
      key: "COMPLETED" as const,
      label: formatStatus("COMPLETED"),
      count: countStatus("COMPLETED"),
    },
    {
      key: "PENDING" as const,
      label: formatStatus("PENDING"),
      count: countStatus("PENDING"),
    },
    {
      key: "FAILED" as const,
      label: formatStatus("FAILED"),
      count: countStatus("FAILED"),
    },
  ].filter((f) => f.key === "all" || f.count > 0),
);

const filteredPayments = computed(() =>
  [...myPayments.value]
    .filter(
      (p) =>
        statusFilter.value === "all" || p.payment_status === statusFilter.value,
    )
    .sort((a, b) => b.created_at.localeCompare(a.created_at)),
);

// ── Pagination ──
const first = ref(0);
const rowsPerPage = 10;
const pagedPayments = computed(() =>
  filteredPayments.value.slice(first.value, first.value + rowsPerPage),
);
watch(statusFilter, () => (first.value = 0));

// ── Facture ──
const openInvoice = async (paymentId: string) => {
  loadingInvoice.value = paymentId;
  invoiceDialog.value = true;
  invoiceLoading.value = true;
  await fetchInvoice(paymentId);
  invoiceLoading.value = false;
  loadingInvoice.value = null;
};

const handleGenerate = async () => {
  if (!currentInvoice.value) return;
  invoiceLoading.value = true;
  await generateInvoice(currentInvoice.value.payment_id);
  invoiceLoading.value = false;
};

onMounted(fetchMyPayments);
</script>
