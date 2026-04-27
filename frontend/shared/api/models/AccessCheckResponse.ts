/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Vérification rapide d'accès avant démarrage d'une session.
 * Retourné par GET /exams/{exam_id}/access.
 */
export type AccessCheckResponse = {
    exam_id: string;
    has_access: boolean;
    access_type: (string | null);
    expires_at: (string | null);
    reason: (string | null);
};

