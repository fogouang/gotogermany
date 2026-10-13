<template>
  <div class="space-y-5 pb-10">
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
      <div
        class="bg-card border border-line rounded-card shadow-soft overflow-hidden"
      >
        <div :class="['h-1.5', status.bar]"></div>
        <div class="p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center gap-6">
          <div class="flex-1 min-w-0">
            <p
              class="text-xs font-semibold uppercase tracking-wider text-muted mb-2"
            >
              {{ result.exam_name }} · {{ t("result.subject") }}
              {{ result.subject_number }}
              <span
                v-if="isSingleModule && displayedModules[0]"
                class="ml-1 normal-case tracking-normal bg-card-2 border border-line px-2 py-0.5 rounded-full"
              >
                {{ displayedModules.map((m) => m.name).join(" + ") }}
              </span>
            </p>

            <div class="flex items-center gap-3 mb-2">
              <div
                :class="[
                  'w-10 h-10 rounded-leaf flex items-center justify-center shrink-0',
                  status.chip,
                ]"
              >
                <i :class="['pi text-lg', status.icon]"></i>
              </div>
              <h1 class="text-2xl font-bold text-ink">{{ status.title }}</h1>
            </div>

            <p
              v-if="result.result_message"
              class="text-sm text-muted leading-relaxed max-w-lg"
            >
              {{ result.result_message }}
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
            </div>
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
                  :class="status.ring"
                  :stroke-dasharray="`${(Math.min(totals.percent ?? 0, 100) / 100) * 201} 201`"
                />
              </svg>
              <div
                class="absolute inset-0 flex flex-col items-center justify-center"
              >
                <span
                  class="text-2xl font-extrabold text-ink leading-none tabular-nums"
                >
                  {{
                    totals.percent != null ? Math.round(totals.percent) : "-"
                  }}
                </span>
                <span class="text-[11px] text-muted">%</span>
              </div>
            </div>
            <div class="text-left sm:text-center">
              <p
                v-if="totals.complete"
                class="text-sm font-semibold text-ink tabular-nums"
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
      </div>

      <!-- ── Résultat par module ── -->
      <div class="bg-card border border-line rounded-card overflow-hidden">
        <div
          class="px-5 sm:px-6 py-4 border-b border-line flex items-center justify-between gap-3"
        >
          <h2 class="font-semibold text-ink">
            {{
              isSingleModule
                ? t("result.module_result")
                : t("result.official.written_part")
            }}
          </h2>
          <span
            v-if="!isSingleModule && totals.complete"
            class="text-sm font-semibold text-ink tabular-nums"
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
          <div
            v-for="group in groups"
            :key="group.key"
            class="px-5 sm:px-6 py-4"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-11 h-11 rounded-leaf bg-primary/10 flex items-center justify-center shrink-0"
              >
                <i
                  :class="[
                    'pi text-primary',
                    moduleIcon(group.modules[0]?.slug),
                  ]"
                ></i>
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-3 mb-1.5">
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

                <!-- Barre -->
                <div
                  v-if="groupPoints(group) != null"
                  class="flex items-center gap-2"
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
                  <span class="text-xs text-muted w-10 text-right tabular-nums">
                    {{ Math.round(groupPercent(group) ?? 0) }} %
                  </span>
                </div>

                <!-- Correction en attente -->
                <div
                  v-else
                  class="flex items-center gap-1.5 text-amber-600 text-xs"
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

                <!-- Détail du bloc (ex. Leseverstehen + Sprachbausteine) -->
                <div v-if="group.modules.length > 1" class="mt-2 space-y-0.5">
                  <p
                    v-for="m in group.modules"
                    :key="m.slug"
                    class="flex justify-between text-xs text-muted"
                  >
                    <span>{{ m.name }}</span>
                    <span class="tabular-nums">
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
              </div>

              <Button
                v-if="
                  group.modules.some(isSchreiben) && correctionStore.current
                "
                :label="t('result.see_correction')"
                icon="pi pi-eye"
                size="small"
                outlined
                severity="secondary"
                class="shrink-0 hidden! sm:inline-flex!"
                @click="goToCorrection"
              />
            </div>
            <Button
              v-if="group.modules.some(isSchreiben) && correctionStore.current"
              :label="t('result.see_correction')"
              icon="pi pi-eye"
              size="small"
              outlined
              severity="secondary"
              class="w-full mt-3 sm:hidden!"
              @click="goToCorrection"
            />
          </div>

          <!-- Oral -->
          <div
            v-if="!isSingleModule"
            class="px-5 sm:px-6 py-4 flex items-center gap-4"
          >
            <div
              class="w-11 h-11 rounded-leaf bg-card-2 border border-line flex items-center justify-center shrink-0"
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
            </div>
            <NuxtLink
              :to="localePath(`/dashboard/sprechen/${result.subject_id}`)"
              class="text-xs font-semibold text-primary hover:underline whitespace-nowrap"
            >
              {{ t("result.official.oral_link") }}
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- ── Pourquoi non réussi ── -->
      <div
        v-if="!isSingleModule && result.passed === false"
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

      <!-- ── Détail des réponses ── -->
      <div
        v-for="module in detailModules"
        :key="`detail-${module.slug}`"
        class="bg-card border border-line rounded-card overflow-hidden"
      >
        <button
          type="button"
          class="w-full flex items-center justify-between px-5 sm:px-6 py-4 hover:bg-card-2 transition-colors"
          @click="toggleModule(module.slug)"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div
              class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0"
            >
              <i
                :class="['pi text-sm text-primary', moduleIcon(module.slug)]"
              ></i>
            </div>
            <h2 class="font-semibold text-ink text-sm truncate">
              {{ t("result.official.block_detail") }} · {{ module.name }}
            </h2>
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
          class="border-t border-line"
        >
          <div
            v-for="teil in module.teile"
            :key="teil.teil_number"
            class="border-b border-line last:border-0"
          >
            <div
              class="px-5 sm:px-6 py-2.5 bg-card-2 flex items-center justify-between"
            >
              <p
                class="text-xs font-semibold text-muted uppercase tracking-wide"
              >
                {{ t("result.official.teil", { n: teil.teil_number }) }}
              </p>
              <span class="text-xs font-semibold text-ink tabular-nums">
                {{
                  t("result.official.points", {
                    got: fmtPts(teil.score_obtained ?? 0),
                    max: fmtPts(teil.max_score),
                  })
                }}
              </span>
            </div>

            <div v-if="teil.answers?.length" class="divide-y divide-line">
              <div
                v-for="answer in teil.answers ?? []"
                :key="answer.question_id"
                class="px-5 sm:px-6 py-3 flex items-start gap-3"
              >
                <span
                  :class="[
                    'w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5',
                    answer.is_correct === true
                      ? 'bg-emerald-500/10 text-emerald-600'
                      : answer.is_correct === false
                        ? 'bg-red-500/10 text-red-500'
                        : 'bg-card-2 text-faint',
                  ]"
                >
                  <i
                    :class="[
                      'pi text-[10px]',
                      answer.is_correct === true
                        ? 'pi-check'
                        : answer.is_correct === false
                          ? 'pi-times'
                          : 'pi-minus',
                    ]"
                  ></i>
                </span>
                <div class="flex-1 min-w-0 text-sm">
                  <div class="flex flex-wrap gap-x-4 gap-y-1">
                    <span class="text-muted">
                      <span class="font-semibold text-ink tabular-nums mr-1"
                        >{{ answer.question_number }}.</span
                      >
                      {{ t("result.your_answer") }} :
                      <strong class="text-ink">{{
                        formatAnswer(answer.user_answer)
                      }}</strong>
                    </span>
                    <span
                      v-if="
                        answer.correct_answer && answer.is_correct === false
                      "
                      class="text-emerald-600"
                    >
                      {{ t("result.correct_answer") }} :
                      <strong>{{ formatAnswer(answer.correct_answer) }}</strong>
                    </span>
                  </div>
                  <p v-if="answer.feedback" class="text-xs text-faint mt-1">
                    {{ answer.feedback }}
                  </p>
                </div>
              </div>
            </div>
            <p v-else class="px-5 sm:px-6 py-3 text-xs text-faint">
              {{ t("result.official.no_answer") }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Actions ── -->
      <div class="flex flex-col sm:flex-row gap-3">
        <Button
          :label="t('result.back_to_exams')"
          icon="pi pi-arrow-left"
          outlined
          severity="secondary"
          class="flex-1"
          @click="navigateTo(localePath('/dashboard/examens'))"
        />
        <Button
          :label="t('result.another_module')"
          icon="pi pi-list"
          outlined
          class="flex-1"
          @click="
            navigateTo(
              localePath(`/dashboard/examens/${slug}/${result.subject_id}`),
            )
          "
        />
        <Button
          :label="t('result.my_results')"
          icon="pi pi-trophy"
          class="flex-1"
          @click="navigateTo(localePath('/dashboard/resultats'))"
        />
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
