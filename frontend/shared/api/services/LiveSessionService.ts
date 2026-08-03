/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateLiveSessionRequest } from '../models/CreateLiveSessionRequest';
import type { LiveSessionListResponse } from '../models/LiveSessionListResponse';
import type { LiveSessionResponse } from '../models/LiveSessionResponse';
import type { SubjectContentResponse } from '../models/SubjectContentResponse';
import type { SubmitNotesRequest } from '../models/SubmitNotesRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LiveSessionService {
    /**
     * Create Live Session
     * Lancée par l'examinateur (staff du centre) — vérifie rôle,
     * appartenance au même centre, et que le sujet a bien un module Sprechen.
     * @param requestBody
     * @param accessToken
     * @returns LiveSessionResponse Successful Response
     * @throws ApiError
     */
    public static createLiveSessionApiV1LiveSessionPost(
        requestBody: CreateLiveSessionRequest,
        accessToken?: (string | null),
    ): CancelablePromise<LiveSessionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/live-session',
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
     * Submit Examiner Notes
     * L'examinateur rédige/complète ses notes — pendant ou après la
     * session. Visibles côté student dès que la session est "ended".
     * @param liveSessionId
     * @param requestBody
     * @param accessToken
     * @returns LiveSessionResponse Successful Response
     * @throws ApiError
     */
    public static submitExaminerNotesApiV1LiveSessionLiveSessionIdNotesPatch(
        liveSessionId: string,
        requestBody: SubmitNotesRequest,
        accessToken?: (string | null),
    ): CancelablePromise<LiveSessionResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/live-session/{live_session_id}/notes',
            path: {
                'live_session_id': liveSessionId,
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
     * Get My Live Sessions
     * Côté student : historique de ses sessions live, notes de
     * l'examinateur incluses une fois la session terminée.
     * @param limit
     * @param offset
     * @param accessToken
     * @returns LiveSessionListResponse Successful Response
     * @throws ApiError
     */
    public static getMyLiveSessionsApiV1LiveSessionMineGet(
        limit: number = 20,
        offset?: number,
        accessToken?: (string | null),
    ): CancelablePromise<LiveSessionListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/live-session/mine',
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
     * Get Launched Live Sessions
     * Côté examinateur : sessions qu'il/elle a lancées.
     * @param limit
     * @param offset
     * @param accessToken
     * @returns LiveSessionListResponse Successful Response
     * @throws ApiError
     */
    public static getLaunchedLiveSessionsApiV1LiveSessionLaunchedGet(
        limit: number = 20,
        offset?: number,
        accessToken?: (string | null),
    ): CancelablePromise<LiveSessionListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/live-session/launched',
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
     * Get Live Session
     * Accessible au candidat ou à l'examinateur concerné par cette session.
     * Déclarée en DERNIER parmi les routes GET : FastAPI matche dans l'ordre
     * de déclaration, donc un chemin dynamique comme celui-ci doit toujours
     * venir après les routes statiques ("/mine", "/launched"), sinon il les
     * intercepterait en premier (live_session_id="mine" -> échec UUID).
     * @param liveSessionId
     * @param accessToken
     * @returns LiveSessionResponse Successful Response
     * @throws ApiError
     */
    public static getLiveSessionApiV1LiveSessionLiveSessionIdGet(
        liveSessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<LiveSessionResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/live-session/{live_session_id}',
            path: {
                'live_session_id': liveSessionId,
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
     * Get Live Session Subject
     * Contenu du sujet Sprechen (instructions/thèmes/points par Teil) —
     * ce qui manquait jusqu'ici : le candidat et l'examinateur ne recevaient
     * aucune information sur le sujet réellement sélectionné pour la session.
     * @param liveSessionId
     * @param accessToken
     * @returns SubjectContentResponse Successful Response
     * @throws ApiError
     */
    public static getLiveSessionSubjectApiV1LiveSessionLiveSessionIdSubjectGet(
        liveSessionId: string,
        accessToken?: (string | null),
    ): CancelablePromise<SubjectContentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/live-session/{live_session_id}/subject',
            path: {
                'live_session_id': liveSessionId,
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
