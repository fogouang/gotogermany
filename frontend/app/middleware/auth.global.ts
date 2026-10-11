type Auth = ReturnType<typeof useAuthStore>;

const directeur = (a: Auth) => a.isDirector;
const secretaire = (a: Auth) => a.isSecretary;
const staffCentre = (a: Auth) => a.isDirector || a.isSecretary;

// Du plus précis au plus général : la première règle qui correspond s'applique
const REGLES: { prefixe: string; autorise: (a: Auth) => boolean }[] = [
  // Admin
  { prefixe: "/admin", autorise: (a) => a.isAdmin },

  // Centre : pages réservées au directeur
  { prefixe: "/centre/dashboard", autorise: directeur },
  { prefixe: "/centre/licence", autorise: directeur },
  { prefixe: "/centre/reglages", autorise: directeur },
  { prefixe: "/centre/secretaires", autorise: directeur },
  { prefixe: "/centre/succursales", autorise: directeur },
  // Centre : page réservée à la secrétaire
  { prefixe: "/centre/etudiants/nouveau", autorise: secretaire },
  // Centre : tout le reste, directeur ou secrétaire
  { prefixe: "/centre", autorise: staffCentre },

  // Enseignant
  { prefixe: "/enseignant", autorise: (a) => a.isTeacher },

  // Ambassadeur
  { prefixe: "/referrals", autorise: (a) => a.isAmbassador },

  // Étudiant : les autres rôles sont renvoyés vers leur espace
  { prefixe: "/dashboard", autorise: (a) => espaceAccueil(a) === "/dashboard" },
];

// Pages réservées aux visiteurs non connectés (aucune pour l'instant)
const PAGES_INVITE: string[] = [];

export default defineNuxtRouteMiddleware(async (to) => {
  const chemin = to.path.replace(/^\/(fr|de)(?=\/|$)/, "") || "/";
  const correspond = (p: string) => chemin === p || chemin.startsWith(`${p}/`);

  const regle = REGLES.find((r) => correspond(r.prefixe));
  const invite = PAGES_INVITE.some(correspond);

  // Page publique : rien à vérifier
  if (!regle && !invite) return;

  const auth = await chargerSession();

  if (invite) {
    return auth.isAuthenticated ? navigateTo(espaceAccueil(auth)) : undefined;
  }

  if (!auth.isAuthenticated) return navigateTo("/");
  if (!regle!.autorise(auth)) return navigateTo(espaceAccueil(auth));
});