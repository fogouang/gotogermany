/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AssignmentCreate = {
    kind?: AssignmentCreate.kind;
    subject_id: string;
    title: string;
    instructions?: (string | null);
    due_at?: (string | null);
    class_ids?: Array<string>;
    student_ids?: Array<string>;
};
export namespace AssignmentCreate {
    export enum kind {
        EXAM = 'exam',
        START_DEUTSCH = 'start_deutsch',
    }
}

