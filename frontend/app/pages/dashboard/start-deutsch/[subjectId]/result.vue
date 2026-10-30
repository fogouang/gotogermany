<!-- pages/dashboard/start-deutsch/[subjectId]/result.vue -->
<template>
  <div class="pb-10">
    <!-- ── Chargement ── -->
    <div v-if="store.loading && !result" class="space-y-4">
      <div class="h-44 animate-pulse rounded-card bg-card-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Introuvable ── -->
    <div
      v-else-if="!result"
      class="flex flex-col items-center justify-center rounded-card border border-line bg-card py-20 text-center"
    >
      <span
        class="mb-4 flex size-14 items-center justify-center rounded-leaf bg-red-500/10"
      >
        <i class="pi pi-exclamation-triangle text-2xl text-red-500" />
      </span>
      <p class="mb-4 font-semibold text-ink">
        {{ t("start_deutsch.result.not_found") }}
      </p>
      <Button
        :label="t('start_deutsch.result.back')"
        outlined
        size="small"
        @click="goToCatalogue"
      />
    </div>

    <template v-else>
      <!-- ══ En-tête du résultat ══ -->
      <section
        class="relative overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <div class="absolute inset-x-0 top-0 h-1" :class="barClass" />

        <div
          class="grid gap-6 p-5 sm:p-7 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center"
        >
          <div class="min-w-0">
            <div class="mb-3 flex flex-wrap items-center gap-2">
              <span
                class="text-xs font-semibold uppercase tracking-wider text-muted"
              >
                Start Deutsch · {{ result.level }}
              </span>
              <span
                v-if="hasPending"
                class="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
              >
                {{ t("start_deutsch.result.provisional") }}
              </span>
            </div>

            <div class="flex items-center gap-3">
              <div
                class="flex size-12 shrink-0 items-center justify-center rounded-leaf"
                :class="statusClass"
              >
                <i class="pi text-xl" :class="statusIcon" />
              </div>
              <h1 class="text-2xl font-bold text-ink sm:text-3xl">
                {{ statusLabel }}
              </h1>
            </div>

            <p class="mt-3 text-sm text-muted">{{ result.subject_title }}</p>

            <div class="mt-4 flex flex-wrap gap-2">
              <span
                class="inline-flex items-center gap-1.5 rounded-full border border-line bg-card-2 px-3 py-1.5 text-xs font-medium text-ink"
              >
                <i class="pi pi-list text-[11px] text-muted" />
                {{
                  t("start_deutsch.result.modules_corrected", {
                    done: scoredModules.length,
                    total: gradedModules.length,
                  })
                }}
              </span>
              <span
                v-if="answerCounts.total"
                class="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold tabular-nums text-emerald-700 dark:text-emerald-400"
              >
                <i class="pi pi-check text-[11px]" />
                {{ answerCounts.right }} / {{ answerCounts.total }}
              </span>
            </div>
          </div>

          <!-- Score -->
          <div
            class="flex items-center gap-5 rounded-card border border-line bg-card-2 p-4 lg:flex-col lg:gap-2 lg:px-8"
          >
            <div class="relative size-28 shrink-0">
              <svg class="size-28 -rotate-90" viewBox="0 0 120 120" aria-hidden="true">
                <circle
                  cx="60"
                  cy="60"
                  r="52"
                  fill="none"
                  stroke-width="10"
                  class="stroke-line"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="52"
                  fill="none"
                  stroke-width="10"
                  stroke-linecap="round"
                  class="transition-[stroke-dasharray] duration-700"
                  :class="ringClass"
                  :stroke-dasharray="`${(scorePercent / 100) * RING} ${RING}`"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-3xl font-extrabold leading-none tabular-nums text-ink">
                  {{ scorePercent }}
                </span>
                <span class="text-xs text-muted">%</span>
              </div>
            </div>
            <div class="lg:text-center">
              <p class="text-base font-bold tabular-nums text-ink">
                {{
                  t("start_deutsch.result.points_of", {
                    score: formatPoints(scoreObtained),
                    max: formatPoints(scoreMax),
                  })
                }}
              </p>
              <p class="text-xs text-muted">
                {{ t("start_deutsch.result.threshold", { pct: PASS }) }}
              </p>
            </div>
          </div>
        </div>
      </section>

      <div
        class="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-start"
      >
        <!-- ══ Colonne principale : détail des réponses ══ -->
        <div class="order-2 min-w-0 space-y-3 lg:order-1">
          <h2 class="font-semibold text-ink">
            {{ t("start_deutsch.result.detail") }}
          </h2>

          <div
            v-for="mod in modules.filter((m) => m.expandable)"
            :key="mod.module_id"
            class="overflow-hidden rounded-card border border-line bg-card"
          >
            <button
              type="button"
              class="flex w-full items-center justify-between gap-3 px-5 py-4 transition-colors hover:bg-card-2 sm:px-6"
              :aria-expanded="expanded.has(mod.module_id)"
              @click="toggle(mod.module_id)"
            >
              <div class="flex min-w-0 items-center gap-3">
                <span
                  class="flex size-9 shrink-0 items-center justify-center rounded-leaf"
                  :class="mod.iconBubble"
                >
                  <i class="pi text-sm" :class="mod.icon" />
                </span>
                <div class="min-w-0 text-left">
                  <p class="truncate text-sm font-semibold text-ink">{{ mod.label }}</p>
                  <p class="text-xs" :class="mod.subClass">{{ mod.sub }}</p>
                </div>
              </div>
              <i
                class="pi text-sm text-muted"
                :class="expanded.has(mod.module_id) ? 'pi-chevron-up' : 'pi-chevron-down'"
              />
            </button>

            <div
              v-if="expanded.has(mod.module_id)"
              class="divide-y divide-line border-t border-line"
            >
              <div
                v-for="teil in mod.raw.teile ?? []"
                :key="teil.teil_id"
                class="px-5 py-4 sm:px-6"
              >
                <div class="mb-2 flex items-center justify-between">
                  <p class="text-xs font-bold uppercase tracking-wide text-muted">
                    Teil {{ teil.teil_number }}
                  </p>
                  <span class="text-xs font-semibold tabular-nums text-muted">
                    {{ formatPoints(teil.score_obtained) }} / {{ teil.max_score }} pts
                  </span>
                </div>

                <ul class="space-y-1.5">
                  <li
                    v-for="answer in teil.answers ?? []"
                    :key="answer.question_id"
                    class="flex items-start gap-3 rounded-leaf bg-card-2 px-3 py-2 text-sm"
                  >
                    <span
                      class="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold"
                      :class="answerBubble(answer.is_correct)"
                    >
                      {{ answer.question_number }}
                    </span>

                    <!-- Texte libre (Schreiben) -->
                    <p
                      v-if="isFreeText(answer.user_answer)"
                      class="min-w-0 flex-1 whitespace-pre-wrap text-ink"
                    >
                      {{ answer.user_answer!.text || "-" }}
                    </p>

                    <!-- Réponse simple ou formulaire -->
                    <div
                      v-else
                      class="flex min-w-0 flex-1 flex-wrap items-center gap-x-2 gap-y-1"
                    >
                      <span
                        class="font-medium"
                        :class="
                          answer.is_correct === false
                            ? 'text-red-600 line-through decoration-1'
                            : 'text-ink'
                        "
                      >
                        {{ formatAnswer(answer.user_answer) }}
                      </span>
                      <template v-if="answer.is_correct === false && answer.correct_answer">
                        <i class="pi pi-arrow-right text-[10px] text-faint" />
                        <span class="font-semibold text-emerald-600">{{
                          formatAnswer(answer.correct_answer)
                        }}</span>
                      </template>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- ══ Colonne latérale : résumé par module ══ -->
        <aside class="order-1 space-y-5 lg:sticky lg:top-5 lg:order-2">
          <div class="overflow-hidden rounded-card border border-line bg-card">
            <div class="border-b border-line px-5 py-4">
              <h2 class="text-sm font-semibold text-ink">
                {{ t("start_deutsch.result.by_module") }}
              </h2>
            </div>

            <div class="divide-y divide-line">
              <div
                v-for="mod in modules"
                :key="`side-${mod.module_id}`"
                class="flex items-center gap-3 px-5 py-4"
              >
                <span
                  class="flex size-10 shrink-0 items-center justify-center rounded-leaf"
                  :class="mod.iconBubble"
                >
                  <i class="pi" :class="mod.icon" />
                </span>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-2">
                    <p class="truncate text-sm font-semibold text-ink">{{ mod.label }}</p>
                    <span
                      v-if="mod.state === 'scored'"
                      class="shrink-0 text-sm font-bold tabular-nums"
                      :class="mod.pct >= PASS ? 'text-emerald-600' : 'text-red-600'"
                    >
                      {{ mod.pct }}%
                    </span>
                  </div>
                  <div v-if="mod.state === 'scored'" class="mt-1.5">
                    <div class="h-2 overflow-hidden rounded-full bg-card-2">
                      <div
                        class="h-full rounded-full transition-[width] duration-500"
                        :class="mod.pct >= PASS ? 'bg-emerald-500' : 'bg-red-500'"
                        :style="{ width: `${mod.pct}%` }"
                      />
                    </div>
                    <p class="mt-1 text-xs tabular-nums text-muted">{{ mod.sub }}</p>
                  </div>
                  <p v-else class="mt-0.5 flex items-center gap-1.5 text-xs" :class="mod.subClass">
                    <i v-if="mod.state === 'pending'" class="pi pi-clock text-xs" />
                    {{ mod.sub }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Modules encore en correction -->
          <div
            v-if="hasPending"
            class="space-y-3 rounded-card border border-amber-500/30 bg-amber-500/10 p-4"
          >
            <p class="text-sm text-ink">
              {{ t("start_deutsch.result.pending_note", { modules: pendingNames }) }}
            </p>
            <Button
              :label="t('start_deutsch.result.refresh')"
              icon="pi pi-refresh"
              size="small"
              outlined
              class="w-full"
              :loading="refreshing"
              @click="refresh"
            />
          </div>

          <div class="flex flex-col gap-2">
            <Button
              :label="t('start_deutsch.result.retry')"
              icon="pi pi-refresh"
              class="w-full"
              @click="retrySubject"
            />
            <Button
              :label="t('start_deutsch.result.back')"
              icon="pi pi-arrow-left"
              outlined
              class="w-full"
              @click="goToCatalogue"
            />
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const store = useStartDeutschSessionStore();

/** Seuil de réussite affiché (60 %, comme aux examens Goethe A1 / A2) */
const PASS = 60;
/** Circonférence de l'anneau (rayon 52) */
const RING = 2 * Math.PI * 52;

const result = computed(() => store.result);
const expanded = ref<Set<string>>(new Set());
const refreshing = ref(false);

// ── Modules ──
// L'oral Start Deutsch n'est pas noté : il ne compte ni dans le score ni dans « en attente »
const ORAL = new Set(["sprechen"]);

const LABELS: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  horen: "Hören",
  hören: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
};
const ICONS: Record<string, string> = {
  lesen: "pi-book",
  hoeren: "pi-volume-up",
  horen: "pi-volume-up",
  hören: "pi-volume-up",
  schreiben: "pi-pencil",
  sprechen: "pi-microphone",
};

type RawModule = NonNullable<
  NonNullable<typeof result.value>["modules"]
>[number];

const pct = (score: number, max: number) =>
  max > 0 ? Math.round((score / max) * 100) : 0;

const modules = computed(() =>
  (result.value?.modules ?? []).map((raw: RawModule) => {
    const slug = raw.slug.toLowerCase();
    const label = LABELS[slug] ?? raw.slug;
    const icon = ICONS[slug] ?? "pi-file";

    if (ORAL.has(slug)) {
      return {
        module_id: raw.module_id,
        raw,
        label,
        icon,
        state: "oral" as const,
        pct: 0,
        sub: t("start_deutsch.result.oral_not_scored"),
        subClass: "text-muted",
        iconBubble: "bg-card-2 text-muted",
        expandable: false,
      };
    }

    if (!raw.is_corrected) {
      return {
        module_id: raw.module_id,
        raw,
        label,
        icon,
        state: "pending" as const,
        pct: 0,
        sub: t("start_deutsch.result.pending"),
        subClass: "text-amber-600",
        iconBubble: "bg-amber-500/15 text-amber-600",
        expandable: (raw.teile ?? []).some(
          (teil) => (teil.answers ?? []).length > 0,
        ),
      };
    }

    const p = pct(raw.score_obtained, raw.max_score);
    return {
      module_id: raw.module_id,
      raw,
      label,
      icon,
      state: "scored" as const,
      pct: p,
      sub: t("start_deutsch.result.points_of", {
        score: formatPoints(raw.score_obtained),
        max: formatPoints(raw.max_score),
      }),
      subClass: "text-muted",
      iconBubble:
        p >= PASS
          ? "bg-emerald-500/10 text-emerald-600"
          : "bg-red-500/10 text-red-600",
      expandable: true,
    };
  }),
);

// ── Score : uniquement sur les modules notés et déjà corrigés ──
const scoredModules = computed(() =>
  modules.value.filter((m) => m.state === "scored"),
);
const scoreObtained = computed(() =>
  scoredModules.value.reduce((s, m) => s + m.raw.score_obtained, 0),
);
const scoreMax = computed(() =>
  scoredModules.value.reduce((s, m) => s + m.raw.max_score, 0),
);
const scorePercent = computed(() => pct(scoreObtained.value, scoreMax.value));

const gradedModules = computed(() =>
  modules.value.filter((m) => m.state !== "oral"),
);

// Réponses justes sur les modules corrigés (hors Schreiben, noté par critères)
const answerCounts = computed(() => {
  let right = 0;
  let total = 0;
  for (const m of scoredModules.value) {
    for (const teil of m.raw.teile ?? []) {
      for (const a of teil.answers ?? []) {
        if (a.is_correct == null || isFreeText(a.user_answer)) continue;
        total += 1;
        if (a.is_correct) right += 1;
      }
    }
  }
  return { right, total };
});

const pendingModules = computed(() =>
  modules.value.filter((m) => m.state === "pending"),
);
const hasPending = computed(() => pendingModules.value.length > 0);
const pendingNames = computed(() =>
  pendingModules.value.map((m) => m.label).join(", "),
);

// ── Statut : formulation neutre, Start Deutsch est un entraînement ──
const statusIcon = computed(() => {
  if (hasPending.value) return "pi-clock";
  return scorePercent.value >= PASS ? "pi-check-circle" : "pi-arrow-up-right";
});

const statusLabel = computed(() => {
  if (hasPending.value) return t("start_deutsch.result.pending_review");
  return scorePercent.value >= PASS
    ? t("start_deutsch.result.good_score")
    : t("start_deutsch.result.keep_practicing");
});

const statusClass = computed(() => {
  if (hasPending.value) return "bg-amber-500/15 text-amber-600";
  return scorePercent.value >= PASS
    ? "bg-emerald-500/10 text-emerald-600"
    : "bg-primary/10 text-primary";
});

const barClass = computed(() => {
  if (hasPending.value) return "bg-amber-500";
  return scorePercent.value >= PASS ? "bg-emerald-500" : "bg-primary";
});

const ringClass = computed(() => {
  if (hasPending.value) return "stroke-amber-500";
  return scorePercent.value >= PASS ? "stroke-emerald-500" : "stroke-primary";
});

// ── Réponses ──
function formatPoints(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function isFreeText(
  answer: Record<string, any> | null | undefined,
): answer is { text?: string } {
  return !!answer && typeof answer.text === "string";
}

/** Réponse simple ({answer}) ou formulaire ({"1": "...", "2": "..."}) */
function formatAnswer(answer: Record<string, any> | null | undefined): string {
  if (!answer) return "-";
  if (answer.answer != null && answer.answer !== "")
    return String(answer.answer);
  const values = Object.values(answer).filter(
    (v) => v != null && String(v).trim() !== "",
  );
  return values.length ? values.join(" · ") : "-";
}

function answerBubble(isCorrect: boolean | null | undefined) {
  if (isCorrect === true) return "bg-emerald-500/15 text-emerald-600";
  if (isCorrect === false) return "bg-red-500/15 text-red-600";
  return "bg-card-2 text-muted";
}

function toggle(moduleId: string) {
  // Nouveau Set pour que Vue détecte le changement
  const next = new Set(expanded.value);
  if (next.has(moduleId)) next.delete(moduleId);
  else next.add(moduleId);
  expanded.value = next;
}

// ── Actions ──
async function refresh() {
  const sessionId =
    (route.query.sessionId as string | undefined) ?? result.value?.session_id;
  if (!sessionId) return;
  refreshing.value = true;
  await store.getResult(sessionId);
  refreshing.value = false;
}

function goToCatalogue() {
  navigateTo(localePath("/dashboard/start-deutsch"));
}

function retrySubject() {
  navigateTo(
    localePath(`/dashboard/start-deutsch/${route.params.subjectId}/session`),
  );
}

onMounted(async () => {
  const sessionId = route.query.sessionId as string | undefined;
  if (sessionId && (!store.result || store.result.session_id !== sessionId)) {
    await store.getResult(sessionId);
  }
  // Modules corrigés ouverts d'office, comme sur le résultat des B
  expanded.value = new Set(
    modules.value.filter((m) => m.state === "scored").map((m) => m.module_id),
  );
});
</script>