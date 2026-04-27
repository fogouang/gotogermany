/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Réponse à la validation d'un code promo avant paiement.
 */
export type PromoCodeValidateResponse = {
    code: string;
    is_valid: boolean;
    discount_type?: (string | null);
    discount_value?: (number | null);
    amount_gross?: (number | null);
    amount_paid?: (number | null);
    discount_amount?: (number | null);
    message: string;
};

