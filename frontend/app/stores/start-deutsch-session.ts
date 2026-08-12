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

interface StartDeutschState {
  subjects: SubjectSummary[];
  subjectsLoading: boolean;

  sessionId: string | null;
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
    // Dérivés de currentQuestion (source de vérité unique) — pas de state
    // séparé à garder synchronisé. Avant ce fix, currentModuleIndex/
    // currentTeilIndex étaient suivis indépendamment de currentQuestionIndex,
    // donc changer d'onglet module ne déplaçait jamais la question affichée
    // (elle restait bloquée sur son ancien index global).
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

    isAnswered: (state) => (questionId: string) => questionId in state.answers,

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

        // 🔍 DEBUG — à retirer une fois que le rendu est stabilisé.
        // Affiche le JSON brut tel que renvoyé par le backend, avant tout
        // traitement (flatten, etc.) — utile pour comparer avec ce qui
        // s'affiche réellement à l'écran.
        console.log("[StartDeutsch] SubjectDetail reçu du backend:", subject);

        const session =
          await StartDeutschService.startSessionApiV1StartDeutschSessionsPost({
            subject_id: subjectId,
          });

        this.sessionId = session.id;
        this.subjectId = subject.id;
        this.subjectTitle = subject.title;
        this.level = subject.level;
        this.subjectNumber = subject.subject_number;
        this.status = session.status;
        this.startedAt = new Date(session.started_at);
        this.modules = subject.modules ?? [];
        this.questions = this._flattenQuestions(this.modules);
        this.currentQuestionIndex = 0;

        // 🔍 DEBUG — la liste aplatie réellement utilisée par le store/UI.
        console.log("[StartDeutsch] questions aplaties:", this.questions);
        console.log("[StartDeutsch] modules:", this.modules);

        return { success: true, sessionId: this.sessionId };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors du démarrage de la session";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
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

    // ── Réponses (sauvegarde locale — envoi groupé au submit) ───

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

        // 🔍 DEBUG — à retirer une fois que le rendu est stabilisé.
        console.log("[StartDeutsch] SessionResultResponse reçu du backend:", result);

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

    // ── Admin — Sujets (liste + suppression) ────────────────────

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

    async adminDeleteSubject(subjectId: string): Promise<{ success: boolean; error?: string }> {
      this._ensureApiConfig();
      try {
        await StartDeutschService.adminDeleteSubjectApiV1StartDeutschAdminSubjectsSubjectIdDelete(subjectId);
        return { success: true };
      } catch (error: any) {
        return { success: false, error: error.body?.detail || "Erreur lors de la suppression." };
      }
    },

    // ── Admin — Import JSON / Audio / Images ────────────────────
    // $fetch natif ici (pas le client OpenAPI généré) — ce sont des
    // endpoints multipart/form-data (fichiers), moins fiables via le
    // client généré. Centralisé dans le store plutôt que dupliqué dans
    // chaque vue (import.vue appelait $fetch directement avant, source
    // de bugs répétés — cf. l'historique CORS/TS de ce module).

    _authHeaders(): HeadersInit {
      const token = useCookie("access_token").value;
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    async adminImportJson(file: File, replace: boolean): Promise<{ success: boolean; data?: any; error?: string }> {
      this._ensureApiConfig();
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("replace", String(replace));

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