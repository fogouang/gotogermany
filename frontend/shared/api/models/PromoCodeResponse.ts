/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PromoCodeResponse = {
    id: string;
    code: string;
    discount_type: string;
    discount_value: number;
    commission_rate: number;
    max_uses: (number | null);
    used_count: number;
    expires_at: (string | null);
    is_active: boolean;
    partner_id: (string | null);
    created_at: string;
};

