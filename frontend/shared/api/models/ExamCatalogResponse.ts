/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LevelAccessResponse } from './LevelAccessResponse';
export type ExamCatalogResponse = {
    id: string;
    provider: string;
    name: string;
    slug: string;
    description: (string | null);
    levels?: Array<LevelAccessResponse>;
};

