/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Admin valide manuellement un accès exam (MyCoolPay indisponible, virement, cash).
 */
export type ManualPaymentRequest = {
    user_id: string;
    exam_id: string;
    plan_id: string;
    /**
     * Ex: 'Virement Orange Money reçu le 16/06/2026'
     */
    note?: (string | null);
};

