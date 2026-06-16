/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Réponse après création d'un paiement manuel.
 */
export type ManualPaymentResponse = {
    payment_id: string;
    transaction_reference: string;
    user_id: string;
    exam_id: string;
    amount_paid: number;
    expires_at: string;
    note: (string | null);
};

