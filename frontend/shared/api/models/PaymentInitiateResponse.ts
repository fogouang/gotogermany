/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Retourné après création du payin My-CoolPay.
 */
export type PaymentInitiateResponse = {
    payment_id: string;
    transaction_reference: string;
    amount_gross: number;
    amount_paid: number;
    discount_amount: number;
    currency: string;
    ussd_code: (string | null);
    message: string;
};

