<!-- pages/dashboard/start-deutsch/[subjectId]/result.vue -->
<template>
  <div class="space-y-6 pb-10">
    <!-- ── Chargement ── -->
    <div v-if="store.loading" class="space-y-4">
      <div class="h-48 animate-pulse rounded-card bg-card-2" />
      <div class="h-64 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Introuvable ── -->
    <div
      v-else-if="!result"
      class="flex flex-col items-center justify-center rounded-card border border-line bg-card py-16 shadow-soft"
    >
      <div class="mb-4 flex size-14 items-center justify-center rounded-card bg-red-500/10">
        <i class="pi pi-exclamation-triangle text-2xl text-red-600" />
      </div>
      <p class="mb-4 font-semibold text-ink">{{ t("start_deutsch.result.not_found") }}</p>
      <Button :label="t('start_deutsch.result.back')" outlined size="small" @click="goToCatalogue" />
    </div>

    <template v-else>
      <!-- ══ Score ══ -->
      <section class="rounded-card border border-line bg-card p-6 text-center shadow-soft sm:p-8">
        <p class="text-xs font-bold uppercase tracking-widest text-faint">
          {{ result.subject_title }} · {{ result.level }}
        </p>
        <p class="mt-2 text-5xl font-bold text-primary">{{ scorePercent }}%</p>
        <p class="mt-1 text-sm text-muted">
          {{ t("start_deutsch.result.score_of", { score: result.score?.toFixed(0) ?? "0" }) }}
        </p>

        <div class="mx-auto mt-5 h-2.5 w-full max-w-sm overflow-hidden rounded-full bg-card-2">
          <div class="h-full rounded-full bg-primary transition-all duration-500" :style="{ width: `${scorePercent}%` }" />
        </div>

        <p
          class="mt-5 inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold"
          :class="statusClass"
        >
          <i :class="['pi', statusIcon]" />
          {{ statusLabel }}
        </p>
      </section>

      <!-- ══ Résultat par module ══ -->
      <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <header class="border-b border-line px-5 py-4 sm:px-6">
          <h2 class="font-semibold text-ink">{{ t("start_deutsch.result.by_module") }}</h2>
        </header>

        <div class="divide-y divide-line">
          <button
            v-for="mod in result.modules ?? []"
            :key="mod.module_id"
            type="button"
            class="flex w-full items-center gap-4 px-5 py-4 text-left transition-colors hover:bg-card-2 sm:px-6"
            @click="toggleModule(mod.module_id)"
          >
            <div class="flex size-11 shrink-0 items-center justify-center rounded-leaf bg-primary/10">
              <i :class="['pi', moduleIcon(mod.slug), 'text-primary']" />
            </div>

            <div class="min-w-0 flex-1">
              <div class="mb-1.5 flex items-center gap-2">
                <p class="text-sm font-semibold text-ink">{{ moduleLabel(mod.slug) }}</p>
                <span
                  v-if="mod.is_corrected"
                  class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-bold"
                  :class="
                    modulePct(mod) >= 60
                      ? 'bg-emerald-500/10 text-emerald-600'
                      : 'bg-red-500/10 text-red-600'
                  "
                >
                  <i :class="['pi text-xs', modulePct(mod) >= 60 ? 'pi-check' : 'pi-times']" />
                  {{ modulePct(mod) }}%
                </span>
                <span v-else class="inline-flex items-center gap-1.5 text-xs text-amber-600">
                  <i class="pi pi-clock text-xs" />
                  {{ t("start_deutsch.result.pending") }}
                </span>
              </div>
              <div v-if="mod.is_corrected" class="flex items-center gap-2">
                <div class="h-2 flex-1 overflow-hidden rounded-full bg-card-2">
                  <div
                    class="h-2 rounded-full transition-all duration-500"
                    :class="modulePct(mod) >= 60 ? 'bg-emerald-500' : 'bg-red-500'"
                    :style="{ width: `${modulePct(mod)}%` }"
                  />
                </div>
                <span class="shrink-0 text-xs font-bold text-muted">
                  {{ mod.score_obtained }}/{{ mod.max_score }}
                </span>
              </div>
            </div>

            <i
              :class="[
                'pi text-sm text-faint',
                expandedModules.has(mod.module_id) ? 'pi-chevron-up' : 'pi-chevron-down',
              ]"
            />
          </button>
        </div>
      </section>

      <!-- ══ Détail des réponses (accordéon) ══ -->
      <section
        v-for="mod in expandedList"
        :key="`detail-${mod.module_id}`"
        class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <header class="border-b border-line px-5 py-3 sm:px-6">
          <p class="text-xs font-bold uppercase tracking-wide text-faint">
            {{ t("start_deutsch.result.detail") }} · {{ moduleLabel(mod.slug) }}
          </p>
        </header>

        <div v-for="teil in mod.teile ?? []" :key="teil.teil_id" class="border-b border-line last:border-0">
          <div class="flex items-center justify-between bg-card-2 px-5 py-3 sm:px-6">
            <p class="text-xs font-bold uppercase tracking-wide text-muted">Teil {{ teil.teil_number }}</p>
            <span class="text-xs font-bold text-muted">
              {{ teil.score_obtained.toFixed(1) }} / {{ teil.max_score }} pts
            </span>
          </div>

          <div class="divide-y divide-line">
            <div
              v-for="answer in teil.answers ?? []"
              :key="answer.question_id"
              class="flex items-start gap-3 px-5 py-3 sm:px-6"
            >
              <div class="mt-0.5 shrink-0">
                <div
                  v-if="answer.is_correct === true"
                  class="flex size-5 items-center justify-center rounded-full bg-emerald-500/10"
                >
                  <i class="pi pi-check text-xs text-emerald-600" />
                </div>
                <div
                  v-else-if="answer.is_correct === false"
                  class="flex size-5 items-center justify-center rounded-full bg-red-500/10"
                >
                  <i class="pi pi-times text-xs text-red-600" />
                </div>
                <div v-else class="flex size-5 items-center justify-center rounded-full bg-card-2">
                  <i class="pi pi-minus text-xs text-faint" />
                </div>
              </div>
              <div class="min-w-0 flex-1 text-sm">
                <span class="text-muted">
                  Q{{ answer.question_number }} · {{ t("start_deutsch.result.your_answer") }} :
                  <strong class="text-ink">{{ formatAnswer(answer.user_answer) }}</strong>
                </span>
                <span
                  v-if="answer.correct_answer && answer.is_correct === false"
                  class="ml-3 text-emerald-600"
                >
                  {{ t("start_deutsch.result.correct_answer") }} :
                  <strong>{{ formatAnswer(answer.correct_answer) }}</strong>
                </span>
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

const expandedModules = ref<Set<string>>(new Set());

const result = computed(() => store.result);

const expandedList = computed(() =>
  (result.value?.modules ?? []).filter((m) => expandedModules.value.has(m.module_id)),
);

const scorePercent = computed(() => {
  if (!result.value?.score || !result.value?.modules?.length) return 0;
  const totalMax = (result.value.modules ?? []).reduce((sum, m) => sum + m.max_score, 0);
  if (totalMax === 0) return 0;
  return Math.round((result.value.score / totalMax) * 100);
});

// Formulation neutre : Start Deutsch est un entraînement, pas un examen à enjeu
const isPending = computed(() => result.value?.status === "PENDING_REVIEW");

const statusIcon = computed(() => {
  if (isPending.value) return "pi-clock";
  return scorePercent.value >= 60 ? "pi-check-circle" : "pi-arrow-up-right";
});

const statusLabel = computed(() => {
  if (isPending.value) return t("start_deutsch.result.pending_review");
  return scorePercent.value >= 60
    ? t("start_deutsch.result.good_score")
    : t("start_deutsch.result.keep_practicing");
});

const statusClass = computed(() => {
  if (isPending.value) return "bg-amber-500/15 text-amber-600";
  return scorePercent.value >= 60 ? "bg-emerald-500/10 text-emerald-600" : "bg-primary/10 text-primary";
});

const moduleLabels: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
};
const moduleIcons: Record<string, string> = {
  lesen: "pi-book",
  hoeren: "pi-volume-up",
  schreiben: "pi-pencil",
  sprechen: "pi-microphone",
};

function moduleLabel(slug: string) {
  return moduleLabels[slug] ?? slug;
}
function moduleIcon(slug: string) {
  return moduleIcons[slug] ?? "pi-file";
}
function modulePct(mod: { score_obtained: number; max_score: number }) {
  return mod.max_score > 0 ? Math.round((mod.score_obtained / mod.max_score) * 100) : 0;
}

function toggleModule(moduleId: string) {
  // Nouveau Set pour que Vue détecte le changement
  const next = new Set(expandedModules.value);
  if (next.has(moduleId)) next.delete(moduleId);
  else next.add(moduleId);
  expandedModules.value = next;
}

function formatAnswer(answer: Record<string, any> | null): string {
  if (!answer) return "-";
  return answer.answer ?? JSON.stringify(answer);
}

function goToCatalogue() {
  navigateTo(localePath("/dashboard/start-deutsch"));
}

function retrySubject() {
  navigateTo(localePath(`/dashboard/start-deutsch/${route.params.subjectId}/session`));
}

onMounted(async () => {
  const sessionId = route.query.sessionId as string | undefined;
  if (sessionId && (!store.result || store.result.session_id !== sessionId)) {
    await store.getResult(sessionId);
  }
});
</script>