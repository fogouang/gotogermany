<!-- pages/centre/dashboard.vue -->
<template>
  <div class="space-y-6">
    <!-- ── Statut d'activation ── -->
    <div
      v-if="summary && (summary.is_blocked || !summary.can_activate)"
      class="flex items-start gap-3 rounded-card border border-red-500/30 bg-red-500/5 p-4"
    >
      <i class="pi pi-lock mt-0.5 text-red-600" />
      <div>
        <p class="text-sm font-semibold text-red-600">
          {{ t("centre.dashboard.blocked_title") }}
        </p>
        <p class="mt-0.5 text-sm text-muted">
          {{ summary.block_reason || t("centre.dashboard.blocked_default") }}
        </p>
      </div>
    </div>

    <div
      v-else-if="summary && summary.overdue_count > 0"
      class="flex items-start gap-3 rounded-card border border-amber-500/30 bg-amber-500/5 p-4"
    >
      <i class="pi pi-clock mt-0.5 text-amber-600" />
      <p class="text-sm text-ink">
        {{
          t(
            "centre.dashboard.overdue_alert",
            {
              hours: summary.payment_delay_hours,
              amount: money(summary.overdue_amount),
            },
            summary.overdue_count,
          )
        }}
      </p>
    </div>

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
        <p
          class="mt-3 text-2xl font-bold"
          :class="kpi.valueClass ?? 'text-ink'"
        >
          <span
            v-if="loadingSummary"
            class="inline-block h-7 w-24 animate-pulse rounded bg-card-2"
          />
          <template v-else>{{ kpi.value }}</template>
        </p>
        <p class="mt-1 text-xs text-muted">{{ kpi.hint }}</p>
      </div>
    </div>

    <p v-if="summaryError" class="text-sm text-red-600">{{ summaryError }}</p>

    <!-- ── Lien d'inscription + demandes en attente ── -->
    <CentreJoinLinkCard />
    <CentreJoinRequestsPanel />

    <!-- ── Plafond d'impayés ── -->
    <section
      v-if="summary && summary.unpaid_limit"
      class="rounded-card border border-line bg-card p-5 shadow-soft"
    >
      <div class="mb-2 flex items-center justify-between gap-3 text-sm">
        <span class="font-medium text-ink">{{
          t("centre.dashboard.limit_title")
        }}</span>
        <span class="text-muted">
          {{ money(summary.owed_to_platform) }} /
          {{ money(summary.unpaid_limit) }}
        </span>
      </div>
      <div class="h-2 w-full overflow-hidden rounded-full bg-card-2">
        <div
          class="h-full rounded-full transition-all"
          :class="limitBarColor"
          :style="{ width: limitPercent + '%' }"
        />
      </div>
      <p class="mt-2 text-xs text-muted">
        {{ t("centre.dashboard.limit_text") }}
      </p>
    </section>

    <!-- ── Dernières activations ── -->
    <section
      class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
    >
      <header class="border-b border-line px-5 py-4">
        <h3 class="font-semibold text-ink">
          {{ t("centre.dashboard.recent_title") }}
        </h3>
        <p class="text-xs text-muted">
          {{ t("centre.dashboard.recent_text") }}
        </p>
      </header>

      <div v-if="loadingSales" class="space-y-3 p-5">
        <div
          v-for="n in 4"
          :key="n"
          class="h-10 animate-pulse rounded-leaf bg-card-2"
        />
      </div>

      <div
        v-else-if="salesStore.mySales.length === 0"
        class="flex flex-col items-center gap-2 px-5 py-10 text-center"
      >
        <span
          class="flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary"
        >
          <i class="pi pi-shopping-bag" />
        </span>
        <p class="text-sm font-medium text-ink">
          {{ t("centre.dashboard.empty_title") }}
        </p>
        <p class="text-xs text-muted">{{ t("centre.dashboard.empty_text") }}</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-line text-left text-xs text-muted">
            <tr>
              <th class="px-5 py-3 font-medium">
                {{ t("centre.dashboard.col_student") }}
              </th>
              <th class="px-5 py-3 font-medium">
                {{ t("centre.dashboard.col_plan") }}
              </th>
              <th class="px-5 py-3 text-right font-medium">
                {{ t("centre.dashboard.col_price") }}
              </th>
              <th class="px-5 py-3 text-right font-medium">
                {{ t("centre.dashboard.col_remaining") }}
              </th>
              <th class="px-5 py-3 font-medium">
                {{ t("centre.dashboard.col_status") }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-line">
            <tr v-for="sale in recentSales" :key="sale.id">
              <td class="px-5 py-3">
                <p class="font-medium text-ink">{{ sale.student_name }}</p>
                <p class="text-xs text-muted">
                  {{ formatDate(sale.created_at) }}
                </p>
              </td>
              <td class="px-5 py-3 text-muted">{{ sale.plan_name || "-" }}</td>
              <td class="whitespace-nowrap px-5 py-3 text-right text-ink">
                {{ money(sale.price) }}
              </td>
              <td
                class="whitespace-nowrap px-5 py-3 text-right font-medium text-ink"
              >
                {{
                  sale.direction === "partner_owes"
                    ? money(sale.remaining)
                    : "-"
                }}
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
    </section>
  </div>
</template>

<script setup lang="ts">
import type { PartnerSaleResponse } from "#shared/api";
import CentreJoinLinkCard from "~/components/centre/JoinLinkCard.vue";
import CentreJoinRequestsPanel from "~/components/centre/JoinRequestsPanel.vue";

definePageMeta({ layout: "centre", watermark: "Übersicht" });

const { t, locale } = useI18n();
const salesStore = useSalesStore();

const money = (n: number) =>
  `${new Intl.NumberFormat(locale.value).format(n)} FCFA`;
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
  });

// ── Solde partenaire ──
const loadingSummary = ref(true);
const summaryError = ref<string | null>(null);
const summary = computed(() => salesStore.mySummary);

const bloque = computed(() => {
  const s = summary.value;
  return !!s && (s.is_blocked || !s.can_activate);
});

const kpis = computed(() => {
  const s = summary.value;
  return [
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
    {
      label: t("centre.dashboard.kpi_activations"),
      value: s
        ? bloque.value
          ? t("centre.dashboard.suspended")
          : t("centre.dashboard.open")
        : "-",
      hint: s?.unpaid_limit
        ? t("centre.dashboard.limit_hint", { amount: money(s.unpaid_limit) })
        : t("centre.dashboard.no_limit"),
      icon: bloque.value ? "pi pi-lock" : "pi pi-lock-open",
      tone: bloque.value
        ? "bg-red-500/10 text-red-600"
        : "bg-emerald-500/10 text-emerald-600",
      valueClass: bloque.value ? "text-red-600" : "text-emerald-600",
    },
  ];
});

const limitPercent = computed(() => {
  const s = summary.value;
  if (!s?.unpaid_limit) return 0;
  return Math.min(100, Math.round((s.owed_to_platform / s.unpaid_limit) * 100));
});

const limitBarColor = computed(() => {
  if (limitPercent.value >= 90) return "bg-red-500";
  if (limitPercent.value >= 70) return "bg-amber-500";
  return "bg-emerald-500";
});

// ── Ventes ──
const loadingSales = ref(true);
const recentSales = computed(() => salesStore.mySales.slice(0, 8));

function saleBadge(sale: PartnerSaleResponse) {
  if (sale.status === "settled")
    return {
      label: t("centre.sales.status.settled"),
      class: "bg-emerald-500/10 text-emerald-600",
    };
  if (sale.is_overdue)
    return {
      label: t("centre.sales.status.overdue"),
      class: "bg-red-500/10 text-red-600",
    };
  if (sale.status === "partial")
    return {
      label: t("centre.sales.status.partial"),
      class: "bg-amber-500/10 text-amber-600",
    };
  return {
    label: t("centre.sales.status.due"),
    class: "bg-sky-500/10 text-sky-600",
  };
}

onMounted(async () => {
  const [sum] = await Promise.all([
    salesStore.fetchMySummary(),
    salesStore.fetchMySales(20),
  ]);
  if (!sum.success) summaryError.value = sum.error;
  loadingSummary.value = false;
  loadingSales.value = false;
});
</script>
