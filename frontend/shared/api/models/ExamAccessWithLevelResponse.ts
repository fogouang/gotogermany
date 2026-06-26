/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Accès enrichi avec infos du level et de l'exam parent.
 * Pour la liste des levels accessibles de l'user.
 */
export type ExamAccessWithLevelResponse = {
    id: string;
    level_id: string;
    access_type: string;
    granted_at: string;
    expires_at: (string | null);
    is_active: boolean;
    cefr_code: string;
    exam_name: string;
    exam_provider: string;
};

