// app/composables/useTheme.ts
// Thème clair / sombre de GoToGermany.
// - Classe appliquée sur <html> : .dark-mode ou .light-mode (lue par main.css
//   et par PrimeVue via darkModeSelector).
// - Choix mémorisé dans localStorage ("gtg-theme").
// - Sans choix enregistré : on suit la préférence du système.

type Theme = "light" | "dark";

const STORAGE_KEY = "gtg-theme";

function appliquer(theme: Theme) {
  const html = document.documentElement;
  html.classList.toggle("dark-mode", theme === "dark");
  html.classList.toggle("light-mode", theme === "light");
  html.style.colorScheme = theme;
}

export function useTheme() {
  const theme = useState<Theme>("theme", () => "light");

  function init() {
    if (import.meta.server) return;
    let initial: Theme;
    try {
      const enregistre = localStorage.getItem(STORAGE_KEY);
      initial =
        enregistre === "dark" || enregistre === "light"
          ? enregistre
          : window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
    } catch {
      initial = "light";
    }
    theme.value = initial;
    appliquer(initial);
  }

  function setTheme(valeur: Theme) {
    theme.value = valeur;
    if (import.meta.client) {
      appliquer(valeur);
      try {
        localStorage.setItem(STORAGE_KEY, valeur);
      } catch {
        // stockage indisponible (navigation privée) : le thème reste pour la session
      }
    }
  }

  function toggleTheme() {
    setTheme(theme.value === "dark" ? "light" : "dark");
  }

  const isDark = computed(() => theme.value === "dark");

  return { theme, isDark, init, setTheme, toggleTheme };
}