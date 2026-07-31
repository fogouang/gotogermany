/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LevelEnrollmentStatus } from './LevelEnrollmentStatus';
export type BalanceSummaryResponse = {
    inscription_due: number;
    inscription_paid: number;
    inscription_remaining: number;
    formation_due: number;
    formation_paid: number;
    formation_remaining: number;
    status: LevelEnrollmentStatus;
};

