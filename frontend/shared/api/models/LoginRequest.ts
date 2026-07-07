/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type LoginRequest = {
    email: string;
    password: string;
    /**
     * Identifiant stable de l'appareil, généré côté client (ex: FingerprintJS ou UUID stocké localement).
     */
    device_fingerprint?: (string | null);
};

