// plugins/i18n-locale.client.ts
export default defineNuxtPlugin((nuxtApp) => {
  const localeCookie = useCookie('app_locale', {
    maxAge: 60 * 60 * 24 * 365
  })

  addRouteMiddleware('locale-restore', () => {
    if (localeCookie.value) {
      // @ts-ignore
      nuxtApp.$i18n.setLocale(localeCookie.value)
    }
  }, { global: true })
})