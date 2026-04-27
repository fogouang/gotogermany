/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SuccessResponse } from '../models/SuccessResponse';
import type { UserAdminResponse } from '../models/UserAdminResponse';
import type { UserChangePasswordRequest } from '../models/UserChangePasswordRequest';
import type { UserMeResponse } from '../models/UserMeResponse';
import type { UserUpdateRequest } from '../models/UserUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UsersService {
    /**
     * Get Me
     * Profil de l'utilisateur connecté.
     * @param accessToken
     * @returns UserMeResponse Successful Response
     * @throws ApiError
     */
    public static getMeApiV1UsersMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<UserMeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Me
     * Mise à jour du profil.
     * @param requestBody
     * @param accessToken
     * @returns UserMeResponse Successful Response
     * @throws ApiError
     */
    public static updateMeApiV1UsersMePatch(
        requestBody: UserUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<UserMeResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/me',
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
     * Change Password
     * Changement de mot de passe.
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static changePasswordApiV1UsersMeChangePasswordPost(
        requestBody: UserChangePasswordRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/me/change-password',
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
     * List Users
     * Liste tous les utilisateurs — admin uniquement.
     * @param skip
     * @param limit
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static listUsersApiV1UsersGet(
        skip?: number,
        limit: number = 100,
        accessToken?: (string | null),
    ): CancelablePromise<Array<UserAdminResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users',
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
     * Get User
     * Détail d'un utilisateur — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static getUserApiV1UsersUserIdGet(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<UserAdminResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{user_id}',
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
     * Delete User
     * Supprime un utilisateur — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteUserApiV1UsersUserIdDelete(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/users/{user_id}',
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
     * Toggle Active
     * Active ou désactive un compte — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static toggleActiveApiV1UsersUserIdToggleActivePatch(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<UserAdminResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/{user_id}/toggle-active',
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
