/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Admin valide manuellement un accès exam (MyCoolPay indisponible, virement, cash).
 */
export type ManualPaymentRequest = {
    user_id: string;
    level_id?: (string | null);
    sd_level?: ('A1' | 'A2' | null);
    plan_id?: (string | null);
    days?: (number | null);
    /**
     * Ex: 'Virement Orange Money reçu le 16/06/2026'
     */
    note?: (string | null);
};

