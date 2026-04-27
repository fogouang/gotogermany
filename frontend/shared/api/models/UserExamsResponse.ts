/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ExamAccessWithExamResponse } from './ExamAccessWithExamResponse';
/**
 * Tous les examens d'un user avec leur statut d'accès.
 * Retourné par GET /users/me/exams.
 */
export type UserExamsResponse = {
    free_exams?: Array<ExamAccessWithExamResponse>;
    paid_exams?: Array<ExamAccessWithExamResponse>;
    total: number;
};

