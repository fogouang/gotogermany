// app/config/navigation.ts
import type {
  EspaceConfig,
  NavRole,
  NavSection,
  PageMeta,
} from "~/types/navigation";

// ── Espaces ─────────────────────────────────────────────
// label / roleLabel servent de repli si la clé i18n est absente.
export const ESPACES: Record<NavRole, EspaceConfig> = {
  admin: { label: "Admin Panel", roleLabel: "Admin", icon: "pi pi-shield" },
  directeur: {
    label: "Espace Centre",
    labelKey: "centre.space",
    roleLabel: "Directeur de centre",
    roleLabelKey: "centre.roles.director",
    icon: "pi pi-building",
  },
  secretaire: {
    label: "Espace Centre",
    labelKey: "centre.space",
    roleLabel: "Secrétaire",
    roleLabelKey: "centre.roles.secretary",
    icon: "pi pi-building",
  },
  enseignant: {
    label: "Espace Enseignant",
    labelKey: "teacher.space",
    roleLabel: "Enseignant",
    roleLabelKey: "teacher.role",
    icon: "pi pi-user",
  },
  ambassadeur: {
    label: "Espace Ambassadeur",
    labelKey: "ambassador.space",
    roleLabel: "Ambassadeur",
    roleLabelKey: "ambassador.role",
    icon: "pi pi-star",
  },
  etudiant: {
    label: "Espace Étudiant",
    labelKey: "dashboard.space",
    roleLabel: "Étudiant",
    roleLabelKey: "dashboard.role",
    icon: "pi pi-graduation-cap",
  },
};

// ── Menus par rôle ──────────────────────────────────────
export const NAVIGATION: Record<NavRole, NavSection[]> = {
  // Admin : en français uniquement (usage interne)
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
      titleKey: "sidebar.main",
      items: [
        {
          labelKey: "centre.nav.overview",
          to: "/centre/dashboard",
          icon: "pi pi-chart-bar",
        },
        {
          labelKey: "centre.nav.branches",
          to: "/centre/succursales",
          icon: "pi pi-sitemap",
        },
        {
          labelKey: "centre.nav.secretaries",
          to: "/centre/secretaires",
          icon: "pi pi-users",
        },
        {
          labelKey: "centre.nav.teachers",
          to: "/centre/enseignants",
          icon: "pi pi-user-edit",
        },
        {
          labelKey: "centre.nav.classes",
          to: "/centre/sessions",
          icon: "pi pi-calendar",
        },
        {
          labelKey: "centre.nav.students",
          to: "/centre/etudiants",
          icon: "pi pi-user",
        },
        {
          labelKey: "centre.nav.progression",
          to: "/centre/progression",
          icon: "pi pi-chart-line",
        },
        {
          labelKey: "centre.nav.settings",
          to: "/centre/reglages",
          icon: "pi pi-cog",
        },
      ],
    },
  ],

  secretaire: [
    {
      titleKey: "sidebar.main",
      items: [
        {
          labelKey: "centre.nav.my_students",
          to: "/centre/etudiants",
          icon: "pi pi-user",
          exact: true,
        },
        {
          labelKey: "centre.nav.new_student",
          to: "/centre/etudiants/nouveau",
          icon: "pi pi-user-plus",
        },
        {
          labelKey: "centre.nav.teachers",
          to: "/centre/enseignants",
          icon: "pi pi-user-edit",
        },
        {
          labelKey: "centre.nav.classes",
          to: "/centre/sessions",
          icon: "pi pi-calendar",
        },
        {
          labelKey: "centre.nav.progression",
          to: "/centre/progression",
          icon: "pi pi-chart-line",
        },
      ],
    },
  ],

  enseignant: [
    {
      titleKey: "sidebar.main",
      items: [
        {
          labelKey: "teacher.nav.classes",
          to: "/enseignant/sessions",
          icon: "pi pi-users",
        },
        {
          labelKey: "teacher.nav.students",
          to: "/enseignant/etudiants",
          icon: "pi pi-user",
        },
        {
          labelKey: "teacher.nav.live",
          to: "/enseignant/live/nouveau",
          icon: "pi pi-microphone",
        },
        {
          labelKey: "teacher.nav.assignments",
          to: "/enseignant/devoirs",
          icon: "pi pi-file-edit",
        },
      ],
    },
  ],

  ambassadeur: [
    {
      items: [
        {
          labelKey: "ambassador.nav.program",
          to: "/referrals",
          icon: "pi pi-users",
        },
      ],
    },
    {
      items: [
        {
          labelKey: "dashboard.space",
          to: "/dashboard",
          icon: "pi pi-arrow-left",
        },
      ],
    },
  ],

  // Étudiant : regroupé par intention.
  // audience "center" = élève de centre uniquement, "independent" = étudiant individuel uniquement.
  // Les sections vides après filtrage sont retirées par useNavigation.
  etudiant: [
    {
      items: [
        {
          labelKey: "dashboard.pages.dashboard",
          to: "/dashboard",
          icon: "pi pi-th-large",
          exact: true,
        },
      ],
    },
    {
      // Ce que l'enseignant du centre donne à l'élève
      titleKey: "sidebar.my_class",
      items: [
        {
          labelKey: "dashboard.pages.devoirs",
          to: "/dashboard/devoirs",
          icon: "pi pi-file-edit",
          audience: "center",
        },
        {
          labelKey: "live_session.nav_label",
          to: "/dashboard/sessions-live",
          icon: "pi pi-video",
          audience: "center",
        },
      ],
    },
    {
      titleKey: "sidebar.practice",
      items: [
        {
          labelKey: "dashboard.pages.examens",
          to: "/dashboard/examens",
          icon: "pi pi-book",
        },
        {
          labelKey: "dashboard.pages.sprechen",
          to: "/dashboard/sprechen",
          icon: "pi pi-microphone",
        },
        {
          labelKey: "dashboard.pages.simulateur",
          to: "/dashboard/simulateur",
          icon: "pi pi-pen-to-square",
        },
        {
          labelKey: "dashboard.pages.start_deutsch",
          to: "/dashboard/start-deutsch",
          icon: "pi pi-graduation-cap",
          audience: "independent",
        },
      ],
    },
    {
      titleKey: "sidebar.follow_up",
      items: [
        {
          labelKey: "dashboard.quick_actions.results",
          to: "/dashboard/resultats",
          icon: "pi pi-chart-line",
        },
        {
          labelKey: "dashboard.pages.methodologie",
          to: "/dashboard/methodologie",
          icon: "pi pi-compass",
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
          labelKey: "dashboard.pages.credits",
          to: "/dashboard/credits",
          icon: "pi pi-sparkles",
        },
        {
          labelKey: "dashboard.pages.factures",
          to: "/dashboard/factures",
          icon: "pi pi-receipt",
        },
      ],
    },
  ],
};

// ── Titres et sous-titres des pages (header des layouts) ─
export const PAGE_META: Record<string, PageMeta> = {
  // Admin : en français uniquement (usage interne)
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
    titleKey: "centre.pages.dashboard.title",
    subtitleKey: "centre.pages.dashboard.subtitle",
  },
  "/centre/succursales": {
    titleKey: "centre.pages.branches.title",
    subtitleKey: "centre.pages.branches.subtitle",
  },
  "/centre/secretaires": {
    titleKey: "centre.pages.secretaries.title",
    subtitleKey: "centre.pages.secretaries.subtitle",
  },
  "/centre/etudiants": {
    titleKey: "centre.pages.students.title",
    subtitleKey: "centre.pages.students.subtitle",
  },
  "/centre/etudiants/nouveau": {
    titleKey: "centre.pages.new_student.title",
    subtitleKey: "centre.pages.new_student.subtitle",
  },
  "/centre/enseignants": {
    titleKey: "centre.pages.teachers.title",
    subtitleKey: "centre.pages.teachers.subtitle",
  },
  "/centre/sessions": {
    titleKey: "centre.pages.classes.title",
    subtitleKey: "centre.pages.classes.subtitle",
  },
  "/centre/sessions-live": {
    titleKey: "centre.pages.live.title",
    subtitleKey: "centre.pages.live.subtitle",
  },
  "/centre/progression": {
    titleKey: "centre.pages.progression.title",
    subtitleKey: "centre.pages.progression.subtitle",
  },

  "/centre/reglages": {
    titleKey: "centre.pages.settings.title",
    subtitleKey: "centre.pages.settings.subtitle",
  },

  // Enseignant
  "/enseignant/sessions": {
    titleKey: "teacher.pages.classes.title",
    subtitleKey: "teacher.pages.classes.subtitle",
  },
  "/enseignant/etudiants": {
    titleKey: "teacher.pages.students.title",
    subtitleKey: "teacher.pages.students.subtitle",
  },
  "/enseignant/live/nouveau": {
    titleKey: "teacher.pages.live.title",
    subtitleKey: "teacher.pages.live.subtitle",
  },

  // Ambassadeur
  "/referrals": {
    titleKey: "ambassador.pages.referrals.title",
    subtitleKey: "ambassador.pages.referrals.subtitle",
  },
};

/** Titre/sous-titre de la page courante, avec repli sur le nom de l'espace */
export function getPageMeta(path: string, fallback: string): PageMeta {
  const sansLangue = path.replace(/^\/(fr|de)(?=\/|$)/, "") || "/";
  const clean =
    sansLangue.length > 1 ? sansLangue.replace(/\/$/, "") : sansLangue;
  return PAGE_META[clean] ?? { title: fallback };
}