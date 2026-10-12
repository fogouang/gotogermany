<!-- components/ui/PageWatermark.vue -->
<!--
  Grand mot allemand en filigrane derrière le contenu de la page,
  répété en haut, au milieu et en bas.
  Le mot vient de definePageMeta({ watermark: "..." }) de chaque page.
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
    >
      {{ word }}
    </span>
  </template>
</template>

<script setup lang="ts">
const route = useRoute();
const word = computed(() => route.meta.watermark as string | undefined);

// Du plus petit (haut) au plus grand (bas), toujours calé à droite
// pour ne jamais passer sur la barre latérale
const copies = [
  {
    key: "top",
    class:
      "right-6 top-20 text-[5rem] opacity-[0.10] lg:text-[7rem] dark:opacity-[0.07]",
  },
  {
    key: "middle",
    class:
      "right-[20%] top-1/2 -translate-y-1/2 text-[7rem] opacity-[0.14] lg:text-[15rem] dark:opacity-[0.09]",
  },
  {
    key: "bottom",
    class:
      "-bottom-6 right-0 text-[10rem] opacity-[0.18] lg:text-[14rem] dark:opacity-[0.12]",
  },
];
</script>
