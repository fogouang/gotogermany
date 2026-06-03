/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TaskSchema } from './TaskSchema';
export type SchreibenSubjectCreate = {
    provider: SchreibenSubjectCreate.provider;
    level: SchreibenSubjectCreate.level;
    title: string;
    description?: (string | null);
    tasks: Array<TaskSchema>;
    display_order?: number;
    is_active?: boolean;
};
export namespace SchreibenSubjectCreate {
    export enum provider {
        TELC = 'telc',
        GOETHE = 'goethe',
        OSD = 'osd',
    }
    export enum level {
        B1 = 'b1',
        B2 = 'b2',
    }
}

