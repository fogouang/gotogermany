<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Hero Section -->
    <section
      class="bg-gradient-primary text-white py-20 relative overflow-hidden"
    >
      <div class="absolute inset-0 opacity-10">
        <div
          class="absolute inset-0"
          style="
            background-image: radial-gradient(
              circle at 2px 2px,
              white 1px,
              transparent 0
            );
            background-size: 40px 40px;
          "
        ></div>
      </div>

      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
        <div
          class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-semibold mb-6 animate-fade-in-down"
        >
          <i class="pi pi-question-circle"></i>
          <span>Centre d'aide</span>
        </div>

        <h1
          class="text-4xl sm:text-5xl font-bold mb-6 animate-fade-in-up"
          style="animation-delay: 0.2s"
        >
          Questions fréquentes
        </h1>

        <p
          class="text-xl text-teal-100 animate-fade-in-up"
          style="animation-delay: 0.3s"
        >
          Trouvez rapidement les réponses à vos questions sur DeutschTest
        </p>
      </div>

      <!-- Wave separator -->
      <div class="absolute bottom-0 left-0 right-0">
        <svg
          viewBox="0 0 1440 80"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          class="w-full"
        >
          <path
            d="M0 0L60 8C120 16 240 32 360 37.3C480 43 600 37 720 32C840 27 960 21 1080 21.3C1200 21 1320 27 1380 29.3L1440 32V80H1380C1320 80 1200 80 1080 80C960 80 840 80 720 80C600 80 480 80 360 80C240 80 120 80 60 80H0V0Z"
            fill="rgb(249, 250, 251)"
          />
        </svg>
      </div>
    </section>

    <!-- FAQ Content -->
    <section class="py-16 -mt-8">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Catégories -->
        <div class="grid sm:grid-cols-3 gap-4 mb-12">
          <button
            v-for="category in categories"
            :key="category.id"
            @click="selectedCategory = category.id"
            :class="[
              'p-4 rounded-xl border-2 transition-all duration-300 text-left group',
              selectedCategory === category.id
                ? 'border-teal-600 bg-teal-50 shadow-lg'
                : 'border-gray-200 bg-white hover:border-teal-300 hover:shadow-md',
            ]"
          >
            <div class="flex items-center gap-3">
              <div
                :class="[
                  'w-12 h-12 rounded-lg flex items-center justify-center transition-all',
                  selectedCategory === category.id
                    ? 'bg-gradient-primary'
                    : 'bg-gray-100 group-hover:bg-teal-100',
                ]"
              >
                <i
                  :class="[
                    category.icon,
                    'text-xl',
                    selectedCategory === category.id
                      ? 'text-white'
                      : 'text-gray-600',
                  ]"
                ></i>
              </div>
              <div>
                <h3
                  :class="[
                    'font-semibold',
                    selectedCategory === category.id
                      ? 'text-teal-900'
                      : 'text-gray-900',
                  ]"
                >
                  {{ category.label }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ category.count }} questions
                </p>
              </div>
            </div>
          </button>
        </div>

        <!-- Questions Accordion -->
        <Accordion
          :value="activeIndex"
          @update:value="activeIndex = $event"
          class="space-y-4"
        >
          <AccordionPanel
            v-for="(faq, index) in filteredFaqs"
            :key="index"
            :value="index"
            class="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-teal-600 transition-all duration-300 bg-white"
          >
            <AccordionHeader
              class="px-6 py-4 hover:bg-teal-50 transition-colors"
            >
              <div class="flex items-start gap-4 w-full">
                <div
                  class="w-10 h-10 bg-gradient-secondary rounded-lg flex items-center justify-center flex-shrink-0 mt-1"
                >
                  <i class="pi pi-question text-white"></i>
                </div>
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900 text-left">
                    {{ faq.question }}
                  </h3>
                </div>
              </div>
            </AccordionHeader>
            <AccordionContent class="px-6 py-4 bg-gray-50">
              <div
                class="ml-14 text-gray-700 leading-relaxed"
                v-html="faq.answer"
              ></div>
            </AccordionContent>
          </AccordionPanel>
        </Accordion>

        <!-- Contact CTA -->
        <Card
          class="mt-12 border-2 border-teal-200 bg-gradient-to-br from-teal-50 to-white"
        >
          <template #content>
            <div class="text-center py-6">
              <div
                class="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4"
              >
                <i class="pi pi-headphones text-3xl text-white"></i>
              </div>
              <h3 class="text-2xl font-bold text-gray-900 mb-3">
                Vous ne trouvez pas votre réponse ?
              </h3>
              <p class="text-gray-600 mb-6 max-w-2xl mx-auto">
                Notre équipe est là pour vous aider. Contactez-nous et nous vous
                répondrons dans les plus brefs délais.
              </p>
              <Button
                label="Nous contacter"
                icon="pi pi-envelope"
                iconPos="right"
                class="!bg-gradient-primary !border-0 !text-white hover:opacity-90 transition-opacity"
                @click="navigateTo('/contact')"
              />
            </div>
          </template>
        </Card>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

useHead({
  title: "FAQ - DeutschTest",
  meta: [
    {
      name: "description",
      content:
        "Questions fréquentes sur DeutschTest : examens, tarifs, inscription, préparation et assistance technique.",
    },
  ],
});

const selectedCategory = ref("all");
const activeIndex = ref();

const categories = [
  { id: "all", label: "Toutes", icon: "pi pi-list", count: 12 },
  { id: "exams", label: "Examens", icon: "pi pi-book", count: 5 },
  { id: "account", label: "Compte", icon: "pi pi-user", count: 4 },
  { id: "technical", label: "Technique", icon: "pi pi-cog", count: 3 },
];

const faqs = [
  // Examens
  {
    category: "exams",
    question: "Quels examens d'allemand sont disponibles sur DeutschTest ?",
    answer:
      "Nous proposons actuellement des simulations complètes pour les examens <strong>Goethe B1</strong> et <strong>Goethe B2</strong>. Nous couvrons également les formats <strong>ÖSD</strong> et <strong>TELC</strong> qui partagent des structures similaires. Les niveaux A1, A2 et C1 seront ajoutés prochainement.",
  },
  {
    category: "exams",
    question: "Les simulations sont-elles conformes aux examens officiels ?",
    answer:
      "Oui, absolument ! Nos simulations respectent scrupuleusement le format, la durée et les critères d'évaluation des examens officiels Goethe-Institut, ÖSD et TELC. Nos contenus sont créés par des examinateurs certifiés avec une expérience réelle des examens.",
  },
  {
    category: "exams",
    question: "Comment fonctionne la correction IA ?",
    answer:
      "Notre système d'IA analyse vos productions écrites et orales selon les <strong>critères officiels</strong> (contenu, cohérence, grammaire, vocabulaire, prononciation). Vous recevez un <strong>feedback détaillé</strong> avec vos points forts, vos axes d'amélioration et une estimation de votre score potentiel.",
  },
  {
    category: "exams",
    question: "Combien de tests puis-je passer ?",
    answer:
      "Avec l'accès <strong>Unique</strong>, vous passez un examen blanc complet. Avec l'accès <strong>Illimité 30 jours</strong>, vous pouvez passer autant de tests que vous le souhaitez pendant 30 jours. Idéal pour une préparation intensive avant votre examen officiel.",
  },
  {
    category: "exams",
    question:
      "Les enregistrements audio sont-ils conformes aux conditions réelles ?",
    answer:
      "Oui, nos enregistrements audio utilisent des <strong>locuteurs natifs</strong> avec les accents standards (allemand, autrichien, suisse). La qualité et le débit correspondent exactement aux conditions d'examen officielles.",
  },

  // Compte
  {
    category: "account",
    question: "Comment créer un compte ?",
    answer:
      "Cliquez sur <strong>\"Commencer gratuitement\"</strong> en haut de la page. Renseignez votre email, créez un mot de passe et validez. Vous recevrez un email de confirmation. C'est tout ! Aucune carte bancaire n'est requise pour créer votre compte.",
  },
  {
    category: "account",
    question: "Quels sont les moyens de paiement acceptés ?",
    answer:
      "Nous acceptons les paiements par <strong>carte bancaire</strong> (Visa, Mastercard), <strong>Mobile Money</strong> (MTN, Orange), et <strong>PayPal</strong>. Tous les paiements sont sécurisés et cryptés.",
  },
  {
    category: "account",
    question: "Puis-je changer de formule après mon inscription ?",
    answer:
      "Oui, vous pouvez passer de l'accès <strong>Unique</strong> à l'accès <strong>Illimité</strong> à tout moment depuis votre tableau de bord. La différence de prix sera calculée automatiquement.",
  },
  {
    category: "account",
    question: "Comment puis-je récupérer mon mot de passe ?",
    answer:
      'Cliquez sur <strong>"Mot de passe oublié ?"</strong> sur la page de connexion. Entrez votre email et vous recevrez un lien de réinitialisation valable 24h. Si vous ne recevez pas l\'email, vérifiez vos spams ou contactez-nous.',
  },

  // Technique
  {
    category: "technical",
    question: "Sur quels appareils puis-je utiliser DeutschTest ?",
    answer:
      "DeutschTest fonctionne sur <strong>ordinateurs</strong> (Windows, Mac, Linux), <strong>tablettes</strong> et <strong>smartphones</strong> (iOS, Android). Nous recommandons un ordinateur avec un micro pour les sections d'expression orale, mais vous pouvez aussi utiliser votre téléphone.",
  },
  {
    category: "technical",
    question: "Ai-je besoin d'une connexion Internet ?",
    answer:
      "Oui, une connexion Internet stable est nécessaire pour passer les examens, charger les audios et recevoir vos corrections. Nous recommandons une connexion d'au moins <strong>2 Mbps</strong> pour une expérience optimale.",
  },
  {
    category: "technical",
    question: "Que faire si j'ai un problème technique pendant un examen ?",
    answer:
      "Votre progression est <strong>sauvegardée automatiquement</strong>. En cas de problème (coupure Internet, bug), vous pouvez reprendre exactement où vous vous étiez arrêté. Si le problème persiste, contactez notre support via le chat en direct ou par email à <strong>lfogouang39@gmail.com</strong>.",
  },
];

const filteredFaqs = computed(() => {
  if (selectedCategory.value === "all") {
    return faqs;
  }
  return faqs.filter((faq) => faq.category === selectedCategory.value);
});
</script>

<style scoped>
/* Animations */
@keyframes fade-in-down {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-down {
  animation: fade-in-down 0.6s ease-out;
  animation-fill-mode: both;
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out;
  animation-fill-mode: both;
}

/* Gradients */
.bg-gradient-primary {
  background: linear-gradient(
    135deg,
    hsl(145 63% 32%) 0%,
    hsl(145 50% 22%) 100%
  );
}

.bg-gradient-secondary {
  background: linear-gradient(135deg, hsl(45 92% 55%) 0%, hsl(35 90% 50%) 100%);
}

/* Accordion animations */
:deep(.p-accordion-content-enter-active) {
  animation: accordion-expand 400ms cubic-bezier(0.65, 0, 0.35, 1);
}

:deep(.p-accordion-content-leave-active) {
  animation: accordion-collapse 400ms cubic-bezier(0.65, 0, 0.35, 1);
}

@keyframes accordion-expand {
  from {
    opacity: 0;
    max-height: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    max-height: 500px;
    transform: scale(1);
  }
}

@keyframes accordion-collapse {
  from {
    opacity: 1;
    max-height: 500px;
    transform: scale(1);
  }
  to {
    opacity: 0;
    max-height: 0;
    transform: scale(0.95);
  }
}
</style>
