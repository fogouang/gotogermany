<!-- pages/dashboard/methodologie/index.vue -->
<!--
  Page temporaire : le guide complet est en cours de mise à jour à partir
  des sources officielles (telc, Goethe, ÖSD). L'ancien contenu est conservé
  dans -index.vue (ignoré par Nuxt) pour être repris.
-->
<template>
  <div class="space-y-6">
    <header>
      <p class="mb-1 text-xs font-bold uppercase tracking-widest text-primary">
        {{ t("methodology.eyebrow") }}
      </p>
      <h1 class="text-2xl font-bold text-ink">{{ t("methodology.title") }}</h1>
      <p class="mt-1 text-sm text-muted">{{ t("methodology.subtitle") }}</p>
    </header>

    <section class="rounded-card border border-line bg-card p-6 shadow-soft sm:p-8">
      <div class="flex flex-col items-start gap-4 sm:flex-row">
        <span class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary/10">
          <i class="pi pi-book text-xl text-primary" />
        </span>
        <div class="min-w-0 flex-1 space-y-2">
          <h2 class="text-base font-semibold text-ink">{{ t("methodology.notice_title") }}</h2>
          <p class="max-w-prose text-sm leading-relaxed text-muted">{{ t("methodology.notice_text") }}</p>
          <div class="flex flex-wrap gap-2 pt-2">
            <NuxtLink
              :to="localePath('/dashboard/simulateur')"
              class="inline-flex items-center gap-2 rounded-leaf bg-primary px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90"
            >
              <i class="pi pi-pen-to-square text-xs" />
              {{ t("methodology.cta_simulator") }}
            </NuxtLink>
            <NuxtLink
              :to="localePath('/dashboard/examens')"
              class="inline-flex items-center gap-2 rounded-leaf border border-line bg-card px-4 py-2 text-sm font-semibold text-ink transition-colors hover:border-primary/40 hover:text-primary"
            >
              <i class="pi pi-book text-xs" />
              {{ t("methodology.cta_exams") }}
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();

useHead({ title: () => t("methodology.title") });
</script>