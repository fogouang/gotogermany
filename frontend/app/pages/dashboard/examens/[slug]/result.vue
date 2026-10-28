<template>
  <div class="pb-10">
    <!-- Chargement -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
    </div>

    <!-- Introuvable -->
    <div
      v-else-if="!result"
      class="flex flex-col items-center justify-center py-20 bg-card border border-line rounded-card"
    >
      <div
        class="w-14 h-14 rounded-leaf bg-red-500/10 flex items-center justify-center mb-4"
      >
        <i class="pi pi-exclamation-triangle text-2xl text-red-500"></i>
      </div>
      <p class="font-semibold text-ink mb-4">{{ t("result.not_found") }}</p>
      <Button
        :label="t('result.back_to_exams')"
        outlined
        size="small"
        @click="navigateTo(localePath('/dashboard/examens'))"
      />
    </div>

    <template v-else>
      <!-- ── En-tête du résultat ── -->
      <section
        class="relative overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <div :class="['absolute inset-x-0 top-0 h-1', status.bar]"></div>

        <div
          class="grid gap-6 p-5 sm:p-7 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center"
        >
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-3">
              <span
                class="text-xs font-semibold uppercase tracking-wider text-muted"
              >
                {{ result.exam_name }} · {{ t("result.subject") }}
                {{ result.subject_number }}
              </span>
              <span
                v-if="isSingleModule && displayedModules[0]"
                class="text-xs font-medium text-ink bg-card-2 border border-line px-2 py-0.5 rounded-full"
              >
                {{ displayedModules.map((m) => m.name).join(" + ") }}
              </span>
            </div>

            <div class="flex items-center gap-3">
              <div
                :class="[
                  'w-12 h-12 rounded-leaf flex items-center justify-center shrink-0',
                  status.chip,
                ]"
              >
                <i :class="['pi text-xl', status.icon]"></i>
              </div>
              <h1 class="text-2xl sm:text-3xl font-bold text-ink">
                {{ status.title }}
              </h1>
            </div>

            <p
              v-if="resultMessage"
              class="mt-3 text-sm text-muted leading-relaxed max-w-xl"
            >
              {{ resultMessage }}
            </p>

            <div class="flex flex-wrap gap-2 mt-4">
              <span
                v-if="actualDuration"
                class="inline-flex items-center gap-1.5 bg-card-2 border border-line text-ink text-xs font-medium px-3 py-1.5 rounded-full"
              >
                <i class="pi pi-clock text-[11px] text-muted"></i>
                {{ actualDuration }}
              </span>
              <span
                class="inline-flex items-center gap-1.5 bg-card-2 border border-line text-ink text-xs font-medium px-3 py-1.5 rounded-full"
              >
                <i class="pi pi-list text-[11px] text-muted"></i>
                {{ displayedModules.length }}
                {{
                  displayedModules.length > 1
                    ? t("result.modules")
                    : t("result.module")
                }}
              </span>
              <span
                v-if="answerCounts.total"
                class="inline-flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 dark:text-emerald-400 text-xs font-semibold px-3 py-1.5 rounded-full tabular-nums"
              >
                <i class="pi pi-check text-[11px]"></i>
                {{ answerCounts.right }} / {{ answerCounts.total }}
              </span>
            </div>
          </div>

          <!-- Score -->
          <div
            class="flex items-center gap-5 rounded-card border border-line bg-card-2 p-4 lg:flex-col lg:gap-2 lg:px-8"
          >
            <div class="relative w-28 h-28 shrink-0">
              <svg class="w-28 h-28 -rotate-90" viewBox="0 0 80 80">
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
                  :class="status.ring"
                  :stroke-dasharray="`${(Math.min(totals.percent ?? 0, 100) / 100) * 201} 201`"
                />
              </svg>
              <div
                class="absolute inset-0 flex flex-col items-center justify-center"
              >
                <span
                  class="text-3xl font-extrabold text-ink leading-none tabular-nums"
                >
                  {{
                    totals.percent != null ? Math.round(totals.percent) : "-"
                  }}
                </span>
                <span class="text-xs text-muted">%</span>
              </div>
            </div>
            <div class="lg:text-center">
              <p
                v-if="totals.complete"
                class="text-base font-bold text-ink tabular-nums"
              >
                {{
                  t("result.official.points", {
                    got: fmtPts(totals.got),
                    max: fmtPts(totals.max),
                  })
                }}
              </p>
              <p class="text-xs text-muted">
                {{
                  t("result.official.threshold", {
                    points: fmtPts(passPoints),
                    pct: passPct,
                  })
                }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <div
        class="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start"
      >
        <!-- ── Colonne principale : détail des réponses ── -->
        <div class="min-w-0 space-y-5 order-2 lg:order-1">
          <!-- Filtre -->
          <div
            v-if="answerCounts.total"
            class="flex flex-wrap items-center justify-between gap-3"
          >
            <h2 class="font-semibold text-ink">
              {{ t("result.official.block_detail") }}
            </h2>
            <div
              class="inline-flex gap-1 p-1 rounded-leaf bg-card border border-line"
              role="tablist"
            >
              <button
                v-for="f in answerFilters"
                :key="f.value"
                type="button"
                role="tab"
                :aria-selected="answerFilter === f.value"
                :class="[
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors tabular-nums',
                  answerFilter === f.value
                    ? 'bg-primary text-white'
                    : 'text-muted hover:text-ink hover:bg-card-2',
                ]"
                @click="answerFilter = f.value"
              >
                {{ f.label }} · {{ f.count }}
              </button>
            </div>
          </div>

          <div
            v-for="module in detailModules"
            :key="`detail-${module.slug}`"
            class="bg-card border border-line rounded-card overflow-hidden"
          >
            <button
              type="button"
              class="w-full flex items-center justify-between gap-3 px-5 sm:px-6 py-4 hover:bg-card-2 transition-colors"
              @click="toggleModule(module.slug)"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div
                  class="w-9 h-9 rounded-leaf bg-primary/10 flex items-center justify-center shrink-0"
                >
                  <i
                    :class="['pi text-sm text-primary', moduleIcon(module.slug)]"
                  ></i>
                </div>
                <div class="min-w-0 text-left">
                  <p class="font-semibold text-ink text-sm truncate">
                    {{ module.name }}
                  </p>
                  <p class="text-xs text-muted tabular-nums">
                    {{ moduleStats(module).right }} /
                    {{ moduleStats(module).total }}
                    {{ t("result.correct_short") }}
                  </p>
                </div>
              </div>
              <i
                :class="[
                  'pi text-muted text-sm',
                  expandedModules.has(module.slug)
                    ? 'pi-chevron-up'
                    : 'pi-chevron-down',
                ]"
              ></i>
            </button>

            <div
              v-if="expandedModules.has(module.slug)"
              class="border-t border-line divide-y divide-line"
            >
              <div v-for="teil in module.teile" :key="teil.teil_number">
                <!-- En-tête du Teil -->
                <div class="px-5 sm:px-6 pt-4 pb-3">
                  <div class="flex items-center justify-between gap-3">
                    <p
                      class="text-xs font-bold uppercase tracking-wide text-ink"
                    >
                      {{ t("result.official.teil", { n: teil.teil_number }) }}
                      <span class="ml-2 font-medium normal-case text-muted">
                        {{ teilStats(teil).right }}/{{ teilStats(teil).total }}
                        {{ t("result.correct_short") }}
                      </span>
                    </p>
                    <span class="text-sm font-bold text-ink tabular-nums">
                      {{
                        t("result.official.points", {
                          got: fmtPts(teil.score_obtained ?? 0),
                          max: fmtPts(teil.max_score),
                        })
                      }}
                    </span>
                  </div>
                  <div class="mt-2 h-1.5 rounded-full bg-card-2 overflow-hidden">
                    <div
                      :class="[
                        'h-full rounded-full transition-all duration-500',
                        barColor(teilPercent(teil)),
                      ]"
                      :style="{ width: `${teilPercent(teil)}%` }"
                    />
                  </div>
                </div>

                <!-- Réponses : une tuile par question, comme un Antwortbogen corrigé -->
                <div
                  v-if="filteredAnswers(teil).length"
                  class="grid gap-2 px-5 sm:px-6 pb-5 sm:grid-cols-2 2xl:grid-cols-3"
                >
                  <div
                    v-for="answer in filteredAnswers(teil)"
                    :key="answer.question_id"
                    :class="[
                      'flex items-start gap-3 rounded-leaf border px-3 py-2.5',
                      answer.is_correct === true
                        ? 'border-emerald-500/30 bg-emerald-500/5'
                        : answer.is_correct === false
                          ? 'border-red-500/25 bg-red-500/5'
                          : 'border-line bg-card-2',
                    ]"
                  >
                    <span
                      :class="[
                        'inline-flex h-7 min-w-7 shrink-0 items-center justify-center rounded-full px-1.5 text-xs font-bold tabular-nums',
                        answer.is_correct === true
                          ? 'bg-emerald-500 text-white'
                          : answer.is_correct === false
                            ? 'bg-red-500 text-white'
                            : 'bg-card border border-line text-muted',
                      ]"
                    >
                      {{ answer.question_number }}
                    </span>

                    <div class="min-w-0 flex-1 text-sm">
                      <p
                        class="line-clamp-2 text-ink"
                        :title="showAnswer(answer.user_answer)"
                      >
                        <span class="text-xs text-muted"
                          >{{ t("result.your_answer") }} :
                        </span>
                        <strong>{{ showAnswer(answer.user_answer) || "-" }}</strong>
                      </p>
                      <p
                        v-if="answer.correct_answer && answer.is_correct === false"
                        class="line-clamp-2 text-xs text-emerald-700 dark:text-emerald-400 mt-0.5"
                        :title="showAnswer(answer.correct_answer)"
                      >
                        {{ t("result.correct_answer") }} :
                        <strong>{{ showAnswer(answer.correct_answer) }}</strong>
                      </p>
                      <p
                        v-if="answer.feedback"
                        class="text-xs text-faint mt-1 line-clamp-3"
                      >
                        {{ answer.feedback }}
                      </p>
                    </div>

                    <i
                      :class="[
                        'pi text-xs mt-1.5 shrink-0',
                        answer.is_correct === true
                          ? 'pi-check text-emerald-600'
                          : answer.is_correct === false
                            ? 'pi-times text-red-500'
                            : 'pi-clock text-faint',
                      ]"
                    ></i>
                  </div>
                </div>
                <p
                  v-else-if="teil.answers?.length"
                  class="px-5 sm:px-6 pb-4 text-xs text-faint"
                >
                  {{ t("result.no_answer_in_filter") }}
                </p>
                <p v-else class="px-5 sm:px-6 pb-4 text-xs text-faint">
                  {{ t("result.official.no_answer") }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Colonne latérale : résumé, toujours visible sur grand écran ── -->
        <aside class="space-y-5 order-1 lg:order-2 lg:sticky lg:top-5">
          <!-- Résultat par module -->
          <div class="bg-card border border-line rounded-card overflow-hidden">
            <div
              class="px-5 py-4 border-b border-line flex items-center justify-between gap-3"
            >
              <h2 class="font-semibold text-ink text-sm">
                {{
                  isSingleModule
                    ? t("result.module_result")
                    : t("result.official.written_part")
                }}
              </h2>
              <span
                v-if="!isSingleModule && totals.complete"
                class="text-sm font-bold text-ink tabular-nums"
              >
                {{
                  t("result.official.points", {
                    got: fmtPts(totals.got),
                    max: fmtPts(totals.max),
                  })
                }}
              </span>
            </div>

            <div class="divide-y divide-line">
              <div v-for="group in groups" :key="group.key" class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-leaf bg-primary/10 flex items-center justify-center shrink-0"
                  >
                    <i
                      :class="[
                        'pi text-primary',
                        moduleIcon(group.modules[0]?.slug),
                      ]"
                    ></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between gap-2">
                      <p class="font-semibold text-ink text-sm truncate">
                        {{ group.label }}
                      </p>
                      <span
                        v-if="groupPoints(group) != null"
                        class="text-sm font-bold text-ink tabular-nums shrink-0"
                      >
                        {{
                          t("result.official.points", {
                            got: fmtPts(groupPoints(group)!),
                            max: fmtPts(groupMax(group)),
                          })
                        }}
                      </span>
                    </div>

                    <div
                      v-if="groupPoints(group) != null"
                      class="mt-1.5 flex items-center gap-2"
                    >
                      <div
                        class="flex-1 h-2 rounded-full bg-card-2 overflow-hidden"
                      >
                        <div
                          :class="[
                            'h-full rounded-full transition-all duration-500',
                            barColor(groupPercent(group)),
                          ]"
                          :style="{
                            width: `${Math.min(groupPercent(group) ?? 0, 100)}%`,
                          }"
                        />
                      </div>
                      <span
                        class="text-xs text-muted w-10 text-right tabular-nums"
                      >
                        {{ Math.round(groupPercent(group) ?? 0) }} %
                      </span>
                    </div>

                    <div
                      v-else
                      class="mt-1 flex items-center gap-1.5 text-amber-600 text-xs"
                    >
                      <i class="pi pi-clock text-xs"></i>
                      <span>
                        {{
                          group.modules.some(isSchreiben)
                            ? t("result.official.correction_pending")
                            : t("result.waiting_correction")
                        }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Détail du bloc (ex. Leseverstehen + Sprachbausteine) -->
                <div
                  v-if="group.modules.length > 1"
                  class="mt-3 ml-13 space-y-1 rounded-leaf bg-card-2 px-3 py-2"
                >
                  <p
                    v-for="m in group.modules"
                    :key="m.slug"
                    class="flex justify-between gap-2 text-xs"
                  >
                    <span class="text-muted">{{ m.name }}</span>
                    <span class="font-semibold text-ink tabular-nums">
                      {{
                        modulePoints(m) != null
                          ? t("result.official.points", {
                              got: fmtPts(modulePoints(m)!),
                              max: fmtPts(m.max_score),
                            })
                          : "-"
                      }}
                    </span>
                  </p>
                </div>

                <Button
                  v-if="group.modules.some(isSchreiben) && correctionStore.current"
                  :label="t('result.see_correction')"
                  icon="pi pi-eye"
                  size="small"
                  outlined
                  severity="secondary"
                  class="w-full mt-3"
                  @click="goToCorrection"
                />
              </div>

              <!-- Oral -->
              <div v-if="!isSingleModule" class="px-5 py-4 flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-leaf bg-card-2 border border-line flex items-center justify-center shrink-0"
                >
                  <i class="pi pi-microphone text-muted"></i>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-ink text-sm">
                    {{ t("result.official.oral_title") }}
                  </p>
                  <p class="text-xs text-muted">
                    {{ t("result.official.oral_text") }}
                  </p>
                  <NuxtLink
                    :to="localePath(`/dashboard/sprechen/${result.subject_id}`)"
                    class="mt-1 inline-block text-xs font-semibold text-primary hover:underline"
                  >
                    {{ t("result.official.oral_link") }}
                  </NuxtLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Pourquoi non réussi -->
          <div
            v-if="result.passed === false && (weakModules.length || (totals.percent != null && totals.percent < passPct))"
            class="flex items-start gap-3 rounded-card border border-amber-500/30 bg-amber-500/5 px-5 py-4"
          >
            <i class="pi pi-info-circle text-amber-600 mt-0.5 shrink-0"></i>
            <div class="text-sm text-ink">
              <p class="font-semibold mb-1">{{ t("result.why_failed") }}</p>
              <p
                v-if="totals.percent != null && totals.percent < passPct"
                class="text-xs text-muted"
              >
                {{
                  t("result.global_score_insufficient", {
                    score: Math.round(totals.percent),
                    threshold: passPct,
                  })
                }}
              </p>
              <p v-if="weakModules.length" class="text-xs text-muted mt-1">
                {{
                  t("result.official.weak_modules", {
                    list: weakModules.join(", "),
                  })
                }}
              </p>
            </div>
          </div>

          <!-- Actions -->
          <div class="grid gap-2">
            <Button
              :label="t('result.my_results')"
              icon="pi pi-trophy"
              class="w-full"
              @click="navigateTo(localePath('/dashboard/resultats'))"
            />
            <Button
              :label="t('result.another_module')"
              icon="pi pi-list"
              outlined
              class="w-full"
              @click="
                navigateTo(
                  localePath(`/dashboard/examens/${slug}/${result.subject_id}`),
                )
              "
            />
            <Button
              :label="t('result.back_to_exams')"
              icon="pi pi-arrow-left"
              text
              severity="secondary"
              class="w-full"
              @click="navigateTo(localePath('/dashboard/examens'))"
            />
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ModuleResultResponse, SessionResultResponse } from "#shared/api";
import { useCorrectionStore } from "~/stores/correction";

definePageMeta({ layout: "dashboard" });

type Group = { key: string; label: string; modules: ModuleResultResponse[] };

const route = useRoute();
const sessionStore = useSessionStore();
const correctionStore = useCorrectionStore();
const { t } = useI18n();
const localePath = useLocalePath();

const slug = route.params.slug as string;
const loading = ref(true);
const result = ref<SessionResultResponse | null>(null);
const expandedModules = ref<Set<string>>(new Set());

// Message traduit à partir de la clé du backend ; à défaut, le texte reçu
const resultMessage = computed(() => {
  const r: any = result.value;
  if (!r) return "";
  if (r.result_message_key) {
    return t(`result.messages.${r.result_message_key}`, r.result_message_params ?? {});
  }
  return r.result_message ?? "";
});

// ── Helpers de slug ───────────────────────────────────

const slugOf = (s?: string) => (s || "").toLowerCase();
const isSchreiben = (m: ModuleResultResponse) =>
  slugOf(m.slug).includes("schreib") || slugOf(m.slug).includes("schriftlich");

// ── Mode module seul / modules combinés ───────────────

const moduleSlug = computed(() => route.query.moduleSlug as string | undefined);
const moduleSlugs = computed(
  () => route.query.moduleSlugs as string | undefined,
);

const isSingleModule = computed(
  () => !!moduleSlug.value || !!moduleSlugs.value || !!result.value?.module_slugs?.length,
);

const displayedModules = computed<ModuleResultResponse[]>(() => {
  const modules = result.value?.modules ?? [];
  if (moduleSlugs.value) {
    const targets = moduleSlugs.value
      .split(",")
      .map((s) => s.trim().toLowerCase());
    return modules.filter((m) =>
      targets.some((s) => slugOf(m.slug).includes(s)),
    );
  }
  if (moduleSlug.value) {
    return modules.filter((m) =>
      slugOf(m.slug).includes(moduleSlug.value!.toLowerCase()),
    );
  }
  return modules;
});

// ── Points ────────────────────────────────────────────

const fmtPts = (n: number) => String(Math.round(n * 10) / 10).replace(".", ",");

// Schreiben : note de la correction IA ramenée aux points du module
function modulePoints(m: ModuleResultResponse): number | null {
  if (
    isSchreiben(m) &&
    m.points_obtained == null &&
    correctionStore.current?.max_score
  ) {
    const c = correctionStore.current;
    return (c.overall_score / c.max_score) * m.max_score;
  }
  if (m.points_obtained != null) return m.points_obtained;
  if (m.score_obtained != null) return (m.score_obtained * m.max_score) / 100;
  return null;
}

// TELC : Sprachbausteine rejoint le bloc Leseverstehen (105 pts)
const groups = computed<Group[]>(() => {
  const out: Group[] = [];
  for (const m of displayedModules.value) {
    const last = out[out.length - 1];
    if (
      slugOf(m.slug).includes("sprachbaustein") &&
      last?.modules.some((x) => slugOf(x.slug).includes("lese"))
    ) {
      last.modules.push(m);
      last.label = `${last.label} + ${m.name}`;
      continue;
    }
    out.push({ key: m.slug, label: m.name, modules: [m] });
  }
  return out;
});

const groupMax = (g: Group) =>
  g.modules.reduce((s, m) => s + (m.max_score || 0), 0);

function groupPoints(g: Group): number | null {
  let total = 0;
  for (const m of g.modules) {
    const p = modulePoints(m);
    if (p == null) return null;
    total += p;
  }
  return total;
}

function groupPercent(g: Group): number | null {
  const p = groupPoints(g);
  const max = groupMax(g);
  return p != null && max > 0 ? (p / max) * 100 : null;
}

const totals = computed(() => {
  let got = 0;
  let max = 0;
  let complete = true;
  for (const m of displayedModules.value) {
    max += m.max_score || 0;
    const p = modulePoints(m);
    if (p == null) complete = false;
    else got += p;
  }
  const percent =
    complete && max > 0 ? (got / max) * 100 : (result.value?.score ?? null);
  return { got, max, complete, percent };
});

const passPct = computed(() => result.value?.total_pass_score || 60);
const passPoints = computed(() => (totals.value.max * passPct.value) / 100);

const barColor = (pct: number | null) =>
  pct != null && pct >= passPct.value ? "bg-emerald-500" : "bg-amber-500";

const weakModules = computed(() =>
  groups.value
    .filter((g) => {
      const pct = groupPercent(g);
      return pct != null && pct < passPct.value;
    })
    .map((g) => g.label),
);

// ── Statut ────────────────────────────────────────────

const isPassed = computed<boolean | null>(() => {
  if (!result.value) return null;
  if (isSingleModule.value) {
    const only = displayedModules.value[0];
    if (
      displayedModules.value.length === 1 &&
      only &&
      isSchreiben(only) &&
      correctionStore.current
    ) {
      return correctionStore.current.passed;
    }
    return result.value.module_passed ?? null;
  }
  return result.value.passed ?? null;
});

const status = computed(() => {
  const pending =
    result.value?.status === "PENDING_REVIEW" || isPassed.value === null;
  if (pending) {
    return {
      title: t("result.pending"),
      icon: "pi-clock",
      bar: "bg-line",
      chip: "bg-card-2 text-muted",
      ring: "text-muted",
    };
  }
  if (isPassed.value) {
    return {
      title: t("result.passed"),
      icon: "pi-check-circle",
      bar: "bg-emerald-500",
      chip: "bg-emerald-500/10 text-emerald-600",
      ring: "text-emerald-500",
    };
  }
  return {
    title: t("result.failed"),
    icon: "pi-times-circle",
    bar: "bg-red-500",
    chip: "bg-red-500/10 text-red-500",
    ring: "text-red-500",
  };
});

// ── Détail ────────────────────────────────────────────

const detailModules = computed(() =>
  displayedModules.value.filter((m) => !isSchreiben(m)),
);

// ── Détail des réponses : filtre, compteurs, affichage ─────────────

type AnswerFilter = "all" | "wrong" | "right";
const answerFilter = ref<AnswerFilter>("all");

// Réponse lisible quelle que soit sa forme :
// "b", { answer: "b" }, { answer: { answer: "b" } } (reprise de session),
// { answer: "Wort", index: 12 } (TestDaF Hören 7), { answers: { col: [...] } } (ÖSD)
const showAnswer = (value: any): string => {
  if (value == null) return "";
  if (Array.isArray(value)) return value.map(showAnswer).filter(Boolean).join(", ");
  if (typeof value === "object") {
    if ("answer" in value) return showAnswer(value.answer);
    if ("answers" in value) return showAnswer(Object.values(value.answers ?? {}));
    if ("text" in value) return showAnswer(value.text);
    return Object.values(value).map(showAnswer).filter(Boolean).join(", ");
  }
  const s = String(value).trim();
  return s.length <= 2 ? s.toUpperCase() : s;
};

const teilStats = (teil: any) => {
  const answers: any[] = teil.answers ?? [];
  return {
    right: answers.filter((a) => a.is_correct === true).length,
    total: answers.length,
  };
};

const teilPercent = (teil: any) =>
  teil.max_score
    ? Math.min(100, Math.round(((teil.score_obtained ?? 0) / teil.max_score) * 100))
    : 0;

const moduleStats = (module: any) =>
  (module.teile ?? []).reduce(
    (acc: { right: number; total: number }, teil: any) => {
      const s = teilStats(teil);
      return { right: acc.right + s.right, total: acc.total + s.total };
    },
    { right: 0, total: 0 },
  );

const allAnswers = computed<any[]>(() =>
  (detailModules.value ?? []).flatMap((m: any) =>
    (m.teile ?? []).flatMap((teil: any) => teil.answers ?? []),
  ),
);

const answerCounts = computed(() => ({
  total: allAnswers.value.length,
  right: allAnswers.value.filter((a) => a.is_correct === true).length,
  wrong: allAnswers.value.filter((a) => a.is_correct === false).length,
}));

const answerFilters = computed(() => [
  { value: "all" as const, label: t("result.filter_all"), count: answerCounts.value.total },
  { value: "wrong" as const, label: t("result.filter_wrong"), count: answerCounts.value.wrong },
  { value: "right" as const, label: t("result.filter_right"), count: answerCounts.value.right },
]);

const filteredAnswers = (teil: any): any[] => {
  const answers: any[] = teil.answers ?? [];
  if (answerFilter.value === "wrong") return answers.filter((a) => a.is_correct === false);
  if (answerFilter.value === "right") return answers.filter((a) => a.is_correct === true);
  return answers;
};

const toggleModule = (s: string) => {
  const next = new Set(expandedModules.value);
  if (next.has(s)) next.delete(s);
  else next.add(s);
  expandedModules.value = next;
};

const formatAnswer = (
  answer: Record<string, any> | null | undefined,
): string => {
  if (!answer) return "-";
  if (answer.answer != null) {
    const v = String(answer.answer);
    return v.length <= 2 ? v.toUpperCase() : v;
  }
  if (answer.answers && typeof answer.answers === "object") {
    return Object.entries(answer.answers)
      .map(([k, v]) => `${k} : ${Array.isArray(v) ? v.join(", ") : v}`)
      .join(" · ");
  }
  if (answer.text) return answer.text;
  return "-";
};

// feedback est un objet côté API : on en extrait le texte lisible
const feedbackText = (
  feedback: Record<string, any> | null | undefined,
): string => {
  if (!feedback) return "";
  if (typeof feedback === "string") return feedback;
  return feedback.comment || feedback.text || feedback.message || "";
};

const moduleIcon = (s?: string) => {
  const v = slugOf(s);
  if (v.includes("sprachbaustein")) return "pi-language";
  if (v.includes("lese")) return "pi-book";
  if (v.includes("hor") || v.includes("hoer") || v.includes("hör"))
    return "pi-volume-up";
  if (v.includes("schreib") || v.includes("schriftlich")) return "pi-pencil";
  return "pi-file";
};

const actualDuration = computed(() => {
  if (!result.value?.submitted_at || !result.value?.started_at) return null;
  const seconds = Math.max(
    0,
    Math.round(
      (new Date(result.value.submitted_at).getTime() -
        new Date(result.value.started_at).getTime()) /
        1000,
    ),
  );
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return h > 0
    ? `${h} h ${String(m).padStart(2, "0")} min`
    : `${m} min ${String(s).padStart(2, "0")} s`;
});

const goToCorrection = () => {
  const sessionId = result.value?.session_id;
  if (!sessionId) return;
  navigateTo(localePath(`/dashboard/examens/${slug}/correction/${sessionId}`));
};

// ── Chargement ────────────────────────────────────────

onMounted(async () => {
  const queryId = route.query.sessionId as string | undefined;
  const cached = sessionStore.result;

  // Le store peut garder le résultat d'une autre session : on vérifie l'id
  if (cached && (!queryId || cached.session_id === queryId)) {
    result.value = cached;
  } else {
    const targetId = queryId || sessionStore.sessionId;
    if (targetId) {
      const res = await sessionStore.getResult(targetId);
      if (res.success) result.value = res.result ?? null;
    }
  }

  if (result.value && displayedModules.value.some(isSchreiben)) {
    try {
      await correctionStore.fetchBySession(result.value.session_id);
    } catch {
      /* correction pas encore disponible */
    }
  }

  loading.value = false;
});
</script>
