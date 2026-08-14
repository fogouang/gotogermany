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
    level_id: string;
    level_name: string;
    label: (string | null);
    start_date: string;
    end_date: (string | null);
    created_at: string;
    teachers?: Array<TrainingSessionTeacherResponse>;
    students?: Array<TrainingSessionStudentResponse>;
};

