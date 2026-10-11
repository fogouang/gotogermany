// app/composables/useChoixExamen.ts
// Choix d'un examen depuis la landing (cartes organismes, liens du footer)
// et redirections après inscription / connexion.
// Connecté : page des examens filtrée. Invité : intention retenue + inscription.
import { useAuthDialog } from "~/composables/useAuthDialog";

export function useChoixExamen() {
  const authStore = useAuthStore();
  const { openSignup } = useAuthDialog();

  // Examen choisi par un visiteur non connecté (organisme + niveau)
  const intention = useCookie<{ provider: string; level?: string } | null>(
    "gtg-exam-intent",
    { maxAge: 60 * 60 * 24 },
  );

  // Page à ouvrir après inscription / connexion (ex. paiement d'une offre)
  const redirection = useCookie<string | null>("gtg-after-auth", {
    maxAge: 60 * 60 * 24,
  });

  function choisir(provider: string, level?: string) {
    if (authStore.isAuthenticated) {
      navigateTo({
        path: "/dashboard/examens",
        query: { provider, ...(level ? { level } : {}) },
      });
    } else {
      intention.value = { provider, level };
      openSignup();
    }
  }

  function retenirRedirection(chemin: string) {
    redirection.value = chemin;
    openSignup();
  }

  // Après inscription / connexion, par ordre de priorité :
  // 1. la page retenue (ex. paiement d'une offre),
  // 2. l'examen choisi sur la landing,
  // 3. le chemin par défaut.
  // Les choix retenus sont consommés (une seule fois).
  function cheminApresConnexion(defaut = "/dashboard") {
    if (redirection.value) {
      const chemin = redirection.value;
      redirection.value = null;
      intention.value = null;
      return chemin;
    }

    const choix = intention.value;
    intention.value = null;
    if (!choix?.provider) return defaut;
    return {
      path: "/dashboard/examens",
      query: {
        provider: choix.provider,
        ...(choix.level ? { level: choix.level } : {}),
      },
    };
  }

  return { choisir, cheminApresConnexion, retenirRedirection };
}