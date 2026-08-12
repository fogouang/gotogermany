<!-- pages/dashboard/start-deutsch/[subjectId]/result.vue -->
<template>
  <div class="space-y-6 pb-10">
    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Not found -->
    <div
      v-else-if="!result"
      class="flex flex-col items-center justify-center py-16 bg-card rounded-2xl border border-line"
    >
      <div class="w-14 h-14 rounded-2xl bg-danger-50 flex items-center justify-center mb-4">
        <i class="pi pi-exclamation-triangle text-2xl text-danger-500"></i>
      </div>
      <p class="font-semibold text-ink mb-4">{{ t("start_deutsch.result.not_found") }}</p>
      <Button :label="t('start_deutsch.result.back')" outlined size="small" @click="goToCatalogue" />
    </div>

    <template v-else>
      <!-- ── Hero score ── -->
      <div class="score-display relative overflow-hidden">
        <div class="absolute -top-10 -right-10 w-48 h-48 rounded-full opacity-10 bg-white"></div>
        <div class="absolute -bottom-8 -left-8 w-32 h-32 rounded-full opacity-10 bg-white"></div>

        <p class="relative text-xs font-bold uppercase tracking-widest opacity-80">
          {{ result.subject_title }} · {{ result.level }}
        </p>
        <p class="score-percentage relative mt-2">{{ scorePercent }}%</p>
        <p class="relative mt-1 text-sm opacity-90">
          {{ t("start_deutsch.result.score_of", { score: result.score?.toFixed(0) ?? "0" }) }}
        </p>

        <div class="relative mx-auto mt-5 h-2.5 w-full max-w-sm overflow-hidden rounded-full bg-white/25">
          <div class="h-full rounded-full bg-white" :style="{ width: `${scorePercent}%` }" />
        </div>

        <p class="relative mt-5 inline-flex items-center gap-2 rounded-full bg-white/15 px-4 py-2 text-sm font-semibold">
          <i :class="['pi', statusIcon]" />
          {{ statusLabel }}
        </p>
      </div>

      <!-- ── Résultat par module ── -->
      <div class="bg-card border border-line rounded-2xl overflow-hidden">
        <div class="px-6 py-4 border-b border-line">
          <h2 class="font-bold text-ink">{{ t("start_deutsch.result.by_module") }}</h2>
        </div>

        <button
          v-for="mod in result.modules ?? []"
          :key="mod.module_id"
          class="w-full px-6 py-4 flex items-center gap-4 hover:bg-hover transition-colors text-left"
          @click="toggleModule(mod.module_id)"
        >
          <div class="w-11 h-11 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
            <i :class="['pi', moduleIcon(mod.slug), 'text-primary-600']" />
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1.5">
              <p class="font-semibold text-ink text-sm">{{ moduleLabel(mod.slug) }}</p>
              <span
                v-if="mod.is_corrected"
                :class="[
                  'inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full',
                  modulePct(mod) >= 60 ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-600',
                ]"
              >
                <i :class="['pi text-xs', modulePct(mod) >= 60 ? 'pi-check' : 'pi-times']" />
                {{ modulePct(mod) }}%
              </span>
              <span v-else class="inline-flex items-center gap-1.5 text-amber-600 text-xs">
                <i class="pi pi-clock text-xs" />
                {{ t("start_deutsch.result.pending") }}
              </span>
            </div>
            <div v-if="mod.is_corrected" class="flex items-center gap-2">
              <div class="flex-1 bg-hover rounded-full h-2 overflow-hidden">
                <div
                  class="h-2 rounded-full transition-all duration-500"
                  :class="modulePct(mod) >= 60 ? 'bg-success-500' : 'bg-danger-400'"
                  :style="{ width: `${modulePct(mod)}%` }"
                />
              </div>
              <span class="text-xs font-bold text-ink-secondary shrink-0">
                {{ mod.score_obtained }}/{{ mod.max_score }}
              </span>
            </div>
          </div>

          <i
            :class="[
              'pi text-ink-tertiary text-sm',
              expandedModules.has(mod.module_id) ? 'pi-chevron-up' : 'pi-chevron-down',
            ]"
          />
        </button>
      </div>

      <!-- ── Détail réponses par module (accordéon) ── -->
      <div
        v-for="mod in (result.modules ?? []).filter((m) => expandedModules.has(m.module_id))"
        :key="`detail-${mod.module_id}`"
        class="bg-card border border-line rounded-2xl overflow-hidden"
      >
        <div class="px-6 py-3 border-b border-line">
          <p class="text-xs font-bold text-ink-tertiary uppercase tracking-wide">
            {{ t("start_deutsch.result.detail") }} — {{ moduleLabel(mod.slug) }}
          </p>
        </div>

        <div v-for="teil in mod.teile ?? []" :key="teil.teil_id" class="border-b border-line last:border-0">
          <div class="px-6 py-3 bg-hover/50 flex items-center justify-between">
            <p class="text-xs font-bold text-ink-secondary uppercase tracking-wide">
              Teil {{ teil.teil_number }}
            </p>
            <span class="text-xs font-bold text-ink-secondary">
              {{ teil.score_obtained.toFixed(1) }} / {{ teil.max_score }} pts
            </span>
          </div>

          <div class="divide-y divide-line">
            <div v-for="answer in teil.answers ?? []" :key="answer.question_id" class="px-6 py-3 flex items-start gap-3">
              <div class="shrink-0 mt-0.5">
                <div
                  v-if="answer.is_correct === true"
                  class="w-5 h-5 rounded-full bg-success-100 flex items-center justify-center"
                >
                  <i class="pi pi-check text-success-600 text-xs" />
                </div>
                <div
                  v-else-if="answer.is_correct === false"
                  class="w-5 h-5 rounded-full bg-danger-100 flex items-center justify-center"
                >
                  <i class="pi pi-times text-danger-500 text-xs" />
                </div>
                <div v-else class="w-5 h-5 rounded-full bg-hover flex items-center justify-center">
                  <i class="pi pi-minus text-ink-tertiary text-xs" />
                </div>
              </div>
              <div class="flex-1 min-w-0 text-sm">
                <span class="text-ink-secondary">
                  Q{{ answer.question_number }} — {{ t("start_deutsch.result.your_answer") }} :
                  <strong class="text-ink">{{ formatAnswer(answer.user_answer) }}</strong>
                </span>
                <span
                  v-if="answer.correct_answer && answer.is_correct === false"
                  class="ml-3 text-success-700"
                >
                  {{ t("start_deutsch.result.correct_answer") }} :
                  <strong>{{ formatAnswer(answer.correct_answer) }}</strong>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Actions ── -->
      <div class="flex flex-col sm:flex-row gap-3">
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
definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const route = useRoute();
const store = useStartDeutschSessionStore();

const expandedModules = ref<Set<string>>(new Set());

const result = computed(() => store.result);

const scorePercent = computed(() => {
  if (!result.value?.score || !result.value?.modules?.length) return 0;
  const totalMax = (result.value.modules ?? []).reduce((sum, m) => sum + m.max_score, 0);
  if (totalMax === 0) return 0;
  return Math.round((result.value.score / totalMax) * 100);
});

// Wording volontairement neutre (pas "échec") — Start Deutsch est un
// entraînement de familiarisation, pas un vrai examen à enjeu
const statusIcon = computed(() => {
  if (result.value?.status === "PENDING_REVIEW") return "pi-clock";
  return scorePercent.value >= 60 ? "pi-check-circle" : "pi-arrow-up-right";
});

const statusLabel = computed(() => {
  if (result.value?.status === "PENDING_REVIEW") return t("start_deutsch.result.pending_review");
  return scorePercent.value >= 60
    ? t("start_deutsch.result.good_score")
    : t("start_deutsch.result.keep_practicing");
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
  if (expandedModules.value.has(moduleId)) expandedModules.value.delete(moduleId);
  else expandedModules.value.add(moduleId);
}

function formatAnswer(answer: Record<string, any> | null): string {
  if (!answer) return "-";
  return answer.answer ?? JSON.stringify(answer);
}

function goToCatalogue() {
  navigateTo("/dashboard/start-deutsch");
}

function retrySubject() {
  navigateTo(`/dashboard/start-deutsch/${route.params.subjectId}/session`);
}

onMounted(async () => {
  const sessionId = route.query.sessionId as string | undefined;
  if (sessionId && (!store.result || store.result.session_id !== sessionId)) {
    await store.getResult(sessionId);
  }
});
</script>