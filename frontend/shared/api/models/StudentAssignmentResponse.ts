/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StudentScoreSheet } from './StudentScoreSheet';
/**
 * Vue élève : uniquement la note finale, jamais le détail.
 */
export type StudentAssignmentResponse = {
    id: string;
    kind?: StudentAssignmentResponse.kind;
    title: string;
    instructions: (string | null);
    exam_name: string;
    cefr_code: string;
    teacher_name: string;
    due_at: (string | null);
    is_late: boolean;
    status: string;
    final_score: (number | null);
    score_sheet?: (StudentScoreSheet | null);
};
export namespace StudentAssignmentResponse {
    export enum kind {
        EXAM = 'exam',
        START_DEUTSCH = 'start_deutsch',
    }
}

