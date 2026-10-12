/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CenterResponse = {
    id: string;
    name: string;
    contact_email: (string | null);
    contact_phone: (string | null);
    is_active: boolean;
    address?: (string | null);
    logo_path?: (string | null);
    ai_credit_pool_balance: number;
    default_credits_per_student: number;
    partner_can_activate?: boolean;
    partner_unpaid_limit?: (number | null);
    partner_payment_delay_hours?: number;
    created_at: string;
};

