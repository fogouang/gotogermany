<template>
  <footer class="bg-gray-900 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
        <!-- Brand -->
        <div class="col-span-2 md:col-span-1">
          <div class="flex items-center gap-2 mb-4">
            <i class="pi pi-flag text-2xl text-indigo-400"></i>
            <span class="text-xl font-bold">DeutschTest</span>
          </div>
          <p class="text-gray-400 text-sm mb-4">
            Votre plateforme de préparation aux examens d'allemand.
          </p>
          <div class="flex gap-3">
            <Button icon="pi pi-facebook" rounded text />
            <Button icon="pi pi-twitter" rounded text />
            <Button icon="pi pi-linkedin" rounded text />
          </div>
        </div>

        <!-- Examens -->
        <div>
          <h3 class="font-semibold mb-4 text-sm sm:text-base">Examens</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="text-gray-400 hover:text-white transition">Goethe-Zertifikat</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">TestDaF</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">ÖSD</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">TELC</a></li>
          </ul>
        </div>

        <!-- Ressources -->
        <div>
          <h3 class="font-semibold mb-4 text-sm sm:text-base">Ressources</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="text-gray-400 hover:text-white transition">Blog</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">Tutoriels</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">FAQ</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">Support</a></li>
          </ul>
        </div>

        <!-- Légal -->
        <div>
          <h3 class="font-semibold mb-4 text-sm sm:text-base">Légal</h3>
          <ul class="space-y-2 text-sm">
            <li><a href="#" class="text-gray-400 hover:text-white transition">CGU</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">Confidentialité</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">Cookies</a></li>
            <li><a href="#" class="text-gray-400 hover:text-white transition">Contact</a></li>
          </ul>
        </div>
      </div>

      <!-- Copyright -->
      <Divider class="my-6 sm:my-8" />
      <div class="text-center text-sm text-gray-400">
        © {{ new Date().getFullYear() }} DeutschTest. Tous droits réservés.
      </div>
    </div>
  </footer>
</template>