<!-- pages/dashboard/start-deutsch/[subjectId]/result.vue -->
<template>
  <div class="space-y-5 pb-10">
    <!-- ── Chargement ── -->
    <div v-if="store.loading && !result" class="space-y-4">
      <div class="h-44 animate-pulse rounded-card bg-card-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Introuvable ── -->
    <div
      v-else-if="!result"
      class="flex flex-col items-center justify-center rounded-card border border-line bg-card py-16 text-center shadow-soft"
    >
      <span
        class="mb-4 flex size-14 items-center justify-center rounded-card bg-red-500/10"
      >
        <i class="pi pi-exclamation-triangle text-2xl text-red-600" />
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
      <!-- ══ Score ══ -->
      <section
        class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-7"
      >
        <div
          class="flex flex-col items-center gap-6 sm:flex-row sm:items-center"
        >
          <!-- Anneau : score sur les modules déjà corrigés -->
          <div class="relative size-32 shrink-0">
            <svg
              class="size-32 -rotate-90"
              viewBox="0 0 120 120"
              aria-hidden="true"
            >
              <circle
                cx="60"
                cy="60"
                r="52"
                fill="none"
                stroke-width="10"
                class="stroke-card-2"
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
            <div
              class="absolute inset-0 flex flex-col items-center justify-center"
            >
              <span class="text-3xl font-extrabold tabular-nums text-ink"
                >{{ scorePercent }}%</span
              >
              <span class="text-[11px] tabular-nums text-muted">
                {{
                  t("start_deutsch.result.points_of", {
                    score: formatPoints(scoreObtained),
                    max: formatPoints(scoreMax),
                  })
                }}
              </span>
            </div>
          </div>

          <div class="min-w-0 flex-1 text-center sm:text-left">
            <div
              class="flex flex-wrap items-center justify-center gap-2 sm:justify-start"
            >
              <span
                class="rounded-leaf bg-primary/10 px-2 py-0.5 text-xs font-bold text-primary"
              >
                {{ result.level }}
              </span>
              <span
                v-if="hasPending"
                class="rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
              >
                {{ t("start_deutsch.result.provisional") }}
              </span>
            </div>
            <h1 class="mt-2 text-lg font-bold text-ink sm:text-xl">
              {{ result.subject_title }}
            </h1>

            <p
              class="mt-3 inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-semibold"
              :class="statusClass"
            >
              <i :class="['pi', statusIcon]" />
              {{ statusLabel }}
            </p>

            <!-- Modules encore en correction -->
            <div
              v-if="hasPending"
              class="mt-4 flex flex-col gap-3 rounded-leaf border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-left sm:flex-row sm:items-center"
            >
              <p class="min-w-0 flex-1 text-sm text-ink">
                {{
                  t("start_deutsch.result.pending_note", {
                    modules: pendingNames,
                  })
                }}
              </p>
              <Button
                :label="t('start_deutsch.result.refresh')"
                icon="pi pi-refresh"
                size="small"
                outlined
                class="shrink-0"
                :loading="refreshing"
                @click="refresh"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- ══ Résultat par module ══ -->
      <section
        class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <header class="border-b border-line px-5 py-4 sm:px-6">
          <h2 class="font-semibold text-ink">
            {{ t("start_deutsch.result.by_module") }}
          </h2>
        </header>

        <div class="divide-y divide-line">
          <div v-for="mod in modules" :key="mod.module_id">
            <!-- Ligne du module -->
            <button
              type="button"
              class="flex w-full items-center gap-4 bg-transparent px-5 py-4 text-left transition-colors enabled:hover:bg-card-2/60 disabled:cursor-default"
              :disabled="!mod.expandable"
              :aria-expanded="
                mod.expandable ? expanded.has(mod.module_id) : undefined
              "
              @click="toggle(mod.module_id)"
            >
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-leaf"
                :class="mod.iconBubble"
              >
                <i :class="['pi', mod.icon]" />
              </span>

              <span class="min-w-0 flex-1">
                <span class="block text-sm font-semibold text-ink">{{
                  mod.label
                }}</span>
                <span class="block text-xs" :class="mod.subClass">{{
                  mod.sub
                }}</span>
              </span>

              <!-- Barre (modules notés et corrigés) -->
              <span
                v-if="mod.state === 'scored'"
                class="hidden w-40 shrink-0 sm:block"
              >
                <span
                  class="block h-1.5 overflow-hidden rounded-full bg-card-2"
                >
                  <span
                    class="block h-full rounded-full transition-[width] duration-500"
                    :class="mod.pct >= PASS ? 'bg-emerald-500' : 'bg-red-500'"
                    :style="{ width: `${mod.pct}%` }"
                  />
                </span>
              </span>

              <span
                v-if="mod.state === 'scored'"
                class="w-14 shrink-0 text-right text-sm font-bold tabular-nums"
                :class="mod.pct >= PASS ? 'text-emerald-600' : 'text-red-600'"
              >
                {{ mod.pct }}%
              </span>

              <i
                v-if="mod.expandable"
                class="pi pi-chevron-down shrink-0 text-xs text-faint transition-transform"
                :class="{ 'rotate-180': expanded.has(mod.module_id) }"
              />
              <span v-else class="w-3 shrink-0" />
            </button>

            <!-- Détail du module, juste sous sa ligne -->
            <div
              v-if="mod.expandable && expanded.has(mod.module_id)"
              class="border-t border-line bg-card-2/40"
            >
              <div
                v-for="teil in mod.raw.teile ?? []"
                :key="teil.teil_id"
                class="px-5 py-4 sm:px-6"
              >
                <div class="mb-2 flex items-center justify-between">
                  <p
                    class="text-xs font-bold uppercase tracking-wide text-muted"
                  >
                    Teil {{ teil.teil_number }}
                  </p>
                  <span class="text-xs font-semibold tabular-nums text-muted">
                    {{ formatPoints(teil.score_obtained) }} /
                    {{ teil.max_score }} pts
                  </span>
                </div>

                <ul class="space-y-1.5">
                  <li
                    v-for="answer in teil.answers ?? []"
                    :key="answer.question_id"
                    class="flex items-start gap-3 rounded-leaf bg-card px-3 py-2 text-sm"
                  >
                    <span
                      class="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold"
                      :class="answerBubble(answer.is_correct)"
                    >
                      {{ answer.question_number }}
                    </span>

                    <!-- Texte libre (Schreiben) -->
                    <div
                      v-if="isFreeText(answer.user_answer)"
                      class="min-w-0 flex-1"
                    >
                      <p class="whitespace-pre-wrap text-ink">
                        {{ answer.user_answer!.text || "-" }}
                      </p>
                    </div>

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
                      <template
                        v-if="
                          answer.is_correct === false && answer.correct_answer
                        "
                      >
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
      </section>

      <!-- ══ Actions ══ -->
      <div class="flex flex-col gap-3 sm:flex-row">
        <Button
          :label="t('start_deutsch.result.back')"
          icon="pi pi-arrow-left"
          outlined
          class="flex-1"
          @click="goToCatalogue"
        />
        <Button
          :label="t('start_deutsch.result.retry')"
          icon="pi pi-refresh"
          class="flex-1"
          @click="retrySubject"
        />
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
});
</script>
