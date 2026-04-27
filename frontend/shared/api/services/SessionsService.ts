/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActiveSessionResponse } from '../models/ActiveSessionResponse';
import type { AnswerSubmitRequest } from '../models/AnswerSubmitRequest';
import type { AnswerSubmitResponse } from '../models/AnswerSubmitResponse';
import type { BulkAnswerSubmitRequest } from '../models/BulkAnswerSubmitRequest';
import type { SessionListResponse } from '../models/SessionListResponse';
import type { SessionResultResponse } from '../models/SessionResultResponse';
import type { SessionStartRequest } from '../models/SessionStartRequest';
import type { SessionStartResponse } from '../models/SessionStartResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SessionsService {
    /**
     * Start Session
     * Démarre une session d'examen.
     * Retourne tout le contenu de l'exam (modules + teile + questions).
     * @param requestBody
     * @param accessToken
     * @returns SessionStartResponse Successful Response
     * @throws ApiError
     */
    public static startSessionApiV1SessionsPost(
        requestBody: SessionStartRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SessionStartResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sessions',
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
     * Get My Sessions
     * Liste toutes les sessions de l'utilisateur connecté.
     * @param skip
     * @param limit
     * @param accessToken
     * @returns SessionListResponse Successful Response
     * @throws ApiError
     */
    public static getMySessionsApiV1SessionsGet(
        skip?: number,
        limit: number = 20,
        accessToken?: (string | null),
    ): CancelablePromise<Array<SessionListResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sessions',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Active Session
     * Retourne la session IN_PROGRESS pour un exam donné.
     * Retourne null si aucune session active.
     * @param examId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getActiveSessionApiV1SessionsActiveGet(
        examId: string,
        accessToken?: (string | null),
    ): CancelablePromise<(ActiveSessionResponse | null)> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sessions/active',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'exam_id': examId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Submit Answer
     * Soumet une réponse à une question.
     * Peut être appelé plusieurs fois — upsert à chaque appel.
     * Pour les questions auto-correctable, retourne is_correct immédiatement.
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns AnswerSubmitResponse Successful Response
     * @throws ApiError
     */
    public static submitAnswerApiV1SessionsSessionIdAnswersPost(
        sessionId: string,
        requestBody: AnswerSubmitRequest,
        accessToken?: (string | null),
    ): CancelablePromise<AnswerSubmitResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sessions/{session_id}/answers',
            path: {
                'session_id': sessionId,
            },
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
     * Submit Bulk Answers
     * Soumission groupée — pour sauvegarder un Teil entier en une fois.
     * Utile avant timeout ou changement de module.
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns AnswerSubmitResponse Successful Response
     * @throws ApiError
     */
    public static submitBulkAnswersApiV1SessionsSessionIdAnswersBulkPost(
        sessionId: string,
        requestBody: BulkAnswerSubmitRequest,
        accessToken?: (string | null),
    ): CancelablePromise<Array<AnswerSubmitResponse>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sessions/{session_id}/answers/bulk',
            path: {
                'session_id': sessionId,
            },
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
     * Submit Session
     * Soumet la session complète.
     * Calcule le score final et retourne le résultat détaillé.
     * Status → COMPLETED ou PENDING_REVIEW si Schreiben/Sprechen présents.
     * @param sessionId
     * @param accessToken
     * @returns SessionResultResponse Successful Response
     * @throws ApiError
     */
    public static submitSessionApiV1SessionsSessionIdSubmitPost(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SessionResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sessions/{session_id}/submit',
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
    /**
     * Get Result
     * Consulte le résultat d'une session soumise.
     * Révèle les correct_answer pour chaque question.
     * @param sessionId
     * @param accessToken
     * @returns SessionResultResponse Successful Response
     * @throws ApiError
     */
    public static getResultApiV1SessionsSessionIdResultGet(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SessionResultResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sessions/{session_id}/result',
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
