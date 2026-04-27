<template>
  <section class="py-20 bg-gradient-to-br from-gray-50 to-teal-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-16">
        <div class="inline-flex items-center gap-2 bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full text-sm font-semibold mb-4">
          <i class="pi pi-star-fill"></i>
          <span>4.9/5 - Plus de 500 avis</span>
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
          Ce que disent nos étudiants
        </h2>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          Des milliers d'étudiants nous font confiance pour réussir leurs examens d'allemand
        </p>
      </div>

      <!-- Stats rapides -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
        <div class="bg-white rounded-2xl p-6 text-center shadow-lg">
          <div class="text-4xl font-bold bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent mb-2">
            95%
          </div>
          <p class="text-sm text-gray-600 font-medium">Taux de réussite</p>
        </div>
        <div class="bg-white rounded-2xl p-6 text-center shadow-lg">
          <div class="text-4xl font-bold text-teal-600 mb-2">4.9/5</div>
          <p class="text-sm text-gray-600 font-medium">Note moyenne</p>
        </div>
        <div class="bg-white rounded-2xl p-6 text-center shadow-lg">
          <div class="text-4xl font-bold text-red-600 mb-2">3K+</div>
          <p class="text-sm text-gray-600 font-medium">Étudiants actifs</p>
        </div>
        <div class="bg-white rounded-2xl p-6 text-center shadow-lg">
          <div class="text-4xl font-bold text-gray-900 mb-2">500+</div>
          <p class="text-sm text-gray-600 font-medium">Avis vérifiés</p>
        </div>
      </div>

      <!-- Carousel de reviews -->
      <Carousel 
        :value="reviews" 
        :numVisible="3" 
        :numScroll="1" 
        :responsiveOptions="responsiveOptions"
        circular
        :autoplayInterval="5000"
        class="reviews-carousel"
      >
        <template #item="{ data }">
          <div class="px-3">
            <Card class="h-full shadow-xl hover:shadow-2xl transition-all duration-300 border-t-4" :class="data.borderColor">
              <template #content>
                <div class="space-y-4">
                  <!-- Rating -->
                  <div class="flex items-center gap-1">
                    <i 
                      v-for="star in 5" 
                      :key="star"
                      class="pi pi-star-fill text-lg"
                      :class="star <= data.rating ? 'text-yellow-400' : 'text-gray-300'"
                    ></i>
                  </div>

                  <!-- Review text -->
                  <p class="text-gray-700 leading-relaxed italic">
                    "{{ data.text }}"
                  </p>

                  <!-- Badge certification -->
                  <div v-if="data.certification" class="inline-flex">
                    <Tag 
                      :value="data.certification" 
                      :class="data.certificationClass"
                      class="!font-semibold"
                    />
                  </div>

                  <!-- Author -->
                  <div class="flex items-center gap-3 pt-4 border-t">
                    <Avatar 
                      :label="data.authorInitial" 
                      :class="data.avatarClass"
                      size="large"
                      shape="circle"
                    />
                    <div>
                      <div class="font-bold text-gray-900">{{ data.author }}</div>
                      <div class="text-sm text-gray-600">{{ data.location }}</div>
                    </div>
                    <i class="pi pi-verified text-teal-600 ml-auto text-xl" v-if="data.verified"></i>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </template>
      </Carousel>

      <!-- CTA -->
      <div class="text-center mt-16">
        <div class="bg-white rounded-3xl p-8 sm:p-12 shadow-2xl max-w-4xl mx-auto border border-gray-100">
          <div class="flex items-center justify-center gap-2 mb-6">
            <i class="pi pi-star-fill text-yellow-400 text-2xl"></i>
            <i class="pi pi-star-fill text-yellow-400 text-2xl"></i>
            <i class="pi pi-star-fill text-yellow-400 text-2xl"></i>
            <i class="pi pi-star-fill text-yellow-400 text-2xl"></i>
            <i class="pi pi-star-fill text-yellow-400 text-2xl"></i>
          </div>
          <h3 class="text-3xl font-bold text-gray-900 mb-4">
            Rejoignez des milliers d'étudiants qui réussissent
          </h3>
          <p class="text-lg text-gray-600 mb-8">
            Commencez votre préparation dès aujourd'hui et obtenez votre certification
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              label="Commencer gratuitement" 
              icon="pi pi-arrow-right"
              iconPos="right"
              size="large"
              class="!bg-gradient-to-r !from-yellow-400 !to-orange-400 !border-0 !text-gray-900 !font-bold !px-8 shadow-xl hover:shadow-2xl"
            />
            <Button 
              label="Voir tous les témoignages" 
              icon="pi pi-comments"
              outlined
              size="large"
              class="!border-2 !border-teal-600 !text-teal-600 hover:!bg-teal-50"
            />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const reviews = ref([
  {
    rating: 5,
    text: "Grâce à DeutschTest, j'ai obtenu mon certificat B1 avec 87%. Les simulations sont vraiment conformes à l'examen officiel. Je recommande à 100% !",
    author: "Marie Dubois",
    authorInitial: "M",
    location: "Paris, France",
    certification: "B1 - 87%",
    certificationClass: "!bg-yellow-100 !text-yellow-800",
    avatarClass: "!bg-yellow-200 !text-yellow-800",
    borderColor: "border-yellow-400",
    verified: true
  },
  {
    rating: 5,
    text: "Plateforme excellente ! Les corrections IA sont très détaillées et m'ont vraiment aidé à progresser en expression écrite. J'ai réussi mon B2 du premier coup.",
    author: "Thomas Laurent",
    authorInitial: "T",
    location: "Lyon, France",
    certification: "B2 - 92%",
    certificationClass: "!bg-red-100 !text-red-800",
    avatarClass: "!bg-red-200 !text-red-800",
    borderColor: "border-red-400",
    verified: true
  },
  {
    rating: 5,
    text: "Les exercices de compréhension orale sont parfaits. J'ai pu m'entraîner autant que je voulais et suivre ma progression. Résultat : 95% au Hören !",
    author: "Sophie Martin",
    authorInitial: "S",
    location: "Bruxelles, Belgique",
    certification: "B1 - 95%",
    certificationClass: "!bg-teal-100 !text-teal-800",
    avatarClass: "!bg-teal-200 !text-teal-800",
    borderColor: "border-teal-400",
    verified: true
  },
  {
    rating: 5,
    text: "Interface intuitive et très complète. Les simulations m'ont mis en conditions réelles. Je me sentais prêt le jour J !",
    author: "Alexandre Petit",
    authorInitial: "A",
    location: "Montréal, Canada",
    certification: "B2 - 89%",
    certificationClass: "!bg-red-100 !text-red-800",
    avatarClass: "!bg-gray-300 !text-gray-800",
    borderColor: "border-gray-400",
    verified: true
  },
  {
    rating: 5,
    text: "Le suivi de progression est très motivant. On voit ses points faibles et on peut travailler dessus. Excellent outil de préparation !",
    author: "Camille Bernard",
    authorInitial: "C",
    location: "Genève, Suisse",
    certification: "B1 - 91%",
    certificationClass: "!bg-yellow-100 !text-yellow-800",
    avatarClass: "!bg-purple-200 !text-purple-800",
    borderColor: "border-purple-400",
    verified: true
  },
  {
    rating: 5,
    text: "Rapport qualité-prix imbattable. Bien mieux que les cours particuliers que je prenais avant. J'ai économisé du temps et de l'argent.",
    author: "Lucas Moreau",
    authorInitial: "L",
    location: "Toulouse, France",
    certification: "B2 - 85%",
    certificationClass: "!bg-red-100 !text-red-800",
    avatarClass: "!bg-blue-200 !text-blue-800",
    borderColor: "border-blue-400",
    verified: true
  }
]);

const responsiveOptions = ref([
  {
    breakpoint: '1024px',
    numVisible: 3,
    numScroll: 1
  },
  {
    breakpoint: '768px',
    numVisible: 2,
    numScroll: 1
  },
  {
    breakpoint: '560px',
    numVisible: 1,
    numScroll: 1
  }
]);
</script>

<style scoped>
/* Style du carousel */
:deep(.p-carousel-content) {
  padding: 1rem 0;
}

:deep(.p-carousel-indicators) {
  padding: 1.5rem 0;
}

:deep(.p-carousel-indicator button) {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #d1d5db;
}

:deep(.p-carousel-indicator.p-highlight button) {
  background: linear-gradient(to right, #facc15, #fb923c);
}

/* Animation hover sur les cards */
.reviews-carousel :deep(.p-card) {
  transition: transform 0.3s ease;
}

.reviews-carousel :deep(.p-card:hover) {
  transform: translateY(-8px);
}
</style>