/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Inscription simplifiée : nom, téléphone, mot de passe. Email facultatif.
 * Avec center_join_token + branch_id : inscription via le lien d'un centre,
 * en attente de validation par la secrétaire.
 */
export type RegisterRequest = {
    full_name: string;
    phone: string;
    password: string;
    email?: (string | null);
    referral_code?: (string | null);
    whatsapp_opt_in?: boolean;
    center_join_token?: (string | null);
    branch_id?: (string | null);
};

