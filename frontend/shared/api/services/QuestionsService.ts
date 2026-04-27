/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BulkQuestionCreateRequest } from '../models/BulkQuestionCreateRequest';
import type { QuestionAdminResponse } from '../models/QuestionAdminResponse';
import type { QuestionCreateRequest } from '../models/QuestionCreateRequest';
import type { QuestionResponse } from '../models/QuestionResponse';
import type { QuestionUpdateRequest } from '../models/QuestionUpdateRequest';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class QuestionsService {
    /**
     * Get Questions By Teil
     * Questions d'un Teil — vue étudiant, sans correct_answer.
     * En pratique, le frontend les reçoit via SessionStartResponse,
     * cet endpoint est utile pour preview ou débogage.
     * @param teilId
     * @param accessToken
     * @returns QuestionResponse Successful Response
     * @throws ApiError
     */
    public static getQuestionsByTeilApiV1TeileTeilIdQuestionsGet(
        teilId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<QuestionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/teile/{teil_id}/questions',
            path: {
                'teil_id': teilId,
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
     * Admin Get Questions
     * Liste toutes les questions d'un Teil avec correct_answer — admin.
     * @param teilId
     * @param accessToken
     * @returns QuestionAdminResponse Successful Response
     * @throws ApiError
     */
    public static adminGetQuestionsApiV1AdminTeileTeilIdQuestionsGet(
        teilId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<QuestionAdminResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/teile/{teil_id}/questions',
            path: {
                'teil_id': teilId,
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
     * Create Question
     * @param teilId
     * @param requestBody
     * @param accessToken
     * @returns QuestionAdminResponse Successful Response
     * @throws ApiError
     */
    public static createQuestionApiV1AdminTeileTeilIdQuestionsPost(
        teilId: string,
        requestBody: QuestionCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<QuestionAdminResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/admin/teile/{teil_id}/questions',
            path: {
                'teil_id': teilId,
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
     * Admin Get Question
     * @param questionId
     * @param accessToken
     * @returns QuestionAdminResponse Successful Response
     * @throws ApiError
     */
    public static adminGetQuestionApiV1AdminQuestionsQuestionIdGet(
        questionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<QuestionAdminResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/questions/{question_id}',
            path: {
                'question_id': questionId,
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
     * Update Question
     * @param questionId
     * @param requestBody
     * @param accessToken
     * @returns QuestionAdminResponse Successful Response
     * @throws ApiError
     */
    public static updateQuestionApiV1AdminQuestionsQuestionIdPatch(
        questionId: string,
        requestBody: QuestionUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<QuestionAdminResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/admin/questions/{question_id}',
            path: {
                'question_id': questionId,
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
     * Delete Question
     * @param questionId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteQuestionApiV1AdminQuestionsQuestionIdDelete(
        questionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/admin/questions/{question_id}',
            path: {
                'question_id': questionId,
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
     * Bulk Create Questions
     * Insert en masse — utilisé par le script d'import.
     * @param teilId
     * @param requestBody
     * @param accessToken
     * @returns QuestionAdminResponse Successful Response
     * @throws ApiError
     */
    public static bulkCreateQuestionsApiV1AdminTeileTeilIdQuestionsBulkPost(
        teilId: string,
        requestBody: BulkQuestionCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<Array<QuestionAdminResponse>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/admin/teile/{teil_id}/questions/bulk',
            path: {
                'teil_id': teilId,
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
     * Replace Questions
     * Remplace toutes les questions d'un Teil.
     * Utile pour re-importer sans conflit.
     * @param teilId
     * @param requestBody
     * @param accessToken
     * @returns QuestionAdminResponse Successful Response
     * @throws ApiError
     */
    public static replaceQuestionsApiV1AdminTeileTeilIdQuestionsReplacePut(
        teilId: string,
        requestBody: BulkQuestionCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<Array<QuestionAdminResponse>> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/admin/teile/{teil_id}/questions/replace',
            path: {
                'teil_id': teilId,
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
}
