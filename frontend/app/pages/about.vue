<template>
  <div class="overflow-hidden">
    <!-- Hero -->
    <section
      class="relative min-h-[70vh] flex items-center justify-center text-white overflow-hidden"
      style="
        background: linear-gradient(
          135deg,
          #0d6e4f 0%,
          #064e3b 60%,
          #0d6e4f 100%
        );
      "
    >
      <div
        class="absolute inset-0 opacity-10"
        style="
          background-image: radial-gradient(
            circle at 2px 2px,
            white 1px,
            transparent 0
          );
          background-size: 40px 40px;
        "
      />
      <div
        class="absolute top-20 right-20 w-64 h-64 rounded-full blur-3xl animate-pulse-slow"
        style="
          background: radial-gradient(
            circle,
            rgba(245, 158, 11, 0.3),
            transparent
          );
        "
      />
      <div
        class="absolute bottom-10 left-10 w-48 h-48 rounded-full blur-3xl animate-pulse-slow-delay"
        style="
          background: radial-gradient(
            circle,
            rgba(245, 158, 11, 0.2),
            transparent
          );
        "
      />

      <div class="relative max-w-4xl mx-auto px-6 text-center">
        <div
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-8"
          style="
            background: rgba(245, 158, 11, 0.2);
            border: 1px solid rgba(245, 158, 11, 0.4);
            color: #f59e0b;
          "
        >
          <i class="pi pi-star-fill text-xs"></i>
          {{ t("about.hero.badge") }}
        </div>

        <h1
          class="text-5xl sm:text-6xl lg:text-7xl font-extrabold mb-6 leading-tight"
        >
          {{ t("about.hero.title_line1") }}<br />
          <span style="color: #f59e0b">{{ t("about.hero.title_line2") }}</span>
        </h1>

        <p
          class="text-xl text-white/75 max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          {{ t("about.hero.subtitle") }}
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <NuxtLink
            to="/tarifs"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition-all hover:scale-105 hover:shadow-xl"
            style="background: #f59e0b; color: #064e3b"
          >
            {{ t("about.hero.cta_start") }} <i class="pi pi-arrow-right"></i>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/examens"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-base transition-all hover:scale-105"
            style="
              background: rgba(255, 255, 255, 0.1);
              border: 2px solid rgba(255, 255, 255, 0.3);
              color: white;
            "
          >
            {{ t("about.hero.cta_exams") }} <i class="pi pi-eye"></i>
          </NuxtLink>
        </div>
      </div>

      <div class="absolute bottom-0 left-0 right-0">
        <svg
          viewBox="0 0 1440 80"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          class="w-full"
        >
          <path
            d="M0 0L60 8C120 16 240 32 360 37.3C480 43 600 37 720 32C840 27 960 21 1080 21.3C1200 21 1320 27 1380 29.3L1440 32V80H0V0Z"
            fill="white"
          />
        </svg>
      </div>
    </section>

    <!-- Stats -->
    <section class="py-16 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-8">
          <div
            v-for="stat in stats"
            :key="stat.key"
            class="text-center hover:scale-105 transition-transform"
          >
            <div
              class="text-4xl sm:text-5xl font-extrabold mb-2"
              style="
                background: linear-gradient(135deg, #0d6e4f, #f59e0b);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
              "
            >
              {{ stat.value }}
            </div>
            <p class="text-gray-500 text-sm font-medium">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="py-20 bg-gray-50">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16">
          <div
            class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold mb-4"
            style="background: #e6f4ef; color: #0d6e4f"
          >
            <i class="pi pi-book"></i> {{ t("about.features.badge") }}
          </div>
          <h2 class="text-4xl font-bold text-gray-900 mb-4">
            {{ t("about.features.title") }}
          </h2>
          <p class="text-lg text-gray-500 max-w-2xl mx-auto">
            {{ t("about.features.subtitle") }}
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div
            v-for="feature in features"
            :key="feature.key"
            class="bg-white rounded-2xl p-7 border-2 border-gray-100 hover:border-transparent hover:shadow-2xl transition-all group relative overflow-hidden"
          >
            <div
              class="absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity rounded-2xl"
              :style="`background: ${feature.color};`"
            />
            <div
              class="w-14 h-14 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 group-hover:rotate-3 transition-all"
              :style="`background: linear-gradient(135deg, ${feature.color}, ${feature.colorDark});`"
            >
              <i :class="['pi text-2xl text-white', feature.icon]"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">
              {{ feature.title }}
            </h3>
            <p class="text-gray-500 leading-relaxed text-sm">
              {{ feature.desc }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Niveaux -->
    <section class="py-20 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-4xl font-bold text-gray-900 mb-4">
            {{ t("about.levels.title") }}
          </h2>
          <p class="text-gray-500 text-lg">{{ t("about.levels.subtitle") }}</p>
        </div>

        <div class="grid md:grid-cols-2 gap-8">
          <div
            class="relative rounded-3xl p-8 overflow-hidden group hover:-translate-y-2 transition-all cursor-pointer border-2"
            style="border-color: #f59e0b; background: white"
            @click="navigateTo('/dashboard/examens')"
          >
            <div
              class="absolute top-0 right-0 text-white text-xs font-bold px-4 py-2 rounded-bl-xl"
              style="background: linear-gradient(135deg, #f59e0b, #d97706)"
            >
              {{ t("about.levels.b1.badge") }}
            </div>
            <div
              class="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all"
              style="background: linear-gradient(135deg, #f59e0b, #d97706)"
            >
              <span class="text-3xl font-extrabold text-white">B1</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-3">
              {{ t("about.levels.b1.name") }}
            </h3>
            <p class="text-gray-500 mb-5 leading-relaxed">
              {{ t("about.levels.b1.desc") }}
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="org in ['Goethe', 'ÖSD', 'TELC']"
                :key="org"
                class="text-xs font-semibold px-3 py-1 rounded-full"
                style="background: rgba(245, 158, 11, 0.12); color: #92400e"
                >{{ org }}</span
              >
            </div>
          </div>

          <div
            class="relative rounded-3xl p-8 overflow-hidden group hover:-translate-y-2 transition-all cursor-pointer border-2"
            style="border-color: #0d6e4f; background: white"
            @click="navigateTo('/dashboard/examens')"
          >
            <div
              class="absolute top-0 right-0 text-white text-xs font-bold px-4 py-2 rounded-bl-xl"
              style="background: linear-gradient(135deg, #0d6e4f, #064e3b)"
            >
              {{ t("about.levels.b2.badge") }}
            </div>
            <div
              class="w-20 h-20 rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all"
              style="background: linear-gradient(135deg, #0d6e4f, #064e3b)"
            >
              <span class="text-3xl font-extrabold text-white">B2</span>
            </div>
            <h3 class="text-2xl font-bold text-gray-900 mb-3">
              {{ t("about.levels.b2.name") }}
            </h3>
            <p class="text-gray-500 mb-5 leading-relaxed">
              {{ t("about.levels.b2.desc") }}
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="org in ['Goethe', 'ÖSD', 'TELC']"
                :key="org"
                class="text-xs font-semibold px-3 py-1 rounded-full"
                style="background: rgba(13, 110, 79, 0.1); color: #064e3b"
                >{{ org }}</span
              >
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Certifications -->
    <section
      class="py-20 text-white relative overflow-hidden"
      style="background: linear-gradient(135deg, #0d6e4f 0%, #064e3b 100%)"
    >
      <div class="relative max-w-5xl mx-auto px-6 text-center">
        <h2 class="text-4xl font-bold mb-4">
          {{ t("about.certifications.title") }}
        </h2>
        <p class="text-white/70 text-lg mb-14 max-w-2xl mx-auto">
          {{ t("about.certifications.subtitle") }}
        </p>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-14">
          <div
            v-for="cert in certifications"
            :key="cert.name"
            class="rounded-2xl p-6 text-center group hover:scale-105 hover:bg-white/20 transition-all"
            style="background: rgba(255, 255, 255, 0.1)"
          >
            <div
              class="w-14 h-14 mx-auto bg-white rounded-full flex items-center justify-center mb-4"
            >
              <i :class="['pi text-2xl', cert.icon]" style="color: #0d6e4f"></i>
            </div>
            <h4 class="font-bold text-lg mb-1">{{ cert.name }}</h4>
            <p class="text-sm" style="color: rgba(255, 255, 255, 0.6)">
              {{ cert.desc }}
            </p>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink
            to="/tarifs"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold transition-all hover:scale-105"
            style="background: #f59e0b; color: #064e3b"
          >
            {{ t("about.certifications.cta_pricing") }}
            <i class="pi pi-tag"></i>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/examens"
            class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-bold transition-all hover:scale-105"
            style="
              background: rgba(255, 255, 255, 0.1);
              border: 2px solid rgba(255, 255, 255, 0.3);
              color: white;
            "
          >
            {{ t("about.certifications.cta_exams") }} <i class="pi pi-play"></i>
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n();

useHead({
  title: "À propos — GoToGermany",
  meta: [
    {
      name: "description",
      content:
        "Préparez-vous aux examens d'allemand B1 et B2 avec GoToGermany.",
    },
  ],
});

const stats = computed(() => [
  { key: "candidates", value: "3 000+", label: t("about.stats.candidates") },
  { key: "success_rate", value: "92%", label: t("about.stats.success_rate") },
  { key: "levels", value: "B1 & B2", label: t("about.stats.levels") },
  { key: "access", value: "24/7", label: t("about.stats.access") },
]);

const features = computed(() => [
  {
    key: "exams",
    icon: "pi-file-edit",
    color: "#0d6e4f",
    colorDark: "#064e3b",
    title: t("about.features.items.exams.title"),
    desc: t("about.features.items.exams.desc"),
  },
  {
    key: "audio",
    icon: "pi-volume-up",
    color: "#F59E0B",
    colorDark: "#d97706",
    title: t("about.features.items.audio.title"),
    desc: t("about.features.items.audio.desc"),
  },
  {
    key: "access",
    icon: "pi-lock",
    color: "#0d6e4f",
    colorDark: "#064e3b",
    title: t("about.features.items.access.title"),
    desc: t("about.features.items.access.desc"),
  },
  {
    key: "progress",
    icon: "pi-chart-bar",
    color: "#F59E0B",
    colorDark: "#d97706",
    title: t("about.features.items.progress.title"),
    desc: t("about.features.items.progress.desc"),
  },
  {
    key: "partners",
    icon: "pi-users",
    color: "#0d6e4f",
    colorDark: "#064e3b",
    title: t("about.features.items.partners.title"),
    desc: t("about.features.items.partners.desc"),
  },
  {
    key: "payment",
    icon: "pi-mobile",
    color: "#F59E0B",
    colorDark: "#d97706",
    title: t("about.features.items.payment.title"),
    desc: t("about.features.items.payment.desc"),
  },
]);

const certifications = computed(() => [
  {
    name: "Goethe-Institut",
    icon: "pi-building",
    desc: t("about.certifications.items.goethe"),
  },
  { name: "ÖSD", icon: "pi-shield", desc: t("about.certifications.items.osd") },
  {
    name: "TELC",
    icon: "pi-verified",
    desc: t("about.certifications.items.telc"),
  },
  {
    name: t("about.certifications.items.partners.name"),
    icon: "pi-home",
    desc: t("about.certifications.items.partners.desc"),
  },
]);
</script>

<style scoped>
@keyframes pulse-slow {
  0%,
  100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.1);
  }
}
@keyframes pulse-slow-delay {
  0%,
  100% {
    opacity: 0.2;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(1.15);
  }
}
.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}
.animate-pulse-slow-delay {
  animation: pulse-slow-delay 5s ease-in-out infinite 1s;
}
</style>
