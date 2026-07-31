/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FormationPaymentType } from './FormationPaymentType';
export type app__modules__enrollments__schemas__PaymentResponse = {
    id: string;
    enrollment_id: string;
    payment_type: FormationPaymentType;
    amount: number;
    paid_at: string;
    recorded_by: string;
    invoice_number: (string | null);
    invoice_url?: (string | null);
    notes: (string | null);
};

