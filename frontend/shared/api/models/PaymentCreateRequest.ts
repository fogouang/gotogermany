/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FormationPaymentType } from './FormationPaymentType';
export type PaymentCreateRequest = {
    payment_type: FormationPaymentType;
    amount: number;
    notes?: (string | null);
};

