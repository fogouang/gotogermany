/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModuleScoreBreakdown } from './ModuleScoreBreakdown';
/**
 * Score par module (Lesen/Hören/Schreiben/Sprechen) pour un sujet précis.
 */
export type SubjectScoreBreakdown = {
    subject_id: string;
    subject_name: string;
    total_sessions: number;
    average_score: (number | null);
    last_session_at: (string | null);
    last_session_id?: (string | null);
    modules: Array<ModuleScoreBreakdown>;
};

