/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SecurityUserInfo } from './SecurityUserInfo';
export type SecurityBlockResponse = {
    user: SecurityUserInfo;
    reason: string;
    incident_id: (string | null);
    blocked_at: string;
};

