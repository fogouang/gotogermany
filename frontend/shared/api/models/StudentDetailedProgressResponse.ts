/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ExamProgressResponse } from './ExamProgressResponse';
import type { ScoreHistoryPoint } from './ScoreHistoryPoint';
/**
 * Vue détaillée d'un étudiant — ventilation par examen/module + historique pour graphes.
 */
export type StudentDetailedProgressResponse = {
    student_id: string;
    student_name: string;
    branch_name: string;
    ai_credits_remaining: number;
    total_sessions: number;
    overall_average_score: (number | null);
    last_session_at: (string | null);
    exams: Array<ExamProgressResponse>;
    score_history: Array<ScoreHistoryPoint>;
};

