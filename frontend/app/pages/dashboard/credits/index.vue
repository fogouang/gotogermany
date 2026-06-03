<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Crédits IA</h1>
      <p class="text-sm text-gray-500">Gérez vos crédits de correction IA</p>
    </div>

    <!-- Solde actuel -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 text-center">
      <div class="w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center mx-auto mb-4">
        <i class="pi pi-sparkles text-3xl text-amber-500"></i>
      </div>
      <p class="text-4xl font-extrabold text-gray-900 mb-1">{{ authStore.aiCredits }}</p>
      <p class="text-gray-500 text-sm">crédit(s) disponible(s)</p>
    </div>

    <!-- Acheter -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
      <h2 class="font-semibold text-gray-900">Acheter des crédits</h2>
      <p class="text-sm text-gray-500">
        Contactez-nous via WhatsApp pour acheter des crédits supplémentaires.
      </p>
      
      <a  href="https://wa.me/237670886288?text=Bonjour, je souhaite acheter des crédits IA sur GoToGermany."
        target="_blank"
        class="flex items-center gap-2 px-4 py-3 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 transition-colors w-fit"
      >
        <i class="pi pi-whatsapp"></i>
        Acheter via WhatsApp
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard', middleware: 'auth' })
const authStore = useAuthStore()
</script>