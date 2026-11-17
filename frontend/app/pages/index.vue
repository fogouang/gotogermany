<template>
  <div>
    <Hero />
    <WhatsappBand />
    <LevelsSection />
    <ModulesSection />

    <!-- Tarifs -->
    <section id="tarifs" class="scroll-mt-20 bg-canvas py-16 sm:py-24">
      <div class="mx-auto max-w-5xl px-4 sm:px-6">
        <div class="mx-auto mb-10 max-w-3xl text-center">
          <h2
            class="font-heading text-3xl font-bold tracking-tight text-ink sm:text-4xl"
          >
            {{ t("pricing.title") }}
          </h2>
          <p class="mt-4 text-base text-muted sm:text-lg">
            {{ t("pricing.subtitle") }}
          </p>
        </div>
        <PricingPlans />
      </div>
    </section>

    <HowIsWork />
    <Temoignages />
    <Cta />
  </div>
</template>

<script setup lang="ts">
import { SITE } from "~/config/site";

definePageMeta({ layout: "default" });

const { t } = useI18n();

useSeo({
  title: () => t("seo.home.title"),
  description: () => t("seo.home.description"),
});

// Données structurées JSON-LD pour Google
useHead({
  script: [
    {
      type: "application/ld+json",
      innerHTML: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        name: SITE.name,
        url: SITE.url,
        logo: `${SITE.url}${SITE.logo}`,
        description:
          "Online preparation platform for Goethe, telc, ÖSD, TestDaF and ECL German language certifications, from B1 to C1.",
        sameAs: [],
        offers: {
          "@type": "Offer",
          category: "German Language Exam Preparation",
          availableLanguage: ["French", "English", "German"],
        },
        teaches: [
          "German Language B1",
          "German Language B2",
          "German Language C1",
          "Goethe-Zertifikat",
          "telc Deutsch",
          "ÖSD Zertifikat",
          "TestDaF",
          "ECL German exam",
        ],
      }),
    },
  ],
});
</script>
