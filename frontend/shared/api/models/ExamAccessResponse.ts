/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Accès à un level — retourné après grant admin ou paiement.
 */
export type ExamAccessResponse = {
    id: string;
    level_id: string;
    access_type: string;
    granted_at: string;
    expires_at: (string | null);
    is_active: boolean;
};

