/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Une ligne de la vue 'évolution des étudiants' — secrétaire (sa branche) ou directeur (tout le centre).
 */
export type StudentProgressResponse = {
    student_id: string;
    student_name: string;
    branch_name: string;
    total_sessions: number;
    average_score: (number | null);
    last_session_at: (string | null);
    ai_credits_remaining: number;
};

