/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TrainingSessionCreateRequest = {
    /**
     * Requis pour un directeur (plusieurs branches possibles). Ignoré pour une secrétaire (sa propre branche s'applique).
     */
    branch_id?: (string | null);
    level_id: string;
    label?: (string | null);
    start_date: string;
    end_date?: (string | null);
};

