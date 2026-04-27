/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnswerDetailResponse } from './AnswerDetailResponse';
export type TeilResultResponse = {
    teil_number: number;
    format_type: string;
    max_score: number;
    score_obtained: number;
    answers?: Array<AnswerDetailResponse>;
};

