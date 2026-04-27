/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthResponse } from '../models/AuthResponse';
import type { LoginRequest } from '../models/LoginRequest';
import type { RegisterRequest } from '../models/RegisterRequest';
import type { SuccessResponse } from '../models/SuccessResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Register
     * Inscription d'un nouvel utilisateur.
     * @param requestBody
     * @returns AuthResponse Successful Response
     * @throws ApiError
     */
    public static registerApiV1AuthRegisterPost(
        requestBody: RegisterRequest,
    ): CancelablePromise<AuthResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Login
     * Connexion — retourne un JWT.
     * @param requestBody
     * @returns AuthResponse Successful Response
     * @throws ApiError
     */
    public static loginApiV1AuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<AuthResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Verify Email
     * Vérification de l'adresse email via le token reçu par email.
     * @param token
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static verifyEmailApiV1AuthVerifyEmailTokenPost(
        token: string,
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/verify-email/{token}',
            path: {
                'token': token,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Request Password Reset
     * Demande de réinitialisation du mot de passe.
     * @param email
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static requestPasswordResetApiV1AuthPasswordResetRequestPost(
        email: string,
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/password-reset/request',
            query: {
                'email': email,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Confirm Password Reset
     * Confirmation du reset avec le token et le nouveau mot de passe.
     * @param token
     * @param newPassword
     * @returns SuccessResponse Successful Response
     * @throws ApiError
     */
    public static confirmPasswordResetApiV1AuthPasswordResetConfirmPost(
        token: string,
        newPassword: string,
    ): CancelablePromise<SuccessResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/password-reset/confirm',
            query: {
                'token': token,
                'new_password': newPassword,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
