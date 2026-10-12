<template>
  <div>
    <LandingHero />
    <LandingLevelsSection />
    <LandingModulesSection />
    <LandingHowIsWork />
    <LandingTemoignages />
    <LandingCta />
  </div>
</template>

<script setup lang="ts">
import { SITE } from "~/config/site";

definePageMeta({ layout: "default" });

const { t } = useI18n();

useSeo({
  title: t("seo.home.title"),
  description: t("seo.home.description"),
});

// DonnÃ©es structurÃ©es JSON-LD pour Google
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
          "Online preparation platform for Goethe, telc, Ã–SD, TestDaF and ECL German language certifications, from B1 to C1.",
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
          "Ã–SD Zertifikat",
          "TestDaF",
          "ECL German exam",
        ],
      }),
    },
  ],
});
</script>
