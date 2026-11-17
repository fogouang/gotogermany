/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Le frontend envoie le sujet + les textes rédigés par le candidat.
 * task_texts est une liste ordonnée : [texte_teil1, texte_teil2, ...]
 * task_choices (optionnel, même ordre) : choix du candidat pour les sujets à options,
 * ex. [{"theme": "A"}, {"variant": "1"}, {}]. Vide = l'IA identifie l'option au texte.
 */
export type SimulatorCorrectRequest = {
    subject_id: string;
    task_texts: Array<string>;
    task_choices?: Array<Record<string, string>>;
};

