/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CreditPurchaseResponse = {
    payment_id: string;
    invoice_number: string;
    credits: number;
    price_per_credit: number;
    total_amount: number;
    payment_status: string;
    ussd?: (string | null);
    action?: (string | null);
    redirect_url?: (string | null);
    transaction_reference?: (string | null);
};

