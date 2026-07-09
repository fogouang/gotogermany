/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Création d'un compte student rattaché à un centre — par la secrétaire.
 */
export type StudentCreateRequest = {
    email: string;
    password: string;
    full_name: string;
    phone?: (string | null);
    target_level_id: string;
    access_duration_days?: (number | null);
};

