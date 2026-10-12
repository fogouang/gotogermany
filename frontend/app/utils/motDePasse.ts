// app/utils/motDePasse.ts

/** Mot de passe lisible (sans 0/O, 1/l/I) pour être dicté facilement */
export function genererMotDePasse(longueur = 10): string {
  const chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const valeurs = crypto.getRandomValues(new Uint32Array(longueur));
  return Array.from(valeurs, (v) => chars[v % chars.length]).join("");
}