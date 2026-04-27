/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Vue admin — inclut correct_answer pour vérification et import.
 */
export type QuestionAdminResponse = {
    id: string;
    teil_id: string;
    question_number: number;
    question_type: string;
    content: Record<string, any>;
    points: number;
    audio_file: (string | null);
    correct_answer: Record<string, any>;
};

