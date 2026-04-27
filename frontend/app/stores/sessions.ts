import { defineStore } from "pinia";
import { SessionsService, OpenAPI } from "#shared/api";
import type { AnswerSubmitRequest, SessionResultResponse } from "#shared/api";

interface Question {
  id: string;
  teil_id: string;
  question_number: number;
  question_type: string;
  content: any;
  points: number;
  audio_file?: string | null;
}

interface Teil {
  id: string;
  teil_number: number;
  format_type: string;
  instructions: string | null;
  max_score: number;
  time_minutes: number | null;
  config: any;
  questions: Question[];
}

interface Module {
  id: string;
  slug: string;
  name: string;
  time_limit_minutes: number;
  max_score: number;
  display_order: number;
  teile: Teil[];
}

interface SessionAnswer {
  question_id: string;
  user_answer: Record<string, any>;
}

interface SessionState {
  sessionId: string | null;
  examId: string;
  examName: string;
  modules: Module[];
  currentModuleIndex: number;
  currentTeilIndex: number;
  questions: Question[];
  answers: Record<string, SessionAnswer>;
  currentQuestionIndex: number;
  startTime: Date | null;
  timeRemaining: number;
  status: string;
  isSubmitting: boolean;
  loading: boolean;
  error: string | null;
  result: SessionResultResponse | null;
  subjectId: string | null;
  subjectNumber: number;
  subjectName: string | null;
}

export const useSessionStore = defineStore("session", {
  state: (): SessionState => ({
    sessionId: null,
    examId: "",
    examName: "",
    modules: [],
    currentModuleIndex: 0,
    currentTeilIndex: 0,
    questions: [],
    answers: {},
    currentQuestionIndex: 0,
    startTime: null,
    timeRemaining: 0,
    status: "IN_PROGRESS",
    isSubmitting: false,
    loading: false,
    error: null,
    result: null,
    subjectId: null,
    subjectNumber: 0,
    subjectName: null,
  }),

  getters: {
    currentModule: (state): Module | undefined =>
      state.modules[state.currentModuleIndex],

    currentTeil: (state): Teil | undefined => {
      const module = state.modules[state.currentModuleIndex];
      return module?.teile?.[state.currentTeilIndex];
    },

    currentQuestion: (state): Question | undefined =>
      state.questions[state.currentQuestionIndex],

    totalQuestions: (state) => state.questions.length,

    answeredQuestions: (state) => Object.keys(state.answers).length,

    progress: (state) => {
      if (state.questions.length === 0) return 0;
      return Math.round(
        (Object.keys(state.answers).length / state.questions.length) * 100,
      );
    },

    isLastQuestion: (state) =>
      state.currentQuestionIndex === state.questions.length - 1,

    isFirstQuestion: (state) => state.currentQuestionIndex === 0,

    currentAnswer: (state) => {
      const question = state.questions[state.currentQuestionIndex];
      return question ? state.answers[question.id] : null;
    },

    timeRemainingFormatted: (state) => {
      const minutes = Math.floor(state.timeRemaining / 60);
      const seconds = state.timeRemaining % 60;
      return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    },

    // Questions groupées par teil pour le navigateur
    questionsByTeil: (state) => {
      const map: Record<string, Question[]> = {};
      state.questions.forEach((q) => {
        if (!map[q.teil_id]) map[q.teil_id] = [];
        map[q.teil_id]!.push(q);
      });
      return map;
    },

    isAnswered: (state) => (questionId: string) => questionId in state.answers,
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    async startSession(examId: string, subjectId?: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;

      try {
        const response = await SessionsService.startSessionApiV1SessionsPost({
          exam_id: examId,
          subject_id: subjectId ?? null,
        });

        this.sessionId = response.session_id;
        this.examId = response.exam_id;
        this.examName = response.exam_name;
        this.subjectId = response.subject_id;
        this.subjectNumber = response.subject_number;
        this.subjectName = response.subject_name ?? null;
        this.status = response.status;
        this.startTime = new Date(response.started_at);
        this.modules = (response.modules || []) as Module[];
        this.questions = this._extractQuestions(this.modules);
        this.timeRemaining = (this.modules[0]?.time_limit_minutes ?? 30) * 60;

        // Recharger les réponses existantes si reprise
        if (response.existing_answers) {
          Object.entries(response.existing_answers).forEach(([qId, ans]) => {
            this.answers[qId] = {
              question_id: qId,
              user_answer: ans as Record<string, any>,
            };
          });
        }

        return { success: true, sessionId: this.sessionId };
      } catch (error: any) {
        this.error =
          error.body?.detail || "Erreur lors du démarrage de la session";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    _extractQuestions(modules: Module[]): Question[] {
      const questions: Question[] = [];
      (modules ?? []).forEach((module) => {
        (module.teile ?? []).forEach((teil) => {
          (teil.questions ?? []).forEach((q) => {
            questions.push({
              id: q.id,
              teil_id: teil.id,
              question_number: q.question_number,
              question_type: q.question_type,
              content: q.content,
              points: q.points || 1,
              audio_file: q.audio_file,
            });
          });
        });
      });
      return questions;
    },

    async saveAnswer(questionId: string, userAnswer: Record<string, any>) {
      this._ensureApiConfig();
      if (!this.sessionId)
        return { success: false, error: "No active session" };

      // Sauvegarde locale immédiate
      this.answers[questionId] = {
        question_id: questionId,
        user_answer: userAnswer,
      };

      try {
        const response =
          await SessionsService.submitAnswerApiV1SessionsSessionIdAnswersPost(
            this.sessionId,
            { question_id: questionId, user_answer: userAnswer },
          );
        return { success: true, response };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    async saveBulkAnswers() {
      this._ensureApiConfig();
      if (!this.sessionId)
        return { success: false, error: "No active session" };

      const answersArray: AnswerSubmitRequest[] = Object.values(
        this.answers,
      ).map((a) => ({
        question_id: a.question_id,
        user_answer: a.user_answer,
      }));

      if (answersArray.length === 0) return { success: true };

      try {
        await SessionsService.submitBulkAnswersApiV1SessionsSessionIdAnswersBulkPost(
          this.sessionId,
          { answers: answersArray },
        );
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    nextQuestion() {
      if (!this.isLastQuestion) this.currentQuestionIndex++;
    },

    previousQuestion() {
      if (!this.isFirstQuestion) this.currentQuestionIndex--;
    },

    goToQuestion(index: number) {
      if (index >= 0 && index < this.questions.length)
        this.currentQuestionIndex = index;
    },

    decrementTimer() {
      if (this.timeRemaining > 0) this.timeRemaining--;
    },

    async submitSession() {
      this._ensureApiConfig();
      if (!this.sessionId)
        return { success: false, error: "No active session" };

      this.isSubmitting = true;
      this.error = null;

      try {
        await this.saveBulkAnswers();

        const result =
          await SessionsService.submitSessionApiV1SessionsSessionIdSubmitPost(
            this.sessionId,
          );

        this.status = result.status;
        this.result = result;

        return { success: true, result };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors de la soumission";
        return { success: false, error: this.error };
      } finally {
        this.isSubmitting = false;
      }
    },

    async getResult(sessionId: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;

      try {
        const result =
          await SessionsService.getResultApiV1SessionsSessionIdResultGet(
            sessionId,
          );
        this.result = result;
        return { success: true, result };
      } catch (error: any) {
        this.error =
          error.body?.detail || "Erreur lors de la récupération du résultat";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async getMySessions(skip = 0, limit = 20) {
      this._ensureApiConfig();
      try {
        const data = await SessionsService.getMySessionsApiV1SessionsGet(
          skip,
          limit,
        );
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error.body?.detail, data: [] };
      }
    },

    resetSession() {
      this.$reset();
    },
  },
});
