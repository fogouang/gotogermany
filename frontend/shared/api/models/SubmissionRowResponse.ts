/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SubmissionRowResponse = {
    student_id: string;
    student_name: string;
    status: string;
    exam_session_id: (string | null);
    sd_session_id?: (string | null);
    started_at: (string | null);
    submitted_at: (string | null);
    graded_at: (string | null);
    is_late: boolean;
    score_breakdown: (Record<string, any> | null);
    final_score: (number | null);
    has_annotated_file: boolean;
};

