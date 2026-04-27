/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response complète d'un paiement — historique.
 */
export type PaymentResponse = {
    id: string;
    exam_id: string;
    plan_id: string;
    promo_code_id: (string | null);
    amount_gross: number;
    amount_paid: number;
    discount_amount: number;
    commission_due: number;
    currency: string;
    payment_status: string;
    transaction_reference: string;
    operator: (string | null);
    completed_at: (string | null);
    created_at: string;
};

