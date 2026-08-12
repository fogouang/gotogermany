/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StartDeutschModulePublic } from './StartDeutschModulePublic';
/**
 * Version complète avec l'arbre Module → Teil → Question, pour démarrer une session.
 */
export type StartDeutschSubjectDetail = {
    id: string;
    level: string;
    subject_number: number;
    title: string;
    description: (string | null);
    is_active: boolean;
    modules?: Array<StartDeutschModulePublic>;
};

