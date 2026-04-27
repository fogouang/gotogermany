export default defineNuxtRouteMiddleware(async () => {
  const authStore = useAuthStore();

  // Rehydrater si store vide mais cookie présent
  if (!authStore.isAuthenticated) {
    const tokenCookie = useCookie("access_token");
    if (!tokenCookie.value) return navigateTo("/");
    await authStore.fetchUser();
  }

  if (!authStore.isAuthenticated) return navigateTo("/");
  if (!authStore.isAdmin) return navigateTo("/");
});
