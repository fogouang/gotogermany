/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PromoCodeCreateRequest } from '../models/PromoCodeCreateRequest';
import type { PromoCodeResponse } from '../models/PromoCodeResponse';
import type { PromoCodeUpdateRequest } from '../models/PromoCodeUpdateRequest';
import type { PromoCodeValidateRequest } from '../models/PromoCodeValidateRequest';
import type { PromoCodeValidateResponse } from '../models/PromoCodeValidateResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PromoCodesService {
    /**
     * Validate Promo Code
     * Valide un code promo et retourne la réduction applicable.
     * Appelé depuis le frontend avant de confirmer le paiement.
     * @param requestBody
     * @param accessToken
     * @returns PromoCodeValidateResponse Successful Response
     * @throws ApiError
     */
    public static validatePromoCodeApiV1PromoCodesValidatePost(
        requestBody: PromoCodeValidateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<PromoCodeValidateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/promo-codes/validate',
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
     * List Promo Codes
     * Liste tous les codes promo — admin uniquement.
     * @param accessToken
     * @returns PromoCodeResponse Successful Response
     * @throws ApiError
     */
    public static listPromoCodesApiV1PromoCodesGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<PromoCodeResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/promo-codes',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Promo Code
     * @param requestBody
     * @param accessToken
     * @returns PromoCodeResponse Successful Response
     * @throws ApiError
     */
    public static createPromoCodeApiV1PromoCodesPost(
        requestBody: PromoCodeCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<PromoCodeResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/promo-codes',
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
     * Get Promo Code
     * @param codeId
     * @param accessToken
     * @returns PromoCodeResponse Successful Response
     * @throws ApiError
     */
    public static getPromoCodeApiV1PromoCodesCodeIdGet(
        codeId: string,
        accessToken?: (string | null),
    ): CancelablePromise<PromoCodeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/promo-codes/{code_id}',
            path: {
                'code_id': codeId,
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
     * Update Promo Code
     * @param codeId
     * @param requestBody
     * @param accessToken
     * @returns PromoCodeResponse Successful Response
     * @throws ApiError
     */
    public static updatePromoCodeApiV1PromoCodesCodeIdPatch(
        codeId: string,
        requestBody: PromoCodeUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<PromoCodeResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/promo-codes/{code_id}',
            path: {
                'code_id': codeId,
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
     * Delete Promo Code
     * @param codeId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deletePromoCodeApiV1PromoCodesCodeIdDelete(
        codeId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/promo-codes/{code_id}',
            path: {
                'code_id': codeId,
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
