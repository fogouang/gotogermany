/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResolveIncidentRequest } from '../models/ResolveIncidentRequest';
import type { SecurityBlockResponse } from '../models/SecurityBlockResponse';
import type { SecurityIncidentResponse } from '../models/SecurityIncidentResponse';
import type { SecuritySummaryResponse } from '../models/SecuritySummaryResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SecurityService {
    /**
     * Summary
     * @param accessToken
     * @returns SecuritySummaryResponse Successful Response
     * @throws ApiError
     */
    public static summaryApiV1SecuritySummaryGet(
        accessToken?: (string | null),
    ): CancelablePromise<SecuritySummaryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/security/summary',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Incidents
     * @param status
     * @param limit
     * @param accessToken
     * @returns SecurityIncidentResponse Successful Response
     * @throws ApiError
     */
    public static listIncidentsApiV1SecurityIncidentsGet(
        status?: (string | null),
        limit: number = 100,
        accessToken?: (string | null),
    ): CancelablePromise<Array<SecurityIncidentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/security/incidents',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'status': status,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Incident
     * @param incidentId
     * @param accessToken
     * @returns SecurityIncidentResponse Successful Response
     * @throws ApiError
     */
    public static getIncidentApiV1SecurityIncidentsIncidentIdGet(
        incidentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SecurityIncidentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/security/incidents/{incident_id}',
            path: {
                'incident_id': incidentId,
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
     * Resolve Incident
     * @param incidentId
     * @param requestBody
     * @param accessToken
     * @returns SecurityIncidentResponse Successful Response
     * @throws ApiError
     */
    public static resolveIncidentApiV1SecurityIncidentsIncidentIdResolvePost(
        incidentId: string,
        requestBody: ResolveIncidentRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SecurityIncidentResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/security/incidents/{incident_id}/resolve',
            path: {
                'incident_id': incidentId,
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
     * List Blocks
     * @param accessToken
     * @returns SecurityBlockResponse Successful Response
     * @throws ApiError
     */
    public static listBlocksApiV1SecurityBlocksGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<SecurityBlockResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/security/blocks',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Unblock User
     * @param userId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static unblockUserApiV1SecurityUsersUserIdUnblockPost(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/security/users/{user_id}/unblock',
            path: {
                'user_id': userId,
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
     * Ban User
     * @param userId
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static banUserApiV1SecurityUsersUserIdBanPost(
        userId: string,
        requestBody: ResolveIncidentRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/security/users/{user_id}/ban',
            path: {
                'user_id': userId,
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
     * Evidence
     * @param userId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static evidenceApiV1SecurityUsersUserIdEvidenceGet(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/security/users/{user_id}/evidence',
            path: {
                'user_id': userId,
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
