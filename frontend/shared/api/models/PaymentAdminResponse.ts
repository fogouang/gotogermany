/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PaymentAdminResponse = {
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
    user_id: string;
    user_email?: (string | null);
    user_name?: (string | null);
    exam_name?: (string | null);
    mycoolpay_ref?: (string | null);
    expires_at?: (string | null);
};

