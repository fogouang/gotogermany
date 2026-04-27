/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PlanCreate = {
    name: string;
    duration_days: number;
    /**
     * Prix en FCFA
     */
    price: number;
    is_active?: boolean;
    description?: (string | null);
    display_order?: number;
};

