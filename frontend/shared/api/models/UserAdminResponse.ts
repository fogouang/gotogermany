/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
/**
 * Réponse étendue pour l'admin.
 */
export type UserAdminResponse = {
    id: string;
    email: string;
    full_name: string;
    phone: (string | null);
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
    ai_credits?: number;
    is_ambassador: boolean;
    role: UserRole;
    is_admin: boolean;
    updated_at: string;
    center_id: (string | null);
    branch_id: (string | null);
};

