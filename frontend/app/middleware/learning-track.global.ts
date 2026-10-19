// middleware/learning-track.global.ts
// Espace étudiant, avant tout affichage :
//   1. un étudiant indépendant qui n'a encore rien choisi (ni niveau, ni
//      parcours) va d'abord à l'accueil ;
//   2. un étudiant ne peut pas ouvrir les pages de l'autre parcours, même en tapant l'adresse.
// S'exécute après le middleware d'accès (ordre alphabétique des middlewares globaux) :
// la session est donc déjà chargée.
import {
  EXAM_ONLY_PATHS,
  START_ONLY_PATHS,
  cheminDans,
} from "~/composables/useLearningTrack";

export default defineNuxtRouteMiddleware((to) => {
  // Le parcours peut venir du cache navigateur : rien à décider côté serveur
  if (import.meta.server) return;

  const chemin = to.path.replace(/^\/(fr|de)(?=\/|$)/, "") || "/";
  if (!chemin.startsWith("/dashboard")) return;

  const authStore = useAuthStore();
  const localePath = useLocalePath();
  const { track, hasChosen } = useLearningTrack();

    // 0. Inscription via le lien d'un centre, pas encore validée : page d'attente
  const enAttente = authStore.isStudent && !authStore.branchId && !!authStore.pendingBranchId;
  if (enAttente) {
    if (chemin === "/dashboard/en-attente") return;
    return navigateTo(localePath("/dashboard/en-attente"), { replace: true });
  }
  if (chemin === "/dashboard/en-attente") {
    return navigateTo(localePath("/dashboard"), { replace: true });
  }

  // 1. Rien choisi : ni niveau du catalogue, ni parcours enregistré
  
  // 1. Rien choisi : ni niveau du catalogue, ni parcours enregistré
  const doitChoisir =
    authStore.isStudent &&
    !authStore.branchId &&
    !authStore.targetLevelId &&
    !hasChosen.value;

  if (doitChoisir) {
    if (chemin === "/dashboard/bienvenue") return;
    return navigateTo(localePath("/dashboard/bienvenue"), { replace: true });
  }

  // 2. Pages réservées à l'autre parcours
  const interdits = track.value === "start_deutsch" ? EXAM_ONLY_PATHS : START_ONLY_PATHS;
  if (cheminDans(chemin, interdits)) {
    return navigateTo(localePath("/dashboard"), { replace: true });
  }
});