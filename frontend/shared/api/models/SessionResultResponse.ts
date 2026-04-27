/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModuleResultResponse } from './ModuleResultResponse';
export type SessionResultResponse = {
    session_id: string;
    exam_id: string;
    exam_name: string;
    subject_id: string;
    subject_number: number;
    status: string;
    score: (number | null);
    score_breakdown: (Record<string, any> | null);
    passed: (boolean | null);
    total_pass_score: number;
    started_at: string;
    submitted_at: (string | null);
    duration_seconds: (number | null);
    modules?: Array<ModuleResultResponse>;
    result_message: (string | null);
};

