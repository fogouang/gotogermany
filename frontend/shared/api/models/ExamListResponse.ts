/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LevelResponse } from './LevelResponse';
export type ExamListResponse = {
    id: string;
    provider: string;
    name: string;
    slug: string;
    description: (string | null);
    is_active: boolean;
    levels?: Array<LevelResponse>;
};

