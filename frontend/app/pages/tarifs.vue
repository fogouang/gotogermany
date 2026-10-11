<template>
  <div class="bg-canvas">
    <AppPageHero
      center
      watermark="Preise"
      :title="t('pricing.title')"
      :subtitle="t('pricing.subtitle')"
    >
      <p
        class="mt-5 inline-flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400"
      >
        <i class="pi pi-bolt text-[11px]" />
        {{ t("pricing.immediate_access") }}
      </p>
    </AppPageHero>

    <!-- Offres -->
    <section class="pb-12 pt-12">
      <div class="mx-auto max-w-5xl px-4 sm:px-6">
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
          v-else-if="activePlans.length === 0"
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
            v-for="(plan, index) in activePlans"
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
                :class="
                  index === recommendedIndex ? 'text-white/65' : 'text-muted'
                "
              >
                {{
                  plan.description ||
                  `${t("pricing.default_description")} ${formatDuration(plan.duration_days)}`
                }}
              </p>

              <!-- Prix -->
              <div class="my-6">
                <div class="flex items-baseline gap-1.5">
                  <span
                    class="font-heading text-4xl font-extrabold tracking-tight"
                  >
                    {{ plan.price.toLocaleString("fr-FR") }}
                  </span>
                  <span
                    class="text-sm font-medium"
                    :class="
                      index === recommendedIndex
                        ? 'text-white/60'
                        : 'text-faint'
                    "
                  >
                    FCFA
                  </span>
                </div>
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
                  :class="
                    index === recommendedIndex ? 'text-white/85' : 'text-ink'
                  "
                >
                  <i
                    class="pi pi-check-circle mt-0.5 text-sm text-accent-500"
                  />
                  {{ t(`pricing.features.${featKey}`) }}
                </li>
              </ul>
              <div v-else class="flex-1" />

              <!-- CTA -->
              <AppButton
                variant="accent"
                block
                size="large"
                icon="pi pi-arrow-right"
                icon-pos="right"
                :label="t('pricing.cta')"
                @click="selectPlan(plan)"
              />
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
    </section>

    <!-- Centres de formation -->
    <section class="pb-16 sm:pb-24">
      <div class="mx-auto max-w-5xl px-4 sm:px-6">
        <div
          class="flex flex-col items-start gap-6 rounded-card border border-line bg-card p-6 shadow-soft sm:p-8 md:flex-row md:items-center"
        >
          <span
            class="flex size-14 shrink-0 items-center justify-center rounded-leaf bg-accent-500/15 text-accent-700 dark:text-accent-400"
          >
            <i class="pi pi-building text-2xl" />
          </span>
          <div class="flex-1">
            <h2 class="font-heading text-xl font-bold text-ink">
              {{ t("pricing.centres_title") }}
            </h2>
            <p class="mt-1.5 text-sm leading-relaxed text-muted">
              {{ t("pricing.centres_desc") }}
            </p>
          </div>
          <div class="flex w-full flex-wrap gap-2 md:w-auto">
            <AppButton
              variant="gradient"
              icon="pi pi-envelope"
              :label="t('pricing.centres_cta')"
              @click="navigateTo(localePath('/contact'))"
            />
            <a
              :href="`https://wa.me/${SITE.phone}`"
              target="_blank"
              rel="noopener"
              class="inline-flex h-10 items-center gap-2 rounded-leaf border border-line bg-card px-4 text-sm font-semibold text-ink transition-colors hover:border-accent-500/50"
            >
              <i class="pi pi-whatsapp text-emerald-500" />
              WhatsApp
            </a>
          </div>
        </div>

        <p class="mt-6 text-center text-sm text-muted">
          {{ t("pricing.faq_text") }}
          <NuxtLink
            :to="localePath('/faq')"
            class="font-semibold text-primary hover:underline"
          >
            {{ t("pricing.faq_link") }}
          </NuxtLink>
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { PlanResponse } from "#shared/api";
import { SITE } from "~/config/site";

definePageMeta({ layout: "default" });

const { t, te } = useI18n();

const localePath = useLocalePath();
const authStore = useAuthStore();
const { activePlans, loading, loadPlans, formatDuration } = usePlans();
const { retenirRedirection } = useChoixExamen();

const featuresTraduites = (features?: string[] | null) =>
  (features ?? []).filter((k) => te(`pricing.features.${k}`));

const moyensPaiement = [
  { src: "/images/orange.jpg", alt: "Orange Money" },
  { src: "/images/momo.jpg", alt: "MTN MoMo" },
  { src: "/images/visa.png", alt: "Visa" },
  { src: "/images/master.png", alt: "Mastercard" },
  { src: "/images/paypal.png", alt: "PayPal" },
];

const recommendedIndex = computed(() => {
  const len = activePlans.value.length;
  if (len === 0) return -1;
  return Math.floor(len / 2);
});

// Connecté : paiement direct. Invité : on retient l'offre et on ouvre l'inscription,
// il arrivera sur le paiement juste après.
const selectPlan = (plan: PlanResponse) => {
  const chemin = `/dashboard/paiement?plan_id=${plan.id}`;
  if (authStore.isAuthenticated) {
    navigateTo(chemin);
  } else {
    retenirRedirection(chemin);
  }
};

onMounted(loadPlans);
</script>
