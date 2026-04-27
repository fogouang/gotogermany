/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Statut d'un paiement — polled par le frontend.
 */
export type PaymentStatusResponse = {
    payment_id: string;
    transaction_reference: string;
    payment_status: string;
    amount_paid: number;
    currency: string;
    operator: (string | null);
    completed_at: (string | null);
    exam_access_granted: boolean;
};

