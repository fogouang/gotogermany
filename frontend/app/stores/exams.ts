//store/exams.ts
import { defineStore } from "pinia";
import { ExamsService, OpenAPI } from "#shared/api";
import type { ExamCatalogResponse, ExamDetailResponse } from "#shared/api";

interface ExamsState {
  catalog: ExamCatalogResponse[];
  currentExam: ExamDetailResponse | null;
  loading: boolean;
  error: string | null;
}

export const useExamsStore = defineStore("exams", {
  state: (): ExamsState => ({
    catalog: [],
    currentExam: null,
    loading: false,
    error: null,
  }),

  getters: {
    examsByProvider: (state) => {
      const grouped: Record<string, ExamCatalogResponse[]> = {};
      (state.catalog ?? []).forEach((exam) => {
        const provider = exam.provider || "unknown";
        if (!grouped[provider]) grouped[provider] = [];
        grouped[provider].push(exam);
      });
      return grouped;
    },

    allLevels: (state) => {
      const levels: any[] = [];
      (state.catalog ?? []).forEach((exam) => {
        (exam.levels ?? []).forEach((level) => {
          levels.push({ ...level, examName: exam.name, examSlug: exam.slug });
        });
      });
      return levels;
    },

    freeLevels: (state) => {
      const levels: any[] = [];
      (state.catalog ?? []).forEach((exam) => {
        (exam.levels ?? [])
          .filter((level) => level.is_free)
          .forEach((level) => {
            levels.push({ ...level, examName: exam.name, examSlug: exam.slug });
          });
      });
      return levels;
    },
  },

  actions: {
    _ensureApiConfig() {
      const config = useRuntimeConfig();
      OpenAPI.BASE = config.public.apiBaseUrl || "http://localhost:8001";
      const tokenCookie = useCookie("access_token");
      OpenAPI.TOKEN = tokenCookie.value ?? undefined;
    },

    async fetchCatalog() {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const catalog = await ExamsService.getCatalogApiV1ExamsGet();
        this.catalog = catalog;
        return { success: true, data: catalog };
      } catch (error: any) {
        console.error("Fetch catalog error:", error);
        this.error = error.body?.detail || "Erreur lors du chargement";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchExamDetail(examId: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const exam =
          await ExamsService.getExamDetailApiV1ExamsExamIdGet(examId);
        this.currentExam = exam;
        return { success: true, data: exam };
      } catch (error: any) {
        console.error("Fetch exam detail error:", error);
        this.error = error.body?.detail || "Erreur lors du chargement";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchExamBySlug(slug: string) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const exam =
          await ExamsService.getExamBySlugApiV1ExamsSlugSlugGet(slug);
        this.currentExam = exam;
        return { success: true, data: exam };
      } catch (error: any) {
        console.error("Fetch exam by slug error:", error);
        this.error = error.body?.detail || "Examen introuvable";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    clearCurrentExam() {
      this.currentExam = null;
    },

    async importJson(file: File, replace = false) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const result =
          await ExamsService.importExamJsonApiV1ExamsAdminImportPost({
            file: file as any,
            replace,
          });
        await this.fetchCatalog(); // rafraîchir le catalogue
        return { success: true, data: result };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors de l'import";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async importAudio(examId: string, files: File[], subjectNumber: number) {
      this._ensureApiConfig();
      this.loading = true;
      this.error = null;
      try {
        const result =
          await ExamsService.importExamAudioApiV1ExamsAdminExamIdAudioPost(
            examId,
            {
              files: files as any,
              subject_number: subjectNumber,
            },
          );
        return { success: true, data: result };
      } catch (error: any) {
        this.error = error.body?.detail || "Erreur lors de l'import audio";
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },
  },
});
