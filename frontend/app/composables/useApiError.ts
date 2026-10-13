// app/composables/useApiError.ts
// Transforme une erreur d'API (ApiError du client généré) en message clair et traduit.
// Gère : 422 Pydantic (liste ou objet de champs), detail texte du backend, réseau, 5xx.

type FieldErrors = Record<string, string>;

export function useApiError() {
  const { t, te } = useI18n();

  /** "body.password" -> "password" -> libellé traduit */
  const fieldName = (loc: string) =>
    loc.split(".").filter(Boolean).pop() ?? loc;
  const fieldLabel = (loc: string) => {
    const f = fieldName(loc);
    return te(`api_errors.fields.${f}`) ? t(`api_errors.fields.${f}`) : f;
  };

  /** Traduit les messages Pydantic les plus courants, sinon garde le texte brut */
  function translateRule(loc: string, msg: string): string {
    // Validateur personnalisé du backend : message déjà rédigé, on retire le préfixe Pydantic
    if (/^value error,\s*/i.test(msg))
      return msg.replace(/^value error,\s*/i, "");
    const field = fieldLabel(loc);
    let m = msg.match(/at least (\d+) characters?/i);
    if (m) return t("api_errors.rules.min_length", { field, n: m[1] });
    m = msg.match(/at most (\d+) characters?/i);
    if (m) return t("api_errors.rules.max_length", { field, n: m[1] });
    if (/valid email|email address/i.test(msg))
      return t("api_errors.rules.email");
    if (/field required|missing/i.test(msg))
      return t("api_errors.rules.required", { field });
    return `${field} : ${msg}`;
  }

  /** Erreurs par champ (clé = nom du champ, valeur = message traduit) */
  function fieldErrors(error: any): FieldErrors {
    const body = error?.body;
    const out: FieldErrors = {};
    if (!body) return out;

    // Format FastAPI par défaut : detail = [{ loc: [...], msg }]
    if (Array.isArray(body.detail)) {
      for (const item of body.detail) {
        const loc = Array.isArray(item?.loc)
          ? item.loc.join(".")
          : String(item?.loc ?? "");
        if (item?.msg) out[fieldName(loc)] = translateRule(loc, item.msg);
      }
    }

    // Format personnalisé : { errors|details|fields: { "body.password": "..." } }
    for (const key of ["errors", "details", "fields"]) {
      const bag = body[key];
      if (bag && typeof bag === "object" && !Array.isArray(bag)) {
        for (const [loc, msg] of Object.entries(bag)) {
          if (typeof msg === "string")
            out[fieldName(loc)] = translateRule(loc, msg);
        }
      }
    }
    return out;
  }

  /** Message unique à afficher en haut d'un formulaire */
  function message(error: any, fallbackKey = "api_errors.generic"): string {
    if (!error) return t(fallbackKey);

    // Pas de réponse du serveur : réseau coupé, serveur injoignable
    if (error.status === undefined || error.status === 0)
      return t("api_errors.network");

    const fields = Object.values(fieldErrors(error));
    if (fields.length) return fields.join(" ");

    const detail = error.body?.detail ?? error.body?.message;
    if (typeof detail === "string" && detail.trim()) return detail;

    if (error.status >= 500) return t("api_errors.server");
    return t(fallbackKey);
  }

  return { message, fieldErrors };
}
