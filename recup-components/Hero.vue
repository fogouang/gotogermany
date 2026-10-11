<template>
  <section class="relative overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-20">
    <!-- Decorative elements -->
    <div class="absolute top-0 left-0 w-64 h-64 bg-indigo-100 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl opacity-50"></div>
    <div class="absolute bottom-0 right-0 w-96 h-96 bg-purple-100 rounded-full translate-x-1/2 translate-y-1/2 blur-3xl opacity-50"></div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
      <div class="text-center max-w-4xl mx-auto">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm mb-6 border border-gray-200">
          <i class="pi pi-star-fill text-yellow-500"></i>
          <span class="text-sm font-semibold text-gray-700">Plateforme #1 de préparation en allemand</span>
        </div>

        <!-- Main heading -->
        <h1 class="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Réussissez vos examens
          <span class="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            d'allemand
          </span>
        </h1>

        <!-- Subheading -->
        <p class="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Entraînez-vous avec des simulations conformes aux examens officiels Goethe et ÖSD. 
          Suivez votre progression et améliorez vos compétences.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            label="Commencer gratuitement"
            icon="pi pi-arrow-right"
            iconPos="right"
            size="large"
            class="!bg-gradient-to-r !from-indigo-600 !to-purple-600 !border-0 !px-8 !py-4 !text-lg shadow-lg hover:shadow-xl transition-shadow"
            @click="scrollToExams"
          />
          <Button
            label="Voir une démo"
            icon="pi pi-play"
            outlined
            size="large"
            class="!px-8 !py-4 !text-lg"
          />
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-8 mt-16 max-w-3xl mx-auto">
          <div class="text-center">
            <div class="text-4xl font-bold text-indigo-600 mb-2">10K+</div>
            <div class="text-sm text-gray-600">Étudiants</div>
          </div>
          <div class="text-center">
            <div class="text-4xl font-bold text-indigo-600 mb-2">95%</div>
            <div class="text-sm text-gray-600">Taux de réussite</div>
          </div>
          <div class="text-center">
            <div class="text-4xl font-bold text-indigo-600 mb-2">500+</div>
            <div class="text-sm text-gray-600">Questions</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const scrollToExams = () => {
  const element = document.querySelector('#examens');
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
};
</script>