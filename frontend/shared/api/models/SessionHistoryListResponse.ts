/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionHistoryItem } from './SessionHistoryItem';
/**
 * response_model for GET /history — matches the typed
 * response_model= convention used throughout the codebase rather
 * than returning a raw dict.
 */
export type SessionHistoryListResponse = {
    items: Array<SessionHistoryItem>;
    total: number;
};

