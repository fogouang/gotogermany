/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubCriterionScore } from './SubCriterionScore';
/**
 * Feedback pour une tâche individuelle — même contrat que corrections/schemas.py.
 */
export type app__modules__schreiben_simulator__schemas__TaskFeedback = {
    key: string;
    label: string;
    corrected_text: string;
    main_strengths?: Array<string>;
    main_weaknesses?: Array<string>;
    score?: (number | null);
    max_score?: (number | null);
    sub_criteria?: (Array<SubCriterionScore> | null);
};

