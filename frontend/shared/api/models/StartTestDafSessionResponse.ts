/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TestDafTaskOut } from './TestDafTaskOut';
export type StartTestDafSessionResponse = {
    session_id: string;
    provider: string;
    level: string;
    total_minutes: number;
    tasks: Array<TestDafTaskOut>;
};

