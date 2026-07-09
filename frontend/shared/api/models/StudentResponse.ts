/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Réponse pour la liste des étudiants d'une succursale (vue secrétaire/directeur).
 */
export type StudentResponse = {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    target_level_id: (string | null);
    first_login_at: (string | null);
    access_expires_at: (string | null);
    created_at: string;
    ai_credits?: number;
};

