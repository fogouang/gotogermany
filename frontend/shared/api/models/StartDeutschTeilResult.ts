/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschAnswerResult } from './StartDeutschAnswerResult';
export type StartDeutschTeilResult = {
    teil_id: string;
    teil_number: number;
    format_type: string;
    max_score: number;
    score_obtained: number;
    answers?: Array<StartDeutschAnswerResult>;
};

