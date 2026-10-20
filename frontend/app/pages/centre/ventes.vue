<!-- pages/centre/ventes.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Indicateurs ── -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="kpi in kpis"
        :key="kpi.label"
        class="rounded-card border border-line bg-card p-5 shadow-soft"
      >
        <div class="flex items-start justify-between gap-3">
          <p class="text-xs font-medium uppercase tracking-wide text-muted">
            {{ kpi.label }}
          </p>
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf"
            :class="kpi.tone"
          >
            <i :class="kpi.icon" class="text-sm" />
          </span>
        </div>
        <p class="mt-3 text-2xl font-bold" :class="kpi.valueClass ?? 'text-ink'">
          <span
            v-if="loading"
            class="inline-block h-7 w-24 animate-pulse rounded bg-card-2"
          />
          <template v-else>{{ kpi.value }}</template>
        </p>
        <p class="mt-1 text-xs text-muted">{{ kpi.hint }}</p>
      </div>
    </div>

    <!-- ── Filtres ── -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="f in filters"
        :key="f.key"
        type="button"
        class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors"
        :class="
          activeFilter === f.key
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-line bg-card text-muted hover:border-primary/30'
        "
        @click="activeFilter = f.key"
      >
        {{ f.label }}
        <span class="rounded-full bg-card-2 px-1.5 text-[10px] text-muted">
          {{ f.count }}
        </span>
      </button>
    </div>

    <!-- ── Ventes ── -->
    <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
      <div v-if="loading" class="space-y-3 p-5">
        <div v-for="n in 6" :key="n" class="h-10 animate-pulse rounded-leaf bg-card-2" />
      </div>

      <div
        v-else-if="filteredSales.length === 0"
        class="flex flex-col items-center gap-2 px-5 py-12 text-center"
      >
        <span
          class="flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary"
        >
          <i class="pi pi-shopping-bag" />
        </span>
        <p class="text-sm font-medium text-ink">{{ t("centre.dashboard.empty_title") }}</p>
        <p class="text-xs text-muted">{{ t("centre.dashboard.empty_text") }}</p>
      </div>

      <template v-else>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-line text-left text-xs text-muted">
              <tr>
                <th class="px-5 py-3 font-medium">{{ t("centre.dashboard.col_student") }}</th>
                <th class="px-5 py-3 font-medium">{{ t("centre.dashboard.col_plan") }}</th>
                <th class="px-5 py-3 text-right font-medium">{{ t("centre.dashboard.col_price") }}</th>
                <th class="px-5 py-3 text-right font-medium">{{ t("centre.sales.col_share") }}</th>
                <th class="px-5 py-3 text-right font-medium">{{ t("centre.dashboard.col_remaining") }}</th>
                <th class="px-5 py-3 font-medium">{{ t("centre.dashboard.col_status") }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-line">
              <tr v-for="sale in pagedSales" :key="sale.id">
                <td class="px-5 py-3">
                  <p class="font-medium text-ink">{{ sale.student_name }}</p>
                  <p class="text-xs text-muted">{{ formatDate(sale.created_at) }}</p>
                </td>
                <td class="px-5 py-3 text-muted">{{ sale.plan_name || "-" }}</td>
                <td class="whitespace-nowrap px-5 py-3 text-right text-ink">
                  {{ money(sale.price) }}
                </td>
                <td class="whitespace-nowrap px-5 py-3 text-right font-medium text-emerald-600">
                  {{ money(sale.partner_share) }}
                </td>
                <td class="whitespace-nowrap px-5 py-3 text-right font-medium text-ink">
                  {{ sale.direction === "partner_owes" ? money(sale.remaining) : "-" }}
                </td>
                <td class="px-5 py-3">
                  <span
                    class="whitespace-nowrap rounded-full px-2 py-0.5 text-[10px] font-semibold"
                    :class="saleBadge(sale).class"
                  >
                    {{ saleBadge(sale).label }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <Paginator
          v-if="filteredSales.length > rows"
          v-model:first="first"
          v-model:rows="rows"
          :total-records="filteredSales.length"
          :rows-per-page-options="[10, 20, 50]"
          class="border-t border-line"
        />
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { PartnerSaleResponse } from "#shared/api";

definePageMeta({ layout: "centre", watermark: "Verkäufe" });

const { t, locale } = useI18n();
const salesStore = useSalesStore();

// Ventes chargées en une fois, pagination côté navigateur
const SALES_LIMIT = 50;

const money = (n: number) => `${new Intl.NumberFormat(locale.value).format(n)} FCFA`;
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

const loading = ref(true);
const summary = computed(() => salesStore.mySummary);

// ── Indicateurs ──
const kpis = computed(() => {
  const s = summary.value;
  return [
    {
      label: t("centre.dashboard.kpi_earned"),
      value: money(s?.earned_total ?? 0),
      hint: t("centre.dashboard.kpi_earned_hint"),
      icon: "pi pi-money-bill",
      tone: "bg-emerald-500/10 text-emerald-600",
      valueClass: "text-emerald-600",
    },
    {
      label: t("centre.dashboard.kpi_to_pay"),
      value: money(s?.owed_to_platform ?? 0),
      hint: t("centre.dashboard.kpi_to_pay_hint"),
      icon: "pi pi-wallet",
      tone: "bg-primary/10 text-primary",
    },
    {
      label: t("centre.dashboard.kpi_overdue"),
      value: money(s?.overdue_amount ?? 0),
      hint: t(
        "centre.dashboard.kpi_overdue_hint",
        { hours: s?.payment_delay_hours ?? 24 },
        s?.overdue_count ?? 0,
      ),
      icon: "pi pi-clock",
      tone: "bg-amber-500/10 text-amber-600",
      valueClass: s?.overdue_amount ? "text-amber-600" : "text-ink",
    },
    {
      label: t("centre.dashboard.kpi_owed"),
      value: money(s?.owed_to_partner ?? 0),
      hint: t("centre.dashboard.kpi_owed_hint"),
      icon: "pi pi-arrow-down-left",
      tone: "bg-emerald-500/10 text-emerald-600",
    },
  ];
});

// ── Statut d'une vente ──
type SaleState = "settled" | "overdue" | "partial" | "due";

function saleState(sale: PartnerSaleResponse): SaleState {
  if (sale.status === "settled") return "settled";
  if (sale.is_overdue) return "overdue";
  if (sale.status === "partial") return "partial";
  return "due";
}

const BADGES: Record<SaleState, string> = {
  settled: "bg-emerald-500/10 text-emerald-600",
  overdue: "bg-red-500/10 text-red-600",
  partial: "bg-amber-500/10 text-amber-600",
  due: "bg-sky-500/10 text-sky-600",
};

function saleBadge(sale: PartnerSaleResponse) {
  const state = saleState(sale);
  return { label: t(`centre.sales.status.${state}`), class: BADGES[state] };
}

// ── Filtres ──
type FilterKey = "all" | "due" | "overdue" | "settled";
const activeFilter = ref<FilterKey>("all");

const filters = computed(() => {
  const list = salesStore.mySales;
  const count = (fn: (s: PartnerSaleResponse) => boolean) => list.filter(fn).length;
  return [
    { key: "all" as const, label: t("centre.students.filter_all"), count: list.length },
    {
      key: "due" as const,
      label: t("centre.sales.status.due"),
      count: count((s) => ["due", "partial"].includes(saleState(s))),
    },
    {
      key: "overdue" as const,
      label: t("centre.sales.status.overdue"),
      count: count((s) => saleState(s) === "overdue"),
    },
    {
      key: "settled" as const,
      label: t("centre.sales.status.settled"),
      count: count((s) => saleState(s) === "settled"),
    },
  ];
});

const filteredSales = computed(() =>
  salesStore.mySales.filter((s) => {
    const st = saleState(s);
    if (activeFilter.value === "due") return st === "due" || st === "partial";
    if (activeFilter.value === "overdue") return st === "overdue";
    if (activeFilter.value === "settled") return st === "settled";
    return true;
  }),
);

// ── Pagination ──
const first = ref(0);
const rows = ref(10);
const pagedSales = computed(() =>
  filteredSales.value.slice(first.value, first.value + rows.value),
);
watch(activeFilter, () => {
  first.value = 0;
});

onMounted(async () => {
  await Promise.all([salesStore.fetchMySummary(), salesStore.fetchMySales(SALES_LIMIT)]);
  loading.value = false;
});
</script>