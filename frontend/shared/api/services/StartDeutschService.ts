/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_import_subject_audio_api_v1_start_deutsch_admin_audio_post } from '../models/Body_import_subject_audio_api_v1_start_deutsch_admin_audio_post';
import type { Body_import_subject_images_api_v1_start_deutsch_admin_images_post } from '../models/Body_import_subject_images_api_v1_start_deutsch_admin_images_post';
import type { Body_import_subject_json_api_v1_start_deutsch_admin_import_post } from '../models/Body_import_subject_json_api_v1_start_deutsch_admin_import_post';
import type { StartDeutschSchreibenCorrectionRequest } from '../models/StartDeutschSchreibenCorrectionRequest';
import type { StartDeutschSchreibenCorrectionResponse } from '../models/StartDeutschSchreibenCorrectionResponse';
import type { StartDeutschSessionCreateRequest } from '../models/StartDeutschSessionCreateRequest';
import type { StartDeutschSessionListItem } from '../models/StartDeutschSessionListItem';
import type { StartDeutschSessionResponse } from '../models/StartDeutschSessionResponse';
import type { StartDeutschSessionResultResponse } from '../models/StartDeutschSessionResultResponse';
import type { StartDeutschSessionSubmitRequest } from '../models/StartDeutschSessionSubmitRequest';
import type { StartDeutschSubjectDetail } from '../models/StartDeutschSubjectDetail';
import type { StartDeutschSubjectSummary } from '../models/StartDeutschSubjectSummary';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StartDeutschService {
    /**
     * List Subjects
     * Catalogue Start Deutsch, accessible à tout étudiant dont le centre a une
     * licence active (vérification faite au niveau du middleware/dependency
     * d'accès centre, pas ici — à brancher comme pour le reste du catalogue).
     * @param level
     * @param accessToken
     * @returns StartDeutschSubjectSummary Successful Response
     * @throws ApiError
     */
    public static listSubjectsApiV1StartDeutschSubjectsGet(
        level?: (string | null),
        accessToken?: (string | null),
    ): CancelablePromise<Array<StartDeutschSubjectSummary>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/start-deutsch/subjects',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'level': level,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Subject Detail
     * Arbre complet Module → Teil → Question (sans correct_answer) pour démarrer une session.
     * @param subjectId
     * @param accessToken
     * @returns StartDeutschSubjectDetail Successful Response
     * @throws ApiError
     */
    public static getSubjectDetailApiV1StartDeutschSubjectsSubjectIdGet(
        subjectId: string,
        accessToken?: (string | null),
    ): CancelablePromise<StartDeutschSubjectDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/start-deutsch/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
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
     * Start Session
     * @param requestBody
     * @param accessToken
     * @returns StartDeutschSessionResponse Successful Response
     * @throws ApiError
     */
    public static startSessionApiV1StartDeutschSessionsPost(
        requestBody: StartDeutschSessionCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StartDeutschSessionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/start-deutsch/sessions',
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
     * List My Sessions
     * @param skip
     * @param limit
     * @param accessToken
     * @returns StartDeutschSessionListItem Successful Response
     * @throws ApiError
     */
    public static listMySessionsApiV1StartDeutschSessionsGet(
        skip?: number,
        limit: number = 20,
        accessToken?: (string | null),
    ): CancelablePromise<Array<StartDeutschSessionListItem>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/start-deutsch/sessions',
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
     * Submit Session
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns StartDeutschSessionResponse Successful Response
     * @throws ApiError
     */
    public static submitSessionApiV1StartDeutschSessionsSessionIdSubmitPost(
        sessionId: string,
        requestBody: StartDeutschSessionSubmitRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StartDeutschSessionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/start-deutsch/sessions/{session_id}/submit',
            path: {
                'session_id': sessionId,
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
     * Get Session Result
     * @param sessionId
     * @param accessToken
     * @returns StartDeutschSessionResultResponse Successful Response
     * @throws ApiError
     */
    public static getSessionResultApiV1StartDeutschSessionsSessionIdResultGet(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<StartDeutschSessionResultResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/start-deutsch/sessions/{session_id}/result',
            path: {
                'session_id': sessionId,
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
     * Correct Schreiben
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns StartDeutschSchreibenCorrectionResponse Successful Response
     * @throws ApiError
     */
    public static correctSchreibenApiV1StartDeutschSessionsSessionIdSchreibenCorrectionPost(
        sessionId: string,
        requestBody: StartDeutschSchreibenCorrectionRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StartDeutschSchreibenCorrectionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/start-deutsch/sessions/{session_id}/schreiben-correction',
            path: {
                'session_id': sessionId,
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
     * Admin List Subjects
     * Liste TOUS les sujets (actifs ou non) — vue admin, pour le sélecteur
     * audio/images et pour repérer les sujets de test à supprimer.
     * @param level
     * @param accessToken
     * @returns StartDeutschSubjectSummary Successful Response
     * @throws ApiError
     */
    public static adminListSubjectsApiV1StartDeutschAdminSubjectsGet(
        level?: (string | null),
        accessToken?: (string | null),
    ): CancelablePromise<Array<StartDeutschSubjectSummary>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/start-deutsch/admin/subjects',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'level': level,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Admin Delete Subject
     * Supprime un sujet et tout ce qui en dépend (modules/teile/questions,
     * sessions/réponses/corrections) — cascade posée au niveau DB.
     * @param subjectId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static adminDeleteSubjectApiV1StartDeutschAdminSubjectsSubjectIdDelete(
        subjectId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/start-deutsch/admin/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
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
     * Import Subject Json
     * Importe un sujet Start Deutsch complet depuis un JSON (structure
     * level/title/modules[].teile[].questions, cf. import_parsers.py pour le
     * détail par format_type). Si replace=true, remplace les questions des
     * Teile déjà existants.
     * @param formData
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importSubjectJsonApiV1StartDeutschAdminImportPost(
        formData: Body_import_subject_json_api_v1_start_deutsch_admin_import_post,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/start-deutsch/admin/import',
            cookies: {
                'access_token': accessToken,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Import Subject Audio
     * @param formData
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importSubjectAudioApiV1StartDeutschAdminAudioPost(
        formData: Body_import_subject_audio_api_v1_start_deutsch_admin_audio_post,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/start-deutsch/admin/audio',
            cookies: {
                'access_token': accessToken,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Import Subject Images
     * @param formData
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importSubjectImagesApiV1StartDeutschAdminImagesPost(
        formData: Body_import_subject_images_api_v1_start_deutsch_admin_images_post,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/start-deutsch/admin/images',
            cookies: {
                'access_token': accessToken,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
