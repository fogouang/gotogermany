/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * L'étudiant paie l'accès à un niveau d'examen (level_id) ou à Start Deutsch (sd_level).
 */
export type PaymentInitiateRequest = {
    level_id?: (string | null);
    sd_level?: ('A1' | 'A2' | null);
    plan_id: string;
    promo_code?: (string | null);
    operator: string;
    phone_number: string;
};

