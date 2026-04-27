/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubjectWithModulesResponse } from './SubjectWithModulesResponse';
/**
 * Level avec subjects + modules + teile (sans questions).
 */
export type LevelWithSubjectsResponse = {
    id: string;
    exam_id: string;
    cefr_code: string;
    total_pass_score: number;
    display_order: number;
    is_free: boolean;
    exam_config: (Record<string, any> | null);
    subject_count?: number;
    subjects?: Array<SubjectWithModulesResponse>;
};

