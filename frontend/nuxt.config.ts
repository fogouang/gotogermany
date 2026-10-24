import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  compatibilityDate: "2026-04-07",

  modules: [
    "@primevue/nuxt-module",
    "@pinia/nuxt",
    "@nuxtjs/i18n",
    "@nuxtjs/sitemap",
    "@nuxtjs/robots",
  ],

  css: ["~/assets/css/main.css", "primeicons/primeicons.css"],

  components: [{ path: "~/components", pathPrefix: false }],

  // ── Site (utilisé par sitemap, robots et i18n) ─────────
  site: {
    url: "https://prep-telc-osd.com",
    name: "GoToGermany",
  },

  // ── SEO global ──────────────────────────────────────────
  // lang, canonical et hreflang sont gérés par page via useLocaleHead (app.vue)
  app: {
    head: {
      charset: "utf-8",
      viewport: "width=device-width, initial-scale=1",
      link: [{ rel: "icon", type: "image/png", href: "/images/logo.png" }],
      meta: [
        // Barre du navigateur mobile : anthracite en clair, sombre en mode sombre
        {
          name: "theme-color",
          content: "#18181b",
          media: "(prefers-color-scheme: light)",
        },
        {
          name: "theme-color",
          content: "#0c0c0e",
          media: "(prefers-color-scheme: dark)",
        },
        { name: "author", content: "GoToGermany" },
        // Open Graph
        { property: "og:site_name", content: "GoToGermany" },
        { property: "og:type", content: "website" },
        {
          property: "og:image",
          content: "https://prep-telc-osd.com/images/og-image.png",
        },
        { property: "og:image:width", content: "1200" },
        { property: "og:image:height", content: "630" },
        // Twitter
        { name: "twitter:card", content: "summary_large_image" },
        {
          name: "twitter:image",
          content: "https://prep-telc-osd.com/images/og-image.png",
        },
        { name: "twitter:creator", content: "@GoToGermany" },
      ],
      script: [
        {
          // Applique le thème AVANT le premier rendu : évite le flash blanc
          // au rechargement en mode sombre. Même clé que useTheme.ts.
          innerHTML: `(function(){try{var t=localStorage.getItem('gtg-theme');if(t!=='dark'&&t!=='light'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}var h=document.documentElement;h.classList.add(t==='dark'?'dark-mode':'light-mode');h.style.colorScheme=t}catch(e){}})();`,
          tagPosition: "head",
        },
      ],
    },
  },

  // ── Sitemap ─────────────────────────────────────────────
  // Généré automatiquement à partir des pages et des langues i18n.
  // Les routes en robots: false (routeRules) en sont exclues.
  sitemap: {
    autoI18n: true,
  },

  // ── Robots ──────────────────────────────────────────────
  // Les espaces privés sont en noindex via routeRules (plus fiable qu'un Disallow).
  robots: {
    disallow: ["/api"],
  },

  i18n: {
    baseUrl: "https://prep-telc-osd.com",
    locales: [
      { code: "en", language: "en", name: "English", file: "en.json" },
      { code: "fr", language: "fr", name: "Français", file: "fr.json" },
      { code: "de", language: "de", name: "Deutsch", file: "de.json" },
    ],
    defaultLocale: "en",
    langDir: "locales/",
    strategy: "prefix_except_default",
    compilation: {
      strictMessage: false,
      escapeHtml: false,
    },

    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: "gtg_locale",
      redirectOn: "root",
      alwaysRedirect: false,
      fallbackLocale: "en",
    },
  },

  primevue: {
    importTheme: { from: "@/theme/gotogermany.ts" },
    autoImport: true,
  },

  nitro: {
    devProxy: {
      "/api": { target: "http://localhost:8081/api", changeOrigin: true },
    },
  },

  runtimeConfig: {
    public: {
      apiBaseUrl:
        process.env.NODE_ENV === "production"
          ? "https://prep-telc-osd.com"
          : "",
      siteUrl: "https://prep-telc-osd.com",
      sprechenWsBaseUrl:
        process.env.NUXT_PUBLIC_SPRECHEN_WS_BASE_URL ??
        (process.env.NODE_ENV === "production"
          ? "wss://prep-telc-osd.com/api/v1/sprechen-simulator"
          : "ws://localhost:8001/api/v1/sprechen-simulator"),
    },
  },

  // ── Espaces privés : rendu client + noindex + hors sitemap ──
  routeRules: {
    "/dashboard/**": { ssr: false, robots: false },
    "/admin/**": { ssr: false, robots: false },
    "/centre/**": { ssr: false, robots: false },
    "/enseignant/**": { ssr: false, robots: false },
    "/referrals/**": { ssr: false, robots: false },
    "/fr/dashboard/**": { ssr: false, robots: false },
    "/fr/admin/**": { ssr: false, robots: false },
    "/fr/centre/**": { ssr: false, robots: false },
    "/fr/enseignant/**": { ssr: false, robots: false },
    "/fr/referrals/**": { ssr: false, robots: false },
    "/de/dashboard/**": { ssr: false, robots: false },
    "/de/admin/**": { ssr: false, robots: false },
    "/de/centre/**": { ssr: false, robots: false },
    "/de/enseignant/**": { ssr: false, robots: false },
    "/de/referrals/**": { ssr: false, robots: false },
  },

  vite: {
    plugins: [tailwindcss()],
  },
} as any);
