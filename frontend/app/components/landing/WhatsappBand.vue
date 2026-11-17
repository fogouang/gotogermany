<template>
  <section class="bg-canvas px-4 sm:px-6 lg:px-8">
    <div
      class="mx-auto flex max-w-6xl flex-col items-start gap-5 rounded-card border border-emerald-500/40 bg-emerald-500/10 p-5 sm:flex-row sm:items-center sm:p-6"
    >
      <span
        class="flex size-12 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white"
      >
        <i class="pi pi-whatsapp text-2xl" />
      </span>
      <div class="flex-1">
        <h2 class="font-heading text-lg font-bold text-ink">
          {{ t("whatsapp_band.title") }}
        </h2>
        <p class="mt-1 text-sm leading-relaxed text-muted">
          {{ t("whatsapp_band.description") }}
        </p>
      </div>
      <a
        :href="WHATSAPP_GROUP"
        target="_blank"
        rel="noopener"
        class="inline-flex h-11 shrink-0 items-center gap-2 rounded-leaf bg-emerald-500 px-5 text-sm font-semibold text-white transition-colors hover:bg-emerald-600"
      >
        <i class="pi pi-whatsapp" />
        {{ t("whatsapp_band.cta") }}
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n();

// À déplacer dans SITE (config/site.ts) si tu veux le réutiliser ailleurs
const WHATSAPP_GROUP = "https://chat.whatsapp.com/CxUdtE70ckv66iQjikHqBF";
</script>