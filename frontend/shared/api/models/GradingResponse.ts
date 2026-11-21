/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TeilGradingOut } from './TeilGradingOut';
export type GradingResponse = {
    session_id: string;
    provider: string;
    level: string;
    teile: Array<TeilGradingOut>;
    total_score: number;
    total_max_score: number;
    passed: boolean;
    level_estimate?: (string | null);
    strengths: Array<string>;
    improvement_areas: Array<string>;
    graded_at: string;
    previous_score_percent?: (number | null);
    score_delta_percent?: (number | null);
};

