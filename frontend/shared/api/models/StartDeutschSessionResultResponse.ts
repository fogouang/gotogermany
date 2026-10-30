/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschModuleResult } from './StartDeutschModuleResult';
/**
 * Résultat d'une session : score par module et par Teil, seuil, réponses.
 */
export type StartDeutschSessionResultResponse = {
    session_id: string;
    subject_id: string;
    subject_title: string;
    level: string;
    status: string;
    score: (number | null);
    total_pass_score: number;
    passed: (boolean | null);
    started_at: string;
    submitted_at: (string | null);
    modules?: Array<StartDeutschModuleResult>;
};

