/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Une question sans son correct_answer — c'est ce que l'étudiant reçoit pendant la session.
 */
export type StartDeutschQuestionPublic = {
    id: string;
    question_number: number;
    content: Record<string, any>;
    points: number;
    image_file: (string | null);
};

