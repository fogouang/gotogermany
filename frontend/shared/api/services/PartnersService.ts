/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PartnerCreateRequest } from '../models/PartnerCreateRequest';
import type { PartnerDetailResponse } from '../models/PartnerDetailResponse';
import type { PartnerStatsResponse } from '../models/PartnerStatsResponse';
import type { PartnerUpdateRequest } from '../models/PartnerUpdateRequest';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PartnersService {
    /**
     * List Partners
     * Liste tous les partenaires — admin uniquement.
     * @param accessToken
     * @returns PartnerDetailResponse Successful Response
     * @throws ApiError
     */
    public static listPartnersApiV1PartnersGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<PartnerDetailResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/partners',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Partner
     * @param requestBody
     * @param accessToken
     * @returns PartnerDetailResponse Successful Response
     * @throws ApiError
     */
    public static createPartnerApiV1PartnersPost(
        requestBody: PartnerCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<PartnerDetailResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/partners',
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
     * Get Partner
     * @param partnerId
     * @param accessToken
     * @returns PartnerDetailResponse Successful Response
     * @throws ApiError
     */
    public static getPartnerApiV1PartnersPartnerIdGet(
        partnerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<PartnerDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/partners/{partner_id}',
            path: {
                'partner_id': partnerId,
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
     * Update Partner
     * @param partnerId
     * @param requestBody
     * @param accessToken
     * @returns PartnerDetailResponse Successful Response
     * @throws ApiError
     */
    public static updatePartnerApiV1PartnersPartnerIdPatch(
        partnerId: string,
        requestBody: PartnerUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<PartnerDetailResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/partners/{partner_id}',
            path: {
                'partner_id': partnerId,
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
     * Delete Partner
     * @param partnerId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deletePartnerApiV1PartnersPartnerIdDelete(
        partnerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/partners/{partner_id}',
            path: {
                'partner_id': partnerId,
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
     * Get Partner Stats
     * Stats codes + utilisations + commissions dues.
     * @param partnerId
     * @param accessToken
     * @returns PartnerStatsResponse Successful Response
     * @throws ApiError
     */
    public static getPartnerStatsApiV1PartnersPartnerIdStatsGet(
        partnerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<PartnerStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/partners/{partner_id}/stats',
            path: {
                'partner_id': partnerId,
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
