/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PlanCreate } from '../models/PlanCreate';
import type { PlanResponse } from '../models/PlanResponse';
import type { PlanUpdate } from '../models/PlanUpdate';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PlansService {
    /**
     * Get Plans
     * Liste les plans actifs — accessible sans auth pour la page tarifs.
     * @returns PlanResponse Successful Response
     * @throws ApiError
     */
    public static getPlansApiV1PlansGet(): CancelablePromise<Array<PlanResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/plans',
        });
    }
    /**
     * Create Plan
     * @param requestBody
     * @param accessToken
     * @returns PlanResponse Successful Response
     * @throws ApiError
     */
    public static createPlanApiV1PlansPost(
        requestBody: PlanCreate,
        accessToken?: (string | null),
    ): CancelablePromise<PlanResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/plans',
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
     * Get Plan
     * @param planId
     * @returns PlanResponse Successful Response
     * @throws ApiError
     */
    public static getPlanApiV1PlansPlanIdGet(
        planId: string,
    ): CancelablePromise<PlanResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/plans/{plan_id}',
            path: {
                'plan_id': planId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Plan
     * @param planId
     * @param requestBody
     * @param accessToken
     * @returns PlanResponse Successful Response
     * @throws ApiError
     */
    public static updatePlanApiV1PlansPlanIdPatch(
        planId: string,
        requestBody: PlanUpdate,
        accessToken?: (string | null),
    ): CancelablePromise<PlanResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/plans/{plan_id}',
            path: {
                'plan_id': planId,
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
     * Delete Plan
     * @param planId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deletePlanApiV1PlansPlanIdDelete(
        planId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/plans/{plan_id}',
            path: {
                'plan_id': planId,
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
