/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Le frontend envoie uniquement l'ID de session.
 * Tout le reste (textes, provider, level, instructions) est récupéré en DB.
 */
export type CorrectionRequest = {
    exam_session_id: string;
};

