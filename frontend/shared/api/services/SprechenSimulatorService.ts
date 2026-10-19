/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionHistoryListResponse } from '../models/SessionHistoryListResponse';
import type { SprechenPreviewResponse } from '../models/SprechenPreviewResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SprechenSimulatorService {
    /**
     * Get Sprechen Preview
     * Même traitement que l'écran de préparation (build_teil_configs) :
     * l'élève voit exactement ce qu'il aura en préparation, jamais le
     * matériel de l'examinatrice.
     * @param subjectId
     * @param accessToken
     * @returns SprechenPreviewResponse Successful Response
     * @throws ApiError
     */
    public static getSprechenPreviewApiV1SprechenSimulatorSubjectsSubjectIdPreviewGet(
        subjectId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SprechenPreviewResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sprechen-simulator/subjects/{subject_id}/preview',
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
     * Get Sprechen History
     * @param provider
     * @param level
     * @param limit
     * @param offset
     * @param accessToken
     * @returns SessionHistoryListResponse Successful Response
     * @throws ApiError
     */
    public static getSprechenHistoryApiV1SprechenSimulatorHistoryGet(
        provider?: (string | null),
        level?: (string | null),
        limit: number = 20,
        offset?: number,
        accessToken?: (string | null),
    ): CancelablePromise<SessionHistoryListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sprechen-simulator/history',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'provider': provider,
                'level': level,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
