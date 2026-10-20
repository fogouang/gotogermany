/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StudentModuleScore } from './StudentModuleScore';
/**
 * Relevé de points façon certificat : modules et total, jamais les réponses.
 */
export type StudentScoreSheet = {
    modules: Array<StudentModuleScore>;
    total_points: number;
    total_max: number;
    is_final: boolean;
    passed: (boolean | null);
};

