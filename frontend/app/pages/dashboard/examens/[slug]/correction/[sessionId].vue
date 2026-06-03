<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Chargement -->
    <div
      v-if="correctionStore.loading"
      class="flex flex-col items-center justify-center min-h-screen gap-4"
    >
      <ProgressSpinner style="width: 60px; height: 60px" />
      <p class="text-gray-600 font-medium">{{ t("correction.loading") }}</p>
    </div>

    <!-- Erreur -->
    <div v-else-if="correctionStore.error" class="max-w-lg mx-auto pt-20 px-6">
      <div
        class="bg-red-50 border border-red-200 rounded-xl p-6 text-center space-y-3"
      >
        <i class="pi pi-exclamation-circle text-red-500 text-3xl"></i>
        <p class="font-semibold text-red-700">
          {{ t("correction.not_found") }}
        </p>
        <p class="text-sm text-red-500">{{ correctionStore.error }}</p>
        <Button :label="t('correction.back')" outlined @click="goBack" />
      </div>
    </div>

    <!-- Résultats -->
    <div v-else-if="correction" class="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <!-- En-tête -->
      <div
        class="rounded-2xl p-6 text-white"
        :class="
          correction.passed
            ? 'bg-linear-to-br from-green-500 to-teal-600'
            : 'bg-linear-to-br from-orange-500 to-red-600'
        "
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm opacity-80 font-medium uppercase tracking-wide">
              {{ correction.provider.toUpperCase() }}
              {{ correction.level.toUpperCase() }} — Schreiben
            </p>
            <h1 class="text-3xl font-bold mt-1">
              {{
                correction.passed
                  ? t("correction.passed")
                  : t("correction.failed")
              }}
            </h1>
            <p class="mt-1 opacity-90">
              {{ correction.overall_score }} / {{ correction.max_score }}
              {{ t("correction.points") }} ({{
                Math.round(correction.score_percentage)
              }}%)
            </p>
          </div>

          <!-- Jauge circulaire -->
          <div class="relative w-20 h-20 shrink-0">
            <svg class="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
              <circle
                cx="40"
                cy="40"
                r="32"
                fill="none"
                stroke="rgba(255,255,255,0.2)"
                stroke-width="8"
              />
              <circle
                cx="40"
                cy="40"
                r="32"
                fill="none"
                stroke="white"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="`${(correction.score_percentage / 100) * 201} 201`"
              />
            </svg>
            <span
              class="absolute inset-0 flex items-center justify-center text-lg font-bold"
            >
              {{ correctionStore.cecrlLevel }}
            </span>
          </div>
        </div>

        <div class="mt-4 bg-white/10 rounded-xl p-4">
          <p class="text-sm leading-relaxed">{{ correction.appreciation }}</p>
        </div>
      </div>

      <!-- Scores par critère -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800 flex items-center gap-2">
            <i class="pi pi-chart-bar text-teal-600"></i>
            {{ t("correction.score_detail") }}
          </h2>
        </div>
        <div class="divide-y divide-gray-100">
          <div
            v-for="c in correctionStore.criteriaList"
            :key="c.key"
            class="px-6 py-4"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-semibold text-gray-700">{{
                c.label
              }}</span>
              <span
                class="text-sm font-bold"
                :class="scoreColor(c.score, c.maxScore)"
              >
                {{ c.score }} / {{ c.maxScore }}
              </span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-2 mb-2">
              <div
                class="h-2 rounded-full transition-all"
                :class="barColor(c.score, c.maxScore)"
                :style="{ width: `${(c.score / c.maxScore) * 100}%` }"
              />
            </div>
            <p class="text-xs text-gray-500 leading-relaxed">
              {{ c.feedback }}
            </p>
          </div>
        </div>
      </div>

      <!-- Feedbacks par tâche -->
      <div
        v-for="task in correctionStore.taskList"
        :key="task.key"
        class="bg-white rounded-2xl border border-gray-200 overflow-hidden"
      >
        <div
          class="px-6 py-4 border-b border-gray-100 flex items-center justify-between"
        >
          <h2 class="font-semibold text-gray-800">{{ task.label }}</h2>
          <Button
            :label="
              expandedTasks.has(task.key)
                ? t('correction.hide')
                : t('correction.see_correction')
            "
            :icon="
              expandedTasks.has(task.key)
                ? 'pi pi-chevron-up'
                : 'pi pi-chevron-down'
            "
            iconPos="right"
            text
            size="small"
            @click="toggleTask(task.key)"
          />
        </div>

        <div v-if="expandedTasks.has(task.key)" class="px-6 py-5 space-y-4">
          <!-- Points forts -->
          <div v-if="task.strengths.length" class="space-y-1">
            <p
              class="text-xs font-semibold text-green-700 uppercase tracking-wide"
            >
              {{ t("correction.strengths") }}
            </p>
            <ul class="space-y-1">
              <li
                v-for="(s, i) in task.strengths"
                :key="i"
                class="flex items-start gap-2 text-sm text-gray-700"
              >
                <i
                  class="pi pi-check-circle text-green-500 mt-0.5 shrink-0"
                ></i>
                <span>{{ s }}</span>
              </li>
            </ul>
          </div>

          <!-- À améliorer -->
          <div v-if="task.weaknesses.length" class="space-y-1">
            <p
              class="text-xs font-semibold text-orange-700 uppercase tracking-wide"
            >
              {{ t("correction.to_improve") }}
            </p>
            <ul class="space-y-1">
              <li
                v-for="(w, i) in task.weaknesses"
                :key="i"
                class="flex items-start gap-2 text-sm text-gray-700"
              >
                <i
                  class="pi pi-exclamation-circle text-orange-400 mt-0.5 shrink-0"
                ></i>
                <span>{{ w }}</span>
              </li>
            </ul>
          </div>

          <!-- Texte corrigé -->
          <div v-if="task.correctedText">
            <p
              class="text-xs font-semibold text-teal-700 uppercase tracking-wide mb-2"
            >
              {{ t("correction.corrected_text") }}
            </p>
            <div class="bg-teal-50 border border-teal-200 rounded-xl p-4">
              <p
                class="text-sm text-gray-800 whitespace-pre-line leading-relaxed"
              >
                {{ task.correctedText }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Corrections détaillées -->
      <div
        v-if="correction.corrections_list?.length"
        class="bg-white rounded-2xl border border-gray-200 overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800 flex items-center gap-2">
            <i class="pi pi-pencil text-orange-500"></i>
            {{ t("correction.detailed_corrections") }}
            <span
              class="ml-auto bg-orange-100 text-orange-700 text-xs font-bold px-2 py-0.5 rounded-full"
            >
              {{ correction.corrections_list.length }}
            </span>
          </h2>
        </div>
        <div class="divide-y divide-gray-100">
          <div
            v-for="(c, i) in correction.corrections_list"
            :key="i"
            class="px-6 py-4"
          >
            <div class="flex items-start gap-3">
              <span
                class="text-xs text-gray-400 font-medium mt-0.5 w-14 shrink-0"
              >
                Teil {{ c.task || "1" }}
              </span>
              <div class="flex-1 space-y-1">
                <p class="text-sm">
                  <span class="line-through text-red-500 mr-2">{{
                    c.error
                  }}</span>
                  <span class="text-green-600 font-medium"
                    >→ {{ c.correction }}</span
                  >
                </p>
                <p class="text-xs text-gray-500">{{ c.explanation }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Conseils -->
      <div
        v-if="correction.suggestions?.length"
        class="bg-white rounded-2xl border border-gray-200 overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800 flex items-center gap-2">
            <i class="pi pi-lightbulb text-yellow-500"></i>
            {{ t("correction.tips") }}
          </h2>
        </div>
        <ul class="divide-y divide-gray-100">
          <li
            v-for="(s, i) in correction.suggestions"
            :key="i"
            class="px-6 py-3 flex items-start gap-3 text-sm text-gray-700"
          >
            <span
              class="w-5 h-5 rounded-full bg-yellow-100 text-yellow-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5"
            >
              {{ i + 1 }}
            </span>
            <span>{{ s }}</span>
          </li>
        </ul>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 pb-6">
        <Button
          :label="t('correction.back_to_exam')"
          icon="pi pi-arrow-left"
          outlined
          class="flex-1"
          @click="goBack"
        />
        <Button
          :label="t('correction.my_results')"
          icon="pi pi-trophy"
          class="flex-1"
          @click="goToResults"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCorrectionStore } from "~/stores/correction";

definePageMeta({ layout: "default", middleware: "auth" });

const { t } = useI18n();
const route = useRoute();
const correctionStore = useCorrectionStore();

const slug = route.params.slug as string;
const sessionId = route.params.sessionId as string;

const expandedTasks = ref<Set<string>>(new Set(["task1"]));
const correction = computed(() => correctionStore.current);

const toggleTask = (key: string) => {
  if (expandedTasks.value.has(key)) expandedTasks.value.delete(key);
  else expandedTasks.value.add(key);
};

const goBack = () => {
  navigateTo(
    `/dashboard/examens/${slug}/session?examId=${route.query.examId ?? ""}`,
  );
};

const goToResults = () => {
  navigateTo({
    path: `/dashboard/examens/${slug}/result`,
    query: { sessionId },
  });
};

const scoreColor = (score: number, max: number): string => {
  const pct = score / max;
  if (pct >= 0.7) return "text-green-600";
  if (pct >= 0.5) return "text-orange-500";
  return "text-red-500";
};

const barColor = (score: number, max: number): string => {
  const pct = score / max;
  if (pct >= 0.7) return "bg-green-500";
  if (pct >= 0.5) return "bg-orange-400";
  return "bg-red-400";
};

onMounted(async () => {
  if (correctionStore.current?.session_id === sessionId) return;
  await correctionStore.fetchBySession(sessionId);
});

useHead({ title: t("correction.page_title") });
</script>
