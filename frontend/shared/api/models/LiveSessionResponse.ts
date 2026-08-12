/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LiveSessionStatus } from './LiveSessionStatus';
export type LiveSessionResponse = {
    id: string;
    examiner_id: string;
    student_id: string;
    subject_id: string;
    status: LiveSessionStatus;
    created_at: string;
    prep_started_at: (string | null);
    live_started_at: (string | null);
    ended_at: (string | null);
    examiner_notes: (string | null);
    notes_sent_at: (string | null);
    student_name: (string | null);
    examiner_name: (string | null);
};

