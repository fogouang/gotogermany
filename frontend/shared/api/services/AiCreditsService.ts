/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreditPurchaseRequest } from '../models/CreditPurchaseRequest';
import type { ManualCreditGrantRequest } from '../models/ManualCreditGrantRequest';
import type { SuccessResponse_CreditBalanceResponse_ } from '../models/SuccessResponse_CreditBalanceResponse_';
import type { SuccessResponse_CreditPricingResponse_ } from '../models/SuccessResponse_CreditPricingResponse_';
import type { SuccessResponse_CreditPurchaseHistoryResponse_ } from '../models/SuccessResponse_CreditPurchaseHistoryResponse_';
import type { SuccessResponse_CreditPurchaseResponse_ } from '../models/SuccessResponse_CreditPurchaseResponse_';
import type { SuccessResponse_list_CreditPurchaseHistoryItem__ } from '../models/SuccessResponse_list_CreditPurchaseHistoryItem__';
import type { SuccessResponse_ManualCreditGrantResponse_ } from '../models/SuccessResponse_ManualCreditGrantResponse_';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AiCreditsService {
    /**
     * Get Pricing
     * @returns SuccessResponse_CreditPricingResponse_ Successful Response
     * @throws ApiError
     */
    public static getPricingApiV1AiCreditsPricingGet(): CancelablePromise<SuccessResponse_CreditPricingResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ai-credits/pricing',
        });
    }
    /**
     * Get Balance
     * @param accessToken
     * @returns SuccessResponse_CreditBalanceResponse_ Successful Response
     * @throws ApiError
     */
    public static getBalanceApiV1AiCreditsBalanceGet(
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse_CreditBalanceResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ai-credits/balance',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Purchase Credits
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse_CreditPurchaseResponse_ Successful Response
     * @throws ApiError
     */
    public static purchaseCreditsApiV1AiCreditsPurchasePost(
        requestBody: CreditPurchaseRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse_CreditPurchaseResponse_> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ai-credits/purchase',
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
     * Get History
     * @param accessToken
     * @returns SuccessResponse_CreditPurchaseHistoryResponse_ Successful Response
     * @throws ApiError
     */
    public static getHistoryApiV1AiCreditsHistoryGet(
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse_CreditPurchaseHistoryResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ai-credits/history',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Grant
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse_ManualCreditGrantResponse_ Successful Response
     * @throws ApiError
     */
    public static adminGrantApiV1AiCreditsAdminGrantPost(
        requestBody: ManualCreditGrantRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse_ManualCreditGrantResponse_> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ai-credits/admin/grant',
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
     * [Admin] Historique des crédits accordés manuellement
     * Liste tous les crédits IA accordés manuellement (operator=MANUAL).
     * Utilisé dans la page admin/paiements-manuels.
     * @param limit
     * @param accessToken
     * @returns SuccessResponse_list_CreditPurchaseHistoryItem__ Successful Response
     * @throws ApiError
     */
    public static adminHistoryApiV1AiCreditsAdminHistoryGet(
        limit: number = 20,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse_list_CreditPurchaseHistoryItem__> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ai-credits/admin/history',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
