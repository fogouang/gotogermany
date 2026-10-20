// app/composables/useNavigation.ts
// Menu, espace et titre de page selon l'utilisateur connecté.
//
// Usage dans un layout :
//   const nav = useNavigation();              // rôle déduit du store
//   const nav = useNavigation("admin");       // rôle imposé par le layout
//   const nav = useNavigation("ambassadeur"); // is_ambassador = drapeau, pas un rôle
import { ESPACES, NAVIGATION, getPageMeta } from "~/config/navigation";
import type { NavItem, NavRole } from "~/types/navigation";

export interface NavItemResolu {
  label: string;
  /** Chemin déjà localisé (/fr/centre/..., /de/centre/...) */
  to: string;
  icon: string;
  exact: boolean;
}

export interface NavSectionResolue {
  title?: string;
  items: NavItemResolu[];
}

/** Retire le préfixe de langue : /fr/centre/x -> /centre/x */
function sansLangue(path: string) {
  const p = path.replace(/^\/(fr|de)(?=\/|$)/, "") || "/";
  return p.length > 1 ? p.replace(/\/$/, "") : p;
}

export function useNavigation(roleImpose?: NavRole) {
  const authStore = useAuthStore();
  const route = useRoute();
  const { t } = useI18n();
  const localePath = useLocalePath();
  const { track } = useLearningTrack();

  // Rôle de navigation : imposé par le layout, sinon déduit du store.
  const role = computed<NavRole>(() => {
    if (roleImpose) return roleImpose;
    if (authStore.isAdmin) return "admin";
    if (authStore.isDirector) return "directeur";
    if (authStore.isSecretary) return "secretaire";
    if (authStore.isTeacher) return "enseignant";
    return "etudiant";
  });

  // Espace avec libellés déjà traduits
  const espace = computed(() => {
    const e = ESPACES[role.value];
    return {
      label: e.labelKey ? t(e.labelKey) : e.label,
      roleLabel: e.roleLabelKey ? t(e.roleLabelKey) : e.roleLabel,
      icon: e.icon,
    };
  });

  const libelle = (item: { label?: string; labelKey?: string }) =>
    item.labelKey ? t(item.labelKey) : (item.label ?? "");

  // Élève de centre : même règle que useVisibleCatalog
  const estEleveCentre = computed(() => !!authStore.branchId);

  // Audience (centre / indépendant) et parcours (examen B1/B2 / Start Deutsch A1/A2)
  const visible = (item: NavItem) =>
    (!item.audience ||
      item.audience === (estEleveCentre.value ? "center" : "independent")) &&
    (!item.track || item.track === track.value) &&
    (!item.ambassadorOnly || authStore.isAmbassador);

  // Sections avec libellés traduits et liens localisés : le layout n'a plus qu'à afficher.
  // Les entrées hors audience ou hors parcours sont retirées, puis les sections vides.
  const sections = computed<NavSectionResolue[]>(() =>
    NAVIGATION[role.value]
      .map((section) => ({
        title: section.titleKey ? t(section.titleKey) : section.title,
        items: section.items.filter(visible).map((item: NavItem) => ({
          label: libelle(item),
          to: localePath(item.to),
          icon: item.icon,
          exact: !!item.exact,
        })),
      }))
      .filter((section) => section.items.length > 0),
  );

  // Lien actif : les deux chemins sont localisés, la comparaison marche dans les 3 langues.
  function estActif(item: NavItemResolu) {
    const path = route.path.replace(/\/$/, "") || "/";
    if (item.exact) return path === item.to;
    return path === item.to || path.startsWith(`${item.to}/`);
  }

  // Titre / sous-titre du header.
  const pageMeta = computed(() => {
    const chemin = sansLangue(route.path);

    // Espace étudiant : clé i18n par segment, comme le faisait déjà le layout dashboard.
    // Les clés utilisent « _ » là où l'URL a « - » (start-deutsch -> start_deutsch).
    if (role.value === "etudiant") {
      const apres = chemin.replace(/^\/dashboard/, "");
      const segment = apres.split("/").filter(Boolean)[0] || "dashboard";
      const cle = segment.replace(/-/g, "_");
      return { title: t(`dashboard.pages.${cle}`, segment) };
    }

    const meta = getPageMeta(chemin, espace.value.label);
    return {
      title: meta.titleKey
        ? t(meta.titleKey)
        : (meta.title ?? espace.value.label),
      subtitle: meta.subtitleKey ? t(meta.subtitleKey) : meta.subtitle,
    };
  });

  const initiale = computed(() =>
    (authStore.userName || espace.value.roleLabel).charAt(0).toUpperCase(),
  );

  // Attend la libération de l'appareil côté serveur avant de quitter.
  async function seDeconnecter() {
    await authStore.logout();
    await navigateTo(localePath("/"));
  }

  return {
    role,
    espace,
    sections,
    estActif,
    pageMeta,
    initiale,
    seDeconnecter,
  };
}
