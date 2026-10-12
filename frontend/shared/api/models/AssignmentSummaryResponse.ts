/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssignmentTargetResponse } from './AssignmentTargetResponse';
export type AssignmentSummaryResponse = {
    id: string;
    title: string;
    instructions: (string | null);
    subject_id: string;
    subject_name: string;
    exam_name: string;
    cefr_code: string;
    due_at: (string | null);
    is_cancelled: boolean;
    created_at: string;
    targets?: Array<AssignmentTargetResponse>;
    expected_count?: number;
    submitted_count?: number;
    graded_count?: number;
};

