/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CenterLicenseResponse } from './CenterLicenseResponse';
/**
 * Vue consolidée pour le panel directeur.
 */
export type LicenseUsageResponse = {
    license: (CenterLicenseResponse | null);
    formula_label: (string | null);
    students_used: number;
    students_remaining: number;
    days_remaining: (number | null);
    branches_breakdown: Record<string, number>;
};

