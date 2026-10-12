/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SettlementCreate = {
    partner_type: SettlementCreate.partner_type;
    partner_id: string;
    direction: SettlementCreate.direction;
    amount: number;
    method: string;
    reference?: (string | null);
    note?: (string | null);
};
export namespace SettlementCreate {
    export enum partner_type {
        CENTER = 'center',
        AMBASSADOR = 'ambassador',
    }
    export enum direction {
        TO_PLATFORM = 'to_platform',
        TO_PARTNER = 'to_partner',
    }
}

