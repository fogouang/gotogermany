/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SimulatorResultResponse = {
    id: string;
    subject_id: string;
    subject_title?: (string | null);
    provider: string;
    level: string;
    overall_score: number;
    max_score: number;
    passed: boolean;
    score_percentage: number;
    result_data: Record<string, any>;
    created_at: string;
};

