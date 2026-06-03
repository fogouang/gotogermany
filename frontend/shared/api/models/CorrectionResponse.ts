/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Réponse complète retournée au frontend.
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
    aufgabe_score: number;
    kohaesion_score: number;
    wortschatz_score: number;
    grammatik_score: number;
    criteria_feedbacks: Record<string, any>;
    task_feedbacks: Record<string, any>;
    corrections_list: Array<Record<string, any>>;
    suggestions: Array<string>;
    appreciation: string;
    ai_provider: string;
    created_at: string;
};

