/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BranchCreateRequest } from '../models/BranchCreateRequest';
import type { BranchResponse } from '../models/BranchResponse';
import type { CenterCreateRequest } from '../models/CenterCreateRequest';
import type { CenterLicenseActivateRequest } from '../models/CenterLicenseActivateRequest';
import type { CenterLicenseExtendRequest } from '../models/CenterLicenseExtendRequest';
import type { CenterLicenseResponse } from '../models/CenterLicenseResponse';
import type { CenterResponse } from '../models/CenterResponse';
import type { LicenseFormulaCreateRequest } from '../models/LicenseFormulaCreateRequest';
import type { LicenseFormulaResponse } from '../models/LicenseFormulaResponse';
import type { LicenseUsageResponse } from '../models/LicenseUsageResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CentersService {
    /**
     * Create Center
     * Créer un centre — crée aussi sa branch principale automatiquement.
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
     * Liste tous les centres — admin ITIA.
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
     * List Formulas
     * Liste les formules de licence actives — admin ITIA.
     * @param accessToken
     * @returns LicenseFormulaResponse Successful Response
     * @throws ApiError
     */
    public static listFormulasApiV1CentersFormulasGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<LicenseFormulaResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/formulas',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Formula
     * Créer une formule de licence (durée × plafond).
     * @param requestBody
     * @param accessToken
     * @returns LicenseFormulaResponse Successful Response
     * @throws ApiError
     */
    public static createFormulaApiV1CentersFormulasPost(
        requestBody: LicenseFormulaCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<LicenseFormulaResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/formulas',
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
     * Liste les succursales du centre du directeur connecté.
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
     * Le directeur crée une succursale supplémentaire pour son propre centre.
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
     * Create Branch
     * Créer une succursale supplémentaire — admin ITIA.
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
     * Activate License
     * Activer une licence pour un centre — après confirmation du paiement.
     * @param centerId
     * @param requestBody
     * @param accessToken
     * @returns CenterLicenseResponse Successful Response
     * @throws ApiError
     */
    public static activateLicenseApiV1CentersCenterIdLicenseActivatePost(
        centerId: string,
        requestBody: CenterLicenseActivateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CenterLicenseResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/{center_id}/license/activate',
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
     * Extend License
     * Étendre le quota d'une licence active — prorata jusqu'à la fin existante.
     * @param centerId
     * @param requestBody
     * @param accessToken
     * @returns CenterLicenseResponse Successful Response
     * @throws ApiError
     */
    public static extendLicenseApiV1CentersCenterIdLicenseExtendPost(
        centerId: string,
        requestBody: CenterLicenseExtendRequest,
        accessToken?: (string | null),
    ): CancelablePromise<CenterLicenseResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/centers/{center_id}/license/extend',
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
     * Get License Certificate Admin
     * Génère et retourne l'attestation PDF de la licence active du centre — admin ITIA.
     * @param centerId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getLicenseCertificateAdminApiV1CentersCenterIdLicenseCertificateGet(
        centerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/{center_id}/license/certificate',
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
     * Get My License Certificate
     * Le directeur génère/télécharge l'attestation de la licence active de son propre centre.
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMyLicenseCertificateApiV1CentersMeLicenseCertificateGet(
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me/license/certificate',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Center Usage
     * Vue consolidée pour le panel directeur : quota, jours restants, répartition par succursale.
     * @param accessToken
     * @returns LicenseUsageResponse Successful Response
     * @throws ApiError
     */
    public static getMyCenterUsageApiV1CentersMeUsageGet(
        accessToken?: (string | null),
    ): CancelablePromise<LicenseUsageResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/centers/me/usage',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
