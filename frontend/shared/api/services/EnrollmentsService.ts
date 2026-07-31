/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__modules__enrollments__schemas__PaymentResponse } from '../models/app__modules__enrollments__schemas__PaymentResponse';
import type { BalanceSummaryResponse } from '../models/BalanceSummaryResponse';
import type { CursusCreateRequest } from '../models/CursusCreateRequest';
import type { CursusResponse } from '../models/CursusResponse';
import type { LevelEnrollmentCreateRequest } from '../models/LevelEnrollmentCreateRequest';
import type { LevelEnrollmentResponse } from '../models/LevelEnrollmentResponse';
import type { PaymentCreateRequest } from '../models/PaymentCreateRequest';
import type { RevenueSummaryResponse } from '../models/RevenueSummaryResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EnrollmentsService {
    /**
     * List Cursus
     * Directeur : tous les cursus du centre. Secrétaire : uniquement sa branche.
     * @param accessToken
     * @returns CursusResponse Successful Response
     * @throws ApiError
     */
    public static listCursusApiV1EnrollmentsCursusGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<CursusResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/enrollments/cursus',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Cursus
     * @param requestBody
     * @param accessToken
     * @returns CursusResponse Successful Response
     * @throws ApiError
     */
    public static createCursusApiV1EnrollmentsCursusPost(
        requestBody: CursusCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CursusResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/enrollments/cursus',
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
     * Get Revenue Summary
     * Revenu total encaissé par le centre, ventilé par succursale — vue directeur.
     * @param accessToken
     * @returns RevenueSummaryResponse Successful Response
     * @throws ApiError
     */
    public static getRevenueSummaryApiV1EnrollmentsRevenueGet(
        accessToken?: (string | null),
    ): CancelablePromise<RevenueSummaryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/enrollments/revenue',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Level Enrollment
     * Le cursus doit appartenir au périmètre de l'appelant (centre, et branche
     * si secrétaire) — vérifié dans EnrollmentService.create_level_enrollment.
     * @param cursusId
     * @param requestBody
     * @param accessToken
     * @returns LevelEnrollmentResponse Successful Response
     * @throws ApiError
     */
    public static createLevelEnrollmentApiV1EnrollmentsCursusCursusIdLevelsPost(
        cursusId: string,
        requestBody: LevelEnrollmentCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<LevelEnrollmentResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/enrollments/cursus/{cursus_id}/levels',
            path: {
                'cursus_id': cursusId,
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
     * Record Payment
     * Refuse un paiement de type 'formation' tant que les frais d'inscription
     * ne sont pas soldés (règle appliquée dans EnrollmentService.record_payment).
     * @param enrollmentId
     * @param requestBody
     * @param accessToken
     * @returns app__modules__enrollments__schemas__PaymentResponse Successful Response
     * @throws ApiError
     */
    public static recordPaymentApiV1EnrollmentsLevelsEnrollmentIdPaymentsPost(
        enrollmentId: string,
        requestBody: PaymentCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<app__modules__enrollments__schemas__PaymentResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/enrollments/levels/{enrollment_id}/payments',
            path: {
                'enrollment_id': enrollmentId,
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
     * List Payments
     * Historique complet des paiements d'un niveau, avec leurs reçus PDF.
     * @param enrollmentId
     * @param accessToken
     * @returns app__modules__enrollments__schemas__PaymentResponse Successful Response
     * @throws ApiError
     */
    public static listPaymentsApiV1EnrollmentsLevelsEnrollmentIdPaymentsGet(
        enrollmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<app__modules__enrollments__schemas__PaymentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/enrollments/levels/{enrollment_id}/payments',
            path: {
                'enrollment_id': enrollmentId,
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
     * Get Balance
     * @param enrollmentId
     * @param accessToken
     * @returns BalanceSummaryResponse Successful Response
     * @throws ApiError
     */
    public static getBalanceApiV1EnrollmentsLevelsEnrollmentIdPaymentsBalanceGet(
        enrollmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<BalanceSummaryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/enrollments/levels/{enrollment_id}/payments/balance',
            path: {
                'enrollment_id': enrollmentId,
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
