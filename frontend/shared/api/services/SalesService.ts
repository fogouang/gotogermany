/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivationRequest } from '../models/ActivationRequest';
import type { ActivationResponse } from '../models/ActivationResponse';
import type { CommissionRuleCreate } from '../models/CommissionRuleCreate';
import type { CommissionRuleResponse } from '../models/CommissionRuleResponse';
import type { CommissionRuleUpdate } from '../models/CommissionRuleUpdate';
import type { PartnerSaleResponse } from '../models/PartnerSaleResponse';
import type { PartnerSettingsUpdate } from '../models/PartnerSettingsUpdate';
import type { PartnerSummaryResponse } from '../models/PartnerSummaryResponse';
import type { SettlementCreate } from '../models/SettlementCreate';
import type { SettlementResponse } from '../models/SettlementResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SalesService {
    /**
     * Activate Account
     * Active le compte d'un élève (encaissé par le partenaire) et enregistre la vente.
     * @param requestBody
     * @param accessToken
     * @returns ActivationResponse Successful Response
     * @throws ApiError
     */
    public static activateAccountApiV1SalesActivationsPost(
        requestBody: ActivationRequest,
        accessToken?: (string | null),
    ): CancelablePromise<ActivationResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sales/activations',
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
     * My Summary
     * @param accessToken
     * @returns PartnerSummaryResponse Successful Response
     * @throws ApiError
     */
    public static mySummaryApiV1SalesMeSummaryGet(
        accessToken?: (string | null),
    ): CancelablePromise<PartnerSummaryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/me/summary',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * My Sales
     * @param limit
     * @param offset
     * @param accessToken
     * @returns PartnerSaleResponse Successful Response
     * @throws ApiError
     */
    public static mySalesApiV1SalesMeSalesGet(
        limit: number = 50,
        offset?: number,
        accessToken?: (string | null),
    ): CancelablePromise<Array<PartnerSaleResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/me/sales',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * My Settlements
     * @param accessToken
     * @returns SettlementResponse Successful Response
     * @throws ApiError
     */
    public static mySettlementsApiV1SalesMeSettlementsGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<SettlementResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/me/settlements',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Rules
     * @param accessToken
     * @returns CommissionRuleResponse Successful Response
     * @throws ApiError
     */
    public static listRulesApiV1SalesAdminCommissionRulesGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<CommissionRuleResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/admin/commission-rules',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Rule
     * @param requestBody
     * @param accessToken
     * @returns CommissionRuleResponse Successful Response
     * @throws ApiError
     */
    public static createRuleApiV1SalesAdminCommissionRulesPost(
        requestBody: CommissionRuleCreate,
        accessToken?: (string | null),
    ): CancelablePromise<CommissionRuleResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sales/admin/commission-rules',
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
     * Update Rule
     * @param ruleId
     * @param requestBody
     * @param accessToken
     * @returns CommissionRuleResponse Successful Response
     * @throws ApiError
     */
    public static updateRuleApiV1SalesAdminCommissionRulesRuleIdPatch(
        ruleId: string,
        requestBody: CommissionRuleUpdate,
        accessToken?: (string | null),
    ): CancelablePromise<CommissionRuleResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/sales/admin/commission-rules/{rule_id}',
            path: {
                'rule_id': ruleId,
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
     * Delete Rule
     * @param ruleId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteRuleApiV1SalesAdminCommissionRulesRuleIdDelete(
        ruleId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/sales/admin/commission-rules/{rule_id}',
            path: {
                'rule_id': ruleId,
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
     * Partners Overview
     * Tous les centres et ambassadeurs avec leur solde et leur statut de blocage.
     * @param accessToken
     * @returns PartnerSummaryResponse Successful Response
     * @throws ApiError
     */
    public static partnersOverviewApiV1SalesAdminPartnersGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<PartnerSummaryResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/admin/partners',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Partner Summary
     * @param partnerType
     * @param partnerId
     * @param accessToken
     * @returns PartnerSummaryResponse Successful Response
     * @throws ApiError
     */
    public static partnerSummaryApiV1SalesAdminPartnersPartnerTypePartnerIdGet(
        partnerType: 'center' | 'ambassador',
        partnerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<PartnerSummaryResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/admin/partners/{partner_type}/{partner_id}',
            path: {
                'partner_type': partnerType,
                'partner_id': partnerId,
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
     * Partner Sales
     * @param partnerType
     * @param partnerId
     * @param limit
     * @param offset
     * @param accessToken
     * @returns PartnerSaleResponse Successful Response
     * @throws ApiError
     */
    public static partnerSalesApiV1SalesAdminPartnersPartnerTypePartnerIdSalesGet(
        partnerType: 'center' | 'ambassador',
        partnerId: string,
        limit: number = 50,
        offset?: number,
        accessToken?: (string | null),
    ): CancelablePromise<Array<PartnerSaleResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/admin/partners/{partner_type}/{partner_id}/sales',
            path: {
                'partner_type': partnerType,
                'partner_id': partnerId,
            },
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Partner Settlements
     * @param partnerType
     * @param partnerId
     * @param accessToken
     * @returns SettlementResponse Successful Response
     * @throws ApiError
     */
    public static partnerSettlementsApiV1SalesAdminPartnersPartnerTypePartnerIdSettlementsGet(
        partnerType: 'center' | 'ambassador',
        partnerId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<SettlementResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/sales/admin/partners/{partner_type}/{partner_id}/settlements',
            path: {
                'partner_type': partnerType,
                'partner_id': partnerId,
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
     * Update Partner Settings
     * @param partnerType
     * @param partnerId
     * @param requestBody
     * @param accessToken
     * @returns PartnerSummaryResponse Successful Response
     * @throws ApiError
     */
    public static updatePartnerSettingsApiV1SalesAdminPartnersPartnerTypePartnerIdSettingsPatch(
        partnerType: 'center' | 'ambassador',
        partnerId: string,
        requestBody: PartnerSettingsUpdate,
        accessToken?: (string | null),
    ): CancelablePromise<PartnerSummaryResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/sales/admin/partners/{partner_type}/{partner_id}/settings',
            path: {
                'partner_type': partnerType,
                'partner_id': partnerId,
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
     * Create Settlement
     * Enregistre un règlement et l'impute sur les ventes les plus anciennes.
     * @param requestBody
     * @param accessToken
     * @returns SettlementResponse Successful Response
     * @throws ApiError
     */
    public static createSettlementApiV1SalesAdminSettlementsPost(
        requestBody: SettlementCreate,
        accessToken?: (string | null),
    ): CancelablePromise<SettlementResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/sales/admin/settlements',
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
