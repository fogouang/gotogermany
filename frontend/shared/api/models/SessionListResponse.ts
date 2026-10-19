/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SessionListResponse = {
    id: string;
    exam_id: string;
    exam_name: string;
    exam_slug: string;
    subject_id: string;
    subject_number: number;
    status: string;
    score: (number | null);
    passed: (boolean | null);
    started_at: string;
    submitted_at: (string | null);
    duration_seconds: (number | null);
    module_slugs?: (Array<string> | null);
    score_breakdown?: (Record<string, any> | null);
};

