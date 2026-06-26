/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ExamAccessWithLevelResponse } from './ExamAccessWithLevelResponse';
/**
 * Tous les levels payants accessibles d'un user.
 * Les 3 premiers sujets de chaque level sont libres par défaut
 * et ne figurent pas ici — ils sont gérés côté backend.
 */
export type UserLevelsResponse = {
    paid_levels?: Array<ExamAccessWithLevelResponse>;
    total: number;
};

