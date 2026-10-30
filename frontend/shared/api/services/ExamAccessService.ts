/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccessCheckResponse } from '../models/AccessCheckResponse';
import type { ExamAccessResponse } from '../models/ExamAccessResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { UserLevelsResponse } from '../models/UserLevelsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ExamAccessService {
    /**
     * Get My Levels
     * Liste tous les levels accessibles de l'utilisateur connecté.
     * @param accessToken
     * @returns UserLevelsResponse Successful Response
     * @throws ApiError
     */
    public static getMyLevelsApiV1AccessMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<UserLevelsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/access/me',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Check Access
     * Vérifie si l'utilisateur a accès à un level.
     * Appelé avant le démarrage d'une session.
     * @param levelId
     * @param accessToken
     * @returns AccessCheckResponse Successful Response
     * @throws ApiError
     */
    public static checkAccessApiV1AccessCheckLevelIdGet(
        levelId: string,
        accessToken?: (string | null),
    ): CancelablePromise<AccessCheckResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/access/check/{level_id}',
            path: {
                'level_id': levelId,
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
     * Admin Grant Access
     * Accorde ou prolonge l'accès d'un utilisateur à un niveau, sans paiement.
     * @param userId
     * @param levelId
     * @param days Nombre de jours offerts. Omis = accès permanent.
     * @param accessToken
     * @returns ExamAccessResponse Successful Response
     * @throws ApiError
     */
    public static adminGrantAccessApiV1AccessAdminGrantPost(
        userId: string,
        levelId: string,
        days?: (number | null),
        accessToken?: (string | null),
    ): CancelablePromise<ExamAccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/access/admin/grant',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'user_id': userId,
                'level_id': levelId,
                'days': days,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Grant Sd Access
     * Accorde ou prolonge l'accès d'un utilisateur à Start Deutsch A1 ou A2, sans paiement.
     * @param userId
     * @param sdLevel
     * @param days Nombre de jours offerts. Omis = accès permanent.
     * @param accessToken
     * @returns ExamAccessResponse Successful Response
     * @throws ApiError
     */
    public static adminGrantSdAccessApiV1AccessAdminGrantSdPost(
        userId: string,
        sdLevel: 'A1' | 'A2',
        days?: (number | null),
        accessToken?: (string | null),
    ): CancelablePromise<ExamAccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/access/admin/grant-sd',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'user_id': userId,
                'sd_level': sdLevel,
                'days': days,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Revoke Sd Access
     * Révoque l'accès d'un utilisateur à Start Deutsch A1 ou A2.
     * @param userId
     * @param sdLevel
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static adminRevokeSdAccessApiV1AccessAdminRevokeSdDelete(
        userId: string,
        sdLevel: 'A1' | 'A2',
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/access/admin/revoke-sd',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'user_id': userId,
                'sd_level': sdLevel,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Revoke Access
     * Révoque l'accès d'un utilisateur à un level — admin uniquement.
     * @param userId
     * @param levelId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static adminRevokeAccessApiV1AccessAdminRevokeDelete(
        userId: string,
        levelId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/access/admin/revoke',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'user_id': userId,
                'level_id': levelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Get User Levels
     * Liste les levels accessibles d'un utilisateur — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns UserLevelsResponse Successful Response
     * @throws ApiError
     */
    public static adminGetUserLevelsApiV1AccessAdminUsersUserIdGet(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<UserLevelsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/access/admin/users/{user_id}',
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
     * Admin Grant All Levels
     * Donne accès à tous les levels actifs à un user.
     * Utile pour les tests ou les cas spéciaux.
     * @param userId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static adminGrantAllLevelsApiV1AccessAdminGrantAllUserIdPost(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/access/admin/grant-all/{user_id}',
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
