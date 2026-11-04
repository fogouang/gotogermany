/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Paiement par carte (Stripe, en euros) d'un niveau d'examen ou Start Deutsch.
 */
export type CardPaymentRequest = {
    level_id?: (string | null);
    sd_level?: ('A1' | 'A2' | null);
    plan_id: string;
    promo_code?: (string | null);
    locale?: CardPaymentRequest.locale;
};
export namespace CardPaymentRequest {
    export enum locale {
        FR = 'fr',
        EN = 'en',
        DE = 'de',
    }
}

