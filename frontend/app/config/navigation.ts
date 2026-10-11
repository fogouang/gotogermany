// app/config/navigation.ts
import type {
  EspaceConfig,
  NavRole,
  NavSection,
  PageMeta,
} from "~/types/navigation";

// ── Espaces ─────────────────────────────────────────────
export const ESPACES: Record<NavRole, EspaceConfig> = {
  admin: { label: "Admin Panel", roleLabel: "Admin", icon: "pi pi-shield" },
  directeur: {
    label: "Espace Centre",
    roleLabel: "Directeur de centre",
    icon: "pi pi-building",
  },
  secretaire: {
    label: "Espace Centre",
    roleLabel: "Secrétaire",
    icon: "pi pi-building",
  },
  enseignant: {
    label: "Espace Enseignant",
    roleLabel: "Enseignant",
    icon: "pi pi-user",
  },
  ambassadeur: {
    label: "Espace Ambassadeur",
    roleLabel: "Ambassadeur",
    icon: "pi pi-star",
  },
  etudiant: {
    label: "Espace Étudiant",
    roleLabel: "Étudiant",
    icon: "pi pi-graduation-cap",
  },
};

// ── Menus par rôle ──────────────────────────────────────
export const NAVIGATION: Record<NavRole, NavSection[]> = {
  admin: [
    {
      title: "Général",
      items: [
        {
          label: "Dashboard",
          to: "/admin",
          icon: "pi pi-chart-bar",
          exact: true,
        },
        { label: "Utilisateurs", to: "/admin/users", icon: "pi pi-users" },
        { label: "Examens", to: "/admin/exams", icon: "pi pi-book" },
        {
          label: "Start Deutsch (A1/A2)",
          to: "/admin/start-deutsch",
          icon: "pi pi-graduation-cap",
        },
        { label: "Centres", to: "/admin/centers", icon: "pi pi-building" },
        { label: "Simulateur", to: "/admin/simulateur", icon: "pi pi-desktop" },
        { label: "Plans", to: "/admin/plans", icon: "pi pi-tag" },
        {
          label: "Paiements",
          to: "/admin/paiements",
          icon: "pi pi-credit-card",
        },
        {
          label: "Paiements manuels",
          to: "/admin/paiements-manuels",
          icon: "pi pi-money-bill",
        },
      ],
    },
    {
      title: "Partenariat",
      items: [
        { label: "Partenaires", to: "/admin/partners", icon: "pi pi-building" },
        { label: "Codes Promo", to: "/admin/promo-code", icon: "pi pi-ticket" },
      ],
    },
    {
      title: "Configuration",
      items: [
        { label: "Paramètres", to: "/admin/settings", icon: "pi pi-cog" },
      ],
    },
  ],

  directeur: [
    {
      title: "Général",
      items: [
        {
          label: "Vue d'ensemble",
          to: "/centre/dashboard",
          icon: "pi pi-chart-bar",
        },
        {
          label: "Succursales",
          to: "/centre/succursales",
          icon: "pi pi-sitemap",
        },
        {
          label: "Secrétaires",
          to: "/centre/secretaires",
          icon: "pi pi-users",
        },
        {
          label: "Enseignants",
          to: "/centre/enseignants",
          icon: "pi pi-user-edit",
        },
        { label: "Sessions", to: "/centre/sessions", icon: "pi pi-calendar" },
        { label: "Étudiants", to: "/centre/etudiants", icon: "pi pi-user" },
        {
          label: "Session live",
          to: "/centre/sessions-live",
          icon: "pi pi-microphone",
        },
        {
          label: "Progression",
          to: "/centre/progression",
          icon: "pi pi-chart-line",
        },
        {
          label: "Historique crédits",
          to: "/centre/credits-historique",
          icon: "pi pi-history",
        },
        { label: "Ma licence", to: "/centre/licence", icon: "pi pi-verified" },
        { label: "Réglages", to: "/centre/reglages", icon: "pi pi-cog" },
      ],
    },
  ],

  secretaire: [
    {
      title: "Général",
      items: [
        {
          label: "Mes étudiants",
          to: "/centre/etudiants",
          icon: "pi pi-user",
          exact: true,
        },
        {
          label: "Nouvel étudiant",
          to: "/centre/etudiants/nouveau",
          icon: "pi pi-user-plus",
        },
        {
          label: "Enseignants",
          to: "/centre/enseignants",
          icon: "pi pi-user-edit",
        },
        { label: "Sessions", to: "/centre/sessions", icon: "pi pi-calendar" },
        {
          label: "Progression",
          to: "/centre/progression",
          icon: "pi pi-chart-line",
        },
        {
          label: "Historique crédits",
          to: "/centre/credits-historique",
          icon: "pi pi-history",
        },
      ],
    },
  ],

  enseignant: [
    {
      title: "Général",
      items: [
        {
          label: "Mes sessions",
          to: "/enseignant/sessions",
          icon: "pi pi-users",
        },
        {
          label: "Mes étudiants",
          to: "/enseignant/etudiants",
          icon: "pi pi-user",
        },
        {
          label: "Lancer un live",
          to: "/enseignant/live/nouveau",
          icon: "pi pi-microphone",
        },
      ],
    },
  ],

  ambassadeur: [
    {
      items: [
        {
          label: "Programme de parrainage",
          to: "/referrals",
          icon: "pi pi-users",
        },
      ],
    },
    {
      items: [
        {
          label: "Espace étudiant",
          to: "/dashboard",
          icon: "pi pi-arrow-left",
        },
      ],
    },
  ],

  // Repris de DashboardSidebar.vue (clés i18n conservées)
  etudiant: [
    {
      titleKey: "sidebar.main",
      items: [
        {
          labelKey: "dashboard.pages.dashboard",
          to: "/dashboard",
          icon: "pi pi-th-large",
          exact: true,
        },
        {
          labelKey: "dashboard.pages.examens",
          to: "/dashboard/examens",
          icon: "pi pi-book",
        },
        {
          labelKey: "dashboard.pages.simulateur",
          to: "/dashboard/simulateur",
          icon: "pi pi-pen-to-square",
        },
        {
          labelKey: "dashboard.pages.sprechen",
          to: "/dashboard/sprechen",
          icon: "pi pi-microphone",
        },
        {
          labelKey: "live_session.nav_label",
          to: "/dashboard/sessions-live",
          icon: "pi pi-video",
        },
        {
          labelKey: "dashboard.pages.start_deutsch",
          to: "/dashboard/start-deutsch",
          icon: "pi pi-graduation-cap",
        },
        {
          labelKey: "dashboard.pages.methodologie",
          to: "/dashboard/methodologie",
          icon: "pi pi-compass",
        },
        {
          labelKey: "dashboard.quick_actions.results",
          to: "/dashboard/resultats",
          icon: "pi pi-chart-line",
        },
      ],
    },
    {
      titleKey: "sidebar.account",
      items: [
        {
          labelKey: "dashboard.pages.profil",
          to: "/dashboard/profil",
          icon: "pi pi-user",
        },
        {
          labelKey: "dashboard.pages.factures",
          to: "/dashboard/factures",
          icon: "pi pi-receipt",
        },
        {
          labelKey: "dashboard.pages.credits",
          to: "/dashboard/credits",
          icon: "pi pi-credit-card",
        },
      ],
    },
  ],
};

// ── Titres et sous-titres des pages (header des layouts) ─
export const PAGE_META: Record<string, PageMeta> = {
  // Admin
  "/admin": { title: "Dashboard", subtitle: "Vue d'ensemble de la plateforme" },
  "/admin/users": {
    title: "Utilisateurs",
    subtitle: "Gestion des comptes et accès",
  },
  "/admin/exams": { title: "Examens", subtitle: "Gestion du contenu" },
  "/admin/start-deutsch": {
    title: "Start Deutsch (A1/A2)",
    subtitle: "Import du contenu de familiarisation A1/A2",
  },
  "/admin/centers": {
    title: "Centres",
    subtitle: "Gestion des centres de formation partenaires",
  },
  "/admin/simulateur": {
    title: "Simulateur",
    subtitle: "Simulateur des examens",
  },
  "/admin/partners": { title: "Partenaires", subtitle: "Centres et affiliés" },
  "/admin/promo-code": {
    title: "Codes Promo",
    subtitle: "Gestion des réductions et commissions",
  },
  "/admin/settings": {
    title: "Paramètres",
    subtitle: "Configuration de la plateforme",
  },
  "/admin/plans": { title: "Plans", subtitle: "Configuration des prix" },
  "/admin/paiements": { title: "Paiements", subtitle: "Gestion des factures" },
  "/admin/paiements-manuels": {
    title: "Paiements manuels",
    subtitle: "Accès exam et crédits IA hors plateforme",
  },

  // Centre
  "/centre/dashboard": {
    title: "Vue d'ensemble",
    subtitle: "Quota et statut de votre licence",
  },
  "/centre/succursales": {
    title: "Succursales",
    subtitle: "Gestion de vos points de formation",
  },
  "/centre/secretaires": {
    title: "Secrétaires",
    subtitle: "Comptes de gestion par succursale",
  },
  "/centre/etudiants": {
    title: "Étudiants",
    subtitle: "Comptes étudiants inscrits",
  },
  "/centre/etudiants/nouveau": {
    title: "Nouvel étudiant",
    subtitle: "Créer un compte étudiant",
  },
  "/centre/enseignants": {
    title: "Enseignants",
    subtitle: "Comptes de gestion enseignant",
  },
  "/centre/sessions": {
    title: "Sessions",
    subtitle: "Cohortes par niveau, avec enseignants et étudiants",
  },
  "/centre/sessions-live": {
    title: "Session live",
    subtitle: "Lancer et suivre un examen oral en direct",
  },
  "/centre/progression": {
    title: "Progression",
    subtitle: "Scores et activité des étudiants",
  },
  "/centre/credits-historique": {
    title: "Historique des crédits",
    subtitle: "Audit des ajustements de crédits IA",
  },
  "/centre/licence": {
    title: "Ma licence",
    subtitle: "Détails et attestation",
  },
  "/centre/reglages": { title: "Réglages", subtitle: "Réglages du compte" },

  // Enseignant
  "/enseignant/sessions": {
    title: "Mes sessions",
    subtitle: "Classes et étudiants qui vous sont assignés",
  },
  "/enseignant/etudiants": {
    title: "Mes étudiants",
    subtitle: "Progression et suivi de vos étudiants",
  },
  "/enseignant/live/nouveau": {
    title: "Session live",
    subtitle: "Lancer un examen oral en direct avec un étudiant",
  },

  // Ambassadeur (route à confirmer : /referrals ou /dashboard/parrainage)
  "/referrals": {
    title: "Programme de parrainage",
    subtitle: "Votre lien, vos filleuls, vos gains",
  },
  referrals: {
    title: "Programme de parrainage",
    subtitle: "Votre lien, vos filleuls, vos gains",
  },
};

/** Titre/sous-titre de la page courante, avec repli sur le nom de l'espace */
export function getPageMeta(path: string, fallback: string): PageMeta {
  const clean = path.length > 1 ? path.replace(/\/$/, "") : path;
  return PAGE_META[clean] ?? { title: fallback };
}
