/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JoinBranchOption } from './JoinBranchOption';
/**
 * Page publique /rejoindre/{token} : nom du centre et succursales.
 */
export type JoinInfoResponse = {
    center_name: string;
    branches: Array<JoinBranchOption>;
};

