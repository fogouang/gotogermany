/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CreditPurchaseRequest = {
    credits: number;
    /**
     * mobile_money | card
     */
    payment_method: string;
    phone_number?: (string | null);
};

