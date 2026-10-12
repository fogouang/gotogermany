// composables/useAccessStatus.ts
// État de l'accès d'un élève (actif, expire bientôt, expiré, aucun) et son badge.
// Même logique que la page centre/etudiants.

export type AccessState = "active" | "soon" | "expired" | "none";

const DAY = 24 * 60 * 60 * 1000;

export function useAccessStatus() {
  const { t, locale } = useI18n();

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString(locale.value, {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }

  function accessState(expiresAt: string | null | undefined): AccessState {
    if (!expiresAt) return "none";
    const left = new Date(expiresAt).getTime() - Date.now();
    if (left < 0) return "expired";
    if (left <= 7 * DAY) return "soon";
    return "active";
  }

  function hasAccess(expiresAt: string | null | undefined) {
    const st = accessState(expiresAt);
    return st === "active" || st === "soon";
  }

  function accessBadge(expiresAt: string | null | undefined) {
    const state = accessState(expiresAt);
    if (state === "none")
      return { label: t("centre.students.access_none"), icon: "pi pi-minus-circle", class: "bg-card-2 text-muted" };
    if (state === "expired")
      return {
        label: t("centre.students.access_expired", { date: formatDate(expiresAt!) }),
        icon: "pi pi-times-circle",
        class: "bg-red-500/10 text-red-600",
      };
    if (state === "soon") {
      const days = Math.max(1, Math.ceil((new Date(expiresAt!).getTime() - Date.now()) / DAY));
      return {
        label: t("centre.students.access_soon", days),
        icon: "pi pi-clock",
        class: "bg-amber-500/10 text-amber-600",
      };
    }
    return {
      label: t("centre.students.access_until", { date: formatDate(expiresAt!) }),
      icon: "pi pi-check-circle",
      class: "bg-emerald-500/10 text-emerald-600",
    };
  }

  return { accessState, hasAccess, accessBadge };
}