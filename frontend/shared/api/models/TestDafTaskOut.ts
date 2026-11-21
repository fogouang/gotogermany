/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TestDafTaskOut = {
    teil_number: number;
    name: string;
    situation?: (string | null);
    instructions?: (string | null);
    prep_seconds: number;
    speak_seconds: number;
    max_score: number;
    stimulus_text?: (string | null);
    stimulus_hidden_after_seconds?: (number | null);
    grafik?: (Record<string, any> | null);
    grafik_seconds?: (number | null);
    gliederung?: (Array<string> | null);
    gliederung_title?: (string | null);
    listen_seconds?: (number | null);
    statement_audio_urls?: Array<string>;
    question_audio_url?: (string | null);
    interlocutor?: (string | null);
};

