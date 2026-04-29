<template>
  <section class="relative overflow-hidden min-h-150 sm:min-h-[700px] flex items-center">

    <!-- Background Image avec overlay -->
    <div class="absolute inset-0">
      <img src="/images/hero-bg.png" alt="Background" class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-grid-pattern opacity-10"></div>
    </div>

    <!-- Content -->
    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 w-full">
      <div class="grid lg:grid-cols-2 gap-12 items-center">

        <!-- Left Column -->
        <div class="text-center lg:text-left space-y-8">

          <!-- Badge -->
          <div class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20 animate-fade-in-down">
            <i class="pi pi-verified text-white"></i>
            <span class="text-sm font-semibold text-white">Certifié Goethe & ÖSD</span>
          </div>

          <!-- Headline -->
          <div class="animate-fade-in-up" style="animation-delay: 0.2s">
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Réussissez vos examens
              <span class="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent block animate-gradient">
                d'allemand
              </span>
            </h1>
            <p class="text-lg sm:text-xl text-gray-100 leading-relaxed">
              Préparez-vous efficacement avec des simulations conformes aux examens officiels.
              Tests adaptatifs, corrections IA, suivi de progression.
            </p>
          </div>

          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start animate-fade-in-up"
            style="animation-delay: 0.4s">
            <Button
              label="Commencer gratuitement"
              icon="pi pi-arrow-right"
              iconPos="right"
              size="large"
              class="bg-white! text-teal-900! !border-0 shadow-xl hover:!bg-gray-100 hover:scale-105 transition-all !font-bold"
              @click="openSignup"
            />
          </div>

          <!-- Trust Signals -->
          <div class="pt-8 border-t border-white/20 animate-fade-in-up" style="animation-delay: 0.6s">
            <p class="text-sm text-gray-200 mb-4 uppercase tracking-wide font-semibold">
              Utilisé par des milliers d'étudiants
            </p>
            <div class="grid grid-cols-3 gap-6">
              <div class="text-center animate-bounce-in" style="animation-delay: 0.7s">
                <div class="text-3xl font-bold text-white">3K+</div>
                <div class="text-sm text-gray-200">Étudiants</div>
              </div>
              <div class="text-center animate-bounce-in" style="animation-delay: 0.8s">
                <div class="text-3xl font-bold text-white">95%</div>
                <div class="text-sm text-gray-200">Taux de réussite</div>
              </div>
              <div class="text-center animate-bounce-in" style="animation-delay: 0.9s">
                <div class="text-3xl font-bold text-white">10K+</div>
                <div class="text-sm text-gray-200">Tests</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - Floating Image -->
        <div class="relative hidden lg:block animate-fade-in-right" style="animation-delay: 0.5s">
          <img
            src="/images/hero2.png"
            alt="Student Success"
            class="w-full h-full object-cover rounded-full animate-float shadow-2xl"
          />
          <div class="absolute -top-4 -right-4 w-24 h-24 bg-linear-to-br from-yellow-400 to-orange-400 rounded-full opacity-50 blur-2xl animate-pulse"></div>
          <div class="absolute -bottom-4 -left-4 w-32 h-32 bg-linear-to-br from-teal-400 to-teal-600 rounded-full opacity-50 blur-2xl animate-pulse-delayed"></div>
        </div>
      </div>
    </div>

    <!-- Wave separator -->
    <div class="absolute bottom-0 left-0 right-0">
      <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full">
        <path d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0V120Z" fill="white"/>
      </svg>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAuthDialog } from '~/composables/useAuthDialog';

const { openSignup } = useAuthDialog()
</script>

<style scoped>
@keyframes fade-in-down {
  from { opacity: 0; transform: translateY(-30px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in-right {
  from { opacity: 0; transform: translateX(50px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes bounce-in {
  0% { opacity: 0; transform: scale(0.3); }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1); }
}
@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
@keyframes pulse-delayed {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.animate-fade-in-down { animation: fade-in-down 0.8s ease-out; animation-fill-mode: both; }
.animate-fade-in-up { animation: fade-in-up 0.8s ease-out; animation-fill-mode: both; }
.animate-fade-in-right { animation: fade-in-right 1s ease-out; animation-fill-mode: both; }
.animate-bounce-in { animation: bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55); animation-fill-mode: both; }
.animate-gradient { background-size: 200% 200%; animation: gradient 3s ease infinite; }
.animate-float { animation: float 4s ease-in-out infinite; }
.animate-pulse-delayed { animation: pulse-delayed 3s ease-in-out infinite; animation-delay: 1.5s; }

.bg-grid-pattern {
  background-image: linear-gradient(to right, rgba(255,255,255,0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 30px 30px;
}
:deep(.p-button) { transition: all 0.3s ease; }
:deep(.p-button:hover) { transform: translateY(-2px); }
:deep(.p-button:active) { transform: translateY(0); }
</style>