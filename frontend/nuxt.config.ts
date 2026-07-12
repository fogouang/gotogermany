import Aura from "@primeuix/themes/aura";
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
        { name: "theme-color", content: "#0d6e4f" },
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
    options: { theme: { preset: Aura } },
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

  vite: {
    plugins: [tailwindcss()],
  },
} as any);
