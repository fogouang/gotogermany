// composables/useLearningTrack.ts
// Parcours de l'étudiant : "exam" (B1/B2 : telc, Goethe, ÖSD) ou "start_deutsch" (A1/A2).
//
// Ordre de lecture :
//   1. élève de centre : toujours "exam" (niveau fixé par le centre)
//   2. champ backend learning_track (source de vérité, suit le compte partout)
//   3. choix enregistré dans ce navigateur, par compte (cache, évite le flash)
//   4. sinon "exam" (comportement d'avant les parcours)
//
// Sans utilisateur chargé (déconnexion en cours, premier rendu), on garde le
// dernier parcours connu : sinon le menu bascule un instant vers « examen ».

export type LearningTrack = "exam" | "start_deutsch";

const STORAGE_PREFIX = "gtg_learning_track";
/** Dernier parcours connu, tous comptes confondus : sert quand aucun utilisateur n'est chargé */
const STORAGE_LAST = `${STORAGE_PREFIX}:last`;

/** Pages réservées à chaque parcours (chemins sans préfixe de langue) */
export const EXAM_ONLY_PATHS = [
  "/dashboard/examens",
  "/dashboard/sprechen",
  "/dashboard/simulateur",
  "/dashboard/sessions-live",
  "/dashboard/methodologie",
];
export const START_ONLY_PATHS = ["/dashboard/start-deutsch"];

/** Vrai si le chemin (sans langue) commence par l'un des préfixes */
export function cheminDans(chemin: string, prefixes: string[]) {
  return prefixes.some((p) => chemin === p || chemin.startsWith(`${p}/`));
}

function estTrack(v: unknown): v is LearningTrack {
  return v === "exam" || v === "start_deutsch";
}

function lireLocal(cle: string): LearningTrack | null {
  if (!import.meta.client) return null;
  try {
    const v = localStorage.getItem(cle);
    return estTrack(v) ? v : null;
  } catch {
    return null;
  }
}

function ecrireLocal(cles: string[], value: LearningTrack) {
  if (!import.meta.client) return;
  try {
    for (const cle of cles) localStorage.setItem(cle, value);
  } catch {
    /* stockage indisponible : le choix vaut pour cette visite */
  }
}

export function useLearningTrack() {
  const authStore = useAuthStore();

  // Choix faits pendant la visite, par clé : réactifs, contrairement au localStorage
  const choixVisite = useState<Record<string, LearningTrack>>("learning-track", () => ({}));

  const userId = computed(() => (authStore.user as { id?: string } | null)?.id ?? null);
  // Une clé par compte ; sans compte chargé, la clé du dernier parcours connu
  const cle = computed(() => (userId.value ? `${STORAGE_PREFIX}:${userId.value}` : STORAGE_LAST));
  const estEleveCentre = computed(() => !!authStore.branchId);

  /** Parcours enregistré dans le compte, ou null */
  const choixServeur = computed<LearningTrack | null>(() => {
    const v = (authStore.user as { learning_track?: unknown } | null)?.learning_track;
    return estTrack(v) ? v : null;
  });

  /** Choix explicite de l'étudiant, ou null s'il n'a jamais choisi */
  const choixExplicite = computed<LearningTrack | null>(
    () => choixServeur.value ?? choixVisite.value[cle.value] ?? lireLocal(cle.value),
  );

  const track = computed<LearningTrack>(() =>
    estEleveCentre.value ? "exam" : (choixExplicite.value ?? "exam"),
  );

  /** L'étudiant a déjà choisi (ou n'a pas à choisir : élève de centre) */
  const hasChosen = computed(() => estEleveCentre.value || choixExplicite.value !== null);

  // Le compte fait foi : on aligne le cache du navigateur sur lui
  if (import.meta.client) {
    watch(
      choixServeur,
      (value) => {
        if (value) ecrireLocal([cle.value, STORAGE_LAST], value);
      },
      { immediate: true },
    );
  }

  function setTrack(value: LearningTrack) {
    if (estEleveCentre.value) return;

    // Effet immédiat dans la visite + cache navigateur
    choixVisite.value = { ...choixVisite.value, [cle.value]: value, [STORAGE_LAST]: value };
    ecrireLocal([cle.value, STORAGE_LAST], value);

    // Enregistrement dans le compte (suit l'étudiant sur tous ses appareils).
    // Best-effort : en cas d'échec, le choix reste valable dans ce navigateur.
    if (authStore.isStudent && choixServeur.value !== value) {
      void authStore.setLearningTrack(value);
    }
  }

  return {
    track,
    hasChosen,
    isExam: computed(() => track.value === "exam"),
    isStartDeutsch: computed(() => track.value === "start_deutsch"),
    canSwitchTrack: computed(() => !estEleveCentre.value),
    setTrack,
  };
}