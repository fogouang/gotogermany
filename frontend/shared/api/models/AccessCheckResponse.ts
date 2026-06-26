/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Vérification rapide d'accès à un level.
 * Retourné par GET /exam-access/check/{level_id}.
 */
export type AccessCheckResponse = {
    level_id: string;
    has_access: boolean;
    access_type: (string | null);
    expires_at: (string | null);
    reason: (string | null);
};

