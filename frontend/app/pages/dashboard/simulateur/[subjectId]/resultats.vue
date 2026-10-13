<!-- pages/dashboard/simulateur/[subjectId]/resultats.vue -->
<template>
  <div>
    <!-- ── Pas de correction ── -->
    <div v-if="!correction" class="mx-auto max-w-lg space-y-4 px-6 pt-20 text-center">
      <i class="pi pi-inbox text-4xl text-faint" />
      <p class="text-sm text-muted">{{ t("simulator_result.no_correction") }}</p>
      <Button :label="t('simulator_result.back_simulator')" outlined @click="goBack" />
    </div>

    <div v-else class="mx-auto max-w-6xl space-y-5 px-4 py-8">
      <!-- ══ Score ══ (couleur pleine voulue : lisible en clair et en sombre) -->
      <section class="overflow-hidden rounded-card" :class="correction.passed ? 'bg-emerald-600' : 'bg-orange-500'">
        <div class="flex items-start justify-between gap-4 px-6 pb-4 pt-6">
          <div>
            <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-white/70">
              {{ correction.provider.toUpperCase() }} · {{ correction.level.toUpperCase() }}
            </p>
            <h1 class="text-2xl font-bold text-white">
              {{ correction.passed ? t("simulator.passed") : t("simulator.not_passed") }}
            </h1>
          </div>
          <div class="relative size-20 shrink-0">
            <svg class="size-20 -rotate-90" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="32" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="8" />
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
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-lg font-bold leading-none text-white">{{ store.cecrlLevel }}</span>
              <span class="text-xs text-white/70">{{ Math.round(correction.score_percentage) }}%</span>
            </div>
          </div>
        </div>
        <div class="grid grid-cols-3 divide-x divide-white/20 bg-black/10">
          <div class="px-4 py-3 text-center">
            <p class="mb-0.5 text-xs uppercase tracking-wide text-white/70">{{ t("simulator_result.score") }}</p>
            <p class="text-base font-bold text-white">{{ correction.overall_score }}/{{ correction.max_score }}</p>
          </div>
          <div class="px-4 py-3 text-center">
            <p class="mb-0.5 text-xs uppercase tracking-wide text-white/70">{{ t("simulator_result.success_rate") }}</p>
            <p class="text-base font-bold text-white">{{ Math.round(correction.score_percentage) }}%</p>
          </div>
          <div class="px-4 py-3 text-center">
            <p class="mb-0.5 text-xs uppercase tracking-wide text-white/70">{{ t("simulator_result.level") }}</p>
            <p class="text-base font-bold text-white">{{ store.cecrlLevel }}</p>
          </div>
        </div>
        <div class="border-t border-white/10 bg-black/10 px-6 py-4">
          <p class="text-sm italic leading-relaxed text-white/90">
            <i class="pi pi-comment mr-2 not-italic text-white/50" />{{ correction.appreciation }}
          </p>
        </div>
      </section>

      <div class="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <!-- ══ Colonne gauche : critères, conseils, corrections ══ -->
        <div class="space-y-5 lg:col-span-1">
          <!-- Critères -->
          <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft">
            <header class="flex items-center gap-2 border-b border-line px-5 py-4">
              <i class="pi pi-chart-bar text-primary" />
              <h2 class="text-sm font-semibold text-ink">{{ t("simulator_result.criteria_title") }}</h2>
            </header>
            <div class="divide-y divide-line">
              <div v-for="c in store.criteriaList" :key="c.key" class="px-5 py-4">
                <div class="mb-2 flex items-center justify-between gap-2">
                  <span class="text-sm font-medium text-ink">{{ c.label }}</span>
                  <div class="flex items-center gap-2">
                    <span class="text-xs tabular-nums text-faint">{{ c.score }}/{{ c.maxScore }}</span>
                    <span class="rounded-full px-2 py-0.5 text-xs font-bold" :class="ratioBadge(c.score, c.maxScore)">
                      {{ Math.round(scoreRatio(c.score, c.maxScore) * 100) }}%
                    </span>
                  </div>
                </div>
                <div class="mb-2 h-1.5 w-full rounded-full bg-card-2">
                  <div
                    class="h-1.5 rounded-full transition-all"
                    :class="barColor(c.score, c.maxScore)"
                    :style="{ width: `${scoreRatio(c.score, c.maxScore) * 100}%` }"
                  />
                </div>
                <p class="text-xs leading-relaxed text-muted">{{ c.feedback }}</p>
              </div>
            </div>
          </section>

          <!-- Conseils -->
          <section
            v-if="correction.suggestions?.length"
            class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
          >
            <header class="flex items-center gap-2 border-b border-line px-5 py-4">
              <i class="pi pi-lightbulb text-amber-500" />
              <h2 class="text-sm font-semibold text-ink">{{ t("simulator_result.tips") }}</h2>
            </header>
            <ul class="divide-y divide-line">
              <li v-for="(s, i) in correction.suggestions" :key="i" class="flex items-start gap-3 px-5 py-3 text-sm text-ink">
                <span
                  class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-amber-500/15 text-xs font-bold text-amber-600"
                >
                  {{ i + 1 }}
                </span>
                <span>{{ s }}</span>
              </li>
            </ul>
          </section>

          <!-- Corrections détaillées -->
          <section
            v-if="correction.corrections_list?.length"
            class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
          >
            <header class="flex items-center gap-2 border-b border-line px-5 py-4">
              <i class="pi pi-pencil text-orange-500" />
              <h2 class="text-sm font-semibold text-ink">{{ t("simulator_result.detailed_corrections") }}</h2>
              <span class="ml-auto rounded-full bg-orange-500/10 px-2 py-0.5 text-xs font-bold text-orange-600">
                {{ correction.corrections_list.length }}
              </span>
            </header>
            <div class="divide-y divide-line">
              <div
                v-for="(c, i) in correction.corrections_list"
                :key="i"
                class="flex items-start gap-3 px-5 py-3 transition-colors hover:bg-card-2"
              >
                <span class="mt-0.5 shrink-0 rounded bg-card-2 px-1.5 py-0.5 text-xs font-semibold text-muted">
                  T{{ c.task || "1" }}
                </span>
                <div class="min-w-0 flex-1">
                  <p class="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
                    <span class="text-red-600 line-through">{{ c.error }}</span>
                    <i class="pi pi-arrow-right text-[10px] text-faint" />
                    <span class="font-medium text-emerald-600">{{ c.correction }}</span>
                  </p>
                  <p class="mt-0.5 text-xs leading-relaxed text-muted">{{ c.explanation }}</p>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- ══ Colonne droite : retour par tâche ══ -->
        <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft lg:col-span-2">
          <header class="flex items-center gap-2 border-b border-line px-5 py-4">
            <i class="pi pi-file-edit text-primary" />
            <h2 class="text-sm font-semibold text-ink">{{ t("simulator_result.task_title") }}</h2>
          </header>
          <Tabs v-model:value="activeTaskTab">
            <TabList class="px-5 pt-3">
              <Tab v-for="task in store.taskList" :key="task.key" :value="task.key" class="text-sm">
                {{ task.label }}
              </Tab>
            </TabList>
            <TabPanels>
              <TabPanel v-for="task in store.taskList" :key="task.key" :value="task.key" class="space-y-5 px-5 py-5">
                <!-- Points forts et points à améliorer -->
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div v-if="task.strengths?.length">
                    <p class="mb-2 flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-emerald-600">
                      <i class="pi pi-check-circle" /> {{ t("simulator_result.strengths") }}
                    </p>
                    <ul class="space-y-1.5">
                      <li
                        v-for="(s, i) in task.strengths ?? []"
                        :key="i"
                        class="flex items-start gap-2 rounded-leaf bg-emerald-500/10 px-3 py-2 text-sm text-ink"
                      >
                        <i class="pi pi-check mt-0.5 shrink-0 text-xs text-emerald-600" />
                        <span>{{ s }}</span>
                      </li>
                    </ul>
                  </div>
                  <div v-if="task.weaknesses?.length">
                    <p class="mb-2 flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-orange-600">
                      <i class="pi pi-exclamation-circle" /> {{ t("simulator_result.to_improve") }}
                    </p>
                    <ul class="space-y-1.5">
                      <li
                        v-for="(w, i) in task.weaknesses ?? []"
                        :key="i"
                        class="flex items-start gap-2 rounded-leaf bg-orange-500/10 px-3 py-2 text-sm text-ink"
                      >
                        <i class="pi pi-times mt-0.5 shrink-0 text-xs text-orange-500" />
                        <span>{{ w }}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <!-- Texte de l'élève et texte corrigé -->
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div class="min-w-0">
                    <p class="mb-2 flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-muted">
                      <i class="pi pi-pencil" /> {{ t("simulator_result.your_text") }}
                    </p>
                    <div class="h-full rounded-card border border-line bg-card-2 p-4">
                      <p class="whitespace-pre-line text-sm leading-relaxed text-ink">
                        {{ originalAnswers[task.key] || t("simulator_result.original_unavailable") }}
                      </p>
                    </div>
                  </div>

                  <div v-if="task.correctedText" class="min-w-0">
                    <p class="mb-2 flex items-center gap-1 text-xs font-semibold uppercase tracking-wide text-primary">
                      <i class="pi pi-sparkles" /> {{ t("simulator_result.corrected_text") }}
                    </p>
                    <div class="h-full rounded-card border border-primary/30 bg-primary/10 p-4">
                      <p class="whitespace-pre-line text-sm leading-relaxed text-ink">{{ task.correctedText }}</p>
                    </div>
                  </div>
                </div>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </section>
      </div>

      <!-- ══ Actions ══ -->
      <div class="flex flex-col gap-3 pb-8 sm:flex-row">
        <Button :label="t('simulator_result.redo')" icon="pi pi-refresh" outlined class="flex-1" @click="goBack" />
        <Button :label="t('simulator_result.choose_another')" icon="pi pi-list" class="flex-1" @click="goToList" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from "~/stores/simulator";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const router = useRouter();
const store = useSimulatorStore();

const subjectId = route.params.subjectId as string;
const correction = computed(() => store.correction);
const originalAnswers = computed(() => store.originalAnswers);
const activeTaskTab = ref<string>(store.taskList?.[0]?.key ?? "");

const goBack = () => router.push(localePath(`/dashboard/simulateur/${subjectId}`));
const goToList = () => router.push(localePath("/dashboard/simulateur"));

// Protégé contre un maximum à 0 (sinon NaN et barre invisible)
const scoreRatio = (score: number, max: number) => (max > 0 ? score / max : 0);

const barColor = (score: number, max: number) => {
  const p = scoreRatio(score, max);
  return p >= 0.7 ? "bg-emerald-500" : p >= 0.5 ? "bg-orange-400" : "bg-red-500";
};

const ratioBadge = (score: number, max: number) => {
  const p = scoreRatio(score, max);
  if (p >= 0.7) return "bg-emerald-500/10 text-emerald-600";
  if (p >= 0.5) return "bg-orange-500/10 text-orange-600";
  return "bg-red-500/10 text-red-600";
};

onMounted(() => {
  if (!store.correction) router.replace(localePath("/dashboard/simulateur"));
});

useHead({ title: t("simulator_result.page_title") });
</script>