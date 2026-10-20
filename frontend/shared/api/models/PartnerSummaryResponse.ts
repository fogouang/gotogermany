/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PartnerSummaryResponse = {
    partner_type: string;
    partner_id: string;
    name: string;
    can_activate: boolean;
    unpaid_limit: (number | null);
    payment_delay_hours: number;
    owed_to_platform: number;
    owed_to_partner: number;
    net_balance: number;
    overdue_amount: number;
    overdue_count: number;
    is_blocked: boolean;
    block_reason: (string | null);
    earned_total?: number;
    trial_active?: boolean;
    trial_ends_at?: (string | null);
    trial_activations_left?: number;
};

