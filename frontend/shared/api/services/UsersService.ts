/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DirectorCreateRequest } from '../models/DirectorCreateRequest';
import type { SecretaryCreateRequest } from '../models/SecretaryCreateRequest';
import type { StudentAccessDatesUpdateRequest } from '../models/StudentAccessDatesUpdateRequest';
import type { StudentCreateRequest } from '../models/StudentCreateRequest';
import type { StudentCreditAdjustRequest } from '../models/StudentCreditAdjustRequest';
import type { StudentDetailedProgressResponse } from '../models/StudentDetailedProgressResponse';
import type { StudentProgressResponse } from '../models/StudentProgressResponse';
import type { StudentResponse } from '../models/StudentResponse';
import type { StudentTargetUpdateRequest } from '../models/StudentTargetUpdateRequest';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { UserAdminResponse } from '../models/UserAdminResponse';
import type { UserChangePasswordRequest } from '../models/UserChangePasswordRequest';
import type { UserMeResponse } from '../models/UserMeResponse';
import type { UserUpdateRequest } from '../models/UserUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UsersService {
    /**
     * Get Me
     * Profil de l'utilisateur connecté.
     * @param accessToken
     * @returns UserMeResponse Successful Response
     * @throws ApiError
     */
    public static getMeApiV1UsersMeGet(
        accessToken?: (string | null),
    ): CancelablePromise<UserMeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Me
     * Mise à jour du profil.
     * @param requestBody
     * @param accessToken
     * @returns UserMeResponse Successful Response
     * @throws ApiError
     */
    public static updateMeApiV1UsersMePatch(
        requestBody: UserUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<UserMeResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/me',
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
     * Get My Credits
     * Retourne le solde de crédits IA de l'utilisateur.
     * @param accessToken
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMyCreditsApiV1UsersMeCreditsGet(
        accessToken?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me/credits',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Change Password
     * Changement de mot de passe.
     * @param requestBody
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static changePasswordApiV1UsersMeChangePasswordPost(
        requestBody: UserChangePasswordRequest,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/me/change-password',
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
     * List Secretaries
     * Liste les secrétaires du centre du directeur connecté.
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static listSecretariesApiV1UsersSecretariesGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<UserAdminResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/secretaries',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Secretary
     * Le directeur crée un compte secrétaire pour une de ses succursales.
     * @param requestBody
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static createSecretaryApiV1UsersSecretariesPost(
        requestBody: SecretaryCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<UserAdminResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/secretaries',
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
     * List Users
     * Liste tous les utilisateurs — admin uniquement.
     * @param skip
     * @param limit
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static listUsersApiV1UsersGet(
        skip?: number,
        limit: number = 100,
        accessToken?: (string | null),
    ): CancelablePromise<Array<UserAdminResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users',
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
     * Get User
     * Détail d'un utilisateur — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static getUserApiV1UsersUserIdGet(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<UserAdminResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
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
     * Delete User
     * Supprime un utilisateur — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static deleteUserApiV1UsersUserIdDelete(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/users/{user_id}',
            path: {
                'user_id': userId,
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
     * Toggle Active
     * Active ou désactive un compte — admin uniquement.
     * @param userId
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static toggleActiveApiV1UsersUserIdToggleActivePatch(
        userId: string,
        accessToken?: (string | null),
    ): CancelablePromise<UserAdminResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/{user_id}/toggle-active',
            path: {
                'user_id': userId,
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
     * Create Director
     * Créer un compte center_director — admin ITIA, après paiement/activation licence.
     * @param requestBody
     * @param accessToken
     * @returns UserAdminResponse Successful Response
     * @throws ApiError
     */
    public static createDirectorApiV1UsersDirectorsPost(
        requestBody: DirectorCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<UserAdminResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/directors',
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
     * List Students By Center
     * Vue consolidée de tous les étudiants du centre, toutes succursales confondues.
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static listStudentsByCenterApiV1UsersStudentsByCenterGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<StudentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/students/by-center',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Toggle Student Activation
     * Le directeur active/désactive un compte étudiant de son centre.
     * Ne libère jamais le quota consommé (règle permanente/cumulative).
     * @param studentId
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static toggleStudentActivationApiV1UsersStudentsStudentIdActivationPatch(
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<StudentResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/students/{student_id}/activation',
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
     * Update Student Access Dates
     * Le directeur ajuste manuellement la fenêtre d'accès d'un étudiant précis.
     * @param studentId
     * @param requestBody
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static updateStudentAccessDatesApiV1UsersStudentsStudentIdAccessDatesPatch(
        studentId: string,
        requestBody: StudentAccessDatesUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StudentResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/students/{student_id}/access-dates',
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
     * Create Student
     * La secrétaire crée un compte étudiant — bloqué si quota licence atteint,
     * ou si le pool de crédits IA du centre est insuffisant.
     * @param requestBody
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static createStudentApiV1UsersStudentsPost(
        requestBody: StudentCreateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StudentResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/users/students',
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
     * Update Student Target
     * Modifie l'examen/niveau ciblé d'un étudiant — sans consommer une nouvelle place.
     * @param studentId
     * @param requestBody
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static updateStudentTargetApiV1UsersStudentsStudentIdTargetPatch(
        studentId: string,
        requestBody: StudentTargetUpdateRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StudentResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/students/{student_id}/target',
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
     * List Students By Branch
     * Liste des étudiants de la succursale de la secrétaire connectée.
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static listStudentsByBranchApiV1UsersStudentsByBranchGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<StudentResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/students/by-branch',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Adjust Student Credits
     * Recharge individuelle d'un étudiant, prélevée du pool de crédits du
     * centre. Secrétaire limitée à sa succursale, directeur à tout son centre
     * (vérifié dans le service). Chaque action est journalisée pour audit.
     * @param studentId
     * @param requestBody
     * @param accessToken
     * @returns StudentResponse Successful Response
     * @throws ApiError
     */
    public static adjustStudentCreditsApiV1UsersStudentsStudentIdCreditsPatch(
        studentId: string,
        requestBody: StudentCreditAdjustRequest,
        accessToken?: (string | null),
    ): CancelablePromise<StudentResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/students/{student_id}/credits',
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
     * Get Student Progress
     * Progression/scores des étudiants. Secrétaire : sa succursale
     * uniquement. Directeur : tout le centre, toutes succursales.
     * @param accessToken
     * @returns StudentProgressResponse Successful Response
     * @throws ApiError
     */
    public static getStudentProgressApiV1UsersStudentsProgressGet(
        accessToken?: (string | null),
    ): CancelablePromise<Array<StudentProgressResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/students/progress',
            cookies: {
                'access_token': accessToken,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Student Progress Detail
     * Progression détaillée d'un étudiant précis — ventilation par examen/
     * module et historique de scores pour graphes.
     * @param studentId
     * @param accessToken
     * @returns StudentDetailedProgressResponse Successful Response
     * @throws ApiError
     */
    public static getStudentProgressDetailApiV1UsersStudentsStudentIdProgressDetailGet(
        studentId: string,
        accessToken?: (string | null),
    ): CancelablePromise<StudentDetailedProgressResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/students/{student_id}/progress/detail',
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
