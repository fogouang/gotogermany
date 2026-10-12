// app/types/navigation.ts

// Rôles côté navigation : un rôle = un menu.
// (directeur et secrétaire partagent l'espace Centre mais n'ont pas le même menu)
export type NavRole =
  | "admin"
  | "directeur"
  | "secretaire"
  | "enseignant"
  | "ambassadeur"
  | "etudiant";

export interface NavItem {
  /** Libellé en dur (utilisé si labelKey est absent) */
  label?: string;
  /** Clé i18n : prioritaire sur label, affichée via t(labelKey) */
  labelKey?: string;
  to: string;
  /** Classe PrimeIcons complète, ex. "pi pi-users" */
  icon: string;
  /** Actif seulement si le chemin correspond exactement (ex. "/admin") */
  exact?: boolean;
}

export interface NavSection {
  /** Titre de groupe en dur (optionnel) */
  title?: string;
  /** Clé i18n du titre de groupe : prioritaire sur title */
  titleKey?: string;
  items: NavItem[];
}

export interface EspaceConfig {
  /** Nom de l'espace sous le logo, ex. "Espace Centre" */
  label: string;
  /** Clé i18n du nom de l'espace : prioritaire sur label */
  labelKey?: string;
  /** Libellé du rôle (pied de sidebar, badge du header) */
  roleLabel: string;
  /** Clé i18n du rôle : prioritaire sur roleLabel */
  roleLabelKey?: string;
  /** Icône de l'espace */
  icon: string;
}

export interface PageMeta {
  title?: string;
  /** Clé i18n du titre : prioritaire sur title */
  titleKey?: string;
  subtitle?: string;
  /** Clé i18n du sous-titre : prioritaire sur subtitle */
  subtitleKey?: string;
}