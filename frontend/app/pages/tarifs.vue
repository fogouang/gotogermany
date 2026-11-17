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
        <PricingPlans />
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
import { SITE } from "~/config/site";

definePageMeta({ layout: "default" });

const { t } = useI18n();
const localePath = useLocalePath();
</script>