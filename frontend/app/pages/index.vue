<template>
  <div>
    <Hero />
    <LandingLevelsSection />
    <LandingReviewsSection />
  </div>
</template>

<script setup lang="ts">
import Hero from "~/components/landing/Hero.vue";

definePageMeta({ layout: "default" });

useHead({
  title: "Préparation TELC & ÖSD B1/B2 en ligne — prep-telc-osd.com",
  meta: [
    {
      name: "description",
      content:
        "Préparez-vous aux examens TELC et ÖSD B1/B2 avec des simulations conformes aux examens officiels. Audio inclus, corrections automatiques. Paiement MTN & Orange Money.",
    },
    {
      name: "keywords",
      content:
        "préparation TELC B1, ÖSD B1, examen allemand, TELC B2, Goethe B1, Cameroun, préparation examen allemand en ligne",
    },
    {
      property: "og:title",
      content: "Préparation TELC & ÖSD B1/B2 — prep-telc-osd.com",
    },
    {
      property: "og:description",
      content:
        "Simulations d'examens TELC et ÖSD B1/B2 conformes aux standards officiels.",
    },
    { property: "og:type", content: "website" },
    { property: "og:url", content: "https://prep-telc-osd.com" },
  ],
  link: [{ rel: "canonical", href: "https://prep-telc-osd.com" }],
});
</script>
