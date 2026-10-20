type AuthStore = ReturnType<typeof useAuthStore>;

/** Page d'accueil de chaque rôle. L'admin est testé en premier. */
export function espaceAccueil(auth: AuthStore): string {
  if (auth.isAdmin) return "/admin";
  if (auth.isDirector) return "/centre/dashboard";
  if (auth.isSecretary) return "/centre/etudiants";
  if (auth.isTeacher) return "/enseignant/sessions";
  return "/dashboard";
}

/** Recharge l'utilisateur depuis le cookie si le store est vide. */
export async function chargerSession() {
  const auth = useAuthStore();
  if (!auth.isAuthenticated && useCookie("access_token").value) {
    await auth.fetchUser();
  }
  return auth;
}
