// middleware/guest.ts (dernier bloc, mis à jour)
export default defineNuxtRouteMiddleware(async () => {
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    const tokenCookie = useCookie('access_token')
    if (!tokenCookie.value) return // pas connecté → laisser passer
    await authStore.fetchUser()
  }
  if (!authStore.isAuthenticated) return

  if (authStore.isDirector) return navigateTo('/centre/dashboard')
  if (authStore.isSecretary) return navigateTo('/centre/secretaire')
  return navigateTo('/dashboard')
})