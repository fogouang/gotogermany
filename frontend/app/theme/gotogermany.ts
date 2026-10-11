// app/theme/gotogermany.ts
// Preset PrimeVue "Schwarz-Gold" de GoToGermany, basé sur Aura.
// - primary : anthracite en clair, or en sombre (comme main.css)
// - accent  : palette or, exposée en variables CSS (--p-accent-500, etc.)
// - success / danger : laissés à Aura (emerald / red), réservés aux corrections
import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

const GoToGermany = definePreset(Aura, {
  primitive: {
    anthracite: {
      50: "#f6f6f7",
      100: "#ececee",
      200: "#d4d4d8",
      300: "#a1a1aa",
      400: "#71717a",
      500: "#3f3f46",
      600: "#27272a",
      700: "#18181b",
      800: "#121214",
      900: "#0b0b0d",
      950: "#050506",
    },
    gold: {
      50: "#fffbeb",
      100: "#fff3c4",
      200: "#ffe58a",
      300: "#ffd54a",
      400: "#ffc61a",
      500: "#f4b400",
      600: "#d99a00",
      700: "#b37800",
      800: "#8c5c05",
      900: "#6e4808",
      950: "#3f2803",
    },
  },
  semantic: {
    // Échelle primary de base (utilisée par les composants qui lisent primary.X)
    primary: {
      50: "{anthracite.50}",
      100: "{anthracite.100}",
      200: "{anthracite.200}",
      300: "{anthracite.300}",
      400: "{anthracite.400}",
      500: "{anthracite.500}",
      600: "{anthracite.600}",
      700: "{anthracite.700}",
      800: "{anthracite.800}",
      900: "{anthracite.900}",
      950: "{anthracite.950}",
    },
    // Palette or exposée en variables : --p-accent-50 … --p-accent-950
    accent: {
      50: "{gold.50}",
      100: "{gold.100}",
      200: "{gold.200}",
      300: "{gold.300}",
      400: "{gold.400}",
      500: "{gold.500}",
      600: "{gold.600}",
      700: "{gold.700}",
      800: "{gold.800}",
      900: "{gold.900}",
      950: "{gold.950}",
    },
    // Anneau de focus doré : signature de la marque, visible dans les deux modes
    focusRing: {
      width: "2px",
      style: "solid",
      color: "{gold.500}",
      offset: "2px",
    },
    colorScheme: {
      light: {
        primary: {
          color: "{anthracite.700}",
          contrastColor: "#ffffff",
          hoverColor: "{anthracite.600}",
          activeColor: "{anthracite.500}",
        },
        highlight: {
          background: "{gold.100}",
          focusBackground: "{gold.200}",
          color: "{anthracite.700}",
          focusColor: "{anthracite.800}",
        },
        surface: {
          0: "#ffffff",
          50: "#f7f7f5",
          100: "#f4f4f2",
          200: "#e7e5e0",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
          600: "#52525b",
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
          950: "#09090b",
        },
      },
      dark: {
        primary: {
          color: "{gold.500}",
          contrastColor: "{anthracite.700}",
          hoverColor: "{gold.400}",
          activeColor: "{gold.600}",
        },
        highlight: {
          background: "color-mix(in srgb, {gold.500}, transparent 84%)",
          focusBackground: "color-mix(in srgb, {gold.500}, transparent 76%)",
          color: "rgba(255,255,255,.87)",
          focusColor: "rgba(255,255,255,.87)",
        },
        surface: {
          0: "#ffffff",
          50: "#f4f4f5",
          100: "#e4e4e7",
          200: "#d4d4d8",
          300: "#a1a1aa",
          400: "#71717a",
          500: "#52525b",
          600: "#3f3f46",
          700: "#2a2a30",
          800: "#1c1c20",
          900: "#151518",
          950: "#0c0c0e",
        },
      },
    },
  },
});

export default {
  preset: GoToGermany,
  options: {
    // Même classe que main.css et useTheme.ts
    darkModeSelector: ".dark-mode",
    cssLayer: false,
  },
};