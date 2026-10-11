<template>
  <footer class="relative bg-zinc-950 text-white">
    <div class="flag-stripe h-1 w-full" aria-hidden="true" />

    <div class="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
      <div
        class="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-5 lg:gap-12"
      >
        <!-- Marque -->
        <div class="sm:col-span-2">
          <NuxtLink
            :to="localePath('/')"
            class="inline-flex items-center gap-2.5"
            :aria-label="SITE.name"
          >
            <span class="font-heading text-xl font-bold tracking-tight">
              GoTo<span class="text-accent-400">Germany</span>
            </span>
          </NuxtLink>

          <p class="mt-4 max-w-sm text-sm leading-relaxed text-white/60">
            {{ t("footer.tagline") }}
          </p>

          <!-- Contact direct -->
          <div class="mt-6 flex flex-wrap gap-2">
            <a
              :href="`https://wa.me/${SITE.phone}`"
              target="_blank"
              rel="noopener"
              class="inline-flex h-10 items-center gap-2 rounded-leaf border border-white/10 bg-white/5 px-4 text-sm font-medium transition-colors hover:border-white/25 hover:bg-white/10"
            >
              <i class="pi pi-whatsapp text-emerald-400" />
              WhatsApp
            </a>
            <a
              :href="`tel:+${SITE.phone}`"
              class="inline-flex h-10 items-center gap-2 rounded-leaf border border-white/10 bg-white/5 px-4 text-sm font-medium transition-colors hover:border-white/25 hover:bg-white/10"
            >
              <i class="pi pi-phone text-accent-400" />
              {{ SITE.phoneLabel }}
            </a>
          </div>

          <!-- Réseaux sociaux (affichés seulement si une URL est renseignée) -->
          <div v-if="reseaux.length" class="mt-5 flex gap-2">
            <a
              v-for="r in reseaux"
              :key="r.icon"
              :href="r.url"
              target="_blank"
              rel="noopener"
              :aria-label="r.label"
              class="flex size-9 items-center justify-center rounded-full border border-white/10 text-white/60 transition-colors hover:border-accent-500 hover:text-accent-400"
            >
              <i :class="[r.icon, 'text-sm']" />
            </a>
          </div>
        </div>

        <!-- Examens -->
        <div>
          <h3
            class="mb-5 font-heading text-sm font-semibold uppercase tracking-[0.14em] text-white/90"
          >
            {{ t("footer.exams.title") }}
          </h3>
          <ul class="space-y-3 text-sm">
            <li v-for="item in examens" :key="item.label">
              <button
                type="button"
                class="group inline-flex items-center gap-2 text-white/60 transition-colors hover:text-white"
                @click="choisir(item.provider, item.level)"
              >
                <i
                  class="pi pi-angle-right text-[10px] text-accent-500 transition-transform group-hover:translate-x-1"
                />
                {{ item.label }}
              </button>
            </li>
          </ul>
        </div>

        <!-- Ressources + À propos -->
        <div v-for="col in colonnes" :key="col.title">
          <h3
            class="mb-5 font-heading text-sm font-semibold uppercase tracking-[0.14em] text-white/90"
          >
            {{ col.title }}
          </h3>
          <ul class="space-y-3 text-sm">
            <li v-for="item in col.items" :key="item.label">
              <NuxtLink
                :to="localePath(item.href)"
                class="group inline-flex items-center gap-2 text-white/60 transition-colors hover:text-white"
              >
                <i
                  class="pi pi-angle-right text-[10px] text-accent-500 transition-transform group-hover:translate-x-1"
                />
                {{ item.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bas de page -->
      <div
        class="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-6 text-sm text-white/50 md:flex-row"
      >
        <p>
          <span class="font-semibold text-white">{{
            t("footer.copyright")
          }}</span>
        </p>
        <span class="inline-flex items-center gap-1.5">
          <i class="pi pi-shield text-xs text-accent-400" />
          {{ t("footer.secure_payment") }}
        </span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { SITE } from "~/config/site";

const { t } = useI18n();
const localePath = useLocalePath();
const { choisir } = useChoixExamen();

const examens = computed(() => [
  { label: t("footer.exams.links.goethe_b1"), provider: "goethe", level: "B1" },
  { label: t("footer.exams.links.goethe_b2"), provider: "goethe", level: "B2" },
  { label: t("footer.exams.links.telc"), provider: "telc" },
  { label: t("footer.exams.links.osd"), provider: "osd" },
  { label: t("footer.exams.links.testdaf"), provider: "testdaf" },
  { label: t("footer.exams.links.ecl"), provider: "ecl" },
]);

// href vide = page pas encore créée : le lien est masqué
const colonnes = computed(() =>
  [
    {
      title: t("footer.resources.title"),
      items: [
        { label: t("footer.resources.links.faq"), href: "/faq" },
        { label: t("footer.resources.links.guides"), href: "" },
        { label: t("footer.resources.links.tutorials"), href: "" },
      ],
    },
    {
      title: t("footer.about.title"),
      items: [
        { label: t("footer.about.links.mission"), href: "/about" },
        { label: t("footer.about.links.pricing"), href: "/tarifs" },
        { label: t("footer.about.links.contact"), href: "/contact" },
        { label: t("footer.about.links.privacy"), href: "/politique" },
        { label: t("footer.about.links.terms"), href: "/conditions" },
        { label: t("footer.about.links.terms"), href: "" },
      ],
    },
  ].map((col) => ({ ...col, items: col.items.filter((i) => i.href) })),
);

const reseaux = computed(() =>
  [
    { url: SITE.social.facebook, icon: "pi pi-facebook", label: "Facebook" },
    { url: SITE.social.instagram, icon: "pi pi-instagram", label: "Instagram" },
    { url: SITE.social.linkedin, icon: "pi pi-linkedin", label: "LinkedIn" },
    { url: SITE.social.tiktok, icon: "pi pi-tiktok", label: "TikTok" },
  ].filter((r) => r.url),
);
</script>
