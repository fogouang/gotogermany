/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type StudentQuickCreateRequest = {
    full_name: string;
    phone?: (string | null);
    /**
     * Requis si créé par un directeur (plusieurs branches possibles). Ignoré si créé par une secrétaire (sa propre branche s'applique).
     */
    branch_id?: (string | null);
};

