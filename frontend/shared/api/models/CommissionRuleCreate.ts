/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CommissionRuleCreate = {
    partner_type: CommissionRuleCreate.partner_type;
    center_id?: (string | null);
    user_id?: (string | null);
    plan_id?: (string | null);
    rule_type: CommissionRuleCreate.rule_type;
    value: (number | string);
};
export namespace CommissionRuleCreate {
    export enum partner_type {
        CENTER = 'center',
        AMBASSADOR = 'ambassador',
    }
    export enum rule_type {
        PERCENT = 'percent',
        FIXED = 'fixed',
    }
}

