interface SeoOptions {
  title: string
  description: string
  image?: string
  url?: string
  type?: string
}

export const useSeo = (options: SeoOptions) => {
  const config   = useRuntimeConfig()
  const route    = useRoute()
  const { locale } = useI18n()

  const siteUrl  = config.public.siteUrl as string
  const image    = options.image ?? `${siteUrl}/images/og-image.png`
  const url      = options.url   ?? `${siteUrl}${route.fullPath}`
  const type     = options.type  ?? 'website'
  const fullTitle = `${options.title} | GoToGermany`

  useHead({
    title: fullTitle,
    htmlAttrs: { lang: locale.value },
    link: [
      { rel: 'canonical', href: url },
    ],
    meta: [
      { name: 'description',         content: options.description },
      // Open Graph
      { property: 'og:title',        content: fullTitle },
      { property: 'og:description',  content: options.description },
      { property: 'og:image',        content: image },
      { property: 'og:url',          content: url },
      { property: 'og:type',         content: type },
      { property: 'og:locale',       content: locale.value === 'fr' ? 'fr_FR' : 'en_US' },
      { property: 'og:locale:alternate', content: locale.value === 'fr' ? 'en_US' : 'fr_FR' },
      // Twitter
      { name: 'twitter:title',       content: fullTitle },
      { name: 'twitter:description', content: options.description },
      { name: 'twitter:image',       content: image },
    ],
  })
}