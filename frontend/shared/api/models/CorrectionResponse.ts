/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__modules__corrections__schemas__CriterionScore } from './app__modules__corrections__schemas__CriterionScore';
import type { app__modules__corrections__schemas__TaskFeedback } from './app__modules__corrections__schemas__TaskFeedback';
import type { CorrectionError } from './CorrectionError';
/**
 * Réponse complète retournée au frontend — même forme pour tous les examens.
 */
export type CorrectionResponse = {
    id: string;
    session_id: string;
    provider: string;
    level: string;
    overall_score: number;
    max_score: number;
    passed: boolean;
    score_percentage: number;
    appreciation: string;
    floor_reached?: (boolean | null);
    criteria: Array<app__modules__corrections__schemas__CriterionScore>;
    tasks: Array<app__modules__corrections__schemas__TaskFeedback>;
    corrections_list: Array<CorrectionError>;
    suggestions: Array<string>;
    ai_provider: string;
    created_at: string;
};

