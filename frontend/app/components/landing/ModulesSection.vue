<template>
  <section class="relative overflow-hidden bg-card py-16 sm:py-24">
    <div
      class="pointer-events-none absolute inset-0 bg-grid opacity-30 mask-[radial-gradient(ellipse_at_center,black,transparent_70%)]"
      aria-hidden="true"
    />

    <div class="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
      <!-- En-tête -->
      <div class="mx-auto mb-14 max-w-3xl text-center">
        <p
          class="mb-3 inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-primary"
        >
          <span class="h-px w-6 bg-accent-500" />
          {{ t("modules_section.eyebrow") }}
          <span class="h-px w-6 bg-accent-500" />
        </p>
        <h2 class="font-heading text-3xl font-bold tracking-tight text-ink sm:text-4xl">
          {{ t("modules_section.title") }}
        </h2>
        <p class="mt-4 text-base text-muted sm:text-lg">
          {{ t("modules_section.subtitle") }}
        </p>
      </div>

      <!-- Schéma : 4 modules autour du sujet complet -->
      <div class="relative">
        <!-- Anneau de liaison (desktop) -->
        <div
          class="pointer-events-none absolute top-1/2 left-1/2 hidden size-120 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-dashed border-accent-500/30 lg:block"
          aria-hidden="true"
        />

        <div
          class="relative grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-[1fr_minmax(0,20rem)_1fr] lg:grid-rows-2 lg:gap-x-10 lg:gap-y-8"
        >
          <!-- Carte centrale -->
          <div
            class="brand-gradient relative flex flex-col items-center justify-center overflow-hidden rounded-card p-8 text-center shadow-brand sm:col-span-2 lg:col-span-1 lg:col-start-2 lg:row-span-2 lg:row-start-1"
          >
            <div
              class="pointer-events-none absolute -top-12 -right-12 size-40 rounded-full bg-white/10"
              aria-hidden="true"
            />
            <span
              class="relative mb-5 flex size-16 items-center justify-center rounded-leaf bg-white/15 ring-1 ring-white/25"
            >
              <i class="pi pi-verified text-3xl" />
            </span>
            <h3 class="relative font-heading text-xl font-bold">
              {{ t("modules_section.center.title") }}
            </h3>
            <span class="flag-stripe relative my-4 h-1 w-16 rounded-full" />
            <p class="relative text-sm leading-relaxed opacity-85">
              {{ t("modules_section.center.description") }}
            </p>
            <div class="relative mt-6 flex flex-wrap justify-center gap-1.5">
              <span
                v-for="m in modules"
                :key="m.key"
                class="rounded-full bg-white/15 px-2.5 py-1 text-[11px] font-semibold"
              >
                {{ m.name }}
              </span>
            </div>
          </div>

          <!-- Modules -->
          <article
            v-for="m in modules"
            :key="m.key"
            class="group relative flex gap-4 rounded-card border border-line bg-card p-5 shadow-soft transition-all duration-300 ease-spring hover:-translate-y-1 hover:border-accent-500/50 hover:shadow-lift"
            :class="m.position"
          >
            <span
              class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary-50 text-primary-700 transition-colors duration-300 group-hover:bg-accent-500 group-hover:text-accent-950"
            >
              <i :class="[m.icon, 'text-xl']" />
            </span>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <h3 class="font-heading text-lg font-bold text-ink">{{ m.name }}</h3>
                <span class="text-xs text-faint">{{ t(`modules_section.items.${m.key}.label`) }}</span>
              </div>
              <p class="mt-1 text-sm leading-relaxed text-muted">
                {{ t(`modules_section.items.${m.key}.description`) }}
              </p>
            </div>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n();

// Noms officiels des modules (identiques dans les 3 langues).
// position : place dans la grille desktop autour de la carte centrale.
const modules = [
  {
    key: "lesen",
    name: "Lesen",
    icon: "pi pi-book",
    position: "lg:col-start-1 lg:row-start-1",
  },
  {
    key: "hoeren",
    name: "Hören",
    icon: "pi pi-headphones",
    position: "lg:col-start-1 lg:row-start-2",
  },
  {
    key: "schreiben",
    name: "Schreiben",
    icon: "pi pi-pen-to-square",
    position: "lg:col-start-3 lg:row-start-1",
  },
  {
    key: "sprechen",
    name: "Sprechen",
    icon: "pi pi-microphone",
    position: "lg:col-start-3 lg:row-start-2",
  },
];
</script>