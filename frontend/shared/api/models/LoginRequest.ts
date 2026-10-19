/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Connexion par numéro de téléphone (ou email, pour les comptes existants).
 */
export type LoginRequest = {
    /**
     * Numéro de téléphone ou email
     */
    identifier?: (string | null);
    email?: (string | null);
    password: string;
    /**
     * Identifiant stable de l'appareil, généré côté client (ex: FingerprintJS ou UUID stocké localement).
     */
    device_fingerprint?: (string | null);
};

