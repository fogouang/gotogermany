<template>
  <div>
    <Hero />
    <LandingLevelsSection />
    <HowIsWork />
    <Cta />
  </div>
</template>

<script setup lang="ts">
import Cta from '~/components/landing/Cta.vue'
import Hero from '~/components/landing/Hero.vue'
import HowIsWork from '~/components/landing/HowIsWork.vue'

definePageMeta({ layout: 'default' })

const { locale } = useI18n()

useSeo({
  title: locale.value === 'fr'
    ? 'Préparation Goethe, TELC & ÖSD B1/B2 en ligne'
    : 'Goethe, TELC & ÖSD B1/B2 German Exam Preparation Online',
  description: locale.value === 'fr'
    ? 'Préparez vos examens Goethe, TELC et ÖSD B1/B2 avec des simulations conformes aux standards officiels. Audio inclus, corrections IA instantanées. Paiement MTN & Orange Money.'
    : 'Prepare for Goethe, TELC and ÖSD B1/B2 German exams with official-standard mock tests. Audio included, instant AI correction. Pass on your first try.',
})

// Données structurées JSON-LD pour Google
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'EducationalOrganization',
        name: 'GoToGermany',
        url: 'https://prep-telc-osd.com',
        logo: 'https://prep-telc-osd.com/images/logo.png',
        description: 'Online preparation platform for Goethe, TELC and ÖSD German language certifications B1 and B2.',
        sameAs: [],
        offers: {
          '@type': 'Offer',
          category: 'German Language Exam Preparation',
          availableLanguage: ['French', 'English'],
        },
        teaches: [
          'German Language B1',
          'German Language B2',
          'Goethe-Zertifikat',
          'TELC Deutsch',
          'ÖSD Zertifikat',
        ],
      }),
    },
  ],
})
</script>