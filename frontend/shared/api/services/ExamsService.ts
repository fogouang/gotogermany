/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_import_exam_audio_api_v1_exams_admin__exam_id__audio_post } from '../models/Body_import_exam_audio_api_v1_exams_admin__exam_id__audio_post';
import type { Body_import_exam_json_api_v1_exams_admin_import_post } from '../models/Body_import_exam_json_api_v1_exams_admin_import_post';
import type { ExamCatalogResponse } from '../models/ExamCatalogResponse';
import type { ExamCreateRequest } from '../models/ExamCreateRequest';
import type { ExamDetailResponse } from '../models/ExamDetailResponse';
import type { ExamListResponse } from '../models/ExamListResponse';
import type { ExamUpdateRequest } from '../models/ExamUpdateRequest';
import type { LevelCreateRequest } from '../models/LevelCreateRequest';
import type { LevelResponse } from '../models/LevelResponse';
import type { LevelUpdateRequest } from '../models/LevelUpdateRequest';
import type { ModuleCreateRequest } from '../models/ModuleCreateRequest';
import type { ModuleResponse } from '../models/ModuleResponse';
import type { SubjectCreateRequest } from '../models/SubjectCreateRequest';
import type { SubjectResponse } from '../models/SubjectResponse';
import type { SubjectUpdateRequest } from '../models/SubjectUpdateRequest';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { TeilCreateRequest } from '../models/TeilCreateRequest';
import type { TeilResponse } from '../models/TeilResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ExamsService {
    /**
     * Get Catalog
     * @param accessToken
     * @returns ExamCatalogResponse Successful Response
     * @throws ApiError
     */
    public static getCatalogApiV1ExamsGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<ExamCatalogResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/exams',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Exam
     * @param requestBody
     * @param accessToken
     * @returns ExamListResponse Successful Response
     * @throws ApiError
     */
    public static createExamApiV1ExamsPost(
        requestBody: ExamCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<ExamListResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams',
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
     * Get Exam Detail
     * @param examId
     * @param accessToken
     * @returns ExamDetailResponse Successful Response
     * @throws ApiError
     */
    public static getExamDetailApiV1ExamsExamIdGet(
        examId: string,
        accessToken?: (string | null),
    ): CancelablePromise<ExamDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/exams/{exam_id}',
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
     * Update Exam
     * @param examId
     * @param requestBody
     * @param accessToken
     * @returns ExamListResponse Successful Response
     * @throws ApiError
     */
    public static updateExamApiV1ExamsExamIdPatch(
        examId: string,
        requestBody: ExamUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<ExamListResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/exams/{exam_id}',
            path: {
                'exam_id': examId,
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
     * Delete Exam
     * @param examId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteExamApiV1ExamsExamIdDelete(
        examId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/exams/{exam_id}',
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
     * Get Exam By Slug
     * @param slug
     * @param accessToken
     * @returns ExamDetailResponse Successful Response
     * @throws ApiError
     */
    public static getExamBySlugApiV1ExamsSlugSlugGet(
        slug: string,
        accessToken?: (string | null),
    ): CancelablePromise<ExamDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/exams/slug/{slug}',
            path: {
                'slug': slug,
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
     * Get Levels
     * @param examId
     * @param accessToken
     * @returns LevelResponse Successful Response
     * @throws ApiError
     */
    public static getLevelsApiV1ExamsExamIdLevelsGet(
        examId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<LevelResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/exams/{exam_id}/levels',
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
     * Create Level
     * @param examId
     * @param requestBody
     * @param accessToken
     * @returns LevelResponse Successful Response
     * @throws ApiError
     */
    public static createLevelApiV1ExamsExamIdLevelsPost(
        examId: string,
        requestBody: LevelCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<LevelResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams/{exam_id}/levels',
            path: {
                'exam_id': examId,
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
     * Update Level
     * @param levelId
     * @param requestBody
     * @param accessToken
     * @returns LevelResponse Successful Response
     * @throws ApiError
     */
    public static updateLevelApiV1ExamsLevelsLevelIdPatch(
        levelId: string,
        requestBody: LevelUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<LevelResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/exams/levels/{level_id}',
            path: {
                'level_id': levelId,
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
     * Delete Level
     * @param levelId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteLevelApiV1ExamsLevelsLevelIdDelete(
        levelId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/exams/levels/{level_id}',
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
     * Get Subjects
     * Liste les sujets d'un level.
     * @param levelId
     * @param accessToken
     * @returns SubjectResponse Successful Response
     * @throws ApiError
     */
    public static getSubjectsApiV1ExamsLevelsLevelIdSubjectsGet(
        levelId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<SubjectResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/exams/levels/{level_id}/subjects',
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
     * Create Subject
     * Crée un nouveau sujet — subject_number auto-incrémenté.
     * @param levelId
     * @param requestBody
     * @param accessToken
     * @returns SubjectResponse Successful Response
     * @throws ApiError
     */
    public static createSubjectApiV1ExamsLevelsLevelIdSubjectsPost(
        levelId: string,
        requestBody: SubjectCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SubjectResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams/levels/{level_id}/subjects',
            path: {
                'level_id': levelId,
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
     * Delete Subject
     * @param subjectId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteSubjectApiV1ExamsSubjectsSubjectIdDelete(
        subjectId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/exams/subjects/{subject_id}',
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
     * Update Subject
     * @param subjectId
     * @param requestBody
     * @param accessToken
     * @returns SubjectResponse Successful Response
     * @throws ApiError
     */
    public static updateSubjectApiV1ExamsSubjectsSubjectIdPatch(
        subjectId: string,
        requestBody: SubjectUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SubjectResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/exams/subjects/{subject_id}',
            path: {
                'subject_id': subjectId,
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
     * Create Module
     * @param subjectId
     * @param requestBody
     * @param accessToken
     * @returns ModuleResponse Successful Response
     * @throws ApiError
     */
    public static createModuleApiV1ExamsSubjectsSubjectIdModulesPost(
        subjectId: string,
        requestBody: ModuleCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<ModuleResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams/subjects/{subject_id}/modules',
            path: {
                'subject_id': subjectId,
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
     * Delete Module
     * @param moduleId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteModuleApiV1ExamsModulesModuleIdDelete(
        moduleId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/exams/modules/{module_id}',
            path: {
                'module_id': moduleId,
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
     * Create Teil
     * @param moduleId
     * @param requestBody
     * @param accessToken
     * @returns TeilResponse Successful Response
     * @throws ApiError
     */
    public static createTeilApiV1ExamsModulesModuleIdTeilePost(
        moduleId: string,
        requestBody: TeilCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<TeilResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams/modules/{module_id}/teile',
            path: {
                'module_id': moduleId,
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
     * Delete Teil
     * @param teilId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteTeilApiV1ExamsTeileTeilIdDelete(
        teilId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/exams/teile/{teil_id}',
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
     * Import Exam Json
     * Importe un examen complet depuis un fichier JSON.
     * Le JSON est celui généré par generate_telc_b1.py ou generate_exam.py.
     * Si replace=true, supprime et réinsère les questions existantes.
     * @param formData
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importExamJsonApiV1ExamsAdminImportPost(
        formData: Body_import_exam_json_api_v1_exams_admin_import_post,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams/admin/import',
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
     * Import Exam Audio
     * Associe plusieurs fichiers MP3 aux questions d'un sujet.
     * Sélectionner tous les MP3 du dossier audio_telc_YYYYMMDD correspondant.
     * Convention : horen_teil1_audio1.mp3, horen_teil2.mp3, horen_teil3_audio1.mp3...
     * @param examId
     * @param formData
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importExamAudioApiV1ExamsAdminExamIdAudioPost(
        examId: string,
        formData: Body_import_exam_audio_api_v1_exams_admin__exam_id__audio_post,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/exams/admin/{exam_id}/audio',
            path: {
                'exam_id': examId,
            },
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
