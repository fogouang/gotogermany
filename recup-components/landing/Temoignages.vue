<template>
  <section
    v-if="TEMOIGNAGES.length || CENTRES_PARTENAIRES.length"
    class="relative overflow-hidden bg-card py-16 sm:py-24"
  >
    <div
      class="pointer-events-none absolute -top-32 left-1/2 size-120 -translate-x-1/2 rounded-full bg-accent-500/10 blur-3xl"
      aria-hidden="true"
    />

    <div class="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
      <!-- En-tête -->
      <div class="mx-auto mb-12 max-w-3xl text-center">
        <p
          class="mb-3 inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-primary"
        >
          <span class="h-px w-6 bg-accent-500" />
          {{ t("testimonials.eyebrow") }}
          <span class="h-px w-6 bg-accent-500" />
        </p>
        <h2
          class="font-heading text-3xl font-bold tracking-tight text-ink sm:text-4xl"
        >
          {{ t("testimonials.title") }}
        </h2>
        <p class="mt-4 text-base text-muted sm:text-lg">
          {{ t("testimonials.subtitle") }}
        </p>
      </div>

      <!-- Témoignages (seulement s'il y a de vraies citations) -->
      <div v-if="TEMOIGNAGES.length" class="grid gap-5 lg:grid-cols-3">
        <!-- Témoignage mis en avant -->
        <figure
          v-if="vedette"
          class="relative flex flex-col overflow-hidden rounded-card bg-zinc-950 p-8 text-white shadow-lift lg:row-span-2"
        >
          <div
            class="flag-stripe absolute inset-x-0 top-0 h-1"
            aria-hidden="true"
          />
          <i
            class="pi pi-quote-left mb-6 text-3xl text-accent-400"
            aria-hidden="true"
          />
          <blockquote
            class="flex-1 font-heading text-lg leading-relaxed sm:text-xl"
          >
            {{ vedette.citation }}
          </blockquote>
          <figcaption
            class="mt-8 flex items-center gap-3 border-t border-white/10 pt-6"
          >
            <img
              v-if="vedette.photo"
              :src="vedette.photo"
              :alt="vedette.nom"
              loading="lazy"
              class="size-12 rounded-full object-cover ring-2 ring-accent-500/50"
            />
            <span
              v-else
              class="flex size-12 items-center justify-center rounded-full bg-accent-500 font-heading font-bold text-accent-950"
            >
              {{ initiales(vedette.nom) }}
            </span>
            <div class="min-w-0">
              <p class="font-semibold">{{ vedette.nom }}</p>
              <p class="truncate text-sm text-white/60">
                {{ t(`testimonials.roles.${vedette.role}`)
                }}<template v-if="vedette.centre">
                  · {{ vedette.centre }}</template
                ><template v-if="vedette.ville">, {{ vedette.ville }}</template>
              </p>
            </div>
          </figcaption>
        </figure>

        <!-- Autres témoignages -->
        <figure
          v-for="item in autres"
          :key="item.nom + item.citation.slice(0, 20)"
          class="flex flex-col rounded-card border border-line bg-canvas p-6 shadow-soft transition-all duration-300 ease-spring hover:-translate-y-1 hover:shadow-lift"
        >
          <div class="mb-4 flex items-center justify-between gap-3">
            <i
              class="pi pi-quote-left text-xl text-accent-500"
              aria-hidden="true"
            />
            <span
              v-if="item.resultat"
              class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400"
            >
              <i class="pi pi-check-circle text-[11px]" />
              {{ item.resultat }}
            </span>
          </div>
          <blockquote class="flex-1 text-sm leading-relaxed text-ink">
            {{ item.citation }}
          </blockquote>
          <figcaption
            class="mt-5 flex items-center gap-3 border-t border-line pt-4"
          >
            <img
              v-if="item.photo"
              :src="item.photo"
              :alt="item.nom"
              loading="lazy"
              class="size-10 rounded-full object-cover"
            />
            <span
              v-else
              class="flex size-10 items-center justify-center rounded-full bg-primary-50 font-heading text-sm font-bold text-primary-700"
            >
              {{ initiales(item.nom) }}
            </span>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-ink">{{ item.nom }}</p>
              <p class="truncate text-xs text-muted">
                {{ t(`testimonials.roles.${item.role}`)
                }}<template v-if="item.centre"> · {{ item.centre }}</template
                ><template v-if="item.ville">, {{ item.ville }}</template>
              </p>
            </div>
          </figcaption>
        </figure>
      </div>

      <!-- Centres qui utilisent la plateforme -->
      <div
        v-if="CENTRES_PARTENAIRES.length"
        class="text-center"
        :class="{ 'mt-14': TEMOIGNAGES.length }"
      >
        <p
          class="mb-5 text-xs font-semibold uppercase tracking-[0.18em] text-faint"
        >
          {{ t("testimonials.centres") }}
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <span
            v-for="c in CENTRES_PARTENAIRES"
            :key="c.nom"
            class="inline-flex items-center gap-2 rounded-full border border-line bg-canvas px-4 py-2 text-sm font-medium text-ink shadow-soft"
          >
            <i class="pi pi-building text-xs text-accent-500" />
            {{ c.nom
            }}<span v-if="c.ville" class="text-faint">· {{ c.ville }}</span>
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { TEMOIGNAGES, CENTRES_PARTENAIRES } from "~/config/temoignages";

const { t } = useI18n();

const vedette = computed(() => TEMOIGNAGES[0] ?? null);
const autres = computed(() => TEMOIGNAGES.slice(1));

function initiales(nom: string) {
  return nom
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join("");
}
</script>
