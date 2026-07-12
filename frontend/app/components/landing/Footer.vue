<template>
  <footer class="relative bg-gray-950">
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
              src="/images/logo.png"
              alt="Logo"
              class="h-15 object-contain"
            />
          </div>
          <p class="text-gray-400 leading-relaxed mb-6">
           {{ t("footer.tagline") }}
          </p>

          <!-- Social Links -->
          <div class="flex gap-2">
            <a
              href="#"
              class="w-9 h-9 rounded-full border border-gray-700 flex items-center justify-center text-gray-400 hover:text-white hover:border-teal-500 transition-all"
            >
              <i class="pi pi-facebook text-sm"></i>
            </a>
            <a
              href="#"
              class="w-9 h-9 rounded-full border border-gray-700 flex items-center justify-center text-gray-400 hover:text-white hover:border-teal-500 transition-all"
            >
              <i class="pi pi-twitter text-sm"></i>
            </a>
            <a
              href="#"
              class="w-9 h-9 rounded-full border border-gray-700 flex items-center justify-center text-gray-400 hover:text-white hover:border-teal-500 transition-all"
            >
              <i class="pi pi-linkedin text-sm"></i>
            </a>
            <a
              href="#"
              class="w-9 h-9 rounded-full border border-gray-700 flex items-center justify-center text-gray-400 hover:text-white hover:border-teal-500 transition-all"
            >
              <i class="pi pi-instagram text-sm"></i>
            </a>
          </div>
        </div>

        <!-- Examens -->
        <div>
          <h3 class="font-bold mb-5 text-base flex items-center gap-2">
            <i class="pi pi-book text-teal-400"></i>
             {{ t("footer.exams.title") }}
          </h3>
          <ul class="space-y-3 text-sm">
            <li v-for="item in examens" :key="item.label">
              <a
                :href="item.href"
                class="text-gray-400 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs text-teal-500 group-hover:translate-x-1 transition-transform"
                ></i>
                {{ item.label }}
              </a>
            </li>
          </ul>
        </div>

        <!-- Ressources -->
        <div>
          <h3 class="font-bold mb-5 text-base flex items-center gap-2">
            <i class="pi pi-compass text-teal-400"></i>
            {{ t("footer.resources.title") }}
          </h3>
          <ul class="space-y-3 text-sm">
            <li v-for="item in ressources" :key="item.label">
              <a
                :href="item.href"
                class="text-gray-400 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs text-teal-500 group-hover:translate-x-1 transition-transform"
                ></i>
                {{ item.label }}
              </a>
            </li>
          </ul>
        </div>

        <!-- À propos -->
        <div>
          <h3 class="font-bold mb-5 text-base flex items-center gap-2">
            <i class="pi pi-info-circle text-teal-400"></i>
             {{ t("footer.about.title") }}
          </h3>
          <ul class="space-y-3 text-sm">
            <li v-for="item in apropos" :key="item.label">
              <a
                :href="item.href"
                class="text-gray-400 hover:text-white transition-colors flex items-center gap-2 group"
              >
                <i
                  class="pi pi-angle-right text-xs text-teal-500 group-hover:translate-x-1 transition-transform"
                ></i>
                {{ item.label }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom -->
      <div
        class="mt-12 pt-6 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-4"
      >
        <p class="text-sm text-gray-500">
          © {{ new Date().getFullYear() }}
          <span class="font-semibold text-white"> {{ t("footer.copyright") }}</span>
        </p>
        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span class="flex items-center gap-1">
            <i class="pi pi-shield text-teal-400 text-xs"></i>
            {{ t("footer.secure_payment") }}
          </span>
          <span class="text-gray-700">·</span>
          <span class="text-gray-700">·</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { t } = useI18n();

const examens = computed(() => [
  { label: t("footer.exams.links.goethe_b1"), href: "#" },
  { label: t("footer.exams.links.goethe_b2"), href: "#" },
  { label: t("footer.exams.links.osd"), href: "#" },
  { label: t("footer.exams.links.testdaf"), href: "#" },
  { label: t("footer.exams.links.telc"), href: "#" },
]);

const ressources = computed(() => [
  { label: t("footer.resources.links.guides"), href: "#" },
  { label: t("footer.resources.links.faq"), href: "/faq" },
  { label: t("footer.resources.links.tutorials"), href: "#" },
  { label: t("footer.resources.links.privacy_policy"), href: "/politique" },
]);

const apropos = computed(() => [
  { label: t("footer.about.links.mission"), href: "/about" },
  { label: t("footer.about.links.pricing"), href: "#" },
  { label: t("footer.about.links.terms"), href: "#" },
  { label: t("footer.about.links.privacy"), href: "/politique" },
  { label: t("footer.about.links.contact"), href: "/contact" },
]);
</script>
