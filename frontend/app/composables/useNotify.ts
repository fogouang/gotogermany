// app/composables/useNotify.ts
// Raccourcis pour afficher un toast, avec traduction automatique des erreurs d'API.

export function useNotify() {
  const toast = useToast();
  const { t } = useI18n();
  const { message } = useApiError();

  const show = (
    severity: "success" | "info" | "warn" | "error",
    summary: string,
    detail?: string,
    life = 4500,
  ) => toast.add({ severity, summary, detail, life });

  return {
    success: (summary: string, detail?: string) =>
      show("success", summary, detail),
    info: (summary: string, detail?: string) => show("info", summary, detail),
    warn: (summary: string, detail?: string) =>
      show("warn", summary, detail, 6000),
    error: (summary: string, detail?: string) =>
      show("error", summary, detail, 6000),

    /** Erreur d'API : message déjà traduit et précis (champ, réseau, serveur...) */
    apiError: (error: any, fallbackKey?: string) =>
      show("error", t("toast.error_title"), message(error, fallbackKey), 6000),
  };
}
