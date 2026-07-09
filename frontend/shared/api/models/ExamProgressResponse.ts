/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModuleScoreBreakdown } from './ModuleScoreBreakdown';
/**
 * Progression détaillée sur un examen précis (ex: Goethe-Zertifikat B2).
 */
export type ExamProgressResponse = {
    exam_id: string;
    exam_name: string;
    total_sessions: number;
    average_score: (number | null);
    last_session_at: (string | null);
    modules: Array<ModuleScoreBreakdown>;
};

