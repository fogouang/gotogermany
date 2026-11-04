/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InvoiceResponse } from '../models/InvoiceResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class InvoicesService {
    /**
     * Generate Invoice
     * Marque le reçu comme disponible (le PDF est généré au téléchargement).
     * @param paymentId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static generateInvoiceApiV1InvoicesGeneratePaymentIdPost(
        paymentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/invoices/generate/{payment_id}',
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
     * Get Invoice
     * Détails de la facture d'un paiement.
     * @param paymentId
     * @param accessToken
     * @returns InvoiceResponse Successful Response
     * @throws ApiError
     */
    public static getInvoiceApiV1InvoicesPaymentPaymentIdGet(
        paymentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<InvoiceResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/invoices/payment/{payment_id}',
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
     * Download Invoice Pdf
     * Reçu PDF généré à la volée : rien n'est stocké sur le serveur.
     * Réservé à l'élève qui a payé et aux admins.
     * @param paymentId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadInvoicePdfApiV1InvoicesPaymentIdPdfGet(
        paymentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/invoices/{payment_id}/pdf',
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
}
