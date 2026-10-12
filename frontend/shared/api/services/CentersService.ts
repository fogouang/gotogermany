/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_my_logo_api_v1_centers_me_logo_post } from '../models/Body_upload_my_logo_api_v1_centers_me_logo_post';
import type { BranchCreateRequest } from '../models/BranchCreateRequest';
import type { BranchResponse } from '../models/BranchResponse';
import type { CenterCreateRequest } from '../models/CenterCreateRequest';
import type { CenterCreditPoolRechargeRequest } from '../models/CenterCreditPoolRechargeRequest';
import type { CenterCreditTransactionResponse } from '../models/CenterCreditTransactionResponse';
import type { CenterDefaultCreditsUpdateRequest } from '../models/CenterDefaultCreditsUpdateRequest';
import type { CenterPoolResponse } from '../models/CenterPoolResponse';
import type { CenterResponse } from '../models/CenterResponse';
import type { CenterUpdateRequest } from '../models/CenterUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CentersService {
    /**
     * Get My Center
     * @param accessToken
     * @returns CenterResponse Successful Response
     * @throws ApiError
     */
    public static getMyCenterApiV1CentersMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<CenterResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update My Center
     * @param requestBody
     * @param accessToken
     * @returns CenterResponse Successful Response
     * @throws ApiError
     */
    public static updateMyCenterApiV1CentersMePatch(
        requestBody: CenterUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CenterResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/centers/me',
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
     * List My Branches
     * @param accessToken
     * @returns BranchResponse Successful Response
     * @throws ApiError
     */
    public static listMyBranchesApiV1CentersMeBranchesGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<BranchResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me/branches',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create My Branch
     * @param requestBody
     * @param accessToken
     * @returns BranchResponse Successful Response
     * @throws ApiError
     */
    public static createMyBranchApiV1CentersMeBranchesPost(
        requestBody: BranchCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<BranchResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/me/branches',
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
     * Get My Center Pool
     * @param accessToken
     * @returns CenterPoolResponse Successful Response
     * @throws ApiError
     */
    public static getMyCenterPoolApiV1CentersMePoolGet(
        accessToken?: (string | null),
    ): CancelablePromise<CenterPoolResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me/pool',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Default Credits
     * @param requestBody
     * @param accessToken
     * @returns CenterPoolResponse Successful Response
     * @throws ApiError
     */
    public static updateDefaultCreditsApiV1CentersMeDefaultCreditsPatch(
        requestBody: CenterDefaultCreditsUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CenterPoolResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/centers/me/default-credits',
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
     * Get My Center Credit Transactions
     * @param accessToken
     * @returns CenterCreditTransactionResponse Successful Response
     * @throws ApiError
     */
    public static getMyCenterCreditTransactionsApiV1CentersMeCreditTransactionsGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<CenterCreditTransactionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me/credit-transactions',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Credit Transactions
     * @param accessToken
     * @returns CenterCreditTransactionResponse Successful Response
     * @throws ApiError
     */
    public static getMyCreditTransactionsApiV1CentersMeCreditTransactionsMineGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<CenterCreditTransactionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me/credit-transactions/mine',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload My Logo
     * Upload du logo du centre, affiché en en-tête des reçus PDF.
     * @param formData
     * @param accessToken
     * @returns CenterResponse Successful Response
     * @throws ApiError
     */
    public static uploadMyLogoApiV1CentersMeLogoPost(
        formData: Body_upload_my_logo_api_v1_centers_me_logo_post,
        accessToken?: (string | null),
    ): CancelablePromise<CenterResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/me/logo',
            cookies: {
                'access_token': accessToken,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Center
     * Créer un centre (crée aussi sa succursale principale).
     * @param requestBody
     * @param accessToken
     * @returns CenterResponse Successful Response
     * @throws ApiError
     */
    public static createCenterApiV1CentersPost(
        requestBody: CenterCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CenterResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers',
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
     * List Centers
     * @param skip
     * @param limit
     * @param accessToken
     * @returns CenterResponse Successful Response
     * @throws ApiError
     */
    public static listCentersApiV1CentersGet(
        skip?: number,
        limit: number = 100,
        accessToken?: (string | null),
    ): CancelablePromise<Array<CenterResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers',
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
     * Create Branch
     * @param centerId
     * @param requestBody
     * @param accessToken
     * @returns BranchResponse Successful Response
     * @throws ApiError
     */
    public static createBranchApiV1CentersCenterIdBranchesPost(
        centerId: string,
        requestBody: BranchCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<BranchResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/{center_id}/branches',
            path: {
                'center_id': centerId,
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
     * Toggle Center Active
     * @param centerId
     * @param accessToken
     * @returns CenterResponse Successful Response
     * @throws ApiError
     */
    public static toggleCenterActiveApiV1CentersCenterIdToggleActivePatch(
        centerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<CenterResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/centers/{center_id}/toggle-active',
            path: {
                'center_id': centerId,
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
     * Recharge Credit Pool
     * @param centerId
     * @param requestBody
     * @param accessToken
     * @returns CenterPoolResponse Successful Response
     * @throws ApiError
     */
    public static rechargeCreditPoolApiV1CentersCenterIdCreditPoolRechargePost(
        centerId: string,
        requestBody: CenterCreditPoolRechargeRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CenterPoolResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/{center_id}/credit-pool/recharge',
            path: {
                'center_id': centerId,
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
}
