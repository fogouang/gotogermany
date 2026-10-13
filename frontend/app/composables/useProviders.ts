// app/composables/useProviders.ts
// Organismes certificateurs : nom, abréviation, couleurs (une seule source pour toutes les pages)

export interface ProviderInfo {
  /** Nom complet, ex. "Goethe-Institut" */
  name: string;
  /** Nom court pour les libellés de niveau, ex. "Goethe" */
  brand: string;
  /** Abréviation pour les badges, ex. "GI" */
  short: string;
  badge: string;
  bar: string;
  dot: string;
  text: string;
}

const PROVIDERS: Record<string, ProviderInfo> = {
  goethe: { name: "Goethe-Institut", brand: "Goethe", short: "GI", badge: "bg-emerald-500/10 text-emerald-600", bar: "bg-emerald-500", dot: "bg-emerald-500", text: "text-emerald-600" },
  telc: { name: "telc", brand: "telc", short: "TE", badge: "bg-red-500/10 text-red-600", bar: "bg-red-500", dot: "bg-red-500", text: "text-red-600" },
  osd: { name: "ÖSD", brand: "ÖSD", short: "ÖSD", badge: "bg-sky-500/10 text-sky-600", bar: "bg-sky-500", dot: "bg-sky-500", text: "text-sky-600" },
  testdaf: { name: "TestDaF", brand: "TestDaF", short: "TD", badge: "bg-violet-500/10 text-violet-600", bar: "bg-violet-500", dot: "bg-violet-500", text: "text-violet-600" },
  ecl: { name: "ECL", brand: "ECL", short: "ECL", badge: "bg-amber-500/15 text-amber-600", bar: "bg-amber-500", dot: "bg-amber-500", text: "text-amber-600" },
};

const FALLBACK: Omit<ProviderInfo, "name" | "brand" | "short"> = {
  badge: "bg-primary/10 text-primary",
  bar: "bg-primary",
  dot: "bg-primary",
  text: "text-primary",
};

/** Clé normalisée : minuscules, sans accent ("ÖSD" -> "osd") */
export const normProvider = (p?: string | null) =>
  (p ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

export function useProviders() {
  const order = Object.keys(PROVIDERS);

  const info = (p: string): ProviderInfo =>
    PROVIDERS[normProvider(p)] ?? { ...FALLBACK, name: p, brand: p, short: p.slice(0, 2).toUpperCase() };

  /** Position d'affichage (organismes inconnus à la fin) */
  const orderOf = (p: string) => order.indexOf(normProvider(p)) + 1 || 99;

  return { info, orderOf, knownKeys: order };
}