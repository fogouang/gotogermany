/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SchreibenSubjectCreate } from '../models/SchreibenSubjectCreate';
import type { SchreibenSubjectResponse } from '../models/SchreibenSubjectResponse';
import type { SchreibenSubjectUpdate } from '../models/SchreibenSubjectUpdate';
import type { SimulatorCorrectRequest } from '../models/SimulatorCorrectRequest';
import type { SimulatorCorrectResponse } from '../models/SimulatorCorrectResponse';
import type { SimulatorResultResponse } from '../models/SimulatorResultResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SchreibenSimulatorService {
    /**
     * List Subjects
     * Liste les sujets simulateur actifs, avec filtres optionnels.
     * @param provider Filtrer par provider (telc, goethe, osd)
     * @param level Filtrer par niveau (b1, b2)
     * @param accessToken
     * @returns SchreibenSubjectResponse Successful Response
     * @throws ApiError
     */
    public static listSubjectsApiV1SchreibenSimulatorGet(
        provider?: (string | null),
        level?: (string | null),
        accessToken?: (string | null),
    ): CancelablePromise<Array<SchreibenSubjectResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/schreiben-simulator',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'provider': provider,
                'level': level,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Subject
     * Admin : crée un nouveau sujet simulateur.
     * @param requestBody
     * @param accessToken
     * @returns SchreibenSubjectResponse Successful Response
     * @throws ApiError
     */
    public static createSubjectApiV1SchreibenSimulatorPost(
        requestBody: SchreibenSubjectCreate,
        accessToken?: (string | null),
    ): CancelablePromise<SchreibenSubjectResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/schreiben-simulator',
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
     * Get Subject
     * Récupère un sujet simulateur par son ID.
     * @param subjectId
     * @param accessToken
     * @returns SchreibenSubjectResponse Successful Response
     * @throws ApiError
     */
    public static getSubjectApiV1SchreibenSimulatorSubjectIdGet(
        subjectId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SchreibenSubjectResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/schreiben-simulator/{subject_id}',
            path: {
                'subject_id': subjectId,
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
     * Update Subject
     * Admin : met à jour un sujet simulateur.
     * @param subjectId
     * @param requestBody
     * @param accessToken
     * @returns SchreibenSubjectResponse Successful Response
     * @throws ApiError
     */
    public static updateSubjectApiV1SchreibenSimulatorSubjectIdPatch(
        subjectId: string,
        requestBody: SchreibenSubjectUpdate,
        accessToken?: (string | null),
    ): CancelablePromise<SchreibenSubjectResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/schreiben-simulator/{subject_id}',
            path: {
                'subject_id': subjectId,
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
     * Delete Subject
     * Admin : supprime un sujet simulateur.
     * @param subjectId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteSubjectApiV1SchreibenSimulatorSubjectIdDelete(
        subjectId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/schreiben-simulator/{subject_id}',
            path: {
                'subject_id': subjectId,
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
     * Correct Submission
     * Lance la correction IA d'un sujet simulateur.
     * Le candidat envoie subject_id + ses textes rédigés (task_texts).
     * @param requestBody
     * @param accessToken
     * @returns SimulatorCorrectResponse Successful Response
     * @throws ApiError
     */
    public static correctSubmissionApiV1SchreibenSimulatorCorrectPost(
        requestBody: SimulatorCorrectRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SimulatorCorrectResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/schreiben-simulator/correct',
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
     * My Results
     * Historique des corrections simulateur de l'utilisateur connecté.
     * @param accessToken
     * @returns SimulatorResultResponse Successful Response
     * @throws ApiError
     */
    public static myResultsApiV1SchreibenSimulatorMyResultsGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<SimulatorResultResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/schreiben-simulator/my/results',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List All Subjects
     * Admin : liste tous les sujets (y compris inactifs).
     * @param provider
     * @param level
     * @param activeOnly
     * @param accessToken
     * @returns SchreibenSubjectResponse Successful Response
     * @throws ApiError
     */
    public static listAllSubjectsApiV1SchreibenSimulatorAdminAllGet(
        provider?: (string | null),
        level?: (string | null),
        activeOnly: boolean = false,
        accessToken?: (string | null),
    ): CancelablePromise<Array<SchreibenSubjectResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/schreiben-simulator/admin/all',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'provider': provider,
                'level': level,
                'active_only': activeOnly,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
