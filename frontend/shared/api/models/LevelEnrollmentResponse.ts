/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CursusLevel } from './CursusLevel';
import type { LevelEnrollmentStatus } from './LevelEnrollmentStatus';
export type LevelEnrollmentResponse = {
    id: string;
    cursus_id: string;
    level: CursusLevel;
    inscription_fee_amount: number;
    formation_fee_amount: number;
    status: LevelEnrollmentStatus;
    created_at: string;
};

