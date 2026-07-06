<template>
  <div class="space-y-6 pb-10">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
    </div>

    <!-- Not found -->
    <div
      v-else-if="!result"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-gray-100"
    >
      <div
        class="w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mb-4"
      >
        <i class="pi pi-exclamation-triangle text-2xl text-red-400"></i>
      </div>
      <p class="font-semibold text-gray-700 mb-4">
        {{ t("result.not_found") }}
      </p>
      <Button
        :label="t('result.back_to_exams')"
        outlined
        size="small"
        @click="navigateTo('/dashboard/examens')"
      />
    </div>

    <div v-else class="space-y-6">
      <!-- ── Hero résultat ── -->
      <div
        class="relative rounded-2xl p-6 text-white overflow-hidden"
        :class="heroBg"
      >
        <!-- Cercle décoratif -->
        <div
          class="absolute -top-10 -right-10 w-48 h-48 rounded-full opacity-10 bg-white"
        ></div>
        <div
          class="absolute -bottom-8 -left-8 w-32 h-32 rounded-full opacity-10 bg-white"
        ></div>

        <div class="relative flex items-start justify-between gap-4">
          <div class="flex-1">
            <!-- Breadcrumb -->
            <p
              class="text-xs font-bold uppercase tracking-widest opacity-70 mb-2"
            >
              {{ result.exam_name }} · {{ t("result.subject") }}
              {{ result.subject_number }}
              <span
                v-if="isSingleModule"
                class="ml-2 bg-white/20 px-2 py-0.5 rounded-full"
              >
                {{ displayedModules[0]?.name }}
              </span>
            </p>

            <!-- Titre résultat -->
            <div class="flex items-center gap-3 mb-2">
              <div
                class="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center shrink-0"
              >
                <i :class="['pi text-xl', heroIcon]"></i>
              </div>
              <h1 class="text-2xl font-bold">{{ heroTitle }}</h1>
            </div>

            <p class="text-sm opacity-85 leading-relaxed max-w-md">
              {{ result.result_message }}
            </p>

            <!-- Tags info -->
            <div class="flex flex-wrap gap-2 mt-4">
              <span
                v-if="actualDuration"
                class="inline-flex items-center gap-1 bg-white/15 text-white text-xs font-semibold px-3 py-1.5 rounded-full"
              >
                <i class="pi pi-clock text-xs"></i>
                {{ actualDuration }}
              </span>
              <span
                class="inline-flex items-center gap-1 bg-white/15 text-white text-xs font-semibold px-3 py-1.5 rounded-full"
              >
                <i class="pi pi-list text-xs"></i>
                {{ displayedModules.length }}
                {{ isSingleModule ? t("result.module") : t("result.modules") }}
              </span>
            </div>
          </div>

          <!-- Score global -->
          <div class="text-center shrink-0">
            <div class="relative w-20 h-20">
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
                  :stroke-dasharray="`${(scorePercent / 100) * 201} 201`"
                />
              </svg>
              <div
                class="absolute inset-0 flex flex-col items-center justify-center"
              >
                <span class="text-xl font-extrabold leading-none">
                  {{ displayScore }}
                </span>
                <span class="text-xs opacity-70">/100</span>
              </div>
            </div>
            <p class="text-xs opacity-60 mt-1">
              {{ t("result.min_score") }} {{ result.total_pass_score }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Résumé modules ── -->
      <div
        class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-gray-50">
          <h2 class="font-bold text-gray-800">
            {{
              isSingleModule
                ? t("result.module_result")
                : t("result.modules_result")
            }}
          </h2>
        </div>
        <div
          v-for="module in displayedModules"
          :key="module.slug"
          class="px-6 py-4 flex items-center gap-4"
        >
          <!-- Icône module -->
          <div
            :class="[
              'w-11 h-11 rounded-xl flex items-center justify-center shrink-0',
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
            <div class="flex items-center gap-2 mb-1.5">
              <p class="font-semibold text-gray-900 text-sm">
                {{ module.name }}
              </p>

              <!-- ✅ Badge Schreiben : source = correctionStore, pas module.is_corrected -->
              <span
                v-if="isSchreiben(module) && correctionStore.current"
                :class="[
                  'inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full',
                  correctionStore.current.passed
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-600',
                ]"
              >
                <i
                  :class="[
                    'pi text-xs',
                    correctionStore.current.passed ? 'pi-check' : 'pi-times',
                  ]"
                ></i>
                {{
                  correctionStore.current.passed
                    ? t("result.module_passed")
                    : t("result.module_failed")
                }}
              </span>

              <!-- Badge autres modules : logique existante -->
              <span
                v-else-if="
                  !isSchreiben(module) &&
                  module.is_corrected &&
                  module.score_obtained !== null
                "
                :class="[
                  'inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full',
                  (module.score_obtained ?? 0) >= 60
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-600',
                ]"
              >
                <i
                  :class="[
                    'pi text-xs',
                    (module.score_obtained ?? 0) >= 60
                      ? 'pi-check'
                      : 'pi-times',
                  ]"
                ></i>
                {{
                  (module.score_obtained ?? 0) >= 60
                    ? t("result.module_passed")
                    : t("result.module_failed")
                }}
              </span>
            </div>

            <!-- ✅ Barre progression Schreiben : source = correctionStore -->
            <div
              v-if="isSchreiben(module) && correctionStore.current"
              class="flex items-center gap-2"
            >
              <div class="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                <div
                  class="h-2 rounded-full transition-all duration-500"
                  :class="
                    correctionStore.current.passed
                      ? 'bg-green-500'
                      : 'bg-orange-400'
                  "
                  :style="{
                    width: `${Math.min(correctionStore.scorePercentage, 100)}%`,
                  }"
                />
              </div>
              <span
                class="text-sm font-bold text-gray-700 shrink-0 w-14 text-right"
              >
                {{ correctionStore.current.overall_score }}/{{
                  correctionStore.current.max_score
                }}
              </span>
            </div>

            <!-- Barre progression autres modules : logique existante -->
            <div
              v-else-if="module.is_corrected"
              class="flex items-center gap-2"
            >
              <!-- ... contenu inchangé ... -->
            </div>

            <!-- En attente : Schreiben pas encore corrigé (edge case), ou autres modules -->
            <div
              v-else-if="!(isSchreiben(module) && correctionStore.current)"
              class="flex items-center gap-1.5 text-amber-600 text-xs"
            >
              <i class="pi pi-clock text-xs"></i>
              <span>{{ t("result.waiting_correction") }}</span>
            </div>
          </div>

          <Button
            v-if="isSchreiben(module) && correctionStore.current"
            :label="t('result.see_correction')"
            icon="pi pi-eye"
            size="small"
            outlined
            severity="secondary"
            class="shrink-0"
            @click="goToSchreibenCorrection"
          />
        </div>
      </div>

      <!-- ── Info seuil de réussite ── -->
      <div
        v-if="!isSingleModule && result.passed === false"
        class="flex items-start gap-3 bg-orange-50 border border-orange-100 rounded-2xl px-5 py-4"
      >
        <i class="pi pi-info-circle text-orange-500 mt-0.5 shrink-0"></i>
        <div class="text-sm text-orange-800">
          <p class="font-semibold mb-1">{{ t("result.why_failed") }}</p>
          <ul class="space-y-1 text-xs">
            <li v-if="(result.score ?? 0) < result.total_pass_score">
              ·
              {{
                t("result.global_score_insufficient", {
                  score: result.score?.toFixed(0) ?? 0,
                  threshold: result.total_pass_score,
                })
              }}
            </li>
            <li v-for="m in failedModules" :key="m.slug">
              ·
              {{
                t("result.module_score_insufficient", {
                  module: m.name,
                  score: m.score_obtained?.toFixed(0),
                })
              }}
            </li>
          </ul>
        </div>
      </div>

      <!-- ── Détail réponses par module ── -->
      <div
        v-for="module in displayedModules.filter(
          (m) =>
            !m.slug.includes('schreiben') && !m.slug.includes('schriftlich'),
        )"
        :key="`detail-${module.slug}`"
        class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <!-- Header accordéon -->
        <button
          class="w-full flex items-center justify-between px-6 py-4 border-b border-gray-50 hover:bg-gray-50/70 transition-colors"
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
            <h2 class="font-semibold text-gray-800 text-sm">
              {{ t("result.detail_title") }}-{{ module.name }}
            </h2>
          </div>
          <i
            :class="[
              'pi text-gray-400 text-sm',
              expandedModules.has(module.slug)
                ? 'pi-chevron-up'
                : 'pi-chevron-down',
            ]"
          ></i>
        </button>

        <!-- Contenu accordéon -->
        <div v-if="expandedModules.has(module.slug)">
          <div
            v-for="teil in module.teile"
            :key="teil.teil_number"
            class="border-b border-gray-50 last:border-0"
          >
            <!-- Teil header -->
            <div
              class="px-6 py-3 bg-gray-50/50 flex items-center justify-between"
            >
              <p
                class="text-xs font-bold text-gray-500 uppercase tracking-wide"
              >
                Teil {{ teil.teil_number }}
              </p>
              <span class="text-xs font-bold text-gray-600">
                {{ teil.score_obtained?.toFixed(1) ?? "-" }} /
                {{ teil.max_score }} pts
              </span>
            </div>

            <!-- Réponses -->
            <div class="divide-y divide-gray-50">
              <div
                v-for="answer in teil.answers"
                :key="answer.question_id"
                class="px-6 py-3 flex items-start gap-3"
              >
                <div class="shrink-0 mt-0.5">
                  <div
                    v-if="answer.is_correct === true"
                    class="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center"
                  >
                    <i class="pi pi-check text-green-600 text-xs"></i>
                  </div>
                  <div
                    v-else-if="answer.is_correct === false"
                    class="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center"
                  >
                    <i class="pi pi-times text-red-500 text-xs"></i>
                  </div>
                  <div
                    v-else
                    class="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center"
                  >
                    <i class="pi pi-minus text-gray-400 text-xs"></i>
                  </div>
                </div>
                <div class="flex-1 min-w-0 text-sm">
                  <div class="flex flex-wrap gap-x-4 gap-y-1 text-gray-600">
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

      <!-- ── Actions ── -->
      <div class="flex flex-col sm:flex-row gap-3">
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
import { useCorrectionStore } from "~/stores/correction";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const route = useRoute();
const router = useRouter();
const sessionStore = useSessionStore();
const { t } = useI18n();

const correctionStore = useCorrectionStore();
const loading = ref(true);
const result = ref<SessionResultResponse | null>(null);
const expandedModules = ref<Set<string>>(new Set());

const schreibenModule = computed(() =>
  displayedModules.value.find(
    (m) =>
      m.slug.toLowerCase().includes("schreib") ||
      m.slug.toLowerCase().includes("schriftlich"),
  ),
);

const isSchreiben = (module: any) =>
  module.slug.toLowerCase().includes("schreib") ||
  module.slug.toLowerCase().includes("schriftlich");

// ── Mode module seul / modules combinés ──────────────────
const moduleSlug = computed(() => route.query.moduleSlug as string | undefined);
const moduleSlugs = computed(
  () => route.query.moduleSlugs as string | undefined,
);
const isSingleModule = computed(
  () => !!moduleSlug.value || !!moduleSlugs.value,
);

const displayedModules = computed(() => {
  if (!result.value?.modules) return [];

  if (moduleSlugs.value) {
    const targetSlugs = moduleSlugs.value
      .split(",")
      .map((s) => s.trim().toLowerCase());
    return result.value.modules.filter((m) =>
      targetSlugs.some((slug) => m.slug.toLowerCase().includes(slug)),
    );
  }

  if (moduleSlug.value) {
    return result.value.modules.filter((m) =>
      m.slug.toLowerCase().includes(moduleSlug.value!.toLowerCase()),
    );
  }

  return result.value.modules;
});

// ── Score & résultat ─────────────────────────────────────
const isPassed = computed(() => {
  if (isSingleModule.value) return result.value?.module_passed ?? null;
  return result.value?.passed ?? null;
});

const displayScore = computed(() => {
  if (
    isSingleModule.value &&
    displayedModules.value[0]?.score_obtained != null
  ) {
    return displayedModules.value[0].score_obtained.toFixed(0);
  }
  return result.value?.score != null ? result.value.score.toFixed(0) : "-";
});

const scorePercent = computed(() => {
  const s = parseFloat(displayScore.value);
  return isNaN(s) ? 0 : Math.min(s, 100);
});

const failedModules = computed(() =>
  (result.value?.modules ?? []).filter(
    (m) => m.score_obtained !== null && (m.score_obtained ?? 0) < 60,
  ),
);

// ── Hero ─────────────────────────────────────────────────
const heroBg = computed(() => {
  if (result.value?.status === "PENDING_REVIEW")
    return "bg-gradient-to-br from-gray-500 to-gray-700";
  if (isPassed.value === true)
    return "bg-gradient-to-br from-green-500 to-teal-600";
  if (isPassed.value === false)
    return "bg-gradient-to-br from-orange-500 to-red-500";
  return "bg-gradient-to-br from-gray-500 to-gray-700";
});

const heroIcon = computed(() => {
  if (result.value?.status === "PENDING_REVIEW") return "pi-clock";
  if (isPassed.value === true) return "pi-check-circle";
  if (isPassed.value === false) return "pi-times-circle";
  return "pi-clock";
});

const heroTitle = computed(() => {
  if (result.value?.status === "PENDING_REVIEW") return t("result.pending");
  if (isPassed.value === true) return t("result.passed");
  if (isPassed.value === false) return t("result.failed");
  return t("result.pending");
});

// ── Helpers ──────────────────────────────────────────────
const toggleModule = (slug: string) => {
  if (expandedModules.value.has(slug)) expandedModules.value.delete(slug);
  else expandedModules.value.add(slug);
};

const goToSchreibenCorrection = () => {
  const slug = route.params.slug as string;
  const sessionId = result.value?.session_id;
  if (!sessionId) return;
  navigateTo({
    path: `/dashboard/examens/${slug}/correction/${sessionId}`,
    query: { examId: result.value?.exam_id },
  });
};

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
  const slug = (s || "").toLowerCase();
  if (slug.includes("lese")) return "pi-book";
  if (slug.includes("hoer") || slug.includes("hör")) return "pi-volume-up";
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return "pi-pencil";
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return "pi-microphone";
  if (slug.includes("sprachbaustein")) return "pi-language";
  return "pi-file";
};

const getModuleBg = (s: string) => {
  const slug = (s || "").toLowerCase();
  if (slug.includes("lese")) return "bg-blue-50";
  if (slug.includes("hoer") || slug.includes("hör")) return "bg-purple-50";
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return "bg-green-50";
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return "bg-orange-50";
  if (slug.includes("sprachbaustein")) return "bg-pink-50";
  return "bg-gray-50";
};

const getModuleIconColor = (s: string) => {
  const slug = (s || "").toLowerCase();
  if (slug.includes("lese")) return "text-blue-500";
  if (slug.includes("hoer") || slug.includes("hör")) return "text-purple-500";
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return "text-green-500";
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return "text-orange-500";
  if (slug.includes("sprachbaustein")) return "text-pink-500";
  return "text-gray-500";
};

// ── Chargement ───────────────────────────────────────────
onMounted(async () => {
  if (sessionStore.result) {
    result.value = sessionStore.result;
  } else {
    const queryId = route.query.sessionId as string | undefined;
    const targetId = queryId || sessionStore.sessionId;
    if (targetId) {
      const res = await sessionStore.getResult(targetId);
      if (res.success) result.value = res.result ?? null;
    }
  }

  // ✅ Récupère la correction IA Schreiben déjà lancée au submit,
  // une fois qu'on sait quelle session/quels modules sont concernés.
  const sessionId =
    result.value?.session_id || (route.query.sessionId as string);
  if (sessionId && schreibenModule.value) {
    await correctionStore.fetchBySession(sessionId);
  }

  loading.value = false;
});
</script>
