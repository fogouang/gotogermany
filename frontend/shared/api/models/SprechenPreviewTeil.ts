/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Ce que l'élève a le droit de voir d'un Teil : jamais le matériel
 * de l'examinatrice (texte de B, présentation de Kandidat B...).
 */
export type SprechenPreviewTeil = {
    teil_number: number;
    name: string;
    format_type: string;
    instructions: string;
    duration_minutes: number;
    max_score?: (number | null);
    content_points?: Array<string>;
    themes?: (Record<string, any> | null);
    scenario?: (string | null);
    stimulus_people?: (Array<Record<string, string>> | null);
    stimulus_text?: (string | null);
};

