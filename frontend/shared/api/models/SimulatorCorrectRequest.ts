/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Le frontend envoie le sujet + les textes rédigés par le candidat.
 * task_texts est une liste ordonnée : [texte_teil1, texte_teil2, ...]
 */
export type SimulatorCorrectRequest = {
    subject_id: string;
    task_texts: Array<string>;
};

