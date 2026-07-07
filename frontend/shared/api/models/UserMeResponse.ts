/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
/**
 * Réponse pour /users/me — inclut le contexte centre/branch si applicable.
 */
export type UserMeResponse = {
    id: string;
    email: string;
    full_name: string;
    phone: (string | null);
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
    ai_credits?: number;
    role: UserRole;
    center_id: (string | null);
    branch_id: (string | null);
    target_level_id: (string | null);
    access_expires_at: (string | null);
};

