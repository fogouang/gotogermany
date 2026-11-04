/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SecurityUserInfo } from './SecurityUserInfo';
export type SecurityIncidentResponse = {
    id: string;
    user: SecurityUserInfo;
    rule: string;
    severity: string;
    action: string;
    ip: (string | null);
    user_agent: (string | null);
    status: string;
    created_at: string;
    resolved_at?: (string | null);
    resolution_note?: (string | null);
    details?: Record<string, any>;
};

