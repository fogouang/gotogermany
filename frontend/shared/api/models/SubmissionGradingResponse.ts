/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SessionResultResponse } from './SessionResultResponse';
import type { SubmissionRowResponse } from './SubmissionRowResponse';
export type SubmissionGradingResponse = {
    submission: SubmissionRowResponse;
    teacher_comment: (string | null);
    result: (SessionResultResponse | null);
};

