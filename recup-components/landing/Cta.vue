<template>
  <section class="bg-canvas px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
    <div
      class="relative mx-auto max-w-6xl overflow-hidden rounded-4xl bg-zinc-950 px-6 py-12 text-white shadow-lift sm:px-12 sm:py-16"
    >
      <!-- Décor -->
      <div
        class="pointer-events-none absolute -top-32 -right-24 size-96 rounded-full bg-accent-500/25 blur-3xl"
        aria-hidden="true"
      />
      <div
        class="pointer-events-none absolute -bottom-40 -left-24 size-96 rounded-full bg-accent-500/10 blur-3xl"
        aria-hidden="true"
      />
      <div
        class="pointer-events-none absolute inset-0 opacity-[0.07] bg-[linear-gradient(#fff_1px,transparent_1px),linear-gradient(90deg,#fff_1px,transparent_1px)] bg-size-[48px_48px]"
        aria-hidden="true"
      />
      <div class="flag-stripe absolute inset-x-0 top-0 h-1" aria-hidden="true" />

      <div class="relative grid items-center gap-12 lg:grid-cols-[1.2fr_1fr]">
        <!-- Texte -->
        <div>
          <p
            class="mb-4 inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-accent-400"
          >
            <span class="h-px w-6 bg-accent-500" />
            {{ t("cta_section.title") }}
          </p>

          <h2 class="font-heading text-3xl leading-tight font-bold tracking-tight sm:text-4xl lg:text-5xl">
            {{ t("cta_section.title_line1") }}
            {{ t("cta_section.title_line2") }}
            <span class="text-accent-400">{{ t("cta_section.title_line3") }}</span>
          </h2>

          <div class="mt-8 flex flex-wrap items-center gap-3">
            <AppButton
              variant="accent"
              size="large"
              icon="pi pi-arrow-right"
              icon-pos="right"
              :label="t('cta_section.button')"
              @click="handleCta"
            />
            <a
              :href="`https://wa.me/${TELEPHONE}`"
              target="_blank"
              rel="noopener"
              class="inline-flex h-12 items-center gap-2 rounded-leaf border border-white/15 bg-white/5 px-5 text-sm font-semibold text-white transition-colors hover:border-white/30 hover:bg-white/10"
            >
              <i class="pi pi-whatsapp text-base text-emerald-400" />
              WhatsApp
            </a>
          </div>

          <a
            :href="`tel:+${TELEPHONE}`"
            class="mt-6 inline-flex items-center gap-2 text-sm text-white/70 transition-colors hover:text-accent-400"
          >
            <i class="pi pi-phone text-xs" />
            {{ t("cta_section.phone") }}
          </a>
        </div>

        <!-- Fiche de résultat (illustration en HTML) -->
        <div class="relative mx-auto w-full max-w-sm">
          <div
            class="absolute inset-0 translate-x-3 translate-y-3 rotate-3 rounded-card bg-accent-500/20"
            aria-hidden="true"
          />
          <div
            class="relative rounded-card border border-white/10 bg-white/6 p-6 backdrop-blur-md"
            aria-hidden="true"
          >
            <div class="mb-5 flex items-center justify-between">
              <span class="font-heading text-sm font-semibold text-white/80">
                Prüfungsergebnis
              </span>
              <span
                class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-bold text-emerald-400"
              >
                <i class="pi pi-check-circle text-[11px]" />
                Bestanden
              </span>
            </div>

            <ul class="space-y-3">
              <li
                v-for="(module, i) in modules"
                :key="module"
                class="flex items-center gap-3"
              >
                <span
                  class="flex size-8 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400"
                >
                  <i class="pi pi-check text-xs" />
                </span>
                <span class="flex-1 text-sm font-medium text-white">{{ module }}</span>
                <span class="h-1.5 w-24 overflow-hidden rounded-full bg-white/10">
                  <span
                    class="block h-full rounded-full bg-linear-to-r from-accent-500 to-accent-300"
                    :style="{ width: `${78 + i * 5}%` }"
                  />
                </span>
              </li>
            </ul>

            <div class="mt-6 flex items-center gap-3 border-t border-white/10 pt-5">
              <span
                class="flex size-10 items-center justify-center rounded-leaf bg-accent-500 text-accent-950"
              >
                <i class="pi pi-verified" />
              </span>
              <div class="leading-tight">
                <p class="font-heading text-sm font-bold">Zertifikat</p>
                <p class="flag-stripe mt-1.5 h-0.5 w-12 rounded-full" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAuthDialog } from "~/composables/useAuthDialog";

const authStore = useAuthStore();
const { openSignup } = useAuthDialog();
const { t } = useI18n();

// Numéro au format international sans "+" ni espaces (tel: et wa.me)
const TELEPHONE = "237691850913";

const modules = ["Lesen", "Hören", "Schreiben", "Sprechen"];

const handleCta = () => {
  if (authStore.isAuthenticated) {
    navigateTo("/dashboard/simulateur");
  } else {
    openSignup();
  }
};
</script>