/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentMethod } from './PaymentMethod';
/**
 * Extension du quota d'une licence active — admin ITIA uniquement.
 */
export type CenterLicenseExtendRequest = {
    additional_students: number;
    payment_method: PaymentMethod;
    payment_reference?: (string | null);
};

