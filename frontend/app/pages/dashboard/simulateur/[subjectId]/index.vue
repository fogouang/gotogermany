<!-- pages/dashboard/simulateur/[subjectId]/index.vue -->
<template>
  <div class="flex h-screen flex-col overflow-hidden bg-canvas">
    <!-- ── Chargement ── -->
    <div v-if="store.loading" class="flex flex-1 items-center justify-center">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- ── Erreur ── -->
    <div v-else-if="store.error" class="flex flex-1 items-center justify-center">
      <div class="max-w-lg space-y-4 px-6 text-center">
        <i class="pi pi-exclamation-circle text-4xl text-red-500" />
        <p class="font-medium text-red-600">{{ store.error }}</p>
        <Button :label="t('simulator_subject.back')" outlined @click="router.back()" />
      </div>
    </div>

    <template v-else-if="subject">
      <!-- ══ Barre du haut ══ -->
      <div class="flex shrink-0 items-center gap-3 border-b border-line bg-card px-4 py-3">
        <Button icon="pi pi-arrow-left" text rounded :aria-label="t('simulator_subject.back')" @click="router.back()" />
        <div class="flex items-center gap-2">
          <span class="rounded-full px-2 py-0.5 text-xs font-bold uppercase" :class="providerColor(subject.provider)">
            {{ subject.provider }}
          </span>
          <span class="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-bold uppercase text-primary">
            {{ subject.level }}
          </span>
        </div>
        <h1 class="min-w-0 flex-1 truncate text-sm font-semibold text-ink">{{ subject.title }}</h1>
        <span class="ml-auto shrink-0 text-xs text-faint">
          {{ totalWords }} {{ t("simulator_subject.words_written") }}
        </span>
      </div>

      <!-- ══ Onglets des Teile ══ -->
      <div class="shrink-0 border-b border-line bg-card px-4">
        <div class="flex overflow-x-auto">
          <button
            v-for="(task, i) in subject.tasks"
            :key="i"
            type="button"
            class="flex shrink-0 items-center gap-2 whitespace-nowrap border-b-2 px-4 py-3 text-sm font-medium transition-colors"
            :class="activeTab === i ? 'border-primary text-primary' : 'border-transparent text-muted hover:text-ink'"
            @click="activeTab = i"
          >
            <span
              class="flex size-5 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors"
              :class="wordCount(i) >= (task.word_count_min ?? 0) ? 'bg-primary text-white' : 'bg-card-2 text-muted'"
            >
              <i v-if="wordCount(i) >= (task.word_count_min ?? 0)" class="pi pi-check text-[10px]" />
              <template v-else>{{ i + 1 }}</template>
            </span>
            <span>Teil {{ task.teil }}</span>
            <span class="hidden text-xs text-faint sm:inline">({{ wordCount(i) }}/{{ task.word_count_max }})</span>
          </button>
        </div>
      </div>

      <!-- ══ Consignes | rédaction et correction | caractères spéciaux ══ -->
      <div class="flex min-h-0 flex-1 overflow-hidden">
        <div class="min-h-0 flex-1 overflow-hidden">
          <template v-for="(task, i) in subject.tasks" :key="i">
            <div v-show="activeTab === i" class="flex h-full flex-col lg:flex-row">
              <!-- ── Consignes ── -->
              <div class="overflow-y-auto border-r border-line bg-card lg:w-[45%]">
                <div class="mx-auto max-w-xl space-y-4 p-6 lg:mx-0">
                  <SprachlicheMittelPanel :mittel-key="mittelKey(task)" />

                  <!-- Cas 1 : choix entre thèmes (telc / ÖSD B2) -->
                  <template v-if="task.themes">
                    <div v-if="!selectedThemes[i]" class="space-y-3">
                      <p class="text-sm font-semibold text-ink">{{ t("simulator_subject.choose_theme") }}</p>
                      <div class="grid grid-cols-1 gap-3">
                        <button
                          v-for="(theme, key) in task.themes"
                          :key="key"
                          type="button"
                          class="rounded-card border-2 border-line bg-card p-4 text-left transition-colors hover:border-primary/40"
                          @click="selectedThemes[i] = String(key)"
                        >
                          <p class="mb-1 font-semibold text-ink">Thema {{ key }} : {{ theme.titel }}</p>
                          <p class="line-clamp-2 text-xs text-muted">{{ theme.stimulus }}</p>
                        </button>
                      </div>
                    </div>

                    <template v-else>
                      <div class="mb-2 flex items-center justify-between gap-2">
                        <p class="text-sm font-semibold text-ink">
                          Thema {{ selectedThemes[i] }} : {{ task.themes[selectedThemes[i]!]?.titel }}
                        </p>
                        <button type="button" class="text-xs text-muted hover:text-ink" @click="selectedThemes[i] = null">
                          {{ t("simulator_subject.change_theme") }}
                        </button>
                      </div>

                      <div class="rounded-card border border-line bg-card-2 p-5">
                        <p class="text-sm italic text-ink">{{ task.themes[selectedThemes[i]!]?.stimulus }}</p>
                      </div>

                      <div class="rounded-card border border-amber-500/30 bg-amber-500/10 p-5">
                        <p class="mb-2 text-xs font-bold uppercase tracking-wide text-amber-600">
                          {{ t("simulator_subject.task_label") }}
                        </p>
                        <ul class="space-y-1">
                          <li
                            v-for="(prompt, pi) in task.themes[selectedThemes[i]!]?.prompts"
                            :key="pi"
                            class="flex gap-2 text-sm text-ink"
                          >
                            <span class="shrink-0 font-bold text-amber-600">•</span>
                            <span>{{ prompt }}</span>
                          </li>
                        </ul>
                        <p v-if="task.word_count_target" class="mt-3 text-xs font-medium text-amber-600">
                          {{ t("simulator_subject.approx") }} {{ task.word_count_target }} {{ t("simulator_subject.words") }}
                        </p>
                      </div>
                    </template>
                  </template>

                  <!-- Cas 2 : choix entre variantes d'opinion (ÖSD) -->
                  <template v-else-if="task.opinion_variants">
                    <div v-if="!selectedVariants[i]" class="space-y-3">
                      <p class="text-sm font-semibold text-ink">{{ t("simulator_subject.choose_theme") }}</p>
                      <div class="grid grid-cols-1 gap-3">
                        <button
                          v-for="(variant, key) in task.opinion_variants"
                          :key="key"
                          type="button"
                          class="rounded-card border-2 border-line bg-card p-4 text-left transition-colors hover:border-primary/40"
                          @click="selectedVariants[i] = String(key)"
                        >
                          <p class="font-semibold text-ink">{{ variant.thema }}</p>
                        </button>
                      </div>
                    </div>

                    <template v-else>
                      <div class="mb-2 flex items-center justify-between gap-2">
                        <p class="text-sm font-semibold text-ink">
                          {{ task.opinion_variants[selectedVariants[i]!]?.thema }}
                        </p>
                        <button type="button" class="text-xs text-muted hover:text-ink" @click="selectedVariants[i] = null">
                          {{ t("simulator_subject.change_theme") }}
                        </button>
                      </div>

                      <div v-if="task.opinion_variants[selectedVariants[i]!]?.aussagen?.length" class="space-y-2">
                        <div
                          v-for="(aussage, ai) in task.opinion_variants[selectedVariants[i]!].aussagen"
                          :key="ai"
                          class="rounded-leaf border border-line bg-card-2 p-3 text-sm italic text-ink"
                        >
                          « {{ aussage }} »
                        </div>
                      </div>

                      <div v-if="task.leitpunkte?.length" class="rounded-card border border-amber-500/30 bg-amber-500/10 p-5">
                        <p class="mb-2 text-xs font-bold uppercase tracking-wide text-amber-600">
                          {{ t("simulator_subject.task_label") }}
                        </p>
                        <ul class="space-y-1">
                          <li v-for="(punkt, pi) in task.leitpunkte" :key="pi" class="flex gap-2 text-sm text-ink">
                            <span class="shrink-0 font-bold text-amber-600">•</span>
                            <span>{{ punkt }}</span>
                          </li>
                        </ul>
                        <p v-if="task.word_count_target" class="mt-3 text-xs font-medium text-amber-600">
                          {{ t("simulator_subject.approx") }} {{ task.word_count_target }} {{ t("simulator_subject.words") }}
                        </p>
                      </div>
                    </template>
                  </template>

                  <!-- Cas 3 : formats simples -->
                  <template v-else>
                    <!-- E-mail stimulus (telc) -->
                    <div
                      v-if="task.stimulus_email?.sender || task.stimulus_email?.subject || task.stimulus_email?.body"
                      class="overflow-hidden rounded-card border border-line bg-card"
                    >
                      <div class="space-y-1 border-b border-line bg-card-2 px-5 py-3">
                        <div class="flex items-center gap-2 text-sm">
                          <span class="w-16 font-semibold text-muted">Von:</span>
                          <span class="font-medium text-ink">{{ task.stimulus_email.sender }}</span>
                        </div>
                        <div class="flex items-center gap-2 text-sm">
                          <span class="w-16 font-semibold text-muted">Betreff:</span>
                          <span class="text-ink">{{ task.stimulus_email.subject }}</span>
                        </div>
                      </div>
                      <p class="whitespace-pre-line px-5 py-4 text-sm leading-relaxed text-ink">
                        {{ task.stimulus_email.body }}
                      </p>
                    </div>

                    <!-- Forum (Goethe) -->
                    <div v-else-if="task.stimulus" class="rounded-card border border-line bg-card-2 p-5">
                      <div class="mb-2 flex items-center gap-2">
                        <i class="pi pi-comment text-muted" />
                        <span class="text-sm font-semibold text-ink">
                          {{ getStimulusAuthor(task) || t("simulator_subject.comment") }}
                        </span>
                      </div>
                      <p v-if="getStimulusTitle(task)" class="mb-2 text-xs font-semibold text-muted">
                        {{ getStimulusTitle(task) }}
                      </p>
                      <p class="text-sm italic text-ink">{{ getStimulusText(task) }}</p>
                    </div>

                    <!-- Annonce (telc / ÖSD) -->
                    <div v-if="task.context_ad" class="overflow-hidden rounded-card border border-line bg-card">
                      <p class="border-b border-line bg-card-2 px-5 py-3 text-xs font-semibold uppercase tracking-wide text-muted">
                        {{ t("simulator_subject.ad_context") }}
                      </p>
                      <p class="whitespace-pre-line px-5 py-4 text-sm leading-relaxed text-ink">{{ task.context_ad }}</p>
                    </div>

                    <!-- Destinataire -->
                    <div v-if="task.recipient" class="rounded-leaf border border-line bg-card-2 px-4 py-2 text-sm">
                      <span class="font-semibold text-muted">An:</span>
                      <span class="ml-2 text-ink">{{ task.recipient }}</span>
                    </div>

                    <!-- Promesses et réalité (ÖSD) -->
                    <div v-if="task.info_comparison" class="overflow-hidden rounded-card border border-line bg-card">
                      <div class="border-b border-line bg-card-2 px-5 py-3">
                        <p class="text-sm font-semibold text-ink">{{ task.info_comparison.anbieter }}</p>
                        <p class="mt-1 text-xs text-muted">{{ task.info_comparison.situation }}</p>
                      </div>
                      <div class="grid grid-cols-1 gap-4 px-5 py-4 sm:grid-cols-2">
                        <div>
                          <p class="mb-2 text-xs font-bold uppercase text-emerald-600">Versprochen</p>
                          <ul class="space-y-1">
                            <li v-for="(v, vi) in task.info_comparison.versprechen" :key="vi" class="flex gap-1.5 text-xs text-ink">
                              <i class="pi pi-check mt-0.5 text-[10px] text-emerald-600" />{{ v }}
                            </li>
                          </ul>
                        </div>
                        <div>
                          <p class="mb-2 text-xs font-bold uppercase text-red-600">Probleme</p>
                          <ul class="space-y-1">
                            <li v-for="(p, pi) in task.info_comparison.probleme" :key="pi" class="flex gap-1.5 text-xs text-ink">
                              <i class="pi pi-times mt-0.5 text-[10px] text-red-600" />{{ p }}
                            </li>
                          </ul>
                        </div>
                      </div>
                      <div v-if="task.info_comparison.kontakt" class="border-t border-line bg-card-2 px-5 py-3 text-xs text-muted">
                        Kontakt: {{ task.info_comparison.kontakt }}
                      </div>
                    </div>

                    <!-- Thème simple -->
                    <div v-if="task.topic" class="rounded-card border border-amber-500/30 bg-amber-500/10 p-5">
                      <p class="mb-2 text-xs font-bold uppercase tracking-wide text-amber-600">Thema</p>
                      <p class="text-base font-bold text-ink">{{ task.topic }}</p>
                    </div>

                    <!-- Scénario -->
                    <div v-if="task.scenario" class="rounded-card border border-amber-500/30 bg-amber-500/10 p-5">
                      <p class="mb-2 text-xs font-bold uppercase tracking-wide text-amber-600">
                        {{ t("simulator_subject.task_label") }}
                      </p>
                      <p class="text-sm leading-relaxed text-ink">{{ task.scenario }}</p>
                    </div>

                    <!-- Points à traiter -->
                    <div v-if="task.prompts?.length" class="rounded-card border border-amber-500/30 bg-amber-500/10 p-5">
                      <p v-if="!task.scenario" class="mb-2 text-xs font-bold uppercase tracking-wide text-amber-600">
                        {{ t("simulator_subject.task_label") }}
                      </p>
                      <ul class="space-y-1">
                        <li v-for="(prompt, pi) in task.prompts" :key="pi" class="flex gap-2 text-sm text-ink">
                          <span class="shrink-0 font-bold text-amber-600">•</span>
                          <span>{{ prompt }}</span>
                        </li>
                      </ul>
                      <p class="mt-3 text-xs font-medium text-amber-600">
                        {{ task.word_count_min }}-{{ task.word_count_max }} {{ t("simulator_subject.word_range") }}
                        <span v-if="task.register === 'formell'"> · {{ t("simulator_subject.formal_required") }}</span>
                      </p>
                    </div>
                    <div v-else class="rounded-card border border-amber-500/30 bg-amber-500/10 p-4">
                      <p class="text-xs font-medium text-amber-600">
                        {{ task.word_count_min }}-{{ task.word_count_max }} {{ t("simulator_subject.word_range") }}
                      </p>
                    </div>
                  </template>

                  <!-- Navigation entre Teile -->
                  <div class="flex justify-between pt-2">
                    <Button
                      v-if="i > 0"
                      :label="t('simulator_subject.prev_teil')"
                      icon="pi pi-arrow-left"
                      text
                      size="small"
                      @click="activeTab = i - 1"
                    />
                    <div v-else />
                    <Button
                      v-if="i < subject.tasks.length - 1"
                      :label="t('simulator_subject.next_teil')"
                      icon="pi pi-arrow-right"
                      icon-pos="right"
                      size="small"
                      severity="secondary"
                      @click="activeTab = i + 1"
                    />
                  </div>
                </div>
              </div>

              <!-- ── Rédaction et correction ── -->
              <div class="overflow-y-auto bg-canvas lg:w-[55%]">
                <div class="mx-auto max-w-2xl space-y-4 p-6">
                  <!-- Zone de rédaction : verrouillée tant qu'un thème ou une variante n'est pas choisi -->
                  <div
                    class="overflow-hidden rounded-card border-2 border-line bg-card transition-colors focus-within:border-primary/60"
                  >
                    <textarea
                      v-if="isWritingUnlocked(i, task)"
                      :id="`simulator-answer-${i}`"
                      :ref="(el) => setTextareaRef(el, i)"
                      v-model="answers[i]"
                      :placeholder="t('simulator_subject.write_placeholder')"
                      class="w-full resize-none border-0 bg-transparent p-5 text-sm text-ink placeholder:text-faint focus:outline-none focus:ring-0"
                      rows="12"
                      @focus="activeTextareaIndex = i"
                    />
                    <div v-else class="p-5 text-sm italic text-faint">
                      {{ t("simulator_subject.choose_theme_first") }}
                    </div>
                    <div class="flex items-center justify-between border-t border-line bg-card-2 px-5 py-2">
                      <span class="text-xs text-muted">{{ wordCount(i) }} {{ t("simulator_subject.words_count") }}</span>
                      <div class="flex items-center gap-2">
                        <div class="h-1 w-24 rounded-full bg-line">
                          <div
                            class="h-1 rounded-full transition-all"
                            :class="wordCount(i) >= task.word_count_max ? 'bg-emerald-500' : 'bg-primary'"
                            :style="{ width: `${Math.min((wordCount(i) / task.word_count_max) * 100, 100)}%` }"
                          />
                        </div>
                        <span
                          class="text-xs font-medium"
                          :class="wordCount(i) >= task.word_count_min ? 'text-emerald-600' : 'text-faint'"
                        >
                          / {{ task.word_count_max }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Avancement par Teil -->
                  <div class="flex flex-wrap items-center gap-2">
                    <span
                      v-for="(task2, ti) in subject.tasks"
                      :key="ti"
                      class="rounded-full px-2 py-1 text-xs font-medium"
                      :class="wordCount(ti) >= (task2.word_count_min ?? 0) ? 'bg-primary/10 text-primary' : 'bg-card-2 text-faint'"
                    >
                      Teil {{ task2.teil }} : {{ wordCount(ti) }}/{{ task2.word_count_max }}
                    </span>
                  </div>

                  <!-- Crédits IA -->
                  <div class="flex items-center justify-between rounded-card border border-amber-500/30 bg-amber-500/10 px-4 py-3">
                    <div class="flex items-center gap-2">
                      <i class="pi pi-sparkles text-amber-600" />
                      <span class="text-sm font-medium text-ink">
                        {{ authStore.aiCredits }}
                        {{ authStore.aiCredits <= 1 ? t("simulator_subject.credit") : t("simulator_subject.credits") }}
                      </span>
                    </div>
                    <NuxtLink
                      v-if="authStore.aiCredits === 0"
                      :to="localePath('/dashboard/credits')"
                      class="rounded-leaf bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-amber-600"
                    >
                      {{ t("simulator_subject.buy_credits") }}
                    </NuxtLink>
                  </div>

                  <!-- Pas encore soumis -->
                  <div v-if="!store.correction && !store.correcting && !store.correctionError">
                    <Button
                      :label="authStore.aiCredits > 0 ? t('simulator_subject.correct_btn') : t('simulator_subject.no_credits')"
                      icon="pi pi-sparkles"
                      :disabled="!canCorrect || authStore.aiCredits <= 0"
                      class="w-full"
                      size="large"
                      @click="launchCorrection"
                    />
                    <p v-if="!canCorrect && authStore.aiCredits > 0" class="mt-2 text-center text-xs text-faint">
                      {{ t("simulator_subject.correct_hint") }}
                    </p>
                    <p v-if="authStore.aiCredits === 0" class="mt-2 text-center text-xs text-red-600">
                      {{ t("simulator_subject.no_credits_hint") }}
                    </p>
                  </div>

                  <!-- Correction en cours -->
                  <div
                    v-else-if="store.correcting"
                    class="flex flex-col items-center gap-3 rounded-card border border-primary/30 bg-primary/10 py-8"
                  >
                    <i class="pi pi-spin pi-spinner text-2xl text-primary" />
                    <p class="text-sm font-medium text-ink">{{ t("simulator_subject.correcting") }}</p>
                    <p class="text-xs text-muted">{{ t("simulator_subject.correcting_sub") }}</p>
                  </div>

                  <!-- Erreur de correction -->
                  <div
                    v-else-if="store.correctionError"
                    class="flex items-start gap-3 rounded-card border border-red-500/30 bg-red-500/5 p-4"
                  >
                    <i class="pi pi-exclamation-circle mt-0.5 shrink-0 text-red-600" />
                    <div class="min-w-0 flex-1">
                      <p class="text-sm font-medium text-red-600">{{ t("simulator_subject.error_title") }}</p>
                      <p class="mt-1 text-xs text-muted">{{ store.correctionError }}</p>
                    </div>
                    <Button :label="t('simulator_subject.retry')" size="small" outlined severity="danger" @click="launchCorrection" />
                  </div>

                  <!-- Résultat disponible -->
                  <div
                    v-else-if="store.correction"
                    class="rounded-card border-2 bg-card p-5"
                    :class="store.correction.passed ? 'border-emerald-500' : 'border-orange-500'"
                  >
                    <div class="flex flex-wrap items-center justify-between gap-3">
                      <div class="flex items-center gap-3">
                        <div
                          class="flex size-12 items-center justify-center rounded-full text-sm font-bold text-white"
                          :class="store.correction.passed ? 'bg-emerald-500' : 'bg-orange-500'"
                        >
                          {{ store.scorePercentage }}%
                        </div>
                        <div>
                          <p class="text-sm font-semibold text-ink">
                            {{ store.correction.passed ? t("simulator.passed") : t("simulator.not_passed") }}
                          </p>
                          <p class="text-xs text-muted">
                            {{ store.correction.overall_score }} / {{ store.correction.max_score }}
                            {{ t("simulator_subject.points_label") }}
                          </p>
                        </div>
                      </div>
                      <Button
                        :label="t('simulator_subject.see_results')"
                        icon="pi pi-arrow-right"
                        icon-pos="right"
                        size="small"
                        @click="goToResults"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- ── Caractères spéciaux allemands ── -->
        <div class="flex w-14 shrink-0 flex-col items-center gap-1.5 overflow-y-auto border-l border-line bg-card py-4">
          <button
            v-for="char in specialChars"
            :key="char"
            type="button"
            class="size-9 rounded-leaf border border-line bg-card-2 text-sm font-semibold text-ink transition-colors hover:border-primary/40 hover:bg-primary/10 hover:text-primary"
            :title="t('simulator_subject.insert_char', { char })"
            @click="insertChar(char)"
          >
            {{ char }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ComponentPublicInstance } from "vue";
import { useSimulatorStore } from "~/stores/simulator";
import SprachlicheMittelPanel from "~/components/session/SprachlicheMittelPanel.vue";
import { resolveMittelKey } from "#shared/sprachlicheMittel";

definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const router = useRouter();
const store = useSimulatorStore();
const authStore = useAuthStore();

const subjectId = route.params.subjectId as string;
const activeTab = ref(0);
const answers = ref<string[]>([]);
const subject = computed(() => store.currentSubject);

watch(
  subject,
  (s) => {
    if (s) answers.value = s.tasks.map(() => "");
  },
  { immediate: true },
);

const wordCount = (i: number): number => {
  const text = answers.value[i] || "";
  return text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0;
};

const totalWords = computed(() => answers.value.reduce((sum, _, i) => sum + wordCount(i), 0));
const canCorrect = computed(() => answers.value.some((_, i) => wordCount(i) > 0));

const launchCorrection = async () => {
  store.clearCorrection();
  await store.correct(subjectId, answers.value);
  await authStore.fetchUser();
};

const goToResults = () => router.push(localePath(`/dashboard/simulateur/${subjectId}/resultats`));

// Couleur d'identité par fournisseur, en transparence pour rester lisible en sombre
const providerColor = (p: string) =>
  ({
    goethe: "bg-blue-500/10 text-blue-600",
    telc: "bg-purple-500/10 text-purple-600",
    osd: "bg-orange-500/10 text-orange-600",
  })[p.toLowerCase()] ?? "bg-card-2 text-muted";

// ── Sprachliche Mittel : dérivé des champs typés du sujet ──
const mittelKey = (task: any) =>
  resolveMittelKey({
    provider: subject.value?.provider?.toUpperCase() ?? "",
    cefrCode: subject.value?.level?.toUpperCase() ?? "",
    moduleSlug: "schreiben",
    formatType: task.themes ? "oral_monologue" : undefined, // ADJUST: pas de format_type réel ici, à vérifier contre resolveMittelKey
    teilNumber: task.teil,
  });

// ── Choix de thème / variante d'opinion : un état par tâche ──
const selectedThemes = ref<Record<number, string | null>>({});
const selectedVariants = ref<Record<number, string | null>>({});

const isWritingUnlocked = (i: number, task: any): boolean => {
  if (task.themes) return !!selectedThemes.value[i];
  if (task.opinion_variants) return !!selectedVariants.value[i];
  return true;
};

// ── Stimulus : string simple, objet {text, title, author} ou JSON en string ──
const parseStimulus = (raw: any): { text: string; title?: string; author?: string } => {
  if (!raw) return { text: "" };
  if (typeof raw === "object") return { text: raw.text || "", title: raw.title, author: raw.author };
  if (typeof raw === "string") {
    const trimmed = raw.trim();
    if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
      try {
        const parsed = JSON.parse(trimmed);
        return { text: parsed.text || raw, title: parsed.title, author: parsed.author };
      } catch {
        return { text: raw };
      }
    }
    return { text: raw };
  }
  return { text: String(raw) };
};

const getStimulusText = (task: any): string => parseStimulus(task.stimulus).text;
const getStimulusAuthor = (task: any): string => parseStimulus(task.stimulus).author || task.stimulus_author || "";
const getStimulusTitle = (task: any): string => parseStimulus(task.stimulus).title || "";

// ── Caractères spéciaux allemands ──
const specialChars = ["ä", "ö", "ü", "Ä", "Ö", "Ü", "ß"];

const textareaRefs = ref<Record<number, HTMLTextAreaElement | null>>({});
const activeTextareaIndex = ref(0);

function setTextareaRef(el: Element | ComponentPublicInstance | null, i: number) {
  textareaRefs.value[i] = el as HTMLTextAreaElement | null;
}

function insertChar(char: string) {
  const i = activeTab.value;
  const el = textareaRefs.value[i];
  const current = answers.value[i] || "";

  if (!el) {
    answers.value[i] = current + char;
    return;
  }

  const start = el.selectionStart ?? current.length;
  const end = el.selectionEnd ?? current.length;
  answers.value[i] = current.slice(0, start) + char + current.slice(end);

  nextTick(() => {
    el.focus();
    const newPos = start + char.length;
    el.setSelectionRange(newPos, newPos);
  });
}

onMounted(async () => {
  store.clearCorrection();
  await store.fetchSubject(subjectId);
});

useHead({ title: t("simulator_subject.page_title") });
</script>