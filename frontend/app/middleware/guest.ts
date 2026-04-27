export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    const tokenCookie = useCookie('access_token')
    if (!tokenCookie.value) return // pas connecté → laisser passer
    await authStore.fetchUser()
  }

  if (authStore.isAuthenticated) return navigateTo('/dashboard')
})