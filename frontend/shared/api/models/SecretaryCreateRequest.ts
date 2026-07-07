/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Création d'un compte branch_secretary — par le directeur de centre.
 */
export type SecretaryCreateRequest = {
    email: string;
    password: string;
    full_name: string;
    phone?: (string | null);
    branch_id: string;
};

