// app/types/navigation.ts
import type { LearningTrack } from "~/composables/useLearningTrack";

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
  /**
   * Visibilité dans l'espace étudiant :
   * "center" = élève de centre uniquement, "independent" = étudiant individuel uniquement.
   * Absent = visible par tous.
   */
  audience?: "center" | "independent";
  /**
   * Parcours de l'étudiant qui voit cette entrée :
   * "exam" = B1/B2 (telc, Goethe, ÖSD), "start_deutsch" = A1/A2.
   * Absent = visible dans les deux parcours.
   */
  track?: LearningTrack;
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