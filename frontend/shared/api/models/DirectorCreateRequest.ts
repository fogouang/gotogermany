/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Création d'un compte center_director — admin ITIA uniquement.
 */
export type DirectorCreateRequest = {
    email: string;
    password: string;
    full_name: string;
    phone?: (string | null);
    center_id: string;
};

