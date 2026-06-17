<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Erreur -->
    <div
      v-else-if="!result"
      class="text-center py-16 bg-white rounded-xl border border-gray-100"
    >
      <i
        class="pi pi-exclamation-triangle text-4xl text-red-400 mb-3 block"
      ></i>
      <p class="font-medium text-gray-700">{{ t("result.not_found") }}</p>
      <Button
        :label="t('result.back_to_exams')"
        outlined
        class="mt-4"
        @click="navigateTo('/dashboard/examens')"
      />
    </div>

    <div v-else class="space-y-6">
      <!-- En-tête -->
      <div
        class="rounded-2xl p-6 text-white"
        :class="
          result.passed === true
            ? 'bg-linear-to-br from-green-500 to-teal-600'
            : result.passed === false
              ? 'bg-linear-to-br from-orange-500 to-red-500'
              : 'bg-linear-to-br from-gray-600 to-gray-700'
        "
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm opacity-75 font-medium mb-1">
              {{ result.exam_name }} · {{ t("result.subject") }}
              {{ result.subject_number }}
              <span
                v-if="isSingleModule"
                class="ml-2 bg-white/20 px-2 py-0.5 rounded-full text-xs"
              >
                {{ displayedModules[0]?.name }}
              </span>
            </p>
            <h1 class="text-2xl font-bold">
              {{
                result.passed === true
                  ? t("result.passed")
                  : result.passed === false
                    ? t("result.failed")
                    : t("result.pending")
              }}
            </h1>
            <p class="mt-1 opacity-80 text-sm">{{ result.result_message }}</p>
          </div>

          <!-- Score global -->
          <div class="text-center shrink-0">
            <div class="text-4xl font-extrabold">
              {{ result.score != null ? result.score.toFixed(0) : "-" }}
            </div>
            <div class="text-xs opacity-70 mt-0.5">
              / 100 · {{ t("result.min_score") }} {{ result.total_pass_score }}
            </div>
            <div v-if="actualDuration" class="text-xs opacity-60 mt-1">
              {{ actualDuration }}
            </div>
          </div>
        </div>
      </div>

      <!-- Modules -->
      <div
        class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800">
            {{
              isSingleModule
                ? t("result.module_result")
                : t("result.modules_result")
            }}
          </h2>
        </div>
        <div class="divide-y divide-gray-50">
          <div
            v-for="module in displayedModules"
            :key="module.slug"
            class="px-6 py-4 flex items-center gap-4"
          >
            <div
              :class="[
                'w-10 h-10 rounded-xl flex items-center justify-center shrink-0',
                getModuleBg(module.slug),
              ]"
            >
              <i
                :class="[
                  'pi',
                  getModuleIcon(module.slug),
                  getModuleIconColor(module.slug),
                ]"
              ></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900">{{ module.name }}</p>
              <div v-if="module.is_corrected" class="mt-1.5">
                <div class="flex items-center gap-2 mb-1">
                  <div class="flex-1 bg-gray-100 rounded-full h-1.5">
                    <div
                      class="h-1.5 rounded-full transition-all"
                      :class="
                        (module.score_obtained ?? 0) >= 60
                          ? 'bg-green-500'
                          : 'bg-orange-400'
                      "
                      :style="{ width: `${moduleScorePercent(module)}%` }"
                    />
                  </div>
                  <span class="text-sm font-bold text-gray-700 shrink-0">
                    {{ module.score_obtained?.toFixed(1) ?? "-" }} / {{ module.max_score }}
                  </span>
                </div>
              </div>
              <div
                v-else
                class="flex items-center gap-1.5 mt-1 text-amber-600 text-xs"
              >
                <i class="pi pi-clock text-xs"></i>
                <span>{{ t("result.waiting_correction") }}</span>
              </div>
            </div>
            <Button
              v-if="module.slug.includes('schreiben') && module.is_corrected"
              :label="t('result.see_correction')"
              icon="pi pi-eye"
              size="small"
              outlined
              severity="secondary"
              @click="goToSchreibenCorrection"
            />
          </div>
        </div>
      </div>

      <!-- Détail des réponses -->
      <div
        v-for="module in displayedModules.filter(
          (m) => !m.slug.includes('schreiben'),
        )"
        :key="`detail-${module.slug}`"
        class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <button
          class="w-full flex items-center justify-between px-6 py-4 border-b border-gray-100 hover:bg-gray-50 transition-colors"
          @click="toggleModule(module.slug)"
        >
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
                getModuleBg(module.slug),
              ]"
            >
              <i
                :class="[
                  'pi text-sm',
                  getModuleIcon(module.slug),
                  getModuleIconColor(module.slug),
                ]"
              ></i>
            </div>
            <h2 class="font-semibold text-gray-800">
              {{ t("result.detail_title") }} - {{ module.name }}
            </h2>
          </div>
          <i
            :class="[
              'pi text-gray-400',
              expandedModules.has(module.slug)
                ? 'pi-chevron-up'
                : 'pi-chevron-down',
            ]"
          ></i>
        </button>

        <div v-if="expandedModules.has(module.slug)">
          <div
            v-for="teil in module.teile"
            :key="teil.teil_number"
            class="border-b border-gray-50 last:border-0"
          >
            <div class="px-6 py-3 bg-gray-50 flex items-center justify-between">
              <p
                class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
              >
                Teil {{ teil.teil_number }}
              </p>
              <span class="text-xs font-bold text-gray-600">
                {{ teil.score_obtained?.toFixed(1) ?? "-" }} /
                {{ teil.max_score }} pts
              </span>
            </div>
            <div class="divide-y divide-gray-50">
              <div
                v-for="answer in teil.answers"
                :key="answer.question_id"
                class="px-6 py-3 flex items-start gap-3"
              >
                <div class="shrink-0 mt-0.5">
                  <i
                    v-if="answer.is_correct === true"
                    class="pi pi-check-circle text-green-500"
                  ></i>
                  <i
                    v-else-if="answer.is_correct === false"
                    class="pi pi-times-circle text-red-400"
                  ></i>
                  <i v-else class="pi pi-circle text-gray-300"></i>
                </div>
                <div class="flex-1 min-w-0 text-sm">
                  <div class="flex flex-wrap gap-4 text-gray-600">
                    <span>
                      Q{{ answer.question_number }} -
                      {{ t("result.your_answer") }} :
                      <strong class="text-gray-900">{{
                        formatAnswer(answer.user_answer)
                      }}</strong>
                    </span>
                    <span
                      v-if="
                        answer.correct_answer && answer.is_correct === false
                      "
                      class="text-green-700"
                    >
                      {{ t("result.correct_answer") }} :
                      <strong>{{ formatAnswer(answer.correct_answer) }}</strong>
                    </span>
                  </div>
                  <p v-if="answer.feedback" class="text-xs text-gray-400 mt-1">
                    {{ answer.feedback }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col sm:flex-row gap-3 pb-6">
        <Button
          :label="t('result.back_to_exams')"
          icon="pi pi-arrow-left"
          outlined
          class="flex-1"
          @click="navigateTo('/dashboard/examens')"
        />
        <Button
          v-if="isSingleModule"
          :label="t('result.another_module')"
          icon="pi pi-list"
          outlined
          class="flex-1"
          @click="router.back()"
        />
        <Button
          :label="t('result.my_results')"
          icon="pi pi-trophy"
          class="flex-1"
          @click="navigateTo('/dashboard/resultats')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ModuleResultResponse, SessionResultResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const route = useRoute();
const router = useRouter();
const sessionStore = useSessionStore();
const { t } = useI18n();

const loading = ref(true);
const result = ref<SessionResultResponse | null>(null);
const expandedModules = ref<Set<string>>(new Set());

// Détecte si on vient d'un module seul
const moduleSlug = computed(() => route.query.moduleSlug as string | undefined);
const isSingleModule = computed(() => !!moduleSlug.value);

// Filtre les modules à afficher
const displayedModules = computed(() => {
  if (!result.value?.modules) return [];
  if (isSingleModule.value) {
    return result.value.modules.filter((m) =>
      m.slug.toLowerCase().includes(moduleSlug.value!.toLowerCase()),
    );
  }
  return result.value.modules;
});

const toggleModule = (slug: string) => {
  if (expandedModules.value.has(slug)) expandedModules.value.delete(slug);
  else expandedModules.value.add(slug);
};

// ── Navigation ───────────────────────────────────────────

const goToSchreibenCorrection = () => {
  const slug = route.params.slug as string;
  const sessionId = result.value?.session_id;
  if (!sessionId) return;
  navigateTo({
    path: `/dashboard/examens/${slug}/correction/${sessionId}`,
    query: { examId: result.value?.exam_id },
  });
};

// ── Helpers ──────────────────────────────────────────────

const actualDuration = computed(() => {
  if (!result.value?.submitted_at || !result.value?.started_at) return null;
  const start = new Date(result.value.started_at).getTime();
  const end = new Date(result.value.submitted_at).getTime();
  const seconds = Math.round((end - start) / 1000);
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m${s.toString().padStart(2, "0")}s`;
});

const formatAnswer = (answer: Record<string, any> | null): string => {
  if (!answer) return "-";
  return answer.answer ?? answer.text ?? JSON.stringify(answer);
};

const getModuleIcon = (s: string) => {
  if (s.includes("lesen")) return "pi-book";
  if (s.includes("horen") || s.includes("hören")) return "pi-volume-up";
  if (s.includes("schreiben")) return "pi-pencil";
  if (s.includes("sprechen")) return "pi-microphone";
  return "pi-file";
};

const getModuleBg = (s: string) => {
  if (s.includes("lesen")) return "bg-blue-50";
  if (s.includes("horen") || s.includes("hören")) return "bg-purple-50";
  if (s.includes("schreiben")) return "bg-green-50";
  if (s.includes("sprechen")) return "bg-orange-50";
  return "bg-gray-50";
};

const getModuleIconColor = (s: string) => {
  if (s.includes("lesen")) return "text-blue-500";
  if (s.includes("horen") || s.includes("hören")) return "text-purple-500";
  if (s.includes("schreiben")) return "text-green-500";
  if (s.includes("sprechen")) return "text-orange-500";
  return "text-gray-500";
};

const moduleScorePercent = (module: ModuleResultResponse): number => {
  if (!module.score_obtained || !module.max_score) return 0
  return Math.round((module.score_obtained / module.max_score) * 100)
}

// ── Chargement ───────────────────────────────────────────

onMounted(async () => {
  // 1. Depuis le store (soumission directe)
  if (sessionStore.result) {
    result.value = sessionStore.result;
    loading.value = false;
    return;
  }

  // 2. Depuis query ?sessionId=
  const sessionId = route.query.sessionId as string;
  if (sessionId) {
    const res = await sessionStore.getResult(sessionId);
    if (res.success) result.value = res.result ?? null;
    loading.value = false;
    return;
  }

  // 3. Depuis sessionId du store
  if (sessionStore.sessionId) {
    const res = await sessionStore.getResult(sessionStore.sessionId);
    if (res.success) result.value = res.result ?? null;
  }

  loading.value = false;
});
</script>
