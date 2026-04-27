/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Accès à un exam — retourné après paiement ou inscription.
 */
export type ExamAccessResponse = {
    id: string;
    exam_id: string;
    access_type: string;
    granted_at: string;
    expires_at: (string | null);
    is_active: boolean;
};

