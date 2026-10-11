<template>
  <section class="relative bg-canvas py-16 sm:py-24">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <!-- En-tête -->
      <div class="mx-auto mb-12 max-w-3xl text-center">
        <p
          class="mb-3 inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-primary"
        >
          <span class="h-px w-6 bg-accent-500" />
          {{ t("exams_section.title") }}
          <span class="h-px w-6 bg-accent-500" />
        </p>
        <h2
          class="font-heading text-3xl font-bold tracking-tight text-ink sm:text-4xl"
        >
          {{ t("exams_section.subtitle1") }}<br />
          <span class="text-accent-600 dark:text-accent-400">{{
            t("exams_section.subtitle2")
          }}</span>
          {{ t("exams_section.subtitle3") }}
        </h2>
      </div>

      <!-- Organismes -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div
          v-for="org in orgs"
          :key="org.key"
          role="button"
          tabindex="0"
          class="group relative flex cursor-pointer flex-col items-center overflow-hidden rounded-card border border-line bg-card p-6 text-center shadow-soft transition-all duration-300 ease-spring hover:-translate-y-1 hover:border-accent-500/50 hover:shadow-lift focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent-500"
          @click="choisir(org.key)"
          @keydown.enter="choisir(org.key)"
        >
          <!-- Halo doré au survol -->
          <div
            class="pointer-events-none absolute -top-16 left-1/2 size-40 -translate-x-1/2 rounded-full bg-accent-500/0 blur-2xl transition-colors duration-300 group-hover:bg-accent-500/20"
            aria-hidden="true"
          />

          <!-- Logo -->
          <div
            class="relative mb-4 flex size-20 items-center justify-center rounded-card border border-line bg-white shadow-soft transition-transform duration-300 ease-spring group-hover:scale-105"
          >
            <img
              v-if="!logosEnErreur.has(org.key)"
              :src="`/images/${org.logo}`"
              :alt="org.name"
              loading="lazy"
              class="size-14 object-contain"
              @error="logosEnErreur.add(org.key)"
            />
            <span v-else class="font-heading text-xl font-bold text-zinc-900">
              {{ org.name.charAt(0) }}
            </span>
          </div>

          <!-- Nom -->
          <h3 class="relative font-heading text-lg font-bold text-ink">
            {{ org.name }}
          </h3>
          <p class="relative mt-1 mb-5 line-clamp-2 min-h-8 text-xs text-faint">
            {{ org.subtitle }}
          </p>

          <!-- Niveaux : chacun cliquable -->
          <div class="relative mb-5 flex flex-wrap justify-center gap-2">
            <button
              v-for="lvl in org.levels"
              :key="lvl"
              type="button"
              class="rounded-full border border-line bg-card-2 px-3.5 py-1.5 text-xs font-bold text-ink transition-all duration-200 hover:border-accent-500 hover:bg-accent-500 hover:text-accent-950"
              @click.stop="choisir(org.key, lvl)"
            >
              {{ lvl }}
            </button>
          </div>

          <!-- Pied : rend le clic évident -->
          <span
            class="relative mt-auto inline-flex items-center gap-1.5 text-sm font-semibold text-primary transition-colors group-hover:text-accent-600 dark:group-hover:text-accent-400"
          >
            {{ t("exams_section.cta") }}
            <i
              class="pi pi-arrow-right text-xs transition-transform duration-300 ease-spring group-hover:translate-x-1"
            />
          </span>
        </div>
      </div>

      <!-- Baseline -->
      <p
        class="mt-10 flex items-center justify-center gap-2 text-center text-sm text-muted"
      >
        <i class="pi pi-sparkles text-accent-500" />
        {{ t("exams_section.features") }}
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n();
const { choisir } = useChoixExamen();

// Logos introuvables : on affiche l'initiale à la place
const logosEnErreur = reactive(new Set<string>());

const orgs = computed(() => [
  {
    key: "goethe",
    name: t("exams_section.orgs.goethe.name"),
    subtitle: t("exams_section.orgs.goethe.subtitle"),
    logo: "goethe.jpg",
    levels: ["B1", "B2"],
  },
  {
    key: "telc",
    name: t("exams_section.orgs.telc.name"),
    subtitle: t("exams_section.orgs.telc.subtitle"),
    logo: "telc.png",
    levels: ["B1", "B2"],
  },
  {
    key: "osd",
    name: t("exams_section.orgs.osd.name"),
    subtitle: t("exams_section.orgs.osd.subtitle"),
    logo: "osd.png",
    levels: ["B1", "B2"],
  },
  {
    key: "testdaf",
    name: t("exams_section.orgs.testdaf.name"),
    subtitle: t("exams_section.orgs.testdaf.subtitle"),
    logo: "testdaf.png",
    levels: ["B2", "C1"], // à confirmer
  },
  {
    key: "ecl",
    name: t("exams_section.orgs.ecl.name"),
    subtitle: t("exams_section.orgs.ecl.subtitle"),
    logo: "ecl.png",
    levels: ["B1", "B2"], // à confirmer
  },
]);
</script>
