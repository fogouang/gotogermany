/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SprechenPreviewTeil } from './SprechenPreviewTeil';
export type SprechenPreviewResponse = {
    subject_id: string;
    provider: string;
    level: string;
    total_minutes: number;
    teile: Array<SprechenPreviewTeil>;
    credit_cost: number;
    credits_available: number;
    can_start: boolean;
};

