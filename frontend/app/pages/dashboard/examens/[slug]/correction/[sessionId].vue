<template>
  <div class="max-w-3xl mx-auto space-y-5 pb-10">
    <!-- Chargement -->
    <div
      v-if="!ready || correctionStore.loading"
      class="flex flex-col items-center justify-center py-20 gap-4"
    >
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
      <p class="text-sm text-muted">{{ t("correction.loading") }}</p>
    </div>

    <!-- Erreur / introuvable -->
    <div
      v-else-if="correctionStore.error || !correction"
      class="bg-card border border-line rounded-card p-6 text-center space-y-4 max-w-lg mx-auto"
    >
      <div
        class="w-12 h-12 rounded-leaf bg-red-500/10 flex items-center justify-center mx-auto"
      >
        <i class="pi pi-exclamation-circle text-red-500 text-xl"></i>
      </div>
      <p class="font-semibold text-ink">{{ t("correction.not_found") }}</p>
      <p v-if="correctionStore.error" class="text-sm text-muted">
        {{ correctionStore.error }}
      </p>
      <Button
        :label="t('correction.back_to_result')"
        icon="pi pi-arrow-left"
        outlined
        size="small"
        @click="goToResult"
      />
    </div>

    <template v-else>
      <!-- ── En-tête ── -->
      <div
        class="bg-card border border-line rounded-card shadow-soft overflow-hidden"
      >
        <div
          :class="[
            'h-1.5',
            headerPositive ? 'bg-emerald-500' : guidance ? 'bg-amber-500' : 'bg-red-500',
          ]"
        ></div>
        <div class="p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center gap-6">
          <div class="flex-1 min-w-0">
            <p
              class="text-xs font-semibold uppercase tracking-wider text-muted mb-2"
            >
              {{ correction.provider?.toUpperCase() }}
              {{ correction.level?.toUpperCase() }} · Schreiben
            </p>
            <div class="flex items-center gap-3 mb-2">
              <div
                :class="[
                  'w-10 h-10 rounded-leaf flex items-center justify-center shrink-0',
                  headerPositive
                    ? 'bg-emerald-500/10 text-emerald-600'
                    : guidance
                      ? 'bg-amber-500/10 text-amber-600'
                      : 'bg-red-500/10 text-red-500',
                ]"
              >
                <i
                  :class="[
                    'pi text-lg',
                    guidance
                      ? headerPositive
                        ? 'pi-arrow-up-right'
                        : 'pi-arrow-down-right'
                      : headerPositive
                        ? 'pi-check-circle'
                        : 'pi-times-circle',
                  ]"
                ></i>
              </div>
              <!-- telc : pas de verdict isolé pour le Schreiben, seulement le score -->
              <h1 v-if="guidance" class="text-2xl font-bold text-ink">
                {{
                  t("simulator_result.guidance.title", {
                    score: fmtPts(correction.overall_score),
                    max: fmtPts(correction.max_score),
                  })
                }}
              </h1>
              <h1 v-else class="text-2xl font-bold text-ink">
                {{
                  correction.passed
                    ? t("correction.passed")
                    : t("correction.failed")
                }}
              </h1>
            </div>
            <p
              v-if="correction.appreciation"
              class="text-sm text-muted leading-relaxed max-w-lg"
            >
              {{ correction.appreciation }}
            </p>
          </div>

          <!-- Score -->
          <div class="flex sm:flex-col items-center gap-4 sm:gap-1 shrink-0">
            <div class="relative w-24 h-24">
              <svg class="w-24 h-24 -rotate-90" viewBox="0 0 80 80">
                <circle
                  cx="40"
                  cy="40"
                  r="32"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="7"
                  class="text-line"
                />
                <circle
                  cx="40"
                  cy="40"
                  r="32"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="7"
                  stroke-linecap="round"
                  :class="
                    headerPositive
                      ? 'text-emerald-500'
                      : guidance
                        ? 'text-amber-500'
                        : 'text-red-500'
                  "
                  :stroke-dasharray="`${(Math.min(correction.score_percentage, 100) / 100) * 201} 201`"
                />
              </svg>
              <div
                class="absolute inset-0 flex flex-col items-center justify-center"
              >
                <span class="text-xl font-extrabold text-ink leading-none">{{
                  correctionStore.cecrlLevel
                }}</span>
                <span class="text-[11px] text-muted tabular-nums"
                  >{{ Math.round(correction.score_percentage) }} %</span
                >
              </div>
            </div>
            <p class="text-sm font-semibold text-ink tabular-nums">
              {{
                t("result.official.points", {
                  got: fmtPts(correction.overall_score),
                  max: fmtPts(correction.max_score),
                })
              }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Repère telc : place du Schreiben dans la partie écrite ── -->
      <div
        v-if="guidance"
        :class="[
          'rounded-card border p-5',
          guidance.status === 'ahead'
            ? 'border-emerald-500/30 bg-emerald-500/10'
            : 'border-amber-500/30 bg-amber-500/10',
        ]"
      >
        <div class="flex items-start gap-3">
          <i
            :class="[
              'pi mt-0.5 text-lg',
              guidance.status === 'ahead'
                ? 'pi-check-circle text-emerald-600'
                : 'pi-exclamation-triangle text-amber-600',
            ]"
          ></i>
          <div class="min-w-0 flex-1 space-y-3">
            <p class="text-sm font-semibold text-ink">
              {{
                t(`simulator_result.guidance.${guidance.status}`, {
                  needed: fmtPts(guidance.needed_from_other_modules),
                  other: guidance.other_modules_max,
                  pct: Math.round(guidance.needed_percentage),
                })
              }}
            </p>
            <div>
              <div class="h-2 w-full overflow-hidden rounded-full bg-card-2">
                <div
                  class="h-2 rounded-full bg-primary"
                  :style="{ width: `${writtenShare}%` }"
                />
              </div>
              <p class="mt-1 text-xs tabular-nums text-muted">
                {{
                  t("simulator_result.guidance.gauge", {
                    score: fmtPts(guidance.module_score),
                    pass: guidance.written_pass,
                  })
                }}
              </p>
            </div>
            <p class="text-xs leading-relaxed text-muted">
              {{
                t("simulator_result.guidance.rule", {
                  pass: guidance.written_pass,
                  max: guidance.written_max,
                })
              }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Critères ── -->
      <div class="bg-card border border-line rounded-card overflow-hidden">
        <div
          class="px-5 sm:px-6 py-4 border-b border-line flex items-center gap-2"
        >
          <i class="pi pi-chart-bar text-primary"></i>
          <h2 class="font-semibold text-ink">
            {{ t("correction.score_detail") }}
          </h2>
        </div>
        <div class="divide-y divide-line">
          <div
            v-for="c in correctionStore.criteriaList"
            :key="c.key"
            class="px-5 sm:px-6 py-4"
          >
            <div class="flex items-center justify-between gap-3 mb-2">
              <span class="text-sm font-semibold text-ink">{{ c.label }}</span>
              <span
                v-if="c.maxScore > 0"
                :class="[
                  'text-sm font-bold tabular-nums',
                  scoreColor(c.score, c.maxScore),
                ]"
              >
                {{ fmtPts(c.score) }} / {{ fmtPts(c.maxScore) }}
                <!-- telc : lettre officielle du critère -->
                <span
                  v-if="gradeByKey[c.key]"
                  :title="t(`simulator_result.grades.${gradeByKey[c.key]}`)"
                  class="ml-1.5 rounded-full bg-card-2 px-2 py-0.5 text-xs"
                >
                  {{ gradeByKey[c.key] }}
                </span>
              </span>
              <span v-else class="text-sm font-bold tabular-nums text-red-500">
                {{ t("correction.malus", { n: fmtPts(Math.abs(c.score)) }) }}
              </span>
            </div>
            <div
              v-if="c.maxScore > 0"
              class="w-full h-2 rounded-full bg-card-2 overflow-hidden mb-2"
            >
              <div
                :class="[
                  'h-full rounded-full transition-all duration-500',
                  barColor(c.score, c.maxScore),
                ]"
                :style="{
                  width: `${Math.min((c.score / c.maxScore) * 100, 100)}%`,
                }"
              />
            </div>
            <p v-if="c.feedback" class="text-xs text-muted leading-relaxed">
              {{ c.feedback }}
            </p>
          </div>
        </div>
        <!-- Légende des lettres telc -->
        <p
          v-if="guidance"
          class="border-t border-line px-5 sm:px-6 py-3 text-xs leading-relaxed text-faint"
        >
          {{ t("simulator_result.grades.legend") }}
        </p>
      </div>

      <!-- ── Retour par tâche ── -->
      <div
        v-for="task in correctionStore.taskList"
        :key="task.key"
        class="bg-card border border-line rounded-card overflow-hidden"
      >
        <button
          type="button"
          class="w-full flex items-center justify-between px-5 sm:px-6 py-4 hover:bg-card-2 transition-colors"
          @click="toggleTask(task.key)"
        >
          <h2 class="font-semibold text-ink text-sm">{{ task.label }}</h2>
          <i
            :class="[
              'pi text-muted text-sm',
              expandedTasks.has(task.key) ? 'pi-chevron-up' : 'pi-chevron-down',
            ]"
          ></i>
        </button>

        <div
          v-if="expandedTasks.has(task.key)"
          class="border-t border-line px-5 sm:px-6 py-5 space-y-5"
        >
          <div v-if="task.strengths.length">
            <p
              class="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-2"
            >
              {{ t("correction.strengths") }}
            </p>
            <ul class="space-y-1.5">
              <li
                v-for="(s, i) in task.strengths"
                :key="i"
                class="flex items-start gap-2 text-sm text-ink"
              >
                <i
                  class="pi pi-check-circle text-emerald-500 mt-0.5 shrink-0 text-xs"
                ></i>
                <span>{{ s }}</span>
              </li>
            </ul>
          </div>

          <div v-if="task.weaknesses.length">
            <p
              class="text-xs font-semibold uppercase tracking-wide text-amber-600 mb-2"
            >
              {{ t("correction.to_improve") }}
            </p>
            <ul class="space-y-1.5">
              <li
                v-for="(w, i) in task.weaknesses"
                :key="i"
                class="flex items-start gap-2 text-sm text-ink"
              >
                <i
                  class="pi pi-exclamation-circle text-amber-500 mt-0.5 shrink-0 text-xs"
                ></i>
                <span>{{ w }}</span>
              </li>
            </ul>
          </div>

          <!-- Texte de l'élève et texte corrigé -->
          <div
            v-if="task.originalText || task.correctedText"
            class="grid grid-cols-1 gap-4 sm:grid-cols-2"
          >
            <div class="min-w-0">
              <p
                class="text-xs font-semibold uppercase tracking-wide text-muted mb-2"
              >
                <i class="pi pi-pencil text-[11px] mr-1"></i
                >{{ t("correction.your_text") }}
              </p>
              <div class="h-full rounded-leaf border border-line bg-card-2 p-4">
                <p
                  class="text-[15px] text-ink whitespace-pre-line leading-relaxed"
                >
                  {{
                    task.originalText || t("correction.original_unavailable")
                  }}
                </p>
              </div>
            </div>

            <div v-if="task.correctedText" class="min-w-0">
              <p
                class="text-xs font-semibold uppercase tracking-wide text-primary mb-2"
              >
                <i class="pi pi-sparkles text-[11px] mr-1"></i
                >{{ t("correction.corrected_text") }}
              </p>
              <div
                class="h-full rounded-leaf border border-primary/20 bg-primary/5 p-4"
              >
                <p
                  class="text-[15px] text-ink whitespace-pre-line leading-relaxed"
                >
                  {{ task.correctedText }}
                </p>
              </div>
            </div>
          </div>

          <!-- Texte modèle (Mustertext) : version attendue, séparée de la correction -->
          <div v-if="task.modelText">
            <p
              class="text-xs font-semibold uppercase tracking-wide text-emerald-600 mb-1"
            >
              <i class="pi pi-star text-[11px] mr-1"></i
              >{{ t("correction.model_text") }}
            </p>
            <p class="text-xs text-muted mb-2">
              {{ t("correction.model_text_hint") }}
            </p>
            <div
              class="rounded-leaf border border-emerald-500/30 bg-emerald-500/5 p-4"
            >
              <p
                class="text-[15px] text-ink whitespace-pre-line leading-relaxed"
              >
                {{ task.modelText }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Corrections détaillées ── -->
      <div
        v-if="correction.corrections_list?.length"
        class="bg-card border border-line rounded-card overflow-hidden"
      >
        <div
          class="px-5 sm:px-6 py-4 border-b border-line flex items-center justify-between gap-3"
        >
          <div class="flex items-center gap-2">
            <i class="pi pi-pencil text-amber-500"></i>
            <h2 class="font-semibold text-ink">
              {{ t("correction.detailed_corrections") }}
            </h2>
          </div>
          <span
            class="bg-amber-500/10 text-amber-700 text-xs font-bold px-2.5 py-1 rounded-full tabular-nums"
          >
            {{ correction.corrections_list.length }}
          </span>
        </div>
        <div class="divide-y divide-line">
          <div
            v-for="(c, i) in correction.corrections_list"
            :key="i"
            class="px-5 sm:px-6 py-4 flex items-start gap-3"
          >
            <span
              class="text-[11px] font-semibold text-muted bg-card-2 border border-line rounded-full px-2 py-0.5 shrink-0 mt-0.5"
            >
              {{ t("correction.teil", { n: c.task || 1 }) }}
            </span>
            <div class="flex-1 min-w-0 space-y-1">
              <p class="text-sm">
                <span class="line-through text-red-500 mr-2">{{
                  c.error
                }}</span>
                <span class="text-emerald-600 font-semibold"
                  >→ {{ c.correction }}</span
                >
              </p>
              <p
                v-if="c.explanation"
                class="text-xs text-muted leading-relaxed"
              >
                {{ c.explanation }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Conseils ── -->
      <div
        v-if="correction.suggestions?.length"
        class="bg-card border border-line rounded-card overflow-hidden"
      >
        <div
          class="px-5 sm:px-6 py-4 border-b border-line flex items-center gap-2"
        >
          <i class="pi pi-lightbulb text-amber-500"></i>
          <h2 class="font-semibold text-ink">{{ t("correction.tips") }}</h2>
        </div>
        <ul class="divide-y divide-line">
          <li
            v-for="(s, i) in correction.suggestions"
            :key="i"
            class="px-5 sm:px-6 py-3.5 flex items-start gap-3 text-sm text-ink"
          >
            <span
              class="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center shrink-0 mt-0.5"
            >
              {{ i + 1 }}
            </span>
            <span>{{ s }}</span>
          </li>
        </ul>
      </div>

      <!-- ── Actions ── -->
      <div class="flex flex-col sm:flex-row gap-3">
        <Button
          :label="t('correction.back_to_result')"
          icon="pi pi-arrow-left"
          outlined
          severity="secondary"
          class="flex-1"
          @click="goToResult"
        />
        <Button
          :label="t('correction.my_results')"
          icon="pi pi-trophy"
          class="flex-1"
          @click="navigateTo(localePath('/dashboard/resultats'))"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useCorrectionStore } from "~/stores/correction";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const route = useRoute();
const localePath = useLocalePath();
const correctionStore = useCorrectionStore();

const slug = route.params.slug as string;
const sessionId = route.params.sessionId as string;

const ready = ref(false);
const correction = computed(() => correctionStore.current);
const expandedTasks = ref<Set<string>>(new Set(["task1"]));

// telc : pas de verdict isolé (passed = null), repère sur la partie écrite à la place
interface WrittenPartGuidance {
  written_max: number;
  written_pass: number;
  module_score: number;
  module_max: number;
  other_modules_max: number;
  needed_from_other_modules: number;
  needed_percentage: number;
  status: "ahead" | "behind";
}
const guidance = computed<WrittenPartGuidance | null>(
  () => (correction.value as any)?.guidance ?? null,
);

// Lettre telc par critère (A/B/C/D), lue directement dans la réponse
const gradeByKey = computed<Record<string, string>>(() =>
  Object.fromEntries(
    ((correction.value as any)?.criteria ?? [])
      .filter((c: any) => c.grade)
      .map((c: any) => [c.key, c.grade]),
  ),
);

// Couleur de l'en-tête : repère telc si présent, sinon verdict classique
const headerPositive = computed(() =>
  guidance.value
    ? guidance.value.status === "ahead"
    : !!correction.value?.passed,
);

// Part du Schreiben dans les points requis pour valider l'écrit
const writtenShare = computed(() => {
  const g = guidance.value;
  if (!g || !g.written_pass) return 0;
  return Math.min(100, (g.module_score / g.written_pass) * 100);
});

// Nouveau Set à chaque clic : un Set modifié sur place n'est pas suivi par Vue
const toggleTask = (key: string) => {
  const next = new Set(expandedTasks.value);
  if (next.has(key)) next.delete(key);
  else next.add(key);
  expandedTasks.value = next;
};

const goToResult = () =>
  navigateTo(
    localePath({
      path: `/dashboard/examens/${slug}/result`,
      query: { sessionId },
    }),
  );

const fmtPts = (n: number) =>
  String(Math.round((n ?? 0) * 10) / 10).replace(".", ",");

const scoreColor = (score: number, max: number): string => {
  const pct = max > 0 ? score / max : 0;
  if (pct >= 0.7) return "text-emerald-600";
  if (pct >= 0.5) return "text-amber-600";
  return "text-red-500";
};

const barColor = (score: number, max: number): string => {
  const pct = max > 0 ? score / max : 0;
  if (pct >= 0.7) return "bg-emerald-500";
  if (pct >= 0.5) return "bg-amber-500";
  return "bg-red-500";
};

onMounted(async () => {
  if (correctionStore.current?.session_id !== sessionId) {
    try {
      await correctionStore.fetchBySession(sessionId);
    } catch {
      /* l'erreur est exposée par correctionStore.error */
    }
  }
  ready.value = true;
});

useHead({ title: t("correction.page_title") });
</script>