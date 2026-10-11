// app/composables/useNavigation.ts
// Menu, espace et titre de page selon l'utilisateur connecté.
//
// Usage dans un layout :
//   const nav = useNavigation();              // rôle déduit du store
//   const nav = useNavigation("admin");       // rôle imposé par le layout
//   const nav = useNavigation("ambassadeur"); // is_ambassador = drapeau, pas un rôle
import {
  ESPACES,
  NAVIGATION,
  getPageMeta,
} from "~/config/navigation";
import type { NavItem, NavRole } from "~/types/navigation";

export interface NavItemResolu {
  label: string;
  to: string;
  icon: string;
  exact: boolean;
}

export interface NavSectionResolue {
  title?: string;
  items: NavItemResolu[];
}

export function useNavigation(roleImpose?: NavRole) {
  const authStore = useAuthStore();
  const route = useRoute();
  const { t } = useI18n();

  // Rôle de navigation : imposé par le layout, sinon déduit du store.
  const role = computed<NavRole>(() => {
    if (roleImpose) return roleImpose;
    if (authStore.isAdmin) return "admin";
    if (authStore.isDirector) return "directeur";
    if (authStore.isSecretary) return "secretaire";
    if (authStore.isTeacher) return "enseignant";
    return "etudiant";
  });

  const espace = computed(() => ESPACES[role.value]);

  const libelle = (item: { label?: string; labelKey?: string }) =>
    item.labelKey ? t(item.labelKey) : (item.label ?? "");

  // Sections avec libellés déjà traduits : le layout n'a plus qu'à afficher.
  const sections = computed<NavSectionResolue[]>(() =>
    NAVIGATION[role.value].map((section) => ({
      title: section.titleKey ? t(section.titleKey) : section.title,
      items: section.items.map((item: NavItem) => ({
        label: libelle(item),
        to: item.to,
        icon: item.icon,
        exact: !!item.exact,
      })),
    })),
  );

  // Lien actif : exact si demandé, sinon le chemin courant commence par le lien.
  function estActif(item: NavItemResolu) {
    const path = route.path.replace(/\/$/, "") || "/";
    if (item.exact) return path === item.to;
    return path === item.to || path.startsWith(`${item.to}/`);
  }

  // Titre / sous-titre du header. Espace étudiant : clé i18n par segment,
  // comme le faisait déjà le layout dashboard.
  const pageMeta = computed(() => {
    if (role.value === "etudiant") {
      const apres = route.path.replace("/dashboard", "");
      const segment = apres.split("/").filter(Boolean)[0] || "dashboard";
      return { title: t(`dashboard.pages.${segment}`, segment) };
    }
    return getPageMeta(route.path, espace.value.label);
  });

  const initiale = computed(() =>
    (authStore.userName || espace.value.roleLabel).charAt(0).toUpperCase(),
  );

  // Attend la libération de l'appareil côté serveur avant de quitter.
  async function seDeconnecter() {
    await authStore.logout();
    await navigateTo("/");
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