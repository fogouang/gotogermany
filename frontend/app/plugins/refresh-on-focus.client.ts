// plugins/refresh-on-focus.client.ts
export default defineNuxtPlugin(() => {
  const authStore = useAuthStore();

  let refreshing = false;
  const refresh = async () => {
    if (!authStore.isAuthenticated || refreshing) return;
    refreshing = true;
    try {
      await authStore.fetchUser();
    } finally {
      refreshing = false;
    }
  };

  window.addEventListener("focus", refresh);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") refresh();
  });
});