/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReferredUserItem } from './ReferredUserItem';
/**
 * Vue complète du dashboard parrainage d'un ambassadeur.
 */
export type ReferralDashboardResponse = {
    referral_link: string;
    referral_code: string;
    referred_count: number;
    total_earnings: number;
    referred_users: Array<ReferredUserItem>;
};

