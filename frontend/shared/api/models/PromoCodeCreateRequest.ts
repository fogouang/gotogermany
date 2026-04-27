/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PromoCodeCreateRequest = {
    partner_id?: (string | null);
    code: string;
    discount_type: PromoCodeCreateRequest.discount_type;
    discount_value: number;
    commission_rate?: number;
    max_uses?: (number | null);
    expires_at?: (string | null);
    is_active?: boolean;
};
export namespace PromoCodeCreateRequest {
    export enum discount_type {
        PERCENT = 'percent',
        FIXED = 'fixed',
    }
}

