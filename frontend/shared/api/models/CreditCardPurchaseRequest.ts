/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Achat de crédits par carte (Stripe, en euros).
 */
export type CreditCardPurchaseRequest = {
    credits: number;
    locale?: CreditCardPurchaseRequest.locale;
};
export namespace CreditCardPurchaseRequest {
    export enum locale {
        FR = 'fr',
        EN = 'en',
        DE = 'de',
    }
}

