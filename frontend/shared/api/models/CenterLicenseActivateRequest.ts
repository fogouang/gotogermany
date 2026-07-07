/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentMethod } from './PaymentMethod';
/**
 * Activation d'une licence pour un centre — admin ITIA uniquement.
 */
export type CenterLicenseActivateRequest = {
    formula_id: string;
    payment_method: PaymentMethod;
    payment_reference?: (string | null);
};

