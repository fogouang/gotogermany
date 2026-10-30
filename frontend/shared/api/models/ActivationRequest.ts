/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Niveau activé : un niveau d'examen (level_id) ou Start Deutsch (sd_level).
 * Sans l'un ni l'autre, on prend le niveau déjà fixé sur le compte de l'élève.
 */
export type ActivationRequest = {
    student_id: string;
    level_id?: (string | null);
    sd_level?: ('A1' | 'A2' | null);
    plan_id: string;
};

