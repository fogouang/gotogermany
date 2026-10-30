// stores/start-deutsch-session.ts
import { defineStore } from "pinia";
import { StartDeutschService, OpenAPI } from "#shared/api";
import type {
  StartDeutschSubjectSummary as SubjectSummary,
  StartDeutschSubjectDetail as SubjectDetail,
  StartDeutschModulePublic as ModulePublic,
  StartDeutschTeilPublic as TeilPublic,
  StartDeutschQuestionPublic as QuestionPublic,
  StartDeutschSessionListItem as SessionListItem,
  StartDeutschSessionResultResponse as SessionResultResponse,
  StartDeutschSchreibenCorrectionResponse as SchreibenCorrectionResponse,
} from "#shared/api";

interface FlatQuestion extends QuestionPublic {
  teil_id: string;
  format_type: string;
}

interface SessionAnswer {
  question_id: string;
  user_answer: Record<string, any>;
}

export interface StartDeutschMediaFile {
  filename: string;
  teil_number: number;
  module?: string;
  imported: boolean;
}

export interface StartDeutschMediaStatus {
  subject_id: string;
  audio: StartDeutschMediaFile[];
  images: StartDeutschMediaFile[];
}

interface StartDeutschState {
  subjects: SubjectSummary[];
  subjectsLoading: boolean;

  sessionId: string | null;
  /** Renseigné quand la session est la copie d'un devoir */
  assignmentId: string | null;
  subjectId: string | null;
  subjectTitle: string;
  level: string;
  subjectNumber: number;

  modules: ModulePublic[];
  questions: FlatQuestion[];
  currentQuestionIndex: number;
  answers: Record<string, SessionAnswer>;

  status: string;
  startedAt: Date | null;

  isSubmitting: boolean;
  loading: boolean;
  error: string | null;

  result: SessionResultResponse | null;
  schreibenCorrection: SchreibenCorrectionResponse | null;
}

export const useStartDeutschSessionStore = defineStore("start-deutsch-session", {
  state: (): StartDeutschState => ({
    subjects: [],
    subjectsLoading: false,

    sessionId: null,
    assignmentId: null,
    subjectId: null,
    subjectTitle: "",
    level: "",
    subjectNumber: 0,

    modules: [],
    questions: [],
    currentQuestionIndex: 0,
    answers: {},

    status: "IN_PROGRESS",
    startedAt: null,

    isSubmitting: false,
    loading: false,
    error: null,

    result: null,
    schreibenCorrection: null,
  }),

  getters: {
    // Teil, module et index de module se déduisent de la question en cours :
    // un seul état à tenir à jour (currentQuestionIndex).
    currentQuestion: (state): FlatQuestion | undefined =>
      state.questions[state.currentQuestionIndex],

    currentTeil(): TeilPublic | undefined {
      const q = this.currentQuestion as FlatQuestion | undefined;
      if (!q) return undefined;
      for (const module of this.modules as ModulePublic[]) {
        const teil = module.teile?.find((t) => t.id === q.teil_id);
        if (teil) return teil;
      }
      return undefined;
    },

    currentModule(): ModulePublic | undefined {
      const teil = this.currentTeil as TeilPublic | undefined;
      if (!teil) return undefined;
      return (this.modules as ModulePublic[]).find((m) => m.teile?.some((t) => t.id === teil.id));
    },

    currentModuleIndex(): number {
      const mod = this.currentModule as ModulePublic | undefined;
      if (!mod) return 0;
      return (this.modules as ModulePublic[]).findIndex((m) => m.id === mod.id);
    },

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
      const q = state.questions[state.currentQuestionIndex];
      return q ? state.answers[q.id] : null;
    },

    // Une réponse vide (champ effacé, texte supprimé) ne compte pas
    isAnswered: (state) => (questionId: string) => {
      const value = state.answers[questionId]?.user_answer;
      if (!value) return false;
      return Object.values(value).some((v) => v != null && String(v).trim() !== "");
    },

    questionsByTeil: (state) => {
      const map: Record<string, FlatQuestion[]> = {};
      state.questions.forEach((q) => {
        if (!map[q.teil_id]) map[q.teil_id] = [];
        map[q.teil_id]!.push(q);
      });
      return map;
    },
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    // ── Catalogue ──────────────────────────────────────────────

    async fetchSubjects(level?: "A1" | "A2") {
      this._ensureApiConfig();
      this.subjectsLoading = true;
      try {
        this.subjects =
          await StartDeutschService.listSubjectsApiV1StartDeutschSubjectsGet(level);
        return { success: true };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors du chargement du catalogue";
        return { success: false, error: this.error };
      } finally {
        this.subjectsLoading = false;
      }
    },

    // ── Session ────────────────────────────────────────────────

    async startSession(subjectId: string) {
      this._ensureApiConfig();
      this.$reset();
      this.loading = true;
      this.error = null;

      try {
        const subject: SubjectDetail =
          await StartDeutschService.getSubjectDetailApiV1StartDeutschSubjectsSubjectIdGet(subjectId);

        const session =
          await StartDeutschService.startSessionApiV1StartDeutschSessionsPost({
            subject_id: subjectId,
          });

        this._applySession(subject, session);
        return { success: true, sessionId: this.sessionId };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors du démarrage de la session";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    /** Devoir Start Deutsch : la session est créée (ou reprise) par le module des devoirs */
    async startAssignment(assignmentId: string) {
      this._ensureApiConfig();
      this.$reset();
      this.loading = true;
      this.error = null;

      try {
        const session = await $fetch<{
          id: string;
          subject_id: string;
          status: string;
          started_at: string;
        }>(`${OpenAPI.BASE}/api/v1/assignments/${assignmentId}/start-deutsch/start`, {
          method: "POST",
          headers: this._authHeaders(),
        });

        const subject: SubjectDetail =
          await StartDeutschService.getSubjectDetailApiV1StartDeutschSubjectsSubjectIdGet(session.subject_id);

        this._applySession(subject, session);
        this.assignmentId = assignmentId;
        return { success: true, sessionId: this.sessionId };
      } catch (error: any) {
        this.error = error?.data?.detail || error.body?.detail || "Impossible d'ouvrir ce devoir";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    _applySession(
      subject: SubjectDetail,
      session: { id: string; status: string; started_at: string },
    ) {
      this.sessionId = session.id;
      this.subjectId = subject.id;
      this.subjectTitle = subject.title;
      this.level = subject.level;
      this.subjectNumber = subject.subject_number;
      this.status = session.status;
      this.startedAt = new Date(session.started_at);
      this.modules = this._sortTree(subject.modules ?? []);
      this.questions = this._flattenQuestions(this.modules);
      this.currentQuestionIndex = 0;
    },

    /** Modules, Teile et questions dans l'ordre de l'examen */
    _sortTree(modules: ModulePublic[]): ModulePublic[] {
      return [...modules]
        .sort((a, b) => a.order - b.order)
        .map((m) => ({
          ...m,
          teile: [...(m.teile ?? [])]
            .sort((a, b) => a.teil_number - b.teil_number)
            .map((t) => ({
              ...t,
              questions: [...(t.questions ?? [])].sort(
                (a, b) => a.question_number - b.question_number,
              ),
            })),
        }));
    },

    _flattenQuestions(modules: ModulePublic[]): FlatQuestion[] {
      const questions: FlatQuestion[] = [];
      (modules ?? []).forEach((module) => {
        (module.teile ?? []).forEach((teil) => {
          (teil.questions ?? []).forEach((q) => {
            questions.push({
              ...q,
              teil_id: teil.id,
              format_type: teil.format_type,
            });
          });
        });
      });
      return questions;
    },

    // ── Réponses (gardées localement, envoyées à la soumission) ──

    setAnswer(questionId: string, userAnswer: Record<string, any>) {
      this.answers[questionId] = { question_id: questionId, user_answer: userAnswer };
    },

    nextQuestion() {
      if (!this.isLastQuestion) this.currentQuestionIndex++;
    },
    previousQuestion() {
      if (!this.isFirstQuestion) this.currentQuestionIndex--;
    },
    goToQuestion(index: number) {
      if (index >= 0 && index < this.questions.length) this.currentQuestionIndex = index;
    },
    switchToModule(index: number) {
      const targetModule = this.modules[index];
      if (!targetModule) return;
      const firstTeilWithQuestions = targetModule.teile?.find((t) => (t.questions?.length ?? 0) > 0);
      const firstQuestionId = firstTeilWithQuestions?.questions?.[0]?.id;
      if (!firstQuestionId) return;
      const globalIndex = this.questions.findIndex((q) => q.id === firstQuestionId);
      if (globalIndex >= 0) this.currentQuestionIndex = globalIndex;
    },

    // ── Soumission ─────────────────────────────────────────────

    async submitSession() {
      this._ensureApiConfig();
      if (!this.sessionId) return { success: false, error: "Aucune session active" };

      this.isSubmitting = true;
      this.error = null;

      try {
        const answersArray = Object.values(this.answers).map((a) => ({
          question_id: a.question_id,
          user_answer: a.user_answer,
        }));

        const response =
          await StartDeutschService.submitSessionApiV1StartDeutschSessionsSessionIdSubmitPost(
            this.sessionId,
            { answers: answersArray },
          );

        this.status = response.status;
        return { success: true, response };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors de la soumission";
        return { success: false, error: this.error };
      } finally {
        this.isSubmitting = false;
      }
    },

    // ── Résultat ───────────────────────────────────────────────

    async getResult(sessionId: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;

      try {
        const result =
          await StartDeutschService.getSessionResultApiV1StartDeutschSessionsSessionIdResultGet(sessionId);
        this.result = result;

        return { success: true, result };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors de la récupération du résultat";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async getMySessions(skip = 0, limit = 20): Promise<{ success: boolean; data: SessionListItem[]; error?: string }> {
      this._ensureApiConfig();
      try {
        const data =
          await StartDeutschService.listMySessionsApiV1StartDeutschSessionsGet(skip, limit);
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error.body?.detail, data: [] };
      }
    },

    // ── Admin : sujets ─────────────────────────────────────────

    async adminListSubjects(
      level?: "A1" | "A2",
    ): Promise<{ success: boolean; data: SubjectSummary[]; error?: string }> {
      this._ensureApiConfig();
      try {
        const data =
          await StartDeutschService.adminListSubjectsApiV1StartDeutschAdminSubjectsGet(level);
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error.body?.detail, data: [] };
      }
    },

    /** Activer, désactiver, rendre privé (banque des enseignants) ou public */
    async adminUpdateSubject(
      subjectId: string,
      data: { is_active?: boolean; is_private?: boolean },
    ): Promise<{ success: boolean; data?: SubjectSummary; error?: string }> {
      this._ensureApiConfig();
      try {
        const url: string = `${OpenAPI.BASE}/api/v1/start-deutsch/admin/subjects/${subjectId}`;
        const updated = await $fetch<SubjectSummary>(url, {
          method: "PATCH",
          body: data,
          headers: this._authHeaders(),
        });
        return { success: true, data: updated };
      } catch (error: any) {
        return { success: false, error: error?.data?.detail || error?.message || "Erreur lors de la mise à jour." };
      }
    },

    async adminDeleteSubject(subjectId: string): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        await StartDeutschService.adminDeleteSubjectApiV1StartDeutschAdminSubjectsSubjectIdDelete(subjectId);
        return { success: true };
      } catch (error: any) {
        return {
          success: false,
          error: error.body?.detail || error?.data?.detail || "Erreur lors de la suppression.",
        };
      }
    },

    // ── Admin : import JSON, audio, images ─────────────────────
    // $fetch plutôt que le client OpenAPI : envois multipart (fichiers).

    _authHeaders(): HeadersInit {
      const token = useCookie("access_token").value;
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    async adminImportJson(file: File): Promise<{ success: boolean; data?: any; error?: string }> {
      this._ensureApiConfig();
      try {
        const formData = new FormData();
        formData.append("file", file);

        const url: string = `${OpenAPI.BASE}/api/v1/start-deutsch/admin/import`;
        const data = await $fetch(url, {
          method: "POST",
          body: formData,
          headers: this._authHeaders(),
        });
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error?.data?.detail || error?.message || "Erreur lors de l'import." };
      }
    },

    async adminImportAudio(
      subjectId: string,
      files: File[],
    ): Promise<{ success: boolean; data?: any; error?: string }> {
      this._ensureApiConfig();
      try {
        const formData = new FormData();
        formData.append("subject_id", subjectId);
        files.forEach((f) => formData.append("files", f));

        const url: string = `${OpenAPI.BASE}/api/v1/start-deutsch/admin/audio`;
        const data = await $fetch(url, {
          method: "POST",
          body: formData,
          headers: this._authHeaders(),
        });
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error?.data?.detail || error?.message || "Erreur lors de l'import audio." };
      }
    },

    async adminImportImages(
      subjectId: string,
      files: File[],
    ): Promise<{ success: boolean; data?: any; error?: string }> {
      this._ensureApiConfig();
      try {
        const formData = new FormData();
        formData.append("subject_id", subjectId);
        files.forEach((f) => formData.append("files", f));

        const url: string = `${OpenAPI.BASE}/api/v1/start-deutsch/admin/images`;
        const data = await $fetch(url, {
          method: "POST",
          body: formData,
          headers: this._authHeaders(),
        });
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error?.data?.detail || error?.message || "Erreur lors de l'import images." };
      }
    },

    /** Fichiers audio et images attendus par un sujet, et ceux déjà importés */
    async adminMediaStatus(subjectId: string): Promise<{ success: boolean; data?: StartDeutschMediaStatus; error?: string }> {
      this._ensureApiConfig();
      try {
        const url: string = `${OpenAPI.BASE}/api/v1/start-deutsch/admin/subjects/${subjectId}/media`;
        const data = await $fetch<StartDeutschMediaStatus>(url, { headers: this._authHeaders() });
        return { success: true, data };
      } catch (error: any) {
        return { success: false, error: error?.data?.detail || error?.message || "Impossible de lire les médias du sujet." };
      }
    },

    // ── Correction Schreiben ──────────────────────────────────

    async correctSchreiben(teilId: string, submittedText: string) {
      this._ensureApiConfig();
      if (!this.sessionId) return { success: false, error: "Aucune session active" };

      try {
        const correction =
          await StartDeutschService.correctSchreibenApiV1StartDeutschSessionsSessionIdSchreibenCorrectionPost(
            this.sessionId,
            { teil_id: teilId, submitted_text: submittedText },
          );
        this.schreibenCorrection = correction;
        return { success: true, correction };
      } catch (error: any) {
        return { success: false, error: error.body?.detail };
      }
    },

    resetSession() {
      this.$reset();
    },
  },
});