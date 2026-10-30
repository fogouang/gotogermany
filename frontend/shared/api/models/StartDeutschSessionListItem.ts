/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Liste des tentatives de l'étudiant.
 */
export type StartDeutschSessionListItem = {
    id: string;
    subject_id: string;
    subject_title?: string;
    subject_number?: number;
    level?: string;
    status: string;
    score: (number | null);
    score_percent?: (number | null);
    passed: (boolean | null);
    started_at: string;
    submitted_at: (string | null);
};

