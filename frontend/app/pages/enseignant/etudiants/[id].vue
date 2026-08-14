<!-- pages/enseignant/etudiants/[id].vue -->
<template>
  <div>
    <Button
      icon="pi pi-arrow-left"
      label="Retour à mes sessions"
      text
      size="small"
      class="mb-4"
      @click="router.push('/enseignant/sessions')"
    />

    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div v-else-if="detail" class="space-y-6">
      <!-- En-tête étudiant -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 class="text-lg font-bold text-gray-900">
              {{ detail.student_name }}
            </h2>
            <p class="text-sm text-gray-400 mt-0.5">{{ detail.branch_name }}</p>
          </div>
          <div class="flex gap-6 text-sm">
            <div class="text-center">
              <p class="text-2xl font-bold text-gray-900">
                {{ detail.total_sessions }}
              </p>
              <p class="text-xs text-gray-400">sessions</p>
            </div>
            <div class="text-center">
              <p
                class="text-2xl font-bold"
                :class="scoreClass(detail.overall_average_score)"
              >
                {{
                  detail.overall_average_score !== null
                    ? detail.overall_average_score.toFixed(0)
                    : "—"
                }}
              </p>
              <p class="text-xs text-gray-400">score moyen</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Graphique évolution des scores -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="text-sm font-semibold text-gray-700 mb-4">
          Évolution des scores
        </h3>
        <ScoreEvolutionChart :data="detail.score_history" />
      </div>

      <!-- Ventilation par examen -->
      <div
        v-for="exam in detail.exams"
        :key="exam.exam_id"
        class="bg-white rounded-xl border border-gray-200 p-5"
      >
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-semibold text-gray-900">
              {{ exam.exam_name }}
            </h3>
            <p class="text-xs text-gray-400 mt-0.5">
              {{ exam.total_sessions }} session(s)
              <span v-if="exam.last_session_at">
                · dernière le {{ formatDate(exam.last_session_at) }}
              </span>
            </p>
          </div>
          <p class="text-xl font-bold" :class="scoreClass(exam.average_score)">
            {{
              exam.average_score !== null
                ? exam.average_score.toFixed(0) + "/100"
                : "—"
            }}
          </p>
        </div>

        <div
          v-for="subject in exam.subjects"
          :key="subject.subject_id"
          class="border-t border-gray-100 pt-4 mt-4 first:border-0 first:pt-0 first:mt-0"
        >
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs font-medium text-gray-600">
              {{ subject.subject_name }}
            </p>
            <div class="flex items-center gap-3">
              <p
                class="text-sm font-semibold"
                :class="scoreClass(subject.average_score)"
              >
                {{
                  subject.average_score !== null
                    ? subject.average_score.toFixed(0) + "/100"
                    : "—"
                }}
              </p>
              <Button
                v-if="subject.last_session_id"
                label="Voir le détail"
                text
                size="small"
                @click="openResultDialog(subject.last_session_id)"
              />
            </div>
          </div>

          <!-- Détail par module : score + compteurs question par question -->
          <div class="space-y-2 mt-2">
            <div
              v-for="mod in subject.modules"
              :key="mod.module_name"
              class="flex items-center justify-between text-sm bg-gray-50 rounded-lg px-3 py-2"
            >
              <span class="text-gray-700">{{ mod.module_name }}</span>
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-500">
                  {{ mod.questions_correct }} correctes ·
                  {{ mod.questions_incorrect }} échouées /
                  {{ mod.questions_total }}
                </span>
                <span
                  class="font-semibold"
                  :class="scoreClass(mod.average_score)"
                >
                  {{
                    mod.average_score !== null
                      ? mod.average_score.toFixed(0)
                      : "—"
                  }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="detail.exams.length === 0"
        class="text-center py-8 text-gray-400 text-sm"
      >
        Aucune session complétée pour l'instant.
      </div>

      <!-- Commentaires enseignant -->
      <div class="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
        <h3 class="text-sm font-semibold text-gray-700">
          Commentaires ({{ comments.length }})
        </h3>

        <div class="space-y-3">
          <div
            v-for="c in comments"
            :key="c.id"
            class="bg-gray-50 rounded-lg px-4 py-3"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-semibold text-gray-700">{{
                c.teacher_name
              }}</span>
              <span class="text-xs text-gray-400">{{
                formatDate(c.created_at)
              }}</span>
            </div>
            <p class="text-sm text-gray-700 whitespace-pre-wrap">
              {{ c.comment }}
            </p>
          </div>
          <p
            v-if="comments.length === 0"
            class="text-sm text-gray-400"
          >
            Aucun commentaire pour l'instant.
          </p>
        </div>

        <div class="space-y-2">
          <Textarea
            v-model="newComment"
            rows="3"
            class="w-full"
            placeholder="Ajouter un commentaire sur cet étudiant (ex: faiblesse constatée)…"
          />
          <div class="flex items-center gap-3">
            <Button
              label="Publier"
              size="small"
              :loading="postingComment"
              :disabled="!newComment.trim()"
              @click="handlePostComment"
            />
            <p v-if="commentError" class="text-sm text-red-600">
              {{ commentError }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialog détail question par question -->
    <Dialog
      v-model:visible="showResultDialog"
      header="Détail de la session"
      modal
      :style="{ width: '90vw', maxWidth: '48rem' }"
    >
      <div v-if="loadingResult" class="flex justify-center py-8">
        <i class="pi pi-spin pi-spinner text-2xl text-emerald-600"></i>
      </div>
      <div v-else-if="sessionResult" class="space-y-4">
        <div
          v-for="mod in sessionResult.modules"
          :key="mod.slug"
          class="border border-gray-100 rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-2">
            <p class="font-semibold text-gray-900 text-sm">{{ mod.name }}</p>
            <span class="text-xs text-gray-500">
              {{ mod.questions_correct }}/{{ mod.questions_total }} correctes
            </span>
          </div>
          <div
            v-for="teil in mod.teile"
            :key="teil.teil_number"
            class="mt-2 space-y-1"
          >
            <p
              v-for="ans in teil.answers"
              :key="ans.question_id"
              class="text-xs flex items-center justify-between px-2 py-1 rounded"
              :class="ans.is_correct ? 'bg-emerald-50' : 'bg-red-50'"
            >
              <span>Question {{ ans.question_number }}</span>
              <i
                :class="
                  ans.is_correct
                    ? 'pi pi-check text-emerald-600'
                    : 'pi pi-times text-red-500'
                "
              />
            </p>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Fermer" text @click="showResultDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "enseignant",
  middleware: "teacher",
});

import type {
  StudentDetailedProgressResponse,
  TeacherCommentResponse,
} from "#shared/api";
import ScoreEvolutionChart from "~/components/centre/ScoreEvolutionChart.vue";

const route = useRoute();
const router = useRouter();
const teacherPortalStore = useTeacherPortalStore();

const studentId = route.params.id as string;

const loading = ref(true);
const detail = ref<StudentDetailedProgressResponse | null>(null);
const errorMessage = ref<string | null>(null);

const comments = ref<TeacherCommentResponse[]>([]);
const newComment = ref("");
const postingComment = ref(false);
const commentError = ref<string | null>(null);

const showResultDialog = ref(false);
const loadingResult = ref(false);
const sessionResult = ref<any>(null);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("fr-FR");
}

function scoreClass(score: number | null) {
  if (score === null) return "text-gray-400";
  if (score >= 60) return "text-emerald-600";
  return "text-amber-600";
}

async function loadDetail() {
  loading.value = true;
  const result = await teacherPortalStore.fetchStudentProgress(studentId);
  if (result.success && result.detail) {
    detail.value = result.detail;
  } else {
    errorMessage.value = result.error || "Erreur de chargement.";
  }

  const commentsResult = await teacherPortalStore.fetchComments(studentId);
  if (commentsResult.success) {
    comments.value = commentsResult.comments ?? [];
  }

  loading.value = false;
}

async function handlePostComment() {
  if (!newComment.value.trim()) return;
  postingComment.value = true;
  commentError.value = null;

  const result = await teacherPortalStore.addComment(studentId, {
    comment: newComment.value.trim(),
  });

  postingComment.value = false;

  if (result.success && result.comment) {
    comments.value.unshift(result.comment);
    newComment.value = "";
  } else {
    commentError.value = result.error || "Erreur lors de la publication.";
  }
}

async function openResultDialog(sessionId: string) {
  showResultDialog.value = true;
  loadingResult.value = true;
  sessionResult.value = null;

  const result = await teacherPortalStore.fetchSessionResult(studentId, sessionId);
  if (result.success) {
    sessionResult.value = result.result;
  }
  loadingResult.value = false;
}

onMounted(loadDetail);
</script>