/**
 * plugins/auth.client.ts
 *
 * Initialise le store auth au démarrage côté browser.
 * Le .client garantit que les cookies sont disponibles avant l'exécution.
 * Sans ce plugin, le store Pinia se réinitialise à chaque refresh
 * et isAuthenticated devient false → middleware redirige vers /.
 */
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore();
  await authStore.fetchUser();
});
