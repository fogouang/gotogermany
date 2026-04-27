// middleware/auth.ts
export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore();

  // Si déjà authentifié en mémoire → OK
  if (authStore.isAuthenticated) return;

  // Sinon vérifier le cookie et rehydrater
  const tokenCookie = useCookie("access_token");
  if (!tokenCookie.value) {
    return navigateTo("/");
  }

  // Cookie présent mais store vide → fetchUser
  await authStore.fetchUser();

  // Après fetchUser, vérifier à nouveau
  if (!authStore.isAuthenticated) {
    return navigateTo("/");
  }
});
