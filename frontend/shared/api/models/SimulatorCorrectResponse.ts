/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__modules__schreiben_simulator__schemas__CriterionScore } from './app__modules__schreiben_simulator__schemas__CriterionScore';
import type { app__modules__schreiben_simulator__schemas__TaskFeedback } from './app__modules__schreiben_simulator__schemas__TaskFeedback';
/**
 * Réutilise exactement le même contrat que corrections.schemas.CorrectionResponse
 * (criteria/tasks génériques, produits par response_normalizer), moins id/session_id
 * puisqu'ici il n'y a pas de session — remplacés par subject_id.
 */
export type SimulatorCorrectResponse = {
    subject_id: string;
    provider: string;
    level: string;
    overall_score: number;
    max_score: number;
    passed: boolean;
    score_percentage: number;
    appreciation: string;
    floor_reached?: (boolean | null);
    criteria: Array<app__modules__schreiben_simulator__schemas__CriterionScore>;
    tasks: Array<app__modules__schreiben_simulator__schemas__TaskFeedback>;
    corrections_list: Array<Record<string, any>>;
    suggestions: Array<string>;
};

