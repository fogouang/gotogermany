/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Création d'un compte teacher — par le directeur (branch_id requis,
 * plusieurs succursales possibles) ou la secrétaire (sa propre succursale
 * s'applique, branch_id ignoré si fourni).
 */
export type TeacherCreateRequest = {
    email: string;
    password: string;
    full_name: string;
    phone?: (string | null);
    branch_id?: (string | null);
};

