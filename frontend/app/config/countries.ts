// app/config/countries.ts
// Pays proposés au choix du téléphone. Les noms sont générés dans la langue
// de l'interface par Intl.DisplayNames : seuls le code ISO et l'indicatif sont stockés ici.

export interface PhoneCountry {
  /** Code ISO 3166-1 alpha-2 */
  iso: string;
  /** Indicatif sans le + */
  dial: string;
  /** Le 0 initial du numéro national est un préfixe à retirer en international */
  trunkZero?: boolean;
}

// Ordre : Afrique francophone, Afrique (autres), Europe, Amérique du Nord
export const PHONE_COUNTRIES: PhoneCountry[] = [
  { iso: "CM", dial: "237" },
  { iso: "CI", dial: "225" },
  { iso: "SN", dial: "221" },
  { iso: "GA", dial: "241" },
  { iso: "CG", dial: "242" },
  { iso: "CD", dial: "243", trunkZero: true },
  { iso: "BJ", dial: "229" },
  { iso: "TG", dial: "228" },
  { iso: "BF", dial: "226" },
  { iso: "ML", dial: "223" },
  { iso: "GN", dial: "224" },
  { iso: "NE", dial: "227" },
  { iso: "TD", dial: "235" },
  { iso: "CF", dial: "236" },
  { iso: "GQ", dial: "240" },
  { iso: "MG", dial: "261", trunkZero: true },
  { iso: "RW", dial: "250", trunkZero: true },
  { iso: "BI", dial: "257" },
  { iso: "MA", dial: "212", trunkZero: true },
  { iso: "DZ", dial: "213", trunkZero: true },
  { iso: "TN", dial: "216" },
  { iso: "NG", dial: "234", trunkZero: true },
  { iso: "GH", dial: "233", trunkZero: true },
  { iso: "FR", dial: "33", trunkZero: true },
  { iso: "BE", dial: "32", trunkZero: true },
  { iso: "CH", dial: "41", trunkZero: true },
  { iso: "LU", dial: "352" },
  { iso: "DE", dial: "49", trunkZero: true },
  { iso: "AT", dial: "43", trunkZero: true },
  { iso: "IT", dial: "39" },
  { iso: "ES", dial: "34" },
  { iso: "GB", dial: "44", trunkZero: true },
  { iso: "CA", dial: "1" },
  { iso: "US", dial: "1" },
];

export const DEFAULT_PHONE_COUNTRY = "CM";