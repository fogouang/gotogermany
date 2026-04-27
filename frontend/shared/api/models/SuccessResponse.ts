/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response standardisée pour succès
 *
 * Usage:
 * return SuccessResponse(
     * data=user,
     * message="User créé avec succès"
     * )
     */
    export type SuccessResponse = {
        /**
         * Indicateur de succès
         */
        success?: boolean;
        /**
         * Message optionnel
         */
        message?: (string | null);
        /**
         * Données de la réponse
         */
        data?: null;
    };

