/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_testdaf_recording_api_v1_testdaf_sprechen_sessions__session_id__tasks__teil_number__recording_post } from '../models/Body_upload_testdaf_recording_api_v1_testdaf_sprechen_sessions__session_id__tasks__teil_number__recording_post';
import type { GradingResponse } from '../models/GradingResponse';
import type { RecordingReceivedResponse } from '../models/RecordingReceivedResponse';
import type { StartTestDafSessionRequest } from '../models/StartTestDafSessionRequest';
import type { StartTestDafSessionResponse } from '../models/StartTestDafSessionResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TestdafSprechenService {
    /**
     * Start Testdaf Session
     * @param requestBody
     * @param accessToken
     * @returns StartTestDafSessionResponse Successful Response
     * @throws ApiError
     */
    public static startTestdafSessionApiV1TestdafSprechenSessionsPost(
        requestBody: StartTestDafSessionRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StartTestDafSessionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/testdaf-sprechen/sessions',
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
     * Upload Testdaf Recording
     * @param sessionId
     * @param teilNumber
     * @param formData
     * @param accessToken
     * @returns RecordingReceivedResponse Successful Response
     * @throws ApiError
     */
    public static uploadTestdafRecordingApiV1TestdafSprechenSessionsSessionIdTasksTeilNumberRecordingPost(
        sessionId: string,
        teilNumber: number,
        formData: Body_upload_testdaf_recording_api_v1_testdaf_sprechen_sessions__session_id__tasks__teil_number__recording_post,
        accessToken?: (string | null),
    ): CancelablePromise<RecordingReceivedResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/testdaf-sprechen/sessions/{session_id}/tasks/{teil_number}/recording',
            path: {
                'session_id': sessionId,
                'teil_number': teilNumber,
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
    /**
     * Finish Testdaf Session
     * @param sessionId
     * @param accessToken
     * @returns GradingResponse Successful Response
     * @throws ApiError
     */
    public static finishTestdafSessionApiV1TestdafSprechenSessionsSessionIdFinishPost(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<GradingResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/testdaf-sprechen/sessions/{session_id}/finish',
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
     * Abandon Testdaf Session
     * @param sessionId
     * @param accessToken
     * @returns void
     * @throws ApiError
     */
    public static abandonTestdafSessionApiV1TestdafSprechenSessionsSessionIdAbandonPost(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/testdaf-sprechen/sessions/{session_id}/abandon',
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
     * Get Testdaf Audio
     * @param filename
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTestdafAudioApiV1TestdafSprechenAudioFilenameGet(
        filename: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/testdaf-sprechen/audio/{filename}',
            path: {
                'filename': filename,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
