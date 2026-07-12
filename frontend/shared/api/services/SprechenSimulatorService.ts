/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionHistoryListResponse } from '../models/SessionHistoryListResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SprechenSimulatorService {
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
