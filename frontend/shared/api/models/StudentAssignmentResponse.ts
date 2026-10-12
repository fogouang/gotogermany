/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Vue élève : uniquement la note finale, jamais le détail.
 */
export type StudentAssignmentResponse = {
    id: string;
    title: string;
    instructions: (string | null);
    exam_name: string;
    cefr_code: string;
    teacher_name: string;
    due_at: (string | null);
    is_late: boolean;
    status: string;
    final_score: (number | null);
};

