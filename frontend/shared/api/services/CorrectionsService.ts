/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrectionRequest } from '../models/CorrectionRequest';
import type { CorrectionResponse } from '../models/CorrectionResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CorrectionsService {
    /**
     * Lancer la correction IA d'une session Schreiben
     * Lance la correction IA pour le module Schreiben d'une session d'examen. Si la correction existe déjà, elle est retournée sans rappeler l'IA.
     * @param requestBody
     * @param accessToken
     * @returns CorrectionResponse Successful Response
     * @throws ApiError
     */
    public static createCorrectionApiV1CorrectionsPost(
        requestBody: CorrectionRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CorrectionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/corrections/',
            cookies: {
                'access_token': accessToken,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Récupérer une correction par ID
     * @param correctionId
     * @param accessToken
     * @returns CorrectionResponse Successful Response
     * @throws ApiError
     */
    public static getCorrectionApiV1CorrectionsCorrectionIdGet(
        correctionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<CorrectionResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/corrections/{correction_id}',
            path: {
                'correction_id': correctionId,
            },
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Récupérer la correction d'une session
     * Retourne la correction existante pour cette session, ou null si elle n'a pas encore été corrigée.
     * @param sessionId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getCorrectionBySessionApiV1CorrectionsSessionSessionIdGet(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<(CorrectionResponse | null)> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/corrections/session/{session_id}',
            path: {
                'session_id': sessionId,
            },
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
