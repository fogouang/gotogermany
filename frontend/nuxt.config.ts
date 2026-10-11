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

  components: [{ path: "~/components/ui", pathPrefix: false }, "~/components"],
  // ── SEO global ──────────────────────────────────────────
  app: {
    head: {
      charset: "utf-8",
      viewport: "width=device-width, initial-scale=1",
      htmlAttrs: { lang: "en" },
      link: [
        { rel: "icon", type: "image/png", href: "/images/logo.png" },
        { rel: "canonical", href: "https://prep-telc-osd.com" },
      ],
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
  sitemap: {
    siteUrl: "https://prep-telc-osd.com",
    urls: [
      { loc: "/", changefreq: "weekly", priority: 1.0 },
      { loc: "/fr", changefreq: "weekly", priority: 1.0 },
      { loc: "/tarifs", changefreq: "monthly", priority: 0.9 },
      { loc: "/fr/tarifs", changefreq: "monthly", priority: 0.9 },
      { loc: "/about", changefreq: "monthly", priority: 0.7 },
      { loc: "/fr/about", changefreq: "monthly", priority: 0.7 },
      { loc: "/contact", changefreq: "monthly", priority: 0.6 },
      { loc: "/fr/contact", changefreq: "monthly", priority: 0.6 },
      { loc: "/faq", changefreq: "monthly", priority: 0.7 },
      { loc: "/fr/faq", changefreq: "monthly", priority: 0.7 },
    ],
  },

  // ── Robots ──────────────────────────────────────────────
  robots: {
    rules: [
      {
        UserAgent: "*",
        Allow: "/",
        Disallow: ["/dashboard", "/admin", "/api"],
      },
    ],
    sitemap: "https://prep-telc-osd.com/sitemap.xml",
  },

  i18n: {
    locales: [
      { code: "en", name: "English", file: "en.json" },
      { code: "fr", name: "Français", file: "fr.json" },
      { code: "de", name: "Deutsch", file: "de.json" },
    ],
    defaultLocale: "en",
    langDir: "locales/",
    strategy: "prefix_except_default",
    compilation: {
      strictMessage: false,
      escapeHtml: false,
    },

    detectBrowserLanguage: false,
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

  routeRules: {
    "/dashboard/**": { ssr: false },
    "/admin/**": { ssr: false },
    "/centre/**": { ssr: false },
    "/enseignant/**": { ssr: false },
    "/fr/dashboard/**": { ssr: false },
    "/fr/admin/**": { ssr: false },
    "/fr/centre/**": { ssr: false },
    "/fr/enseignant/**": { ssr: false },
    "/de/dashboard/**": { ssr: false },
    "/de/admin/**": { ssr: false },
    "/de/centre/**": { ssr: false },
    "/de/enseignant/**": { ssr: false },
    "/referrals/**": { ssr: false },
    "/fr/referrals/**": { ssr: false },
    "/de/referrals/**": { ssr: false },
  },

  vite: {
    plugins: [tailwindcss()],
  },
} as any);
