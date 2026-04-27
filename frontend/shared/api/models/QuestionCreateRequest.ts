/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type QuestionCreateRequest = {
    question_number: number;
    question_type: string;
    content: Record<string, any>;
    correct_answer: Record<string, any>;
    points?: number;
    audio_file?: (string | null);
};

