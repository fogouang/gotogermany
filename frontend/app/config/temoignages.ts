// app/config/temoignages.ts
// UNIQUEMENT de vrais témoignages, avec l'accord écrit de la personne.
// Le premier de la liste est mis en avant (idéalement un directeur de centre).

export type RoleTemoin = "directeur" | "enseignant" | "etudiant";

export interface Temoignage {
  citation: string;
  nom: string;
  role: RoleTemoin;
  centre?: string;
  ville?: string;
  /** Photo dans public/images/temoignages/ (optionnel, avec accord) */
  photo?: string;
  /** Résultat réel uniquement, ex. "Goethe B1 réussi" */
  resultat?: string;
}

export const TEMOIGNAGES: Temoignage[] = [
  //   {
  //     citation:
  //       "Je suis ému et satisfait de la qualité du contenu proposé par cette plateforme.",
  //     nom: "Prénom N.", // à remplacer par le vrai nom (avec son accord)
  //     role: "directeur",
  //     centre: "Der Weg", // à remplacer, ex. "Der Weg" si c'est bien leur directeur
  //     ville: "Yaoundé",
  //   },
  // À compléter avec un vrai retour d'enseignant :
  // {
  //   citation: "…",
  //   nom: "Prénom N.",
  //   role: "enseignant",
  //   centre: "…",
  //   ville: "…",
  // },
  // À compléter avec un vrai retour d'étudiant :
  // {
  //   citation: "…",
  //   nom: "Prénom N.",
  //   role: "etudiant",
  //   centre: "…",
  //   ville: "…",
  //   resultat: "Goethe B1 réussi", // seulement si c'est vrai
  // },
];
// Centres qui ont accepté d'être cités publiquement
export const CENTRES_PARTENAIRES: { nom: string; ville?: string }[] = [
  { nom: "Der Weg", ville: "Yaoundé" },
  { nom: "IAV DEUTSCH AKADEMIE", ville: "Yaoundé, Rail Ngousso" },
  { nom: "INSTITU MERS", ville: "Yaoundé, Mendong" },
];
