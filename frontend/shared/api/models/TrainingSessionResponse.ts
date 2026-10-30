/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TrainingSessionStudentResponse } from './TrainingSessionStudentResponse';
import type { TrainingSessionTeacherResponse } from './TrainingSessionTeacherResponse';
export type TrainingSessionResponse = {
    id: string;
    branch_id: string;
    branch_name: string;
    track?: TrainingSessionResponse.track;
    level_id: (string | null);
    sd_level?: ('A1' | 'A2' | null);
    cefr_code?: string;
    level_name: string;
    label: (string | null);
    start_date: string;
    end_date: (string | null);
    created_at: string;
    is_draft?: boolean;
    teachers?: Array<TrainingSessionTeacherResponse>;
    students?: Array<TrainingSessionStudentResponse>;
};
export namespace TrainingSessionResponse {
    export enum track {
        EXAM = 'exam',
        START_DEUTSCH = 'start_deutsch',
    }
}

