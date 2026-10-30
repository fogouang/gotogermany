/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssignmentCreate } from '../models/AssignmentCreate';
import type { AssignmentDetailResponse } from '../models/AssignmentDetailResponse';
import type { AssignmentSummaryResponse } from '../models/AssignmentSummaryResponse';
import type { BankSubjectResponse } from '../models/BankSubjectResponse';
import type { Body_upload_annotated_copy_api_v1_assignments__assignment_id__submissions__student_id__annotated_post } from '../models/Body_upload_annotated_copy_api_v1_assignments__assignment_id__submissions__student_id__annotated_post';
import type { GradeRequest } from '../models/GradeRequest';
import type { SessionStartResponse } from '../models/SessionStartResponse';
import type { StartDeutschSessionResponse } from '../models/StartDeutschSessionResponse';
import type { StudentAssignmentResponse } from '../models/StudentAssignmentResponse';
import type { SubmissionGradingResponse } from '../models/SubmissionGradingResponse';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AssignmentsService {
    /**
     * Subject Bank
     * Banque de sujets privés disponibles pour les devoirs.
     * @param levelId
     * @param accessToken
     * @returns BankSubjectResponse Successful Response
     * @throws ApiError
     */
    public static subjectBankApiV1AssignmentsBankGet(
        levelId?: (string | null),
        accessToken?: (string | null),
    ): CancelablePromise<Array<BankSubjectResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/bank',
            cookies: {
                'access_token': accessToken,
            },
            query: {
                'level_id': levelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Assignment
     * @param requestBody
     * @param accessToken
     * @returns AssignmentDetailResponse Successful Response
     * @throws ApiError
     */
    public static createAssignmentApiV1AssignmentsPost(
        requestBody: AssignmentCreate,
        accessToken?: (string | null),
    ): CancelablePromise<AssignmentDetailResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assignments',
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
     * My Teaching Assignments
     * @param accessToken
     * @returns AssignmentSummaryResponse Successful Response
     * @throws ApiError
     */
    public static myTeachingAssignmentsApiV1AssignmentsTeachingGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<AssignmentSummaryResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/teaching',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * My Assignments
     * Devoirs de l'élève : statut et note finale uniquement.
     * @param accessToken
     * @returns StudentAssignmentResponse Successful Response
     * @throws ApiError
     */
    public static myAssignmentsApiV1AssignmentsMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<StudentAssignmentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/me',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Start Assignment
     * Démarre (ou reprend) le devoir : renvoie le contenu du sujet pour le lecteur d'examen.
     * @param assignmentId
     * @param accessToken
     * @returns SessionStartResponse Successful Response
     * @throws ApiError
     */
    public static startAssignmentApiV1AssignmentsAssignmentIdStartPost(
        assignmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SessionStartResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assignments/{assignment_id}/start',
            path: {
                'assignment_id': assignmentId,
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
     * Start Start Deutsch Assignment
     * Devoir Start Deutsch : démarre (ou reprend) la session du lecteur A1/A2.
     * @param assignmentId
     * @param accessToken
     * @returns StartDeutschSessionResponse Successful Response
     * @throws ApiError
     */
    public static startStartDeutschAssignmentApiV1AssignmentsAssignmentIdStartDeutschStartPost(
        assignmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<StartDeutschSessionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assignments/{assignment_id}/start-deutsch/start',
            path: {
                'assignment_id': assignmentId,
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
     * Assignment Detail
     * @param assignmentId
     * @param accessToken
     * @returns AssignmentDetailResponse Successful Response
     * @throws ApiError
     */
    public static assignmentDetailApiV1AssignmentsAssignmentIdGet(
        assignmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<AssignmentDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/{assignment_id}',
            path: {
                'assignment_id': assignmentId,
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
     * Cancel Assignment
     * @param assignmentId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static cancelAssignmentApiV1AssignmentsAssignmentIdCancelPost(
        assignmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assignments/{assignment_id}/cancel',
            path: {
                'assignment_id': assignmentId,
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
     * Download All Schreiben
     * @param assignmentId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadAllSchreibenApiV1AssignmentsAssignmentIdSchreibenZipGet(
        assignmentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/{assignment_id}/schreiben.zip',
            path: {
                'assignment_id': assignmentId,
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
     * Submission For Grading
     * @param assignmentId
     * @param studentId
     * @param accessToken
     * @returns SubmissionGradingResponse Successful Response
     * @throws ApiError
     */
    public static submissionForGradingApiV1AssignmentsAssignmentIdSubmissionsStudentIdGet(
        assignmentId: string,
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SubmissionGradingResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/{assignment_id}/submissions/{student_id}',
            path: {
                'assignment_id': assignmentId,
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
     * Grade Submission
     * @param assignmentId
     * @param studentId
     * @param requestBody
     * @param accessToken
     * @returns SubmissionGradingResponse Successful Response
     * @throws ApiError
     */
    public static gradeSubmissionApiV1AssignmentsAssignmentIdSubmissionsStudentIdGradePost(
        assignmentId: string,
        studentId: string,
        requestBody: GradeRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SubmissionGradingResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assignments/{assignment_id}/submissions/{student_id}/grade',
            path: {
                'assignment_id': assignmentId,
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
     * Download Schreiben
     * @param assignmentId
     * @param studentId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadSchreibenApiV1AssignmentsAssignmentIdSubmissionsStudentIdSchreibenPdfGet(
        assignmentId: string,
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/{assignment_id}/submissions/{student_id}/schreiben.pdf',
            path: {
                'assignment_id': assignmentId,
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
     * Upload Annotated Copy
     * @param assignmentId
     * @param studentId
     * @param formData
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static uploadAnnotatedCopyApiV1AssignmentsAssignmentIdSubmissionsStudentIdAnnotatedPost(
        assignmentId: string,
        studentId: string,
        formData: Body_upload_annotated_copy_api_v1_assignments__assignment_id__submissions__student_id__annotated_post,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/assignments/{assignment_id}/submissions/{student_id}/annotated',
            path: {
                'assignment_id': assignmentId,
                'student_id': studentId,
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
     * Download Annotated Copy
     * @param assignmentId
     * @param studentId
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static downloadAnnotatedCopyApiV1AssignmentsAssignmentIdSubmissionsStudentIdAnnotatedGet(
        assignmentId: string,
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/assignments/{assignment_id}/submissions/{student_id}/annotated',
            path: {
                'assignment_id': assignmentId,
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
