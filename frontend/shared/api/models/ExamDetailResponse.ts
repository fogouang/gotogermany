/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LevelWithSubjectsResponse } from './LevelWithSubjectsResponse';
/**
 * Vue détail — exam + levels + subjects + modules + teile.
 */
export type ExamDetailResponse = {
    id: string;
    provider: string;
    name: string;
    slug: string;
    description: (string | null);
    is_active: boolean;
    levels?: Array<LevelWithSubjectsResponse>;
    created_at: string;
};

