/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type BankSubjectResponse = {
    kind?: BankSubjectResponse.kind;
    subject_id: string;
    subject_name: string;
    subject_number: number;
    exam_id?: (string | null);
    exam_name: string;
    provider: string;
    level_id?: (string | null);
    cefr_code: string;
    modules?: Array<string>;
};
export namespace BankSubjectResponse {
    export enum kind {
        EXAM = 'exam',
        START_DEUTSCH = 'start_deutsch',
    }
}

