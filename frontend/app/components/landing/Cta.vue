<template>
  <section>
    <div
      class="relative bg-cover bg-center bg-no-repeat overflow-hidden"
      style="background-image: url('/images/cta-card-bg3-1.jpg')"
    >
      <!-- Overlay -->
      <div
        class="absolute inset-0"
        style="background-color: #1cb098; mix-blend-mode: hue; z-index: 0"
      />
      <!-- Shape haut-gauche — masqué sur mobile -->
      <div class="absolute top-0 left-0 pointer-events-none hidden md:block" style="z-index: 1">
        <img src="/images/cta_shape4_1.png" alt="" />
      </div>

      <!-- Layout mobile : flex colonne, desktop : relatif avec image absolue -->
      <div class="relative flex flex-col md:block" style="z-index: 2">

        <!-- Texte -->
        <div
          class="max-w-7xl mx-auto px-6 pt-12 pb-8 md:pt-12.5 md:pb-30"
        >
          <div style="max-width: 580px">
            <div class="space-y-6 md:space-y-8">
              <!-- Sub-title -->
              <span
                class="flex items-center gap-2 text-sm font-medium"
                style="color: #1cb098"
              >
                {{ t('cta_section.title') }}
              </span>

              <!-- Titre -->
              <h2
                class="font-extrabold text-white leading-tight"
                style="font-size: clamp(1.8rem, 6vw, 2.8rem)"
              >
                {{ t("cta_section.title_line1") }}<br />
                {{ t("cta_section.title_line2") }}<br />
                <span style="color: #f5a623">{{ t("cta_section.title_line3") }}</span>
              </h2>

              <!-- Téléphone -->
              <a
                href="tel:+237691850913"
                class="block font-bold hover:opacity-80 transition-opacity"
                style="color: #f5a623; font-size: clamp(1.2rem, 4vw, 1.6rem)"
              >
                {{ t("cta_section.phone") }}
              </a>

              <!-- Bouton -->
              <button
                class="inline-flex items-center gap-3 text-white font-bold uppercase tracking-widest px-8 py-4 rounded-full transition-all hover:opacity-90"
                style="background-color: #076152; font-size: 0.75rem; letter-spacing: 0.12em"
                @click="handleCta"
              >
                {{ t("cta_section.button") }}
                <svg width="16" height="14" viewBox="0 0 16 14" fill="none">
                  <path
                    d="M7.5264 0C7.5264 0.6962 8.21633 1.738 8.9138 2.61293C9.81193 3.7394 10.8838 4.72347 12.1137 5.4748C13.0351 6.0374 14.154 6.57747 15.0528 6.57747M7.5264 13.1712C7.5264 12.475 8.21633 11.4332 8.9138 10.5583C9.81193 9.43187 10.8838 8.44773 12.1137 7.6964C13.0351 7.1338 14.154 6.59373 15.0528 6.59373M15.0528 6.5856H0"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Image mobile — inline, centrée, visible seulement sur mobile -->
        <div class="flex justify-center pb-0 md:hidden relative">
          <!-- Cercles déco -->
          <div
            class="absolute inset-0 rounded-full opacity-20"
            style="background-color: #1cb098; mix-blend-mode: overlay; margin: 0 auto; width: 300px; height: 300px; top: 20px"
          />
          <img
            src="/images/cta-thumb4-1.png"
            alt="img"
            class="relative block object-contain object-bottom"
            style="height: 280px; max-width: 100%"
          />
        </div>

        <!-- Image desktop — absolue comme avant -->
        <div class="cta-img4-1 hidden md:block">
          <div class="cta-bg-shape4-1"></div>
          <div class="cta-bg-shape4-2"></div>
          <img
            src="/images/cta-thumb4-1.png"
            alt="img"
            class="relative block object-contain object-bottom"
            style="height: 385px; max-width: 600px"
          />
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

const handleCta = () => {
  if (authStore.isAuthenticated) {
    navigateTo("/dashboard/simulateur");
  } else {
    openSignup();
  }
};
</script>

<style scoped>
/* ── Desktop uniquement ──────────────────────────── */
.cta-img4-1 {
  right: 192px;
  bottom: 0;
  position: absolute;
  z-index: 1;
}
.cta-img4-1 .cta-bg-shape4-1 {
  position: absolute;
  inset: -30px 35px -163px 24px;
  background-color: #1cb098;
  mix-blend-mode: overlay;
  opacity: 0.2;
  border-radius: 50%;
  z-index: -1;
  height: 578px;
  max-width: 541px;
}
.cta-img4-1 .cta-bg-shape4-2 {
  position: absolute;
  inset: -143px -30px -163px;
  background-color: #1cb098;
  opacity: 0.1;
  border-radius: 50%;
  mix-blend-mode: overlay;
  z-index: -2;
  height: 691px;
  max-width: 660px;
}
@media (max-width: 1500px) {
  .cta-img4-1 { right: 60px; max-width: 500px; }
}
@media (max-width: 1299px) {
  .cta-img4-1 { max-width: 600px; }
}
</style>