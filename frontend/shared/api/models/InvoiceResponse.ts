/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PartnerInfoResponse } from './PartnerInfoResponse';
export type InvoiceResponse = {
    transaction_reference: string;
    payment_id: string;
    amount_gross: number;
    amount_paid: number;
    discount_amount: number;
    operator: (string | null);
    payment_date: string;
    invoice_url: (string | null);
    customer_name: (string | null);
    customer_email: (string | null);
    product_description: string;
    partner_info?: (PartnerInfoResponse | null);
};

