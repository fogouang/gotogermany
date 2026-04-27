/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * L'étudiant initie un paiement pour un exam.
 */
export type PaymentInitiateRequest = {
    exam_id: string;
    plan_id: string;
    promo_code?: (string | null);
    operator: string;
    phone_number: string;
};

