<!-- pages/referrals/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Chargement ── -->
    <div v-if="store.loading && !store.dashboard" class="space-y-4">
      <div class="h-32 animate-pulse rounded-card bg-card-2" />
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div v-for="n in 4" :key="n" class="h-24 animate-pulse rounded-card bg-card-2" />
      </div>
      <div class="h-64 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="store.error"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ store.error }}
    </div>

    <template v-else-if="store.dashboard">
      <!-- ── Alerte : activations coupées ── -->
      <div
        v-if="activationBlocked"
        class="flex items-start gap-3 rounded-card border border-red-500/30 bg-red-500/5 p-4 text-sm"
      >
        <i class="pi pi-lock mt-0.5 text-red-600" />
        <div>
          <p class="font-semibold text-red-600">{{ t("referrals.blocked_title") }}</p>
          <p class="mt-0.5 text-muted">
            {{ sales.mySummary?.block_reason || t("referrals.blocked_text") }}
          </p>
        </div>
      </div>

      <!-- ── Lien de parrainage ── -->
      <section class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
        <p class="mb-3 text-sm font-semibold text-ink">{{ t("referrals.your_link") }}</p>
        <div class="flex flex-col gap-2 sm:flex-row">
          <InputText :value="store.referralLink" readonly class="min-w-0 flex-1 font-mono text-sm" @focus="($event.target as HTMLInputElement).select()" />
          <div class="flex gap-2">
            <Button
              :label="copied ? t('referrals.copied') : t('referrals.copy')"
              :icon="copied ? 'pi pi-check' : 'pi pi-copy'"
              :severity="copied ? 'success' : undefined"
              outlined
              class="flex-1 sm:flex-none"
              @click="copyLink"
            />
            <a
              :href="whatsappShareUrl"
              target="_blank"
              rel="noopener"
              class="inline-flex flex-1 items-center justify-center gap-2 rounded-leaf border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-600 transition-colors hover:bg-emerald-500/15 sm:flex-none"
            >
              <i class="pi pi-whatsapp" />
              {{ t("referrals.share_whatsapp") }}
            </a>
          </div>
        </div>
      </section>

      <!-- ── Chiffres ── -->
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div v-for="s in stats" :key="s.label" class="rounded-card border border-line bg-card p-4 shadow-soft">
          <div class="mb-3 flex size-9 items-center justify-center rounded-leaf" :class="s.iconClass">
            <i :class="s.icon" class="text-sm" />
          </div>
          <p class="text-xl font-bold leading-none" :class="s.tone ?? 'text-ink'">{{ s.value }}</p>
          <p class="mt-1.5 text-xs text-muted">{{ s.label }}</p>
        </div>
      </div>

      <p
        v-if="sales.mySummary && sales.mySummary.overdue_amount > 0"
        class="flex items-center gap-2 rounded-leaf bg-amber-500/10 px-4 py-2.5 text-sm text-amber-600"
      >
        <i class="pi pi-clock text-xs" />
        {{ t("referrals.overdue_notice", { amount: fcfa(sales.mySummary.overdue_amount) }, sales.mySummary.overdue_count) }}
      </p>

      <!-- ── Filleuls ── -->
      <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <header class="flex flex-col gap-3 border-b border-line px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 class="font-semibold text-ink">
            {{ t("referrals.your_referrals") }}
            <span class="font-normal text-muted">· {{ store.referredUsers.length }}</span>
          </h2>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="f in filters"
              :key="f.key"
              type="button"
              class="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
              :class="filter === f.key ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
              @click="filter = f.key"
            >
              {{ f.label }} · {{ f.count }}
            </button>
          </div>
        </header>

        <div v-if="!store.referredUsers.length" class="flex flex-col items-center gap-2 px-6 py-12 text-center">
          <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            <i class="pi pi-users" />
          </span>
          <p class="text-sm text-muted">{{ t("referrals.no_referrals_yet") }}</p>
        </div>

        <p v-else-if="!visibleReferrals.length" class="px-5 py-10 text-center text-sm text-muted">
          {{ t("referrals.empty_filter") }}
        </p>

        <ul v-else class="divide-y divide-line">
          <li
            v-for="ru in visibleReferrals"
            :key="ru.user_id"
            class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 sm:px-5"
          >
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-full text-xs font-bold"
              :class="ru.has_paid ? 'bg-primary/10 text-primary' : 'bg-card-2 text-muted'"
            >
              {{ initials(ru.name) }}
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-ink">{{ ru.name }}</p>
              <p class="text-xs text-muted">{{ t("referrals.joined_on", { date: formatDate(ru.joined_at) }) }}</p>
            </div>

            <template v-if="ru.has_paid">
              <div class="text-right">
                <span class="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600">
                  {{ t("referrals.paid") }}
                </span>
                <p class="mt-1 text-xs font-semibold text-emerald-600">+{{ fcfa(ru.total_earned_from_this_user) }}</p>
              </div>
            </template>
            <template v-else>
              <span class="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600">
                {{ t("referrals.not_paid_yet") }}
              </span>
              <Button
                :label="t('referrals.validate_payment')"
                icon="pi pi-bolt"
                size="small"
                :disabled="activationBlocked"
                @click="openValidateDialog(ru)"
              />
            </template>
          </li>
        </ul>
      </section>
    </template>

    <!-- ══ Activation de l'accès ══ -->
    <Dialog
      v-model:visible="validateDialog"
      :header="t('referrals.validate_payment_for', { name: selectedReferral?.name })"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleValidatePayment">
        <p class="flex items-start gap-2 rounded-leaf bg-card-2 px-3 py-2.5 text-xs text-muted">
          <i class="pi pi-info-circle mt-0.5 text-[11px]" />
          {{ t("referrals.activation_hint") }}
        </p>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("referrals.level") }}</label>
          <Select
            v-model="selectedLevelId"
            :options="allLevels"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('referrals.select_level')"
            class="w-full"
            filter
          />
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("referrals.plan") }}</label>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <button
              v-for="plan in allPlans"
              :key="plan.value"
              type="button"
              class="rounded-leaf border px-3 py-2.5 text-left transition-colors"
              :class="selectedPlanId === plan.value ? 'border-primary bg-primary/5 ring-1 ring-primary/30' : 'border-line hover:border-primary/30'"
              @click="selectedPlanId = plan.value"
            >
              <p class="text-sm font-medium text-ink">{{ plan.label }}</p>
              <p class="text-xs text-muted">{{ fcfa(plan.price) }}</p>
            </button>
          </div>
        </div>

        <Message v-if="store.ambassadorError" severity="error" :closable="false">
          {{ store.ambassadorError }}
        </Message>
      </form>
      <template #footer>
        <Button :label="t('referrals.cancel')" text @click="validateDialog = false" />
        <Button
          :label="t('referrals.confirm_validation')"
          icon="pi pi-check"
          :loading="store.settingAmbassador"
          :disabled="!selectedLevelId || !selectedPlanId"
          @click="handleValidatePayment"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useReferralsStore } from "~/stores/referrals";

definePageMeta({ layout: "ambassador", watermark: "Empfehlung" });

const { t, locale } = useI18n();
useHead({ title: t("referrals.page_title") });

const store = useReferralsStore();
const sales = useSalesStore();
const examsStore = useExamsStore();
const plansStore = usePlansStore();
const toast = useToast();

const fcfa = (n: number) => `${Math.round(n).toLocaleString(locale.value)} FCFA`;

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(locale.value, { day: "2-digit", month: "short", year: "numeric" });

// ── Lien ──
const copied = ref(false);

const whatsappShareUrl = computed(() => {
  const text = t("referrals.whatsapp_message", { link: store.referralLink });
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
});

async function copyLink() {
  try {
    await navigator.clipboard.writeText(store.referralLink);
    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch {
    // Presse-papiers indisponible : le champ reste sélectionnable à la main
  }
}

// ── Solde avec la plateforme (nouveau modèle de ventes) ──
const activationBlocked = computed(
  () => !!sales.mySummary && (sales.mySummary.is_blocked || !sales.mySummary.can_activate),
);

const stats = computed(() => {
  const s = sales.mySummary;
  return [
    {
      label: t("referrals.referred_count"),
      value: String(store.referredCount),
      icon: "pi pi-users",
      iconClass: "bg-primary/10 text-primary",
    },
    {
      label: t("referrals.total_earnings"),
      value: fcfa(store.totalEarnings),
      tone: "text-emerald-600",
      icon: "pi pi-wallet",
      iconClass: "bg-emerald-500/10 text-emerald-600",
    },
    {
      label: t("referrals.owed_to_platform"),
      value: s ? fcfa(s.owed_to_platform) : "-",
      tone: s && s.owed_to_platform > 0 ? "text-amber-600" : undefined,
      icon: "pi pi-arrow-up-right",
      iconClass: "bg-amber-500/15 text-amber-600",
    },
    {
      label: t("referrals.owed_to_you"),
      value: s ? fcfa(s.owed_to_partner) : "-",
      icon: "pi pi-arrow-down-left",
      iconClass: "bg-sky-500/10 text-sky-600",
    },
  ];
});

// ── Filtres des filleuls ──
type FilterKey = "all" | "unpaid" | "paid";
const filter = ref<FilterKey>("all");

const filters = computed(() => {
  const list = store.referredUsers;
  return [
    { key: "all" as const, label: t("referrals.filter_all"), count: list.length },
    { key: "unpaid" as const, label: t("referrals.not_paid_yet"), count: list.filter((r) => !r.has_paid).length },
    { key: "paid" as const, label: t("referrals.paid"), count: list.filter((r) => r.has_paid).length },
  ];
});

// À activer d'abord, puis les plus récents
const visibleReferrals = computed(() =>
  [...store.referredUsers]
    .filter((r) => filter.value === "all" || (filter.value === "paid") === r.has_paid)
    .sort(
      (a, b) =>
        Number(a.has_paid) - Number(b.has_paid) ||
        new Date(b.joined_at).getTime() - new Date(a.joined_at).getTime(),
    ),
);

// ── Activation de l'accès ──
const validateDialog = ref(false);
const selectedReferral = ref<{ user_id: string; name: string } | null>(null);
const selectedLevelId = ref("");
const selectedPlanId = ref("");

const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

const allPlans = computed(() =>
  plansStore.sortedPlans.map((plan) => ({ label: plan.name, value: plan.id, price: plan.price })),
);

function openValidateDialog(ru: { user_id: string; name: string }) {
  selectedReferral.value = { user_id: ru.user_id, name: ru.name };
  selectedLevelId.value = "";
  selectedPlanId.value = "";
  store.ambassadorError = null;
  validateDialog.value = true;
}

async function handleValidatePayment() {
  if (!selectedReferral.value || !selectedLevelId.value || !selectedPlanId.value) return;
  const name = selectedReferral.value.name;
  const res = await store.validateManualPayment(
    selectedReferral.value.user_id,
    selectedLevelId.value,
    selectedPlanId.value,
  );
  if (res.success) {
    validateDialog.value = false;
    toast.add({ severity: "success", summary: t("referrals.activated", { name }), life: 3500 });
    // L'activation crée une vente : le solde avec la plateforme change
    await sales.fetchMySummary();
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchDashboard(),
    sales.fetchMySummary(),
    examsStore.catalog.length === 0 ? examsStore.fetchCatalog() : Promise.resolve(),
    plansStore.plans.length === 0 ? plansStore.fetchPlans() : Promise.resolve(),
  ]);
});
</script>