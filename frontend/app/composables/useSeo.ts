import type { MaybeRefOrGetter } from 'vue'

interface SeoOptions {
  title: MaybeRefOrGetter<string>
  description: MaybeRefOrGetter<string>
  /** Image OG imposée ; sinon l'image de la langue courante */
  image?: string
  url?: string
  type?: string
}

const OG_LOCALES: Record<string, string> = { en: 'en_US', fr: 'fr_FR', de: 'de_DE' }
const SITE_NAME = 'GoToGermany'

export const useSeo = (options: SeoOptions) => {
  const config = useRuntimeConfig()
  const route = useRoute()
  const { locale, locales } = useI18n()
  const switchLocalePath = useSwitchLocalePath()

  const siteUrl = (config.public.siteUrl as string).replace(/\/$/, '')
  const type = options.type ?? 'website'

  const title = computed(() => `${toValue(options.title)} | ${SITE_NAME}`)
  const description = computed(() => toValue(options.description))

  // Une image par langue : og-image.png (en), og-image-fr.png, og-image-de.png
  const image = computed(
    () =>
      options.image ??
      `${siteUrl}/images/${locale.value === 'en' ? 'og-image' : `og-image-${locale.value}`}.png`,
  )

  // Sans la query (?activer=..., ?student_id=...) pour ne pas dupliquer les pages
  const url = computed(() => options.url ?? `${siteUrl}${route.path}`)

  const codes = computed(() =>
    (locales.value as Array<string | { code: string }>).map((l) => (typeof l === 'string' ? l : l.code)),
  )

  // hreflang : la même page dans chaque langue, + x-default (anglais)
  const alternates = computed(() => [
    ...codes.value.map((code) => ({
      rel: 'alternate',
      hreflang: code,
      href: `${siteUrl}${switchLocalePath(code as any)}`,
    })),
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}${switchLocalePath('en' as any)}` },
  ])

  useHead({
    title,
    htmlAttrs: { lang: locale },
    link: computed(() => [{ rel: 'canonical', href: url.value }, ...alternates.value]),
    meta: computed(() => [
      { name: 'description', content: description.value },
      // Open Graph
      { property: 'og:site_name', content: SITE_NAME },
      { property: 'og:title', content: title.value },
      { property: 'og:description', content: description.value },
      { property: 'og:image', content: image.value },
      { property: 'og:image:width', content: '1200' },
      { property: 'og:image:height', content: '630' },
      { property: 'og:image:alt', content: title.value },
      { property: 'og:url', content: url.value },
      { property: 'og:type', content: type },
      { property: 'og:locale', content: OG_LOCALES[locale.value] ?? 'en_US' },
      ...codes.value
        .filter((c) => c !== locale.value)
        .map((c) => ({ property: 'og:locale:alternate', content: OG_LOCALES[c] ?? c })),
      // Twitter / X
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: title.value },
      { name: 'twitter:description', content: description.value },
      { name: 'twitter:image', content: image.value },
    ]),
  })
}