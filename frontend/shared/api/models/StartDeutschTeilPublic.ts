/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschQuestionPublic } from './StartDeutschQuestionPublic';
/**
 * Un Teil côté étudiant : les questions n'ont pas de correct_answer.
 */
export type StartDeutschTeilPublic = {
    id: string;
    teil_number: number;
    format_type: string;
    instructions: (string | null);
    audio_file: (string | null);
    max_score: number;
    shared_content?: (Record<string, any> | null);
    questions?: Array<StartDeutschQuestionPublic>;
};

