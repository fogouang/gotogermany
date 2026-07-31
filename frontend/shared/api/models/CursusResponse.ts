/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CursusLevel } from './CursusLevel';
import type { CursusStatus } from './CursusStatus';
import type { LevelEnrollmentResponse } from './LevelEnrollmentResponse';
export type CursusResponse = {
    id: string;
    student_id: string;
    branch_id: string;
    start_level: CursusLevel;
    target_level: CursusLevel;
    status: CursusStatus;
    created_at: string;
    level_enrollments?: Array<LevelEnrollmentResponse>;
};

