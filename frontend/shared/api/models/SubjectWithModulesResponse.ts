/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModuleWithTeilenResponse } from './ModuleWithTeilenResponse';
/**
 * Subject avec modules + teile (sans questions) — pour page détail.
 */
export type SubjectWithModulesResponse = {
    id: string;
    level_id: string;
    subject_number: number;
    name: (string | null);
    is_active: boolean;
    has_audio?: boolean;
    modules?: Array<ModuleWithTeilenResponse>;
};

