/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschModuleResult } from './StartDeutschModuleResult';
/**
 * Résultat complet d'une session — pensé pour alimenter une page de résultat
 * du même esprit que celle déjà en place pour B1/B2 (score par Teil/module,
 * seuil de réussite, réponses détaillées).
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

