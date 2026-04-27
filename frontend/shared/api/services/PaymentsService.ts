/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaymentInitiateRequest } from '../models/PaymentInitiateRequest';
import type { PaymentInitiateResponse } from '../models/PaymentInitiateResponse';
import type { PaymentResponse } from '../models/PaymentResponse';
import type { PaymentStatusResponse } from '../models/PaymentStatusResponse';
import type { PaymentSummaryResponse } from '../models/PaymentSummaryResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PaymentsService {
    /**
     * Initiate Payment
     * Initie un paiement mobile money pour l'accès à un exam.
     *
     * - `exam_id` : l'exam que l'étudiant veut débloquer
     * - `plan_id` : durée choisie (7j, 1 mois, 3 mois…)
     * - `operator` : "MTN" | "ORANGE"
     * - `phone_number` : numéro mobile money
     * - `promo_code` : code partenaire optionnel
     *
     * Retourne un code USSD à composer sur le téléphone.
     * @param requestBody
     * @param accessToken
     * @returns PaymentInitiateResponse Successful Response
     * @throws ApiError
     */
    public static initiatePaymentApiV1PaymentsPost(
        requestBody: PaymentInitiateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<PaymentInitiateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/payments',
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
     * Get Payment Status
     * Polling statut d'un paiement.
     * Appelé toutes les 5s par le frontend jusqu'à COMPLETED ou FAILED.
     * Retourne aussi `exam_access_granted` pour savoir si l'accès est actif.
     * @param transactionReference
     * @param accessToken
     * @returns PaymentStatusResponse Successful Response
     * @throws ApiError
     */
    public static getPaymentStatusApiV1PaymentsStatusTransactionReferenceGet(
        transactionReference: string,
        accessToken?: (string | null),
    ): CancelablePromise<PaymentStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/payments/status/{transaction_reference}',
            path: {
                'transaction_reference': transactionReference,
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
     * Get My Payments
     * Historique des paiements de l'utilisateur connecté.
     * @param accessToken
     * @returns PaymentResponse Successful Response
     * @throws ApiError
     */
    public static getMyPaymentsApiV1PaymentsMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<PaymentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/payments/me',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Payment
     * Détail d'un paiement.
     * @param paymentId
     * @param accessToken
     * @returns PaymentResponse Successful Response
     * @throws ApiError
     */
    public static getPaymentApiV1PaymentsPaymentIdGet(
        paymentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<PaymentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/payments/{payment_id}',
            path: {
                'payment_id': paymentId,
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
     * Get Summary
     * Stats paiements — admin uniquement.
     * @param accessToken
     * @returns PaymentSummaryResponse Successful Response
     * @throws ApiError
     */
    public static getSummaryApiV1PaymentsAdminSummaryGet(
        accessToken?: (string | null),
    ): CancelablePromise<PaymentSummaryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/payments/admin/summary',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
