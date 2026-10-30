/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Accès à un niveau, retourné après grant admin ou paiement.
 */
export type ExamAccessResponse = {
    id: string;
    level_id: (string | null);
    sd_level?: (string | null);
    access_type: string;
    granted_at: string;
    expires_at: (string | null);
    is_active: boolean;
};

