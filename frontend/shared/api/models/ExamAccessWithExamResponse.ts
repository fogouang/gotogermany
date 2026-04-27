/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Accès enrichi avec infos de l'exam — pour la liste
 * des examens accessibles de l'user (GET /users/me/exams).
 */
export type ExamAccessWithExamResponse = {
    id: string;
    exam_id: string;
    access_type: string;
    granted_at: string;
    expires_at: (string | null);
    is_active: boolean;
    exam_name: string;
    exam_slug: string;
    exam_provider: string;
    cefr_code: string;
};

