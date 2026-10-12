/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PartnerSaleResponse = {
    id: string;
    payment_id: string;
    student_id: string;
    student_name: string;
    plan_name: (string | null);
    level_id: (string | null);
    direction: string;
    price: number;
    partner_share: number;
    platform_share: number;
    amount_due: number;
    settled_amount: number;
    remaining: number;
    rule_type: string;
    rule_value: number;
    due_at: (string | null);
    is_overdue: boolean;
    status: string;
    created_at: string;
};

