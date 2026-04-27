<template>
  <footer
    class="relative"
    style="
      background: linear-gradient(
        135deg,
        hsl(145 63% 32%) 0%,
        hsl(145 50% 22%) 100%
      );
    "
  >
    <div
      class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 text-white"
    >
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12"
      >
        <!-- Brand -->
        <div class="lg:col-span-2">
          <div class="flex items-center gap-3 mb-4">
            <img
              src="/images/logo1.png"
              alt="Logo"
              class="h-34 object-contain"
            />
          </div>
          <p class="text-teal-100 leading-relaxed mb-6">
            Votre plateforme de préparation aux examens d'allemand. Simulations
            conformes, corrections IA, suivi de progression.
          </p>

          <!-- Social Links -->
          <div class="flex gap-3">
            <Button
              icon="pi pi-facebook"
              rounded
              text
              class="text-white! hover:bg-white/10!"
            />
            <Button
              icon="pi pi-twitter"
              rounded
              text
              class="text-white! hover:bg-white/10!"
            />
            <Button
              icon="pi pi-linkedin"
              rounded
              text
              class="text-white! hover:bg-white/10!"
            />
            <Button
              icon="pi pi-instagram"
              rounded
              text
              class="text-white! hover:bg-white/10!"
            />
          </div>

          <!-- Newsletter -->
          <div class="mt-6">
            <p class="text-sm font-semibold mb-3">Restez informé</p>
            <div class="flex gap-2">
              <InputText
                placeholder="Votre email"
                class="bg-white/10! border-white/20! text-white! placeholder:text-teal-200! flex-1"
              />
              <Button
                icon="pi pi-arrow-right"
                class="bg-yellow-400! border-0! text-gray-900! hover:bg-yellow-500!"
              />
            </div>
          </div>
        </div>

        <!-- Examens -->
        <div>
          <h3 class="font-bold mb-4 text-lg flex items-center gap-2">
            <i class="pi pi-book text-yellow-400"></i>
            Examens
          </h3>
          <ul class="space-y-3 text-sm">
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Goethe B1
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Goethe B2
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                ÖSD Zertifikat
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                TestDaF
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                TELC Deutsch
              </a>
            </li>
          </ul>
        </div>

        <!-- Ressources -->
        <div>
          <h3 class="font-bold mb-4 text-lg flex items-center gap-2">
            <i class="pi pi-compass text-yellow-400"></i>
            Ressources
          </h3>
          <ul class="space-y-3 text-sm">
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Guides d'étude
              </a>
            </li>
            <li>
              <a
                href="/faq"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                FAQ
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Tutoriels vidéo
              </a>
            </li>
            <li>
              <a
                href="/politique"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Politique et confidentialite
              </a>
            </li>
          </ul>
        </div>

        <!-- À propos & Légal -->
        <div>
          <h3 class="font-bold mb-4 text-lg flex items-center gap-2">
            <i class="pi pi-info-circle text-yellow-400"></i>
            À propos
          </h3>
          <ul class="space-y-3 text-sm">
            <li>
              <a
                href="/about"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Notre mission
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Tarifs
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                CGU
              </a>
            </li>
            <li>
              <a
                href="/politique"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Confidentialité
              </a>
            </li>
            <li>
              <a
                href="/contact"
                class="text-teal-100 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs group-hover:translate-x-1 transition-transform"
                ></i>
                Contact
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Section -->
      <Divider class="my-8! border-white/20!" />

      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <!-- Copyright -->
        <div class="text-sm text-teal-100">
          © {{ new Date().getFullYear() }}
          <span class="font-semibold">DeutschTest</span>. Tous droits réservés.
        </div>

        <!-- Badges -->
        <div class="flex flex-wrap gap-3 items-center">
          <Tag
            value="Certifié Goethe"
            class="bg-white/10! text-white! border-white/20!"
          />
          <Tag
            value="Partenaire ÖSD"
            class="bg-white/10! text-white! border-white/20!"
          />
          <div class="flex items-center gap-1 text-teal-100 text-sm">
            <i class="pi pi-shield text-yellow-400"></i>
            <span>Paiement sécurisé</span>
          </div>
        </div>

       
      </div>
    </div>

    <!-- Decorative wave top -->
    <div class="absolute bottom-full left-0 right-0">
      <svg
        viewBox="0 0 1440 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        class="w-full"
      >
        <path
          d="M0 0L60 8C120 16 240 32 360 37.3C480 43 600 37 720 32C840 27 960 21 1080 21.3C1200 21 1320 27 1380 29.3L1440 32V80H1380C1320 80 1200 80 1080 80C960 80 840 80 720 80C600 80 480 80 360 80C240 80 120 80 60 80H0V0Z"
          fill="hsl(145 63% 32%)"
        />
      </svg>
    </div>
  </footer>
</template>

<script setup lang="ts">
// Footer component
</script>

<style scoped>
:deep(.p-inputtext::placeholder) {
  color: rgba(153, 246, 228, 0.6);
}

:deep(.p-inputtext:focus) {
  border-color: rgba(253, 224, 71, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(253, 224, 71, 0.1);
}
</style>
