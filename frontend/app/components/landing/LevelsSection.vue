<template>
  <section class="py-16 bg-white">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <p
          class="text-sm font-semibold uppercase tracking-widest mb-3"
          style="color: #076152"
        >
          {{ t("exams_section.title") }}
        </p>
        <h2 class="text-3xl sm:text-4xl font-extrabold text-gray-900">
        {{ t("exams_section.subtitle1") }}<br />
          <span style="color: #076152">{{ t("exams_section.subtitle2") }}</span> {{ t("exams_section.subtitle3") }}
        </h2>
      </div>

      <!-- 3 providers -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="org in orgs"
          :key="org.name"
          class="group relative rounded-2xl border border-gray-100 bg-white p-8 text-center hover:border-transparent hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden"
          @mouseenter="active = org.name"
          @mouseleave="active = null"
        >
          <!-- Fond coloré au hover -->
          <div
            class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            :style="`background: linear-gradient(135deg, ${org.color}10 0%, ${org.color}20 100%);`"
          />

          <!-- Logo -->
          <div
            class="relative w-24 h-24 mx-auto rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 bg-white shadow-sm border border-gray-100"
          >
            <img
              :src="`/images/${org.logo}`"
              :alt="org.name"
              class="w-16 h-16 object-contain"
            />
          </div>

          <!-- Nom -->
          <h3 class="relative text-xl font-bold text-gray-900 mb-1">
            {{ org.name }}
          </h3>
          <p class="relative text-xs text-gray-400 mb-6">{{ org.subtitle }}</p>

          <!-- Niveaux B1 / B2 -->
          <div class="relative flex gap-3 justify-center">
            <span
              v-for="lvl in ['B1', 'B2']"
              :key="lvl"
              class="px-5 py-2 rounded-full text-sm font-bold border-2 transition-all duration-300"
              :style="
                active === org.name
                  ? `background: ${org.color}; color: white; border-color: ${org.color};`
                  : `background: white; color: ${org.color}; border-color: ${org.color};`
              "
            >
              {{ lvl }}
            </span>
          </div>
        </div>
      </div>

      <!-- Baseline -->
      <p class="text-center text-sm text-gray-400 mt-8">
      {{   t("exams_section.features")}}
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n();

const active = ref<string | null>(null);

const orgs = computed(() => [
  {
    key: "goethe",
    name: t("exams_section.orgs.goethe.name"),
    subtitle: t("exams_section.orgs.goethe.subtitle"),
    logo: "goethe.jpg",
    color: "#076152",
  },
  {
    key: "telc",
    name: t("exams_section.orgs.telc.name"),
    subtitle: t("exams_section.orgs.telc.subtitle"),
    logo: "telc.png",
    color: "#F59E0B",
  },
  {
    key: "osd",
    name: t("exams_section.orgs.osd.name"),
    subtitle: t("exams_section.orgs.osd.subtitle"),
    logo: "osd.png",
    color: "#6366f1",
  },
]);
</script>
