<template>
  <section class="py-20 bg-white overflow-hidden">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

      <!-- Header -->
      <div class="text-center mb-16">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-4"
          style="background-color: #e6f4ef; color: #0d6e4f;">
          <i class="pi pi-graduation-cap"></i>
          <span>Niveaux CECR B1 & B2</span>
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
          Nos certifications disponibles
        </h2>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          Préparez-vous pour tous les examens officiels d'allemand, du niveau intermédiaire au niveau avancé
        </p>
      </div>

      <!-- Grid B1 + B2 -->
      <div class="grid md:grid-cols-2 gap-8 max-w-3xl mx-auto mb-16">

        <!-- B1 -->
        <div class="cert-card relative rounded-3xl border-2 overflow-hidden group cursor-pointer hover:shadow-2xl transition-all duration-500"
          style="border-color: #F59E0B;">
          <div class="absolute top-0 right-0">
            <div class="text-white text-xs font-bold px-4 py-1.5 rounded-bl-xl"
              style="background: linear-gradient(135deg, #F59E0B, #d97706);">
              POPULAIRE
            </div>
          </div>
          <!-- Fond animé -->
          <div class="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-500"
            style="background: radial-gradient(circle at 30% 50%, #F59E0B 0%, transparent 70%);" />

          <div class="relative p-8 text-center">
            <div class="w-24 h-24 mx-auto rounded-2xl flex items-center justify-center mb-5 shadow-lg
              group-hover:scale-110 group-hover:rotate-3 transition-all duration-500"
              style="background: linear-gradient(135deg, #F59E0B, #d97706);">
              <span class="text-4xl font-extrabold text-white">B1</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-2">Intermédiaire</h3>
            <p class="text-gray-500 text-sm mb-5 leading-relaxed">
              Compréhension des points essentiels sur des sujets familiers au travail, à l'école et dans les loisirs
            </p>
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold"
              style="background-color: #dcfce7; color: #166534;">
              <i class="pi pi-check-circle text-xs"></i> Disponible
            </span>
          </div>
        </div>

        <!-- B2 -->
        <div class="cert-card relative rounded-3xl border-2 overflow-hidden group cursor-pointer hover:shadow-2xl transition-all duration-500"
          style="border-color: #0d6e4f;">
          <div class="absolute top-0 right-0">
            <div class="text-white text-xs font-bold px-4 py-1.5 rounded-bl-xl"
              style="background: linear-gradient(135deg, #0d6e4f, #064e3b);">
              NOUVEAU
            </div>
          </div>
          <div class="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-500"
            style="background: radial-gradient(circle at 70% 50%, #0d6e4f 0%, transparent 70%);" />

          <div class="relative p-8 text-center">
            <div class="w-24 h-24 mx-auto rounded-2xl flex items-center justify-center mb-5 shadow-lg
              group-hover:scale-110 group-hover:rotate-3 transition-all duration-500"
              style="background: linear-gradient(135deg, #0d6e4f, #064e3b);">
              <span class="text-4xl font-extrabold text-white">B2</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-2">Avancé</h3>
            <p class="text-gray-500 text-sm mb-5 leading-relaxed">
              Communication claire et détaillée sur des sujets complexes, y compris techniques et abstraits
            </p>
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold"
              style="background-color: #dcfce7; color: #166534;">
              <i class="pi pi-check-circle text-xs"></i> Disponible
            </span>
          </div>
        </div>
      </div>

      <!-- Certifications reconnues -->
      <div class="rounded-3xl p-8 sm:p-12 text-white relative overflow-hidden"
        style="background: linear-gradient(135deg, #0d6e4f 0%, #064e3b 100%);">

        <!-- Décorations de fond -->
        <div class="absolute top-0 right-0 w-64 h-64 rounded-full opacity-10"
          style="background: radial-gradient(circle, #F59E0B, transparent); transform: translate(30%, -30%);" />
        <div class="absolute bottom-0 left-0 w-48 h-48 rounded-full opacity-10"
          style="background: radial-gradient(circle, #F59E0B, transparent); transform: translate(-30%, 30%);" />

        <div class="relative text-center mb-10">
          <h3 class="text-3xl font-bold mb-3">Certifications reconnues</h3>
          <p class="text-lg" style="color: rgba(255,255,255,0.75);">
            Nos simulations sont conformes aux examens officiels suivants
          </p>
        </div>

        <div class="relative grid sm:grid-cols-2 lg:grid-cols-4 gap-6">

          <!-- Goethe -->
          <div class="cert-org rounded-2xl p-6 text-center group transition-all duration-300 hover:scale-105"
            style="background: rgba(255,255,255,0.1); backdrop-filter: blur(4px);">
            <div class="w-16 h-16 mx-auto bg-white rounded-full flex items-center justify-center mb-4
              group-hover:shadow-lg transition-all duration-300"
              style="box-shadow: 0 0 0 0 rgba(245,158,11,0);">
              <i class="pi pi-building text-2xl" style="color: #0d6e4f;"></i>
            </div>
            <h4 class="font-bold text-lg mb-1">Goethe-Institut</h4>
            <p class="text-sm" style="color: rgba(255,255,255,0.65);">Certification internationale</p>
          </div>

          <!-- ÖSD -->
          <div class="cert-org rounded-2xl p-6 text-center group transition-all duration-300 hover:scale-105"
            style="background: rgba(255,255,255,0.1); backdrop-filter: blur(4px);">
            <div class="w-16 h-16 mx-auto bg-white rounded-full flex items-center justify-center mb-4
              group-hover:shadow-lg transition-all duration-300">
              <i class="pi pi-shield text-2xl" style="color: #0d6e4f;"></i>
            </div>
            <h4 class="font-bold text-lg mb-1">ÖSD</h4>
            <p class="text-sm" style="color: rgba(255,255,255,0.65);">Diplôme autrichien</p>
          </div>

          <!-- TELC -->
          <div class="cert-org rounded-2xl p-6 text-center group transition-all duration-300 hover:scale-105"
            style="background: rgba(255,255,255,0.1); backdrop-filter: blur(4px);">
            <div class="w-16 h-16 mx-auto bg-white rounded-full flex items-center justify-center mb-4
              group-hover:shadow-lg transition-all duration-300">
              <i class="pi pi-verified text-2xl" style="color: #0d6e4f;"></i>
            </div>
            <h4 class="font-bold text-lg mb-1">TELC</h4>
            <p class="text-sm" style="color: rgba(255,255,255,0.65);">Certifications européennes</p>
          </div>

          <!-- TestDaF -->
          <div class="cert-org rounded-2xl p-6 text-center group transition-all duration-300 hover:scale-105"
            style="background: rgba(255,255,255,0.1); backdrop-filter: blur(4px);">
            <div class="w-16 h-16 mx-auto bg-white rounded-full flex items-center justify-center mb-4
              group-hover:shadow-lg transition-all duration-300">
              <i class="pi pi-globe text-2xl" style="color: #0d6e4f;"></i>
            </div>
            <h4 class="font-bold text-lg mb-1">TestDaF</h4>
            <p class="text-sm" style="color: rgba(255,255,255,0.65);">Études universitaires</p>
          </div>
        </div>

        <!-- CTA -->
        <div class="relative text-center mt-10">
          <button
            class="inline-flex items-center gap-2 px-8 py-3 rounded-xl font-bold text-base transition-all duration-300
              hover:scale-105 hover:shadow-xl active:scale-95"
            style="background: white; color: #0d6e4f;"
            @click="scrollToExams"
          >
            Découvrir nos examens
            <i class="pi pi-arrow-down"></i>
          </button>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
const scrollToExams = () => {
  const element = document.querySelector('#examens')
  if (element) element.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.cert-card {
  background: white;
}

.cert-card:hover {
  transform: translateY(-4px);
}

.cert-org:hover {
  background: rgba(255, 255, 255, 0.18) !important;
}

/* Animation pulse sur les icônes au hover */
.cert-org:hover .pi {
  animation: pulse-icon 0.6s ease-in-out;
}

@keyframes pulse-icon {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}
</style>