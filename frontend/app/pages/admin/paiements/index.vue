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
      v-else-if="loadingSummary"
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
      <header class="space-y-3 border-b border-line px-5 py-4">
        <div
          class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
        >
          <!-- Source -->
          <div class="flex flex-wrap gap-1 rounded-leaf bg-card-2 p-1">
            <button
              v-for="s in SOURCES"
              :key="s.value"
              type="button"
              class="inline-flex items-center gap-1.5 rounded-leaf px-3 py-1.5 text-xs font-semibold transition-colors"
              :class="
                source === s.value
                  ? 'bg-card text-ink shadow-soft'
                  : 'text-muted hover:text-ink'
              "
              @click="source = s.value"
            >
              <i :class="s.icon" class="text-[11px]" />
              {{ s.label }}
            </button>
          </div>

          <IconField class="w-full lg:w-80">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="search"
              class="w-full"
              placeholder="Nom, email, téléphone ou référence"
            />
          </IconField>
        </div>

        <!-- Statut -->
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
            <span class="rounded-full bg-card-2 px-1.5 text-[10px] text-muted">{{
              f.count ?? "…"
            }}</span>
          </button>
        </div>
      </header>

      <!-- Chargement -->
      <div v-if="loadingPayments" class="space-y-2 p-5">
        <div
          v-for="n in 5"
          :key="n"
          class="h-14 animate-pulse rounded-leaf bg-card-2"
        />
      </div>

      <!-- Vide -->
      <p
        v-else-if="payments.length === 0"
        class="px-5 py-12 text-center text-sm text-muted"
      >
        Aucun paiement trouvé
      </p>

      <!-- Liste -->
      <template v-else>
        <ul class="divide-y divide-line">
          <li
            v-for="payment in payments"
            :key="payment.id"
            class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-5"
          >
            <!-- Moyen de paiement -->
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-leaf text-[10px] font-black"
              :class="operatorStyle(payment.operator).class"
              v-tooltip.top="operatorStyle(payment.operator).label"
            >
              <i
                v-if="operatorStyle(payment.operator).icon"
                :class="operatorStyle(payment.operator).icon"
                class="text-sm"
              />
              <template v-else>{{ operatorStyle(payment.operator).short }}</template>
            </span>

            <!-- Élève -->
            <div class="min-w-48 flex-1">
              <p class="truncate text-sm font-medium text-ink">
                {{ payment.user_name || payment.user_email || "-" }}
              </p>
              <p class="mt-0.5 truncate text-xs text-muted">
                <span v-if="displayEmail(payment.user_email)">{{
                  displayEmail(payment.user_email)
                }}</span>
                <span v-if="payment.user_phone">
                  <template v-if="displayEmail(payment.user_email)"> · </template
                  >{{ payment.user_phone }}</span
                >
              </p>
            </div>

            <!-- Achat -->
            <div class="min-w-44 flex-1">
              <p class="flex items-center gap-1.5 text-sm text-ink">
                <i :class="kindIcon(payment.kind)" class="text-xs text-muted" />
                <span class="truncate">{{ payment.level_name || "-" }}</span>
              </p>
              <p class="mt-0.5 truncate text-xs text-muted">
                {{ formatDateTime(payment.created_at) }}
                <span v-if="payment.expires_at">
                  · accès jusqu'au {{ formatDate(payment.expires_at) }}</span
                >
              </p>
              <p class="truncate font-mono text-[11px] text-faint">
                {{ payment.transaction_reference }}
                <span v-if="providerRef(payment)">
                  · {{ providerRef(payment) }}</span
                >
              </p>
            </div>

            <!-- Montant -->
            <div class="w-32 text-right">
              <p class="text-sm font-semibold text-ink">
                {{ paymentAmount(payment) }}
              </p>
              <p v-if="isCard(payment)" class="text-xs text-muted">
                ≈ {{ fcfa(payment.amount_paid) }}
              </p>
              <p
                v-else-if="payment.discount_amount > 0"
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

            <!-- Reçu -->
            <div class="w-9 text-right">
              <Button
                v-if="payment.payment_status === 'COMPLETED'"
                icon="pi pi-file-pdf"
                text
                rounded
                size="small"
                severity="secondary"
                v-tooltip.top="'Voir le reçu'"
                aria-label="Voir le reçu"
                @click="openInvoice(payment.id)"
              />
            </div>
          </li>
        </ul>

        <Paginator
          v-if="total > rows"
          v-model:first="first"
          v-model:rows="rows"
          :totalRecords="total"
          :rowsPerPageOptions="[20, 50, 100]"
          class="border-t border-line"
        />
      </template>
    </section>

    <!-- ══ Reçu ══ -->
    <Dialog
      v-model:visible="invoiceDialog"
      header="Détail du reçu"
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
            <p class="truncate text-xs text-muted">
              {{ currentInvoice.operator }}
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
              currentInvoice.charged_amount &&
              currentInvoice.charged_currency === "EUR"
                ? eur(currentInvoice.charged_amount)
                : fcfa(currentInvoice.amount_paid)
            }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Fermer" text @click="invoiceDialog = false" />
        <Button
          v-if="currentInvoice"
          label="Télécharger le PDF"
          icon="pi pi-download"
          :loading="downloading"
          @click="handleDownload"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type {
  PaymentAdminListItem,
  PaymentSummaryResponse,
} from "#shared/api";

definePageMeta({ layout: "admin" });

const toast = useToast();
const { currentInvoice, fetchInvoice, formatDate } = useInvoices();
const { download, downloading } = useApiDownload();

// Composables Nuxt : appelés en haut du setup, jamais après un await
const config = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

// ── Format ──
const fcfa = (n: number) => `${Math.round(n).toLocaleString("fr-FR")} FCFA`;
const eur = (n: number) =>
  Number(n).toLocaleString("fr-FR", { style: "currency", currency: "EUR" });
const formatDateTime = (d: string) =>
  new Date(d).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

const PLACEHOLDER_EMAIL_DOMAIN = "@internal.gotogermany";
const displayEmail = (email?: string | null) =>
  !email || email.endsWith(PLACEHOLDER_EMAIL_DOMAIN) ? "" : email;

// Paiement par carte : charged_amount en centimes
const isCard = (p: PaymentAdminListItem) =>
  !!p.charged_amount && p.charged_currency === "EUR";
const paymentAmount = (p: PaymentAdminListItem) =>
  isCard(p) ? eur(p.charged_amount! / 100) : fcfa(p.amount_paid);

// Référence chez le prestataire : uuid Kratos ou session Stripe
const providerRef = (p: PaymentAdminListItem) => {
  const ref = p.operator === "STRIPE" ? p.provider_ref : p.pawapay_deposit_id;
  return ref ? (ref.length > 18 ? `${ref.slice(0, 18)}…` : ref) : "";
};

function operatorStyle(op?: string | null) {
  switch (op) {
    case "MTN":
      return { label: "MTN Mobile Money", short: "MTN", icon: "", class: "bg-yellow-400 text-black" };
    case "ORANGE":
      return { label: "Orange Money", short: "OM", icon: "", class: "bg-orange-500 text-white" };
    case "STRIPE":
      return { label: "Carte bancaire", short: "", icon: "pi pi-credit-card", class: "bg-sky-500/10 text-sky-600" };
    case "MANUAL":
      return { label: "Paiement manuel", short: "", icon: "pi pi-user-edit", class: "bg-card-2 text-muted" };
    case "PARTNER":
      return { label: "Centre ou ambassadeur", short: "", icon: "pi pi-building", class: "bg-primary/10 text-primary" };
    default:
      return { label: op || "-", short: "?", icon: "", class: "bg-card-2 text-muted" };
  }
}

const kindIcon = (kind?: string | null) =>
  ({
    credits: "pi pi-sparkles",
    start_deutsch: "pi pi-flag",
    exam: "pi pi-book",
  })[kind ?? ""] ?? "pi pi-shopping-bag";

function statusBadge(status: string) {
  if (status === "COMPLETED")
    return { label: "Payé", class: "bg-emerald-500/10 text-emerald-600" };
  if (status === "FAILED")
    return { label: "Échoué", class: "bg-red-500/10 text-red-600" };
  if (status === "PENDING")
    return { label: "En attente", class: "bg-amber-500/15 text-amber-600" };
  return { label: status, class: "bg-card-2 text-muted" };
}

// ── Résumé ──
const summary = ref<PaymentSummaryResponse | null>(null);
const loadingSummary = ref(false);

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

// ── Filtres ──
type Source = "online" | "manual" | "partner" | "all";
type Status = "" | "COMPLETED" | "PENDING" | "FAILED";

const SOURCES: { label: string; value: Source; icon: string }[] = [
  { label: "En ligne", value: "online", icon: "pi pi-globe" },
  { label: "Manuels", value: "manual", icon: "pi pi-user-edit" },
  { label: "Partenaires", value: "partner", icon: "pi pi-building" },
  { label: "Tous", value: "all", icon: "pi pi-list" },
];

const STATUTS: { label: string; value: Status }[] = [
  { label: "Tous", value: "" },
  { label: "Payés", value: "COMPLETED" },
  { label: "En attente", value: "PENDING" },
  { label: "Échoués", value: "FAILED" },
];

const source = ref<Source>("online");
const filterStatus = ref<Status>("");
const search = ref("");
const debouncedSearch = ref("");
let searchTimer: ReturnType<typeof setTimeout> | null = null;
watch(search, (v) => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => (debouncedSearch.value = v.trim()), 350);
});

// Compteurs par statut pour la source et la recherche en cours
const counts = ref<Record<string, number | null>>({});
const filters = computed(() =>
  STATUTS.map((s) => ({ ...s, count: counts.value[s.value] ?? null })),
);

// ── Liste (filtrée et paginée par le serveur) ──
const payments = ref<PaymentAdminListItem[]>([]);
const total = ref(0);
const loadingPayments = ref(false);
const first = ref(0);
const rows = ref(20);

async function api() {
  const mod = await import("#shared/api");
  mod.OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
  mod.OpenAPI.TOKEN = tokenCookie.value ?? undefined;
  return mod.PaymentsService;
}

const listCall = (
  svc: Awaited<ReturnType<typeof api>>,
  status: Status,
  limit: number,
  offset: number,
) =>
  svc.listAdminPaymentsApiV1PaymentsAdminListGet(
    source.value as any,
    (status || null) as any,
    debouncedSearch.value || null,
    limit,
    offset,
  );

async function loadPayments() {
  loadingPayments.value = true;
  try {
    const svc = await api();
    const res = await listCall(svc, filterStatus.value, rows.value, first.value);
    payments.value = res.items;
    total.value = res.total;
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary: e.body?.detail || "Erreur de chargement des paiements",
      life: 3000,
    });
  } finally {
    loadingPayments.value = false;
  }
}

async function loadCounts() {
  counts.value = {};
  try {
    const svc = await api();
    const results = await Promise.all(
      STATUTS.map((s) => listCall(svc, s.value, 1, 0)),
    );
    const next: Record<string, number> = {};
    STATUTS.forEach((s, i) => (next[s.value] = results[i]!.total));
    counts.value = next;
  } catch {
    // Les compteurs restent sur « … », la liste reste utilisable
  }
}

async function loadSummary() {
  loadingSummary.value = true;
  try {
    const svc = await api();
    summary.value = await svc.getSummaryApiV1PaymentsAdminSummaryGet();
  } catch {
    summary.value = null;
  } finally {
    loadingSummary.value = false;
  }
}

// Changement de source ou de recherche : compteurs + liste depuis le début
watch([source, debouncedSearch], () => {
  first.value = 0;
  loadCounts();
  loadPayments();
});
watch(filterStatus, () => {
  first.value = 0;
  loadPayments();
});
watch([first, rows], loadPayments);

// ── Reçu ──
const invoiceDialog = ref(false);
const invoiceLoading = ref(false);

async function openInvoice(paymentId: string) {
  invoiceDialog.value = true;
  invoiceLoading.value = true;
  await fetchInvoice(paymentId);
  invoiceLoading.value = false;
}

async function handleDownload() {
  const inv = currentInvoice.value;
  if (!inv) return;
  const res = await download(
    `/api/v1/invoices/${inv.payment_id}/pdf?lang=fr`,
    `recu_${inv.transaction_reference}.pdf`,
  );
  if (!res.success)
    toast.add({
      severity: "error",
      summary: res.error || "Téléchargement impossible",
      life: 4000,
    });
}

onMounted(() => {
  loadSummary();
  loadCounts();
  loadPayments();
});
</script>