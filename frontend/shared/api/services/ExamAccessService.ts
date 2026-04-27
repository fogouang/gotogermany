/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccessCheckResponse } from '../models/AccessCheckResponse';
import type { ExamAccessResponse } from '../models/ExamAccessResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { UserExamsResponse } from '../models/UserExamsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ExamAccessService {
    /**
     * Get My Exams
     * Liste tous les examens accessibles de l'utilisateur connecté.
     * @param accessToken
     * @returns UserExamsResponse Successful Response
     * @throws ApiError
     */
    public static getMyExamsApiV1AccessMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<UserExamsResponse> {
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
     * Vérifie si l'utilisateur a accès à un exam.
     * Appelé avant le démarrage d'une session.
     * @param examId
     * @param accessToken
     * @returns AccessCheckResponse Successful Response
     * @throws ApiError
     */
    public static checkAccessApiV1AccessCheckExamIdGet(
        examId: string,
        accessToken?: (string | null),
    ): CancelablePromise<AccessCheckResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/access/check/{exam_id}',
            path: {
                'exam_id': examId,
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
     * Accorde manuellement un accès à un utilisateur — admin uniquement.
     * Utile pour les tests et les cas spéciaux.
     * @param userId
     * @param examId
     * @param accessToken
     * @returns ExamAccessResponse Successful Response
     * @throws ApiError
     */
    public static adminGrantAccessApiV1AccessAdminGrantPost(
        userId: string,
        examId: string,
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
                'exam_id': examId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Revoke Access
     * Révoque l'accès d'un utilisateur à un exam — admin uniquement.
     * @param userId
     * @param examId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static adminRevokeAccessApiV1AccessAdminRevokeDelete(
        userId: string,
        examId: string,
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
                'exam_id': examId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Get User Exams
     * Liste les examens accessibles d'un utilisateur — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns UserExamsResponse Successful Response
     * @throws ApiError
     */
    public static adminGetUserExamsApiV1AccessAdminUsersUserIdGet(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<UserExamsResponse> {
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
}
