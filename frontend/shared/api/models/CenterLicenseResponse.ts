/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LicenseStatus } from './LicenseStatus';
import type { PaymentMethod } from './PaymentMethod';
export type CenterLicenseResponse = {
    id: string;
    center_id: string;
    formula_id: string;
    start_date: string;
    end_date: string;
    max_students: number;
    status: LicenseStatus;
    payment_method: (PaymentMethod | null);
    payment_reference: (string | null);
    created_at: string;
};

