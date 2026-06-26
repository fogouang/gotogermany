/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SettingsService {
    /**
     * Get Free Access Mode
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getFreeAccessModeApiV1SettingsFreeAccessGet(
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/settings/free-access',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Toggle Free Access Mode
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static toggleFreeAccessModeApiV1SettingsFreeAccessTogglePost(
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/settings/free-access/toggle',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
