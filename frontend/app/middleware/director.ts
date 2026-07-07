// middleware/director.ts
export default defineNuxtRouteMiddleware(async () => {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) {
    const tokenCookie = useCookie("access_token");
    if (!tokenCookie.value) return navigateTo("/");
    await authStore.fetchUser();
  }

  if (!authStore.isAuthenticated) return navigateTo("/");
  if (!authStore.isDirector) return navigateTo("/");
});