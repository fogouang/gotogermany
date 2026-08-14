/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TeilResultResponse } from './TeilResultResponse';
export type ModuleResultResponse = {
    slug: string;
    name: string;
    max_score: number;
    score_obtained: (number | null);
    is_corrected: boolean;
    questions_correct: number;
    questions_incorrect: number;
    questions_total: number;
    teile?: Array<TeilResultResponse>;
};

