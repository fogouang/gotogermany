/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InfoComparisonSchema } from './InfoComparisonSchema';
import type { OpinionVariantSchema } from './OpinionVariantSchema';
import type { StimulusEmailSchema } from './StimulusEmailSchema';
import type { ThemeSchema } from './ThemeSchema';
export type TaskSchema = {
    teil: number;
    scenario?: string;
    prompts?: Array<string>;
    topic?: string;
    context_ad?: string;
    opinion_quote?: string;
    word_count_min?: number;
    word_count_max?: number;
    stimulus?: (string | Record<string, any> | null);
    stimulus_author?: string;
    themes?: (Record<string, ThemeSchema> | null);
    opinion_variants?: (Record<string, OpinionVariantSchema> | null);
    stimulus_email?: (StimulusEmailSchema | null);
    info_comparison?: (InfoComparisonSchema | null);
    leitpunkte?: Array<string>;
    word_count_target?: (number | null);
    register?: string;
    recipient?: string;
};

