<!-- components/ui/PageWatermark.vue -->
<!--
  Grand mot allemand en filigrane derrière le contenu de la page,
  répété en haut, au milieu et en bas.
  Le mot vient de definePageMeta({ watermark: "..." }) de chaque page.
  La taille est calculée selon la largeur de l'écran ET la longueur du mot.
  Décoratif : non traduit, ignoré par les lecteurs d'écran.
-->
<template>
  <template v-if="word">
    <span
      v-for="copy in copies"
      :key="copy.key"
      aria-hidden="true"
      class="pointer-events-none fixed -z-10 hidden select-none whitespace-nowrap font-heading font-extrabold leading-none tracking-tighter text-transparent [-webkit-text-stroke:1.5px_var(--color-ink)] md:block"
      :class="copy.class"
      :style="{ fontSize: fontSize(copy.share, copy.min, copy.max) }"
    >
      {{ word }}
    </span>
  </template>
</template>

<script setup lang="ts">
const route = useRoute();
const word = computed(() => route.meta.watermark as string | undefined);

// Largeur moyenne d'une lettre (police extra-grasse, lettres resserrées), en em
const LARGEUR_LETTRE = 0.62;

/**
 * Taille pour que le mot occupe `share` (0 à 1) de la largeur de l'écran,
 * bornée entre `min` et `max` (en rem).
 */
function fontSize(share: number, min: number, max: number) {
  const lettres = Math.max(word.value?.length ?? 1, 4);
  const vw = ((share * 100) / (lettres * LARGEUR_LETTRE)).toFixed(2);
  return `clamp(${min}rem, ${vw}vw, ${max}rem)`;
}

// Du plus discret (haut) au plus présent (bas), toujours calé à droite
// pour ne jamais passer sur la barre latérale
const copies = [
  {
    key: "top",
    share: 0.3,
    min: 3,
    max: 8,
    class: "right-6 top-20 opacity-[0.10] dark:opacity-[0.07]",
  },
  {
    key: "middle",
    share: 0.5,
    min: 4,
    max: 13,
    class:
      "right-[12%] top-1/2 -translate-y-1/2 opacity-[0.14] dark:opacity-[0.09]",
  },
  {
    key: "bottom",
    share: 0.7,
    min: 5,
    max: 16,
    class: "-bottom-[0.18em] right-0 opacity-[0.18] dark:opacity-[0.12]",
  },
];
</script>
