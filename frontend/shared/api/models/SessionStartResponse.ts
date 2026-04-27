/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SessionStartResponse = {
    session_id: string;
    exam_id: string;
    exam_name: string;
    subject_id: string;
    subject_number: number;
    subject_name: (string | null);
    status: string;
    started_at: string;
    modules?: Array<Record<string, any>>;
    existing_answers?: Record<string, any>;
};

