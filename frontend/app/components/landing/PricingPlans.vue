<template>
  <div>
    <!-- Choix du parcours -->
    <div class="mb-10 flex justify-center">
      <SelectButton
        v-model="selectedTrack"
        :options="trackOptions"
        optionLabel="label"
        optionValue="value"
        :allowEmpty="false"
      />
    </div>

    <!-- Chargement -->
    <div
      v-if="loading"
      class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="i in 3"
        :key="i"
        class="h-96 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- Aucune offre -->
    <div
      v-else-if="plansAffiches.length === 0"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-leaf bg-primary-50 text-primary-700"
      >
        <i class="pi pi-tag text-xl" />
      </span>
      <p class="text-sm text-muted">{{ t("pricing.no_plans") }}</p>
    </div>

    <!-- Cartes -->
    <div
      v-else
      class="grid grid-cols-1 items-stretch gap-6 sm:grid-cols-2 lg:grid-cols-3"
    >
      <div
        v-for="(plan, index) in plansAffiches"
        :key="plan.id"
        class="relative flex flex-col overflow-hidden rounded-card border transition-all duration-300 ease-spring"
        :class="
          index === recommendedIndex
            ? 'border-accent-500/60 bg-zinc-950 text-white shadow-lift lg:scale-105'
            : 'border-line bg-card shadow-soft hover:-translate-y-1 hover:border-accent-500/40 hover:shadow-lift'
        "
      >
        <div
          v-if="index === recommendedIndex"
          class="flag-stripe absolute inset-x-0 top-0 h-1"
          aria-hidden="true"
        />

        <div class="flex flex-1 flex-col p-6 sm:p-7">
          <!-- Durée + badge -->
          <div class="mb-5 flex items-center justify-between gap-2">
            <span
              class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold"
              :class="
                index === recommendedIndex
                  ? 'bg-white/10 text-white'
                  : 'bg-card-2 text-ink'
              "
            >
              <i class="pi pi-calendar text-[11px]" />
              {{ formatDuration(plan.duration_days) }}
            </span>
            <span
              v-if="index === recommendedIndex"
              class="inline-flex items-center gap-1 rounded-full bg-accent-500 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-accent-950"
            >
              <i class="pi pi-star-fill text-[10px]" />
              {{ t("pricing.popular") }}
            </span>
          </div>

          <!-- Nom + description -->
          <h3 class="font-heading text-xl font-bold">{{ plan.name }}</h3>
          <p
            class="mt-2 text-sm"
            :class="index === recommendedIndex ? 'text-white/65' : 'text-muted'"
          >
            {{
              plan.description ||
              `${t("pricing.default_description")} ${formatDuration(plan.duration_days)}`
            }}
          </p>

          <!-- Prix -->
          <div class="my-6 space-y-2">
            <div class="flex items-baseline gap-1.5">
              <span class="font-heading text-4xl font-extrabold tracking-tight">
                {{ plan.price.toLocaleString("fr-FR") }}
              </span>
              <span
                class="text-sm font-medium"
                :class="index === recommendedIndex ? 'text-white/50' : 'text-faint'"
              >
                FCFA
              </span>
              <span
                class="ml-1 text-xs"
                :class="index === recommendedIndex ? 'text-white/50' : 'text-faint'"
              >
                · Mobile Money
              </span>
            </div>

            <p
              class="text-xs"
              :class="index === recommendedIndex ? 'text-white/60' : 'text-muted'"
            >
              {{ t("pricing.full_access_days", { n: plan.duration_days }) }}
            </p>

            <div v-if="plan.price_eur" class="flex items-baseline gap-1.5">
              <span class="font-heading text-2xl font-bold tracking-tight">
                {{ eur(plan.price_eur) }}
              </span>
              <span
                class="inline-flex items-center gap-1 text-xs"
                :class="index === recommendedIndex ? 'text-white/50' : 'text-faint'"
              >
                · <i class="pi pi-credit-card text-[11px]" />
                {{ t("pricing.by_card") }}
              </span>
            </div>

            <p
              v-if="plan.ai_credits"
              class="mt-3! inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold"
              :class="
                index === recommendedIndex
                  ? 'bg-accent-500/15 text-accent-400'
                  : 'bg-primary/10 text-primary'
              "
            >
              <i class="pi pi-sparkles text-[11px]" />
              {{ t("pricing.ai_credits", plan.ai_credits) }}
            </p>
          </div>

          <!-- Fonctionnalités -->
          <ul
            v-if="featuresTraduites(plan.features).length"
            class="mb-7 flex-1 space-y-2.5 text-sm"
          >
            <li
              v-for="featKey in featuresTraduites(plan.features)"
              :key="featKey"
              class="flex items-start gap-2.5"
              :class="index === recommendedIndex ? 'text-white/85' : 'text-ink'"
            >
              <i class="pi pi-check-circle mt-0.5 text-sm text-accent-500" />
              {{ t(`pricing.features.${featKey}`) }}
            </li>
          </ul>
          <div v-else class="flex-1" />

          <!-- CTA -->
          <div class="space-y-2.5">
            <AppButton
              variant="accent"
              block
              size="large"
              icon="pi pi-arrow-right"
              icon-pos="right"
              :label="t('pricing.cta')"
              @click="selectPlan(plan)"
            />
            <a
              :href="whatsappLink(plan)"
              target="_blank"
              rel="noopener"
              class="flex h-11 w-full items-center justify-center gap-2 rounded-leaf border text-sm font-semibold transition-colors"
              :class="
                index === recommendedIndex
                  ? 'border-white/15 bg-white/5 text-white hover:border-white/30 hover:bg-white/10'
                  : 'border-line bg-card text-ink hover:border-emerald-500/50'
              "
            >
              <i class="pi pi-whatsapp text-emerald-500" />
              {{ t("pricing.buy_whatsapp") }}
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Moyens de paiement -->
    <div class="mt-14 text-center">
      <p class="mb-4 text-sm font-medium text-muted">
        {{ t("pricing.payment_methods") }}
      </p>
      <div class="flex flex-wrap items-center justify-center gap-3">
        <span
          v-for="moyen in moyensPaiement"
          :key="moyen.alt"
          class="flex h-12 w-20 items-center justify-center rounded-leaf border border-line bg-white p-2 shadow-soft"
        >
          <img
            :src="moyen.src"
            :alt="moyen.alt"
            loading="lazy"
            class="max-h-full max-w-full object-contain"
          />
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse } from "#shared/api";
import { SITE } from "~/config/site";

const { t, te, locale } = useI18n();
const authStore = useAuthStore();
const { activePlans, loading, loadPlans, formatDuration } = usePlans();
const { retenirRedirection } = useChoixExamen();

const featuresTraduites = (features?: string[] | null) =>
  (features ?? []).filter((k) => te(`pricing.features.${k}`));

const eur = (n: number) =>
  Number(n).toLocaleString(
    ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ??
      "en-GB",
    { style: "currency", currency: "EUR" },
  );

const moyensPaiement = [
  { src: "/images/orange.jpg", alt: "Orange Money" },
  { src: "/images/momo.jpg", alt: "MTN MoMo" },
  { src: "/images/visa.png", alt: "Visa" },
  { src: "/images/master.png", alt: "Mastercard" },
];

// ── Parcours affiché ──
type Track = "standard" | "start_deutsch";
const selectedTrack = ref<Track>("standard");

const trackOptions = computed(() => [
  { label: t("pricing.tracks.standard"), value: "standard" },
  { label: t("pricing.tracks.start_deutsch"), value: "start_deutsch" },
]);

const plansAffiches = computed(() =>
  activePlans.value.filter(
    (p) => (p.track ?? "standard") === selectedTrack.value,
  ),
);

// Badge Populaire : le plan coché en admin, sinon celui du milieu
const recommendedIndex = computed(() => {
  const list = plansAffiches.value;
  if (list.length === 0) return -1;
  const i = list.findIndex((p) => p.is_popular);
  return i >= 0 ? i : Math.floor(list.length / 2);
});

// Achat par WhatsApp : message prérempli avec la formule choisie
const whatsappLink = (plan: PlanResponse) => {
  const msg = t("pricing.whatsapp_message", {
    plan: plan.name,
    days: plan.duration_days,
    price: plan.price.toLocaleString("fr-FR"),
  });
  return `https://wa.me/${SITE.phone}?text=${encodeURIComponent(msg)}`;
};

// Connecté : paiement direct. Invité : on retient l'offre et on ouvre l'inscription.
const selectPlan = (plan: PlanResponse) => {
  const chemin = `/dashboard/paiement?plan_id=${plan.id}`;
  if (authStore.isAuthenticated) {
    navigateTo(useLocalePath()(chemin));
  } else {
    retenirRedirection(chemin);
  }
};

onMounted(() => {
  if (!activePlans.value.length) loadPlans();
});
</script>