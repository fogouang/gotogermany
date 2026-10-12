// composables/useApiDownload.ts
// Téléchargement de fichiers binaires (PDF, zip) depuis l'API.
// Le client généré lit la réponse comme du texte, ce qui corrompt les fichiers :
// ici on passe par fetch et on récupère un blob.

type DownloadResult = { success: true } | { success: false; error: string };

function nomDepuisEntete(disposition: string | null): string | null {
  if (!disposition) return null;
  const utf8 = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8?.[1]) return decodeURIComponent(utf8[1]);
  const simple = disposition.match(/filename="?([^";]+)"?/i);
  return simple?.[1] ?? null;
}

export function useApiDownload() {
  const config = useRuntimeConfig();
  const tokenCookie = useCookie("access_token");
  const downloading = ref(false);

  /**
   * @param path chemin de l'API, ex. `/api/v1/assignments/${id}/schreiben.zip`
   * @param fallbackName nom du fichier si le backend n'en donne pas
   */
  async function download(path: string, fallbackName: string): Promise<DownloadResult> {
    const base = config.public.apiBaseUrl || "http://localhost:8001";
    downloading.value = true;
    try {
      const res = await fetch(`${base}${path}`, {
        credentials: "include",
        headers: tokenCookie.value ? { Authorization: `Bearer ${tokenCookie.value}` } : {},
      });

      if (!res.ok) {
        let detail = "";
        try {
          const body = await res.json();
          if (typeof body?.detail === "string") detail = body.detail;
        } catch {
          // réponse non JSON : on garde le message par défaut de la page
        }
        return { success: false, error: detail };
      }

      const blob = await res.blob();
      const name = nomDepuisEntete(res.headers.get("content-disposition")) ?? fallbackName;

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = name;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);

      return { success: true };
    } catch {
      return { success: false, error: "" };
    } finally {
      downloading.value = false;
    }
  }

  return { download, downloading };
}