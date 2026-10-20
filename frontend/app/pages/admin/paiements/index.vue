<!-- pages/admin/paiements/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Chiffres ── -->
    <div v-if="summary" class="grid grid-cols-2 gap-3 xl:grid-cols-4">
      <div
        v-for="s in stats"
        :key="s.label"
        class="rounded-card border border-line bg-card p-4 shadow-soft"
      >
        <div
          class="mb-3 flex size-9 items-center justify-center rounded-leaf"
          :class="s.iconClass"
        >
          <i :class="s.icon" class="text-sm" />
        </div>
        <p class="text-xl font-bold leading-none" :class="s.tone">
          {{ s.value }}
        </p>
        <p class="mt-1.5 text-xs text-muted">{{ s.label }}</p>
      </div>
    </div>
    <div
      v-else-if="loadingPayments"
      class="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6"
    >
      <div
        v-for="n in 6"
        :key="n"
        class="h-28 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Paiements ── -->
    <section
      class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
    >
      <header
        class="flex flex-col gap-3 border-b border-line px-5 py-4 lg:flex-row lg:items-center lg:justify-between"
      >
        <h2 class="font-semibold text-ink">Paiements manuels</h2>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="f in filters"
            :key="f.value"
            type="button"
            class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors"
            :class="
              filterStatus === f.value
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-line bg-card text-muted hover:border-primary/30'
            "
            @click="filterStatus = f.value"
          >
            {{ f.label }}
            <span
              class="rounded-full bg-card-2 px-1.5 text-[10px] text-muted"
              >{{ f.count }}</span
            >
          </button>
        </div>
        <IconField class="w-full lg:w-72">
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="search"
            class="w-full"
            placeholder="Élève, email, niveau ou référence"
          />
        </IconField>
      </header>

      <!-- Chargement -->
      <div v-if="loadingPayments" class="space-y-2 p-5">
        <div
          v-for="n in 5"
          :key="n"
          class="h-12 animate-pulse rounded-leaf bg-card-2"
        />
      </div>

      <!-- Vide -->
      <p
        v-else-if="filteredPayments.length === 0"
        class="px-5 py-12 text-center text-sm text-muted"
      >
        Aucun paiement trouvé
      </p>

      <!-- Liste -->
      <template v-else>
        <ul class="divide-y divide-line">
          <li
            v-for="payment in paginatedPayments"
            :key="payment.id"
            class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-5"
          >
            <!-- Élève + niveau + référence -->
            <div class="min-w-48 flex-1">
              <p class="truncate text-sm font-medium text-ink">
                {{ payment.user_name || payment.user_email || "-" }}
              </p>
              <p
                class="mt-0.5 flex flex-wrap items-center gap-x-2 text-xs text-muted"
              >
                <span v-if="payment.level_name">{{ payment.level_name }}</span>
                <span>· {{ formatDate(payment.created_at) }}</span>
                <span class="font-mono"
                  >· {{ payment.transaction_reference }}</span
                >
              </p>
            </div>

            <!-- Montant -->
            <div class="w-36 text-right">
              <p class="text-sm font-semibold text-ink">
                {{ fcfa(payment.amount_paid) }}
              </p>
              <p
                v-if="payment.discount_amount > 0"
                class="text-xs text-emerald-600"
              >
                -{{ fcfa(payment.discount_amount) }}
              </p>
            </div>

            <!-- Statut -->
            <span
              class="w-24 rounded-full px-2 py-0.5 text-center text-[11px] font-semibold"
              :class="statusBadge(payment.payment_status).class"
            >
              {{ statusBadge(payment.payment_status).label }}
            </span>

            <!-- Facture -->
            <div class="w-9 text-right">
              <Button
                v-if="payment.payment_status === 'COMPLETED'"
                icon="pi pi-file-pdf"
                text
                rounded
                size="small"
                severity="secondary"
                v-tooltip.top="'Voir la facture'"
                aria-label="Voir la facture"
                @click="openInvoice(payment.id)"
              />
            </div>
          </li>
        </ul>

        <Paginator
          v-if="filteredPayments.length > 20"
          v-model:first="first"
          v-model:rows="rows"
          :totalRecords="filteredPayments.length"
          :rowsPerPageOptions="[20, 50, 100]"
          class="border-t border-line"
        />
      </template>
    </section>

    <!-- ══ Facture ══ -->
    <Dialog
      v-model:visible="invoiceDialog"
      header="Détail facture"
      modal
      :style="{ width: '95vw', maxWidth: '34rem' }"
    >
      <div v-if="invoiceLoading" class="space-y-3">
        <div
          v-for="n in 3"
          :key="n"
          class="h-14 animate-pulse rounded-leaf bg-card-2"
        />
      </div>

      <div v-else-if="currentInvoice" class="space-y-4 text-sm">
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div class="rounded-leaf bg-card-2 p-3">
            <p class="text-xs text-muted">Client</p>
            <p class="font-medium text-ink">
              {{ currentInvoice.customer_name }}
            </p>
            <p class="truncate text-xs text-muted">
              {{ currentInvoice.customer_email }}
            </p>
          </div>
          <div class="rounded-leaf bg-card-2 p-3">
            <p class="text-xs text-muted">Date</p>
            <p class="font-medium text-ink">
              {{ formatDate(currentInvoice.payment_date) }}
            </p>
          </div>
        </div>

        <div class="rounded-leaf bg-card-2 p-3">
          <p class="mb-1 text-xs text-muted">Produit</p>
          <p class="font-medium text-ink">
            {{ currentInvoice.product_description }}
          </p>
        </div>

        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-muted">Montant brut</span>
            <span class="text-ink">{{
              fcfa(currentInvoice.amount_gross)
            }}</span>
          </div>
          <div
            v-if="currentInvoice.discount_amount > 0"
            class="flex justify-between text-emerald-600"
          >
            <span>Réduction</span>
            <span>- {{ fcfa(currentInvoice.discount_amount) }}</span>
          </div>
          <div
            class="flex justify-between border-t border-line pt-2 text-base font-bold"
          >
            <span class="text-ink">Total payé</span>
            <span class="text-emerald-600">{{
              fcfa(currentInvoice.amount_paid)
            }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Fermer" text @click="invoiceDialog = false" />
        <Button
          v-if="currentInvoice?.invoice_url"
          label="Télécharger PDF"
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
          label="Générer PDF"
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
import type { PaymentAdminResponse, PaymentSummaryResponse } from "#shared/api";

definePageMeta({ layout: "admin" });

const toast = useToast();
const {
  currentInvoice,
  fetchInvoice,
  generateInvoice,
  downloadInvoice,
  formatDate,
} = useInvoices();

const fcfa = (n: number) => `${n.toLocaleString("fr-FR")} FCFA`;

// Composables Nuxt : appelés en haut du setup, jamais après un await
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

// ── Résumé ──
const summary = ref<PaymentSummaryResponse | null>(null);

const stats = computed(() => {
  const s = summary.value;
  if (!s) return [];
  return [
    {
      label: "Paiements réussis",
      value: s.total_completed.toLocaleString("fr-FR"),
      tone: "text-ink",
      icon: "pi pi-check-circle",
      iconClass: "bg-emerald-500/10 text-emerald-600",
    },
    {
      label: "Revenus",
      value: fcfa(s.total_revenue),
      tone: "text-emerald-600",
      icon: "pi pi-wallet",
      iconClass: "bg-emerald-500/10 text-emerald-600",
    },
    {
      label: "Commissions dues",
      value: fcfa(s.total_commissions_due),
      tone: "text-amber-600",
      icon: "pi pi-percentage",
      iconClass: "bg-amber-500/15 text-amber-600",
    },
    {
      label: "Total paiements",
      value: s.total_payments.toLocaleString("fr-FR"),
      tone: "text-ink",
      icon: "pi pi-list",
      iconClass: "bg-primary/10 text-primary",
    },
    {
      label: "Paiements échoués",
      value: s.total_failed.toLocaleString("fr-FR"),
      tone: "text-red-600",
      icon: "pi pi-times-circle",
      iconClass: "bg-red-500/10 text-red-600",
    },
    {
      label: "Réductions accordées",
      value: fcfa(s.total_discounts),
      tone: "text-sky-600",
      icon: "pi pi-tag",
      iconClass: "bg-sky-500/10 text-sky-600",
    },
  ];
});

// ── Paiements ──
const payments = ref<PaymentAdminResponse[]>([]);
const loadingPayments = ref(false);
const filterStatus = ref("");
const search = ref("");

const STATUTS = [
  { label: "Tous", value: "" },
  { label: "Payés", value: "COMPLETED" },
  { label: "En attente", value: "PENDING" },
  { label: "Échoués", value: "FAILED" },
];

const filters = computed(() =>
  STATUTS.map((s) => ({
    ...s,
    count: s.value
      ? payments.value.filter((p) => p.payment_status === s.value).length
      : payments.value.length,
  })),
);

function statusBadge(status: string) {
  if (status === "COMPLETED")
    return { label: "Payé", class: "bg-emerald-500/10 text-emerald-600" };
  if (status === "FAILED")
    return { label: "Échoué", class: "bg-red-500/10 text-red-600" };
  if (status === "PENDING")
    return { label: "En attente", class: "bg-amber-500/15 text-amber-600" };
  return { label: status, class: "bg-card-2 text-muted" };
}

const filteredPayments = computed(() => {
  const q = search.value.trim().toLowerCase();
  return payments.value
    .filter(
      (p) => !filterStatus.value || p.payment_status === filterStatus.value,
    )
    .filter(
      (p) =>
        !q ||
        p.transaction_reference.toLowerCase().includes(q) ||
        (p.user_name ?? "").toLowerCase().includes(q) ||
        (p.user_email ?? "").toLowerCase().includes(q) ||
        (p.level_name ?? "").toLowerCase().includes(q),
    );
});

// ── Pagination ──
const first = ref(0);
const rows = ref(20);
const paginatedPayments = computed(() =>
  filteredPayments.value.slice(first.value, first.value + rows.value),
);

watch([filterStatus, search], () => {
  first.value = 0;
});

// ── Chargement ──
async function loadData() {
  loadingPayments.value = true;
  try {
    const { PaymentsService, OpenAPI } = await import("#shared/api");
    OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
    OpenAPI.TOKEN = tokenCookie.value ?? undefined;

    // Seule liste disponible côté admin : les paiements manuels
    const [sum, list] = await Promise.all([
      PaymentsService.getSummaryApiV1PaymentsAdminSummaryGet(),
      PaymentsService.listManualPaymentsApiV1PaymentsAdminManualListGet(),
    ]);
    summary.value = sum;
    payments.value = list;
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary: e.body?.detail || "Erreur",
      life: 3000,
    });
  } finally {
    loadingPayments.value = false;
  }
}

// ── Facture ──
const invoiceDialog = ref(false);
const invoiceLoading = ref(false);

async function openInvoice(paymentId: string) {
  invoiceDialog.value = true;
  invoiceLoading.value = true;
  await fetchInvoice(paymentId);
  invoiceLoading.value = false;
}

async function handleGenerate() {
  if (!currentInvoice.value) return;
  invoiceLoading.value = true;
  await generateInvoice(currentInvoice.value.payment_id);
  invoiceLoading.value = false;
}

onMounted(loadData);
</script>
