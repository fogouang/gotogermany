<!-- pages/admin/index.vue -->
<template>
  <div class="space-y-6">
    <!-- ── Indicateurs ── -->
    <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
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
        <p class="mt-3 text-2xl font-bold text-ink">
          <span v-if="loading" class="inline-block h-7 w-20 animate-pulse rounded bg-card-2" />
          <template v-else>{{ kpi.value }}</template>
        </p>
        <p class="mt-1 text-xs text-muted">{{ kpi.hint }}</p>
      </div>
    </div>

    <FreeAccessToggle />

    <!-- ── Accès rapides ── -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
      <NuxtLink
        v-for="s in shortcuts"
        :key="s.to"
        :to="s.to"
        class="flex items-center gap-3 rounded-card border border-line bg-card p-4 shadow-soft transition-colors hover:border-primary/30 hover:bg-primary/5"
      >
        <span
          class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary"
        >
          <i :class="s.icon" class="text-sm" />
        </span>
        <span class="min-w-0">
          <span class="block truncate text-sm font-medium text-ink">{{ s.label }}</span>
          <span class="block truncate text-[11px] text-muted">{{ s.hint }}</span>
        </span>
      </NuxtLink>
    </div>

    <!-- ── Partenaires à surveiller ── -->
    <section
      class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
    >
      <header class="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h3 class="font-semibold text-ink">Partenaires à surveiller</h3>
          <p class="text-xs text-muted">
            Paiements en retard ou activations bloquées
          </p>
        </div>
        <NuxtLink
          to="/admin/partners"
          class="flex items-center gap-1 text-xs font-medium text-primary hover:underline"
        >
          Tous les partenaires
          <i class="pi pi-arrow-right text-[10px]" />
        </NuxtLink>
      </header>

      <div v-if="loading" class="space-y-3 p-5">
        <div v-for="n in 3" :key="n" class="h-12 animate-pulse rounded-leaf bg-card-2" />
      </div>

      <div v-else-if="salesError" class="px-5 py-8 text-center text-sm text-red-600">
        {{ salesError }}
      </div>

      <div
        v-else-if="watchList.length === 0"
        class="flex items-center gap-3 px-5 py-6"
      >
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600"
        >
          <i class="pi pi-check" />
        </span>
        <div>
          <p class="text-sm font-medium text-ink">Tout est à jour</p>
          <p class="text-xs text-muted">Aucun retard ni blocage chez les partenaires.</p>
        </div>
      </div>

      <ul v-else class="divide-y divide-line">
        <li
          v-for="p in watchList"
          :key="p.partner_type + p.partner_id"
          class="flex items-center gap-4 px-5 py-3"
        >
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf"
            :class="
              p.partner_type === 'center'
                ? 'bg-primary/10 text-primary'
                : 'bg-amber-500/10 text-amber-600'
            "
          >
            <i
              :class="p.partner_type === 'center' ? 'pi pi-building' : 'pi pi-star'"
              class="text-sm"
            />
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-ink">{{ p.name }}</p>
            <p class="truncate text-xs text-muted">
              {{ p.partner_type === "center" ? "Centre" : "Ambassadeur" }}
              <template v-if="p.block_reason"> · {{ p.block_reason }}</template>
              <template v-else-if="p.overdue_count">
                · {{ p.overdue_count }} vente(s) en retard
              </template>
            </p>
          </div>
          <div class="text-right">
            <p class="text-sm font-semibold text-red-600">
              {{ fcfa(p.overdue_amount || p.owed_to_platform) }}
            </p>
            <span
              class="inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold"
              :class="
                p.is_blocked
                  ? 'bg-red-500/10 text-red-600'
                  : 'bg-amber-500/10 text-amber-600'
              "
            >
              {{ p.is_blocked ? "Bloqué" : "En retard" }}
            </span>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import FreeAccessToggle from "~/components/admin/FreeAccessToggle.vue";

definePageMeta({ layout: "admin" });

const usersStore = useAdminUsersStore();
const centersStore = useAdminCentersStore();
const salesStore = useSalesStore();

const loading = ref(true);
const salesError = ref<string | null>(null);

const fcfa = (n: number) => `${new Intl.NumberFormat("fr-FR").format(n)} FCFA`;

// ── Indicateurs ──
const newUsersThisWeek = computed(() => {
  const limit = Date.now() - 7 * 24 * 60 * 60 * 1000;
  return usersStore.users.filter((u) => new Date(u.created_at).getTime() >= limit)
    .length;
});

const activeCenters = computed(
  () => centersStore.centers.filter((c) => c.is_active).length,
);

const kpis = computed(() => [
  {
    label: "Utilisateurs",
    value: usersStore.users.length,
    hint: `+${newUsersThisWeek.value} ces 7 derniers jours`,
    icon: "pi pi-users",
    tone: "bg-primary/10 text-primary",
  },
  {
    label: "Centres actifs",
    value: `${activeCenters.value} / ${centersStore.centers.length}`,
    hint: `${salesStore.partners.length} partenaires au total`,
    icon: "pi pi-building",
    tone: "bg-sky-500/10 text-sky-600",
  },
  {
    label: "À encaisser",
    value: fcfa(salesStore.totalOwedToPlatform),
    hint: "Dû par les partenaires",
    icon: "pi pi-arrow-down-left",
    tone: "bg-emerald-500/10 text-emerald-600",
  },
  {
    label: "À reverser",
    value: fcfa(salesStore.totalOwedToPartners),
    hint: `${salesStore.blockedPartners.length} partenaire(s) bloqué(s)`,
    icon: "pi pi-arrow-up-right",
    tone: "bg-amber-500/10 text-amber-600",
  },
]);

// ── Partenaires à surveiller : bloqués d'abord, puis par retard ──
const watchList = computed(() =>
  salesStore.partners
    .filter((p) => p.is_blocked || p.overdue_amount > 0)
    .sort(
      (a, b) =>
        Number(b.is_blocked) - Number(a.is_blocked) ||
        b.overdue_amount - a.overdue_amount,
    )
    .slice(0, 6),
);

// ── Raccourcis ──
const shortcuts = [
  { to: "/admin/users", label: "Utilisateurs", hint: "Comptes et accès", icon: "pi pi-users" },
  { to: "/admin/centers", label: "Centres", hint: "Directeurs et crédits IA", icon: "pi pi-building" },
  { to: "/admin/partners", label: "Partenaires", hint: "Ventes et règlements", icon: "pi pi-wallet" },
  { to: "/admin/paiements-manuels", label: "Paiements manuels", hint: "Accès et pass journalier", icon: "pi pi-money-bill" },
  { to: "/admin/exams", label: "Examens", hint: "Sujets publics et privés", icon: "pi pi-book" },
  { to: "/admin/plans", label: "Plans", hint: "Prix et durées", icon: "pi pi-tag" },
];

onMounted(async () => {
  const [, , sales] = await Promise.all([
    usersStore.users.length === 0 ? usersStore.fetchUsers() : Promise.resolve(),
    centersStore.centers.length === 0 ? centersStore.fetchCenters() : Promise.resolve(),
    salesStore.fetchPartners(),
  ]);
  if (!sales.success) salesError.value = sales.error;
  loading.value = false;
});
</script>