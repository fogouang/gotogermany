/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschCriterionScore } from './StartDeutschCriterionScore';
export type StartDeutschSchreibenCorrectionResponse = {
    id: string;
    session_id: string;
    teil_id: string;
    submitted_text: string;
    criteria_scores: Record<string, StartDeutschCriterionScore>;
    overall_score: number;
    max_score: number;
    passed: boolean;
    feedback: (string | null);
    created_at: string;
};

