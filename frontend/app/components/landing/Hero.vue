<template>
  <section
    class="relative overflow-hidden bg-canvas pt-10 pb-16 sm:pt-14 lg:pb-24"
  >
    <!-- Décor : grille discrète + halos -->
   
    <div
      class="pointer-events-none absolute -top-40 -left-40 size-120 rounded-full bg-accent-500/15 blur-3xl"
      aria-hidden="true"
    />
    <div
      class="pointer-events-none absolute -right-40 -bottom-48 size-136 rounded-full bg-primary/10 blur-3xl"
      aria-hidden="true"
    />

    <div
      class="relative mx-auto flex w-full max-w-7xl flex-col items-center gap-12 px-6 md:flex-row md:justify-between md:gap-8"
    >
      <!-- Texte -->
      <div class="fade-in-up w-full md:max-w-xl">
        <h1
          class="font-heading text-3xl leading-tight font-bold tracking-tight text-ink sm:text-4xl lg:text-5xl lg:leading-[1.1]"
        >
          {{ t("hero.title") }}
        </h1>
        <p
          class="mt-5 max-w-lg text-base leading-relaxed text-muted sm:text-lg"
        >
          {{ t("hero.subtitle") }}
        </p>

        <!-- CTA -->
        <div class="mt-8 flex flex-wrap items-center gap-3">
          <AppButton
            variant="gradient"
            size="large"
            icon="pi pi-arrow-right"
            icon-pos="right"
            :label="t('hero.cta')"
            @click="handleCta"
          />
          <AppLinkButton
            :to="localePath('/tarifs')"
            variant="outline"
            size="md"
            :label="t('nav.pricing')"
            icon="pi pi-tags"
            icon-pos="left"
            class="h-12!"
          />
        </div>

        <!-- Preuve sociale -->
        <div class="mt-8 flex items-center gap-3">
          <div class="flex items-center gap-0.5">
            <i
              v-for="i in 5"
              :key="i"
              class="pi pi-star-fill text-sm text-accent-500"
            />
          </div>
          <p class="text-sm">
            <span class="font-semibold text-ink">5.0</span>
            <span class="text-muted"> · {{ t("hero.social_proof") }}</span>
          </p>
        </div>

        <!-- Organismes préparés -->
        <div class="mt-6 flex flex-wrap items-center gap-2">
          <span
            v-for="org in ['Goethe', 'telc', 'ÖSD', 'TestDaF', 'ECL']"
            :key="org"
            class="inline-flex items-center gap-1.5 rounded-full border border-line bg-card px-3 py-1 text-xs font-semibold text-ink shadow-soft"
          >
            <i
              class="pi pi-check-circle text-[11px] text-emerald-600 dark:text-emerald-400"
            />
            {{ org }}
          </span>
          <span
            class="inline-flex items-center rounded-full bg-primary-50 px-3 py-1 text-xs font-bold text-primary-700"
          >
            B1 · B2
          </span>
        </div>
      </div>

      <!-- Image -->
      <div class="relative w-full max-w-xl md:max-w-160">
        <!-- Halo + anneau doré -->
        <div
          class="pointer-events-none absolute inset-[8%] rounded-full bg-accent-500/20 blur-2xl"
          aria-hidden="true"
        />
        <div
          class="pointer-events-none absolute inset-[4%] rounded-full border border-dashed border-accent-500/40"
          aria-hidden="true"
        />

        <img
          :alt="t('hero.image_alt')"
          draggable="false"
          class="relative z-10 h-full w-full select-none drop-shadow-[0_30px_60px_rgba(24,24,27,0.25)]"
          src="/images/hero-student.png"
          fetchpriority="high"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAuthDialog } from "~/composables/useAuthDialog";

const { t } = useI18n();
const localePath = useLocalePath();

const authStore = useAuthStore();
const { openSignup } = useAuthDialog();

// Connecté : direction son espace ; invité : inscription
const handleCta = () => {
  if (authStore.isAuthenticated) {
    if (authStore.isAdmin) navigateTo("/admin");
    else if (authStore.isDirector) navigateTo("/centre/dashboard");
    else if (authStore.isSecretary) navigateTo("/centre/etudiants");
    else if (authStore.isTeacher) navigateTo("/enseignant/sessions");
    else navigateTo("/dashboard");
  } else {
    openSignup();
  }
};
</script>
