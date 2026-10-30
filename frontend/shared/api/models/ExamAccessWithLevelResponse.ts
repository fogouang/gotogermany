/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Accès enrichi avec infos du niveau et de l'examen parent.
 * Pour la liste des niveaux accessibles de l'user.
 */
export type ExamAccessWithLevelResponse = {
    id: string;
    level_id: (string | null);
    sd_level?: (string | null);
    access_type: string;
    granted_at: string;
    expires_at: (string | null);
    is_active: boolean;
    cefr_code: string;
    exam_name: string;
    exam_provider: string;
};

