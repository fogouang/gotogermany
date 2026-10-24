<script setup lang="ts">
// Génère sur chaque page : <html lang>, canonical de la page,
// balises hreflang (en, fr, de, x-default) et og:locale
const i18nHead = useLocaleHead({ lang: true, seo: true });

useHead(() => ({
  htmlAttrs: {
    lang: i18nHead.value.htmlAttrs?.lang,
  },
  link: [...(i18nHead.value.link || [])],
  meta: [...(i18nHead.value.meta || [])],
}));
</script>

<template>
  <div class="overflow-x-hidden">
    <NuxtLoadingIndicator color="#F4B400" :height="3" />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>
