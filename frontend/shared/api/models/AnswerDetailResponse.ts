/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AnswerDetailResponse = {
    question_id: string;
    question_number: number;
    question_type: string;
    user_answer: Record<string, any>;
    correct_answer: (Record<string, any> | null);
    is_correct: (boolean | null);
    score_obtained: (number | null);
    points_possible: number;
    feedback: (Record<string, any> | null);
    corrected_at: (string | null);
};

