/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschTeilResult } from './StartDeutschTeilResult';
export type StartDeutschModuleResult = {
    module_id: string;
    slug: string;
    max_score: number;
    score_obtained: number;
    is_corrected: boolean;
    teile?: Array<StartDeutschTeilResult>;
};

