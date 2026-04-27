/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Vue étudiant — correct_answer exclu.
 * Le frontend affiche le contenu et collecte la réponse.
 */
export type QuestionResponse = {
    id: string;
    teil_id: string;
    question_number: number;
    question_type: string;
    content: Record<string, any>;
    points: number;
    audio_file: (string | null);
};

