<script setup lang="ts">
const { t } = useI18n();
const localePath = useLocalePath();

useSeo({
  title: t("seo.about.title"),
  description: t("seo.about.description"),
});

const valeurs = [
  { key: "format", icon: "pi pi-clone" },
  { key: "clarity", icon: "pi pi-chart-bar" },
  { key: "access", icon: "pi pi-mobile" },
];

const offre = [
  { key: "exams", icon: "pi pi-book" },
  { key: "audio", icon: "pi pi-headphones" },
  { key: "correction", icon: "pi pi-pen-to-square" },
  { key: "progress", icon: "pi pi-chart-line" },
  { key: "payment", icon: "pi pi-wallet" },
  { key: "centres", icon: "pi pi-building" },
];
</script>

<template>
  <div class="bg-canvas">
    <AppPageHero
      icon="pi pi-compass"
      watermark="Über uns"
      :eyebrow="t('about.hero.badge')"
      :title="t('about.hero.title')"
      :subtitle="t('about.hero.subtitle')"
    />

    <!-- Mission -->
    <section class="py-16 sm:py-20">
      <div class="mx-auto grid max-w-6xl items-center gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:gap-16">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-accent-600 dark:text-accent-400">
            {{ t("about.mission.eyebrow") }}
          </p>
          <h2 class="mt-3 font-heading text-2xl font-extrabold text-ink sm:text-4xl">
            {{ t("about.mission.title") }}
          </h2>
          <p class="mt-5 leading-relaxed text-muted sm:text-lg">
            {{ t("about.mission.p1") }}
          </p>
          <p class="mt-4 leading-relaxed text-muted sm:text-lg">
            {{ t("about.mission.p2") }}
          </p>
        </div>

        <div class="rounded-card border border-line bg-card p-6 shadow-soft sm:p-8">
          <p class="font-heading text-lg font-bold text-ink">
            {{ t("about.values.title") }}
          </p>
          <ul class="mt-6 space-y-6">
            <li v-for="v in valeurs" :key="v.key" class="flex gap-4">
              <span class="grid size-11 shrink-0 place-items-center rounded-leaf bg-accent-500/10 text-accent-600 dark:text-accent-400">
                <i :class="v.icon" />
              </span>
              <div>
                <p class="font-semibold text-ink">
                  {{ t(`about.values.items.${v.key}.title`) }}
                </p>
                <p class="mt-1 text-sm leading-relaxed text-muted">
                  {{ t(`about.values.items.${v.key}.desc`) }}
                </p>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Offre -->
    <section class="border-y border-line bg-card-2/50 py-16 sm:py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6">
        <div class="mx-auto max-w-2xl text-center">
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-accent-600 dark:text-accent-400">
            {{ t("about.offer.eyebrow") }}
          </p>
          <h2 class="mt-3 font-heading text-2xl font-extrabold text-ink sm:text-4xl">
            {{ t("about.offer.title") }}
          </h2>
          <p class="mt-4 text-muted sm:text-lg">{{ t("about.offer.subtitle") }}</p>
        </div>

        <div class="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="o in offre"
            :key="o.key"
            class="group rounded-card border border-line bg-card p-6 shadow-soft transition duration-300 ease-spring hover:-translate-y-1 hover:border-primary/30 hover:shadow-lift"
          >
            <span class="grid size-12 place-items-center rounded-leaf bg-primary/10 text-primary transition-transform duration-300 ease-spring group-hover:scale-110">
              <i :class="[o.icon, 'text-lg']" />
            </span>
            <h3 class="mt-5 font-heading text-lg font-bold text-ink">
              {{ t(`about.offer.items.${o.key}.title`) }}
            </h3>
            <p class="mt-2 text-sm leading-relaxed text-muted">
              {{ t(`about.offer.items.${o.key}.desc`) }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Examens couverts (composant de la landing, cartes cliquables) -->
    <LevelsSection />

    <!-- Indépendance -->
    <section class="px-4 sm:px-6">
      <div class="mx-auto flex max-w-6xl gap-4 rounded-card border-l-4 border-accent-500 bg-accent-500/10 p-6 sm:p-8">
        <i class="pi pi-info-circle mt-1 text-xl text-accent-600 dark:text-accent-400" />
        <div>
          <p class="font-heading text-lg font-bold text-ink">
            {{ t("about.independence.title") }}
          </p>
          <p class="mt-2 leading-relaxed text-muted">
            {{ t("about.independence.text") }}
          </p>
        </div>
      </div>
    </section>

    <!-- Centres + CTA -->
    <section class="py-16 sm:py-20">
      <div class="mx-auto grid max-w-6xl gap-6 px-4 sm:px-6 lg:grid-cols-2">
        <div class="flex flex-col rounded-card border border-line bg-card p-6 shadow-soft sm:p-8">
          <span class="grid size-12 place-items-center rounded-leaf bg-primary/10 text-primary">
            <i class="pi pi-building text-lg" />
          </span>
          <h2 class="mt-5 font-heading text-xl font-bold text-ink sm:text-2xl">
            {{ t("about.centres.title") }}
          </h2>
          <p class="mt-3 flex-1 leading-relaxed text-muted">
            {{ t("about.centres.text") }}
          </p>
          <NuxtLink
            :to="localePath('/contact')"
            class="mt-6 inline-flex items-center gap-2 font-semibold text-primary hover:underline"
          >
            {{ t("about.centres.cta") }}
            <i class="pi pi-arrow-right text-xs" />
          </NuxtLink>
        </div>

        <div class="relative overflow-hidden rounded-card bg-zinc-950 p-6 text-white shadow-lift sm:p-8">
          <div class="flag-stripe absolute inset-x-0 top-0 h-1" aria-hidden="true" />
          <div
            class="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-accent-500/20 blur-3xl"
            aria-hidden="true"
          />
          <h2 class="relative font-heading text-xl font-bold sm:text-2xl">
            {{ t("about.cta.title") }}
          </h2>
          <p class="relative mt-3 text-white/70">{{ t("about.cta.subtitle") }}</p>
          <div class="relative mt-6 flex flex-wrap gap-3">
            <AppLinkButton
              :to="localePath('/tarifs')"
              :label="t('about.cta.pricing')"
              icon="pi pi-arrow-right"
              variant="light"
            />
            <NuxtLink
              :to="localePath('/faq')"
              class="inline-flex items-center gap-2 rounded-xl border border-white/15 px-5 py-2.5 font-semibold transition hover:bg-white/10"
            >
              <i class="pi pi-question-circle text-sm" />
              {{ t("about.cta.faq") }}
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>