/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TeilResponse } from './TeilResponse';
export type ModuleWithTeilenResponse = {
    id: string;
    slug: string;
    name: string;
    time_limit_minutes: number;
    max_score: number;
    display_order: number;
    teile?: Array<TeilResponse>;
};

