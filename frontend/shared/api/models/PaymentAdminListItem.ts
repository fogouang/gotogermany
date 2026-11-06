/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Ligne de la liste admin : élève, achat et références chez le prestataire.
 */
export type PaymentAdminListItem = {
    id: string;
    level_id: (string | null);
    sd_level?: (string | null);
    plan_id: (string | null);
    promo_code_id: (string | null);
    amount_gross: number;
    amount_paid: number;
    discount_amount: number;
    commission_due: number;
    currency: string;
    payment_status: string;
    transaction_reference: string;
    operator: (string | null);
    completed_at: (string | null);
    created_at: string;
    invoice_url?: (string | null);
    charged_amount?: (number | null);
    charged_currency?: (string | null);
    user_id: string;
    user_email?: (string | null);
    user_name?: (string | null);
    level_name?: (string | null);
    pawapay_deposit_id?: (string | null);
    expires_at?: (string | null);
    user_phone?: (string | null);
    kind?: string;
    credits?: (number | null);
    provider_ref?: (string | null);
};

