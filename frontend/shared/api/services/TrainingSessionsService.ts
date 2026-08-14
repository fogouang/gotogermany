/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StudentDetailedProgressResponse } from '../models/StudentDetailedProgressResponse';
import type { StudentEndRequest } from '../models/StudentEndRequest';
import type { StudentEnrollRequest } from '../models/StudentEnrollRequest';
import type { StudentProgressResponse } from '../models/StudentProgressResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { TeacherAssignRequest } from '../models/TeacherAssignRequest';
import type { TeacherCommentCreateRequest } from '../models/TeacherCommentCreateRequest';
import type { TeacherCommentResponse } from '../models/TeacherCommentResponse';
import type { TrainingSessionCreateRequest } from '../models/TrainingSessionCreateRequest';
import type { TrainingSessionResponse } from '../models/TrainingSessionResponse';
import type { TrainingSessionStatsResponse } from '../models/TrainingSessionStatsResponse';
import type { TrainingSessionUpdateRequest } from '../models/TrainingSessionUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TrainingSessionsService {
    /**
     * Create Session
     * @param requestBody
     * @param accessToken
     * @returns TrainingSessionResponse Successful Response
     * @throws ApiError
     */
    public static createSessionApiV1TrainingSessionsPost(
        requestBody: TrainingSessionCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<TrainingSessionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/training-sessions',
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
     * List Sessions By Center
     * @param accessToken
     * @returns TrainingSessionResponse Successful Response
     * @throws ApiError
     */
    public static listSessionsByCenterApiV1TrainingSessionsByCenterGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<TrainingSessionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/by-center',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Sessions By Branch
     * @param accessToken
     * @returns TrainingSessionResponse Successful Response
     * @throws ApiError
     */
    public static listSessionsByBranchApiV1TrainingSessionsByBranchGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<TrainingSessionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/by-branch',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List My Sessions
     * @param accessToken
     * @returns TrainingSessionResponse Successful Response
     * @throws ApiError
     */
    public static listMySessionsApiV1TrainingSessionsMineGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<TrainingSessionResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/mine',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Students Progress For Teacher
     * Progression agrégée (score moyen, dernière session...) des
     * étudiants actifs de l'enseignant, dédupliquée à travers ses sessions.
     * @param accessToken
     * @returns StudentProgressResponse Successful Response
     * @throws ApiError
     */
    public static getStudentsProgressForTeacherApiV1TrainingSessionsStudentsProgressGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<StudentProgressResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/students/progress',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Session
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns TrainingSessionResponse Successful Response
     * @throws ApiError
     */
    public static updateSessionApiV1TrainingSessionsSessionIdPatch(
        sessionId: string,
        requestBody: TrainingSessionUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<TrainingSessionResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/training-sessions/{session_id}',
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
     * Assign Teacher
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static assignTeacherApiV1TrainingSessionsSessionIdTeachersPost(
        sessionId: string,
        requestBody: TeacherAssignRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/training-sessions/{session_id}/teachers',
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
     * Remove Teacher
     * @param sessionId
     * @param teacherId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static removeTeacherApiV1TrainingSessionsSessionIdTeachersTeacherIdDelete(
        sessionId: string,
        teacherId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/training-sessions/{session_id}/teachers/{teacher_id}',
            path: {
                'session_id': sessionId,
                'teacher_id': teacherId,
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
     * Enroll Student
     * @param sessionId
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static enrollStudentApiV1TrainingSessionsSessionIdStudentsPost(
        sessionId: string,
        requestBody: StudentEnrollRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/training-sessions/{session_id}/students',
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
     * End Student
     * @param sessionId
     * @param studentId
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static endStudentApiV1TrainingSessionsSessionIdStudentsStudentIdEndPatch(
        sessionId: string,
        studentId: string,
        requestBody: StudentEndRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/training-sessions/{session_id}/students/{student_id}/end',
            path: {
                'session_id': sessionId,
                'student_id': studentId,
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
     * Get Session Stats
     * @param sessionId
     * @param accessToken
     * @returns TrainingSessionStatsResponse Successful Response
     * @throws ApiError
     */
    public static getSessionStatsApiV1TrainingSessionsSessionIdStatsGet(
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<TrainingSessionStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/{session_id}/stats',
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
     * Get Student Progress For Teacher
     * @param studentId
     * @param accessToken
     * @returns StudentDetailedProgressResponse Successful Response
     * @throws ApiError
     */
    public static getStudentProgressForTeacherApiV1TrainingSessionsStudentsStudentIdProgressGet(
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<StudentDetailedProgressResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/students/{student_id}/progress',
            path: {
                'student_id': studentId,
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
     * Get Student Session Result For Teacher
     * @param studentId
     * @param sessionId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getStudentSessionResultForTeacherApiV1TrainingSessionsStudentsStudentIdSessionsSessionIdResultGet(
        studentId: string,
        sessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/students/{student_id}/sessions/{session_id}/result',
            path: {
                'student_id': studentId,
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
     * Add Student Comment
     * @param studentId
     * @param requestBody
     * @param accessToken
     * @returns TeacherCommentResponse Successful Response
     * @throws ApiError
     */
    public static addStudentCommentApiV1TrainingSessionsStudentsStudentIdCommentsPost(
        studentId: string,
        requestBody: TeacherCommentCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<TeacherCommentResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/training-sessions/students/{student_id}/comments',
            path: {
                'student_id': studentId,
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
     * List Student Comments For Teacher
     * @param studentId
     * @param accessToken
     * @returns TeacherCommentResponse Successful Response
     * @throws ApiError
     */
    public static listStudentCommentsForTeacherApiV1TrainingSessionsStudentsStudentIdCommentsGet(
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<TeacherCommentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/students/{student_id}/comments',
            path: {
                'student_id': studentId,
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
     * List Student Comments For Director
     * @param studentId
     * @param accessToken
     * @returns TeacherCommentResponse Successful Response
     * @throws ApiError
     */
    public static listStudentCommentsForDirectorApiV1TrainingSessionsStudentsStudentIdCommentsAllGet(
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<Array<TeacherCommentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/training-sessions/students/{student_id}/comments/all',
            path: {
                'student_id': studentId,
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
