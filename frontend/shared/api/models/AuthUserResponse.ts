/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
/**
 * Infos user retournées dans la response auth.
 */
export type AuthUserResponse = {
    id: string;
    email: string;
    full_name: string;
    phone?: (string | null);
    is_admin: boolean;
    is_verified: boolean;
    is_ambassador: boolean;
    role: UserRole;
    center_id?: (string | null);
    branch_id?: (string | null);
    requested_branch_id?: (string | null);
};

