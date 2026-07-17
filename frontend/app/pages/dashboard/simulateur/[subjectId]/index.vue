<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden">

    <!-- Loading -->
    <div v-if="store.loading" class="flex-1 flex items-center justify-center">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Erreur -->
    <div v-else-if="store.error" class="flex-1 flex items-center justify-center">
      <div class="max-w-lg px-6 text-center space-y-4">
        <i class="pi pi-exclamation-circle text-red-400 text-4xl"></i>
        <p class="text-red-600 font-medium">{{ store.error }}</p>
        <Button :label="t('simulator_subject.back')" outlined @click="router.back()" />
      </div>
    </div>

    <!-- Contenu -->
    <template v-else-if="subject">

      <!-- Barre de navigation sticky -->
      <div class="shrink-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3">
        <Button icon="pi pi-arrow-left" text rounded @click="router.back()" />
        <div class="flex items-center gap-2">
          <span :class="['text-xs font-bold px-2 py-0.5 rounded-full uppercase', providerColor(subject.provider)]">
            {{ subject.provider }}
          </span>
          <span class="text-xs font-bold px-2 py-0.5 rounded-full uppercase bg-indigo-100 text-indigo-700">
            {{ subject.level }}
          </span>
        </div>
        <h1 class="text-sm font-semibold text-gray-800 truncate flex-1">{{ subject.title }}</h1>
        <span class="ml-auto text-xs text-gray-400 shrink-0">
          {{ totalWords }} {{ t("simulator_subject.words_written") }}
        </span>
      </div>

      <!-- Tabs -->
      <div class="shrink-0 bg-white border-b border-gray-100 px-4">
        <div class="flex gap-0 overflow-x-auto">
          <button
            v-for="(task, i) in subject.tasks"
            :key="i"
            :class="[
              'flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap shrink-0',
              activeTab === i
                ? 'border-teal-600 text-teal-700'
                : 'border-transparent text-gray-500 hover:text-gray-700',
            ]"
            @click="activeTab = i"
          >
            <span
              :class="[
                'w-5 h-5 rounded-full text-xs font-bold flex items-center justify-center shrink-0 transition-colors',
                wordCount(i) >= (task.word_count_min ?? 0)
                  ? 'bg-teal-600 text-white'
                  : 'bg-gray-200 text-gray-500',
              ]"
            >
              {{ wordCount(i) >= (task.word_count_min ?? 0) ? "✓" : i + 1 }}
            </span>
            <span class="font-medium">Teil {{ task.teil }}</span>
            <span class="text-xs text-gray-400 hidden sm:inline">({{ wordCount(i) }}/{{ task.word_count_max }})</span>
          </button>
        </div>
      </div>

      <!-- Layout trois colonnes : consignes | rédaction+correction | caractères spéciaux -->
      <div class="flex-1 overflow-hidden min-h-0 flex">
        <div class="flex-1 overflow-hidden min-h-0">
          <template v-for="(task, i) in subject.tasks" :key="i">
            <div v-show="activeTab === i" class="h-full flex flex-col lg:flex-row">

              <!-- ── Colonne gauche : consignes ───────────────── -->
              <div class="lg:w-[45%] bg-white border-r border-gray-100 overflow-y-auto">
                <div class="p-6 space-y-4 max-w-xl mx-auto lg:mx-0">

                  <!-- Sprachliche Mittel -->
                  <SprachlicheMittelPanel :mittel-key="mittelKey(task)" />

                  <!-- ══ CAS 1 : choix entre thèmes (Telc/ÖSD B2) ══ -->
                  <template v-if="task.themes">
                    <div v-if="!selectedThemes[i]" class="space-y-3">
                      <p class="text-sm font-semibold text-gray-700">
                        {{ t("simulator_subject.choose_theme") }}
                      </p>
                      <div class="grid grid-cols-1 gap-3">
                        <button
                          v-for="(theme, key) in task.themes"
                          :key="key"
                          class="p-4 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-teal-400 transition-colors"
                          @click="selectedThemes[i] = String(key)"
                        >
                          <p class="font-semibold text-gray-900 mb-1">
                            Thema {{ key }} : {{ theme.titel }}
                          </p>
                          <p class="text-xs text-gray-500 line-clamp-2">{{ theme.stimulus }}</p>
                        </button>
                      </div>
                    </div>

                    <template v-else>
                      <div class="flex items-center justify-between mb-2">
                        <p class="text-sm font-semibold text-gray-700">
                          Thema {{ selectedThemes[i] }} : {{ task.themes[selectedThemes[i]!]?.titel }}
                        </p>
                        <button class="text-xs text-gray-400 hover:text-gray-600" @click="selectedThemes[i] = null">
                          {{ t("simulator_subject.change_theme") }}
                        </button>
                      </div>

                      <div class="bg-gray-50 border border-gray-200 rounded-xl p-5">
                        <p class="text-sm text-gray-800 italic">{{ task.themes[selectedThemes[i]!]?.stimulus }}</p>
                      </div>

                      <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                        <p class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">
                          {{ t("simulator_subject.task_label") }}
                        </p>
                        <ul class="space-y-1">
                          <li
                            v-for="(prompt, pi) in task.themes[selectedThemes[i]!]?.prompts"
                            :key="pi"
                            class="flex gap-2 text-sm text-amber-800"
                          >
                            <span class="font-bold shrink-0">–</span>
                            <span>{{ prompt }}</span>
                          </li>
                        </ul>
                        <p v-if="task.word_count_target" class="mt-3 text-xs text-amber-600 font-medium">
                          {{ t("simulator_subject.approx") }} {{ task.word_count_target }} {{ t("simulator_subject.words") }}
                        </p>
                      </div>
                    </template>
                  </template>

                  <!-- ══ CAS 2 : choix entre variantes d'opinion (ÖSD) ══ -->
                  <template v-else-if="task.opinion_variants">
                    <div v-if="!selectedVariants[i]" class="space-y-3">
                      <p class="text-sm font-semibold text-gray-700">
                        {{ t("simulator_subject.choose_theme") }}
                      </p>
                      <div class="grid grid-cols-1 gap-3">
                        <button
                          v-for="(variant, key) in task.opinion_variants"
                          :key="key"
                          class="p-4 bg-white border-2 border-gray-200 rounded-xl text-left hover:border-teal-400 transition-colors"
                          @click="selectedVariants[i] = String(key)"
                        >
                          <p class="font-semibold text-gray-900">{{ variant.thema }}</p>
                        </button>
                      </div>
                    </div>

                    <template v-else>
                      <div class="flex items-center justify-between mb-2">
                        <p class="text-sm font-semibold text-gray-700">
                          {{ task.opinion_variants[selectedVariants[i]!]?.thema }}
                        </p>
                        <button class="text-xs text-gray-400 hover:text-gray-600" @click="selectedVariants[i] = null">
                          {{ t("simulator_subject.change_theme") }}
                        </button>
                      </div>

                      <div v-if="task.opinion_variants[selectedVariants[i]!]?.aussagen?.length" class="space-y-2">
                        <div
                          v-for="(aussage, ai) in task.opinion_variants[selectedVariants[i]!].aussagen"
                          :key="ai"
                          class="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-800 italic"
                        >
                          « {{ aussage }} »
                        </div>
                      </div>

                      <div v-if="task.leitpunkte?.length" class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                        <p class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">
                          {{ t("simulator_subject.task_label") }}
                        </p>
                        <ul class="space-y-1">
                          <li v-for="(punkt, pi) in task.leitpunkte" :key="pi" class="flex gap-2 text-sm text-amber-800">
                            <span class="font-bold shrink-0">–</span>
                            <span>{{ punkt }}</span>
                          </li>
                        </ul>
                        <p v-if="task.word_count_target" class="mt-3 text-xs text-amber-600 font-medium">
                          {{ t("simulator_subject.approx") }} {{ task.word_count_target }} {{ t("simulator_subject.words") }}
                        </p>
                      </div>
                    </template>
                  </template>

                  <!-- ══ CAS 3 : formats simples ══ -->
                  <template v-else>
                    <!-- Stimulus e-mail (Telc) -->
                    <div
                      v-if="task.stimulus_email?.sender || task.stimulus_email?.subject || task.stimulus_email?.body"
                      class="bg-white border border-gray-200 rounded-xl overflow-hidden"
                    >
                      <div class="bg-gray-50 border-b border-gray-200 px-5 py-3 space-y-1">
                        <div class="flex items-center gap-2 text-sm">
                          <span class="font-semibold text-gray-500 w-16">Von:</span>
                          <span class="text-gray-900 font-medium">{{ task.stimulus_email.sender }}</span>
                        </div>
                        <div class="flex items-center gap-2 text-sm">
                          <span class="font-semibold text-gray-500 w-16">Betreff:</span>
                          <span class="text-gray-900">{{ task.stimulus_email.subject }}</span>
                        </div>
                      </div>
                      <div class="px-5 py-4">
                        <p class="text-sm text-gray-800 whitespace-pre-line leading-relaxed">{{ task.stimulus_email.body }}</p>
                      </div>
                    </div>

                    <!-- Stimulus forum (Goethe) -->
                    <div v-else-if="task.stimulus" class="bg-gray-50 border border-gray-200 rounded-xl p-5">
                      <div class="flex items-center gap-2 mb-2">
                        <i class="pi pi-comment text-gray-500"></i>
                        <span class="text-sm font-semibold text-gray-700">
                          {{ getStimulusAuthor(task) || t("simulator_subject.comment") }}
                        </span>
                      </div>
                      <p v-if="getStimulusTitle(task)" class="text-xs font-semibold text-gray-500 mb-2">
                        {{ getStimulusTitle(task) }}
                      </p>
                      <p class="text-sm text-gray-800 italic">{{ getStimulusText(task) }}</p>
                    </div>

                    <!-- Context ad (Telc/ÖSD annonce) -->
                    <div v-if="task.context_ad" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
                      <div class="bg-gray-50 border-b border-gray-200 px-5 py-3">
                        <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                          {{ t("simulator_subject.ad_context") }}
                        </p>
                      </div>
                      <div class="px-5 py-4">
                        <p class="text-sm text-gray-800 whitespace-pre-line leading-relaxed">{{ task.context_ad }}</p>
                      </div>
                    </div>

                    <!-- Destinataire -->
                    <div v-if="task.recipient" class="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm">
                      <span class="font-semibold text-gray-500">An:</span>
                      <span class="text-gray-900 ml-2">{{ task.recipient }}</span>
                    </div>

                    <!-- Info comparaison (ÖSD promesses vs réalité) -->
                    <div v-if="task.info_comparison" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
                      <div class="bg-gray-50 border-b border-gray-200 px-5 py-3">
                        <p class="text-sm font-semibold text-gray-800">{{ task.info_comparison.anbieter }}</p>
                        <p class="text-xs text-gray-500 mt-1">{{ task.info_comparison.situation }}</p>
                      </div>
                      <div class="px-5 py-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <p class="text-xs font-bold text-green-700 uppercase mb-2">Versprochen</p>
                          <ul class="space-y-1">
                            <li v-for="(v, vi) in task.info_comparison.versprechen" :key="vi" class="text-xs text-gray-700 flex gap-1.5">
                              <span class="text-green-600">✓</span>{{ v }}
                            </li>
                          </ul>
                        </div>
                        <div>
                          <p class="text-xs font-bold text-red-700 uppercase mb-2">Problème</p>
                          <ul class="space-y-1">
                            <li v-for="(p, pi) in task.info_comparison.probleme" :key="pi" class="text-xs text-gray-700 flex gap-1.5">
                              <span class="text-red-600">✗</span>{{ p }}
                            </li>
                          </ul>
                        </div>
                      </div>
                      <div v-if="task.info_comparison.kontakt" class="px-5 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                        Kontakt: {{ task.info_comparison.kontakt }}
                      </div>
                    </div>

                    <!-- Sujet simple (topic) -->
                    <div v-if="task.topic" class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                      <p class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">Thema :</p>
                      <p class="text-base font-bold text-amber-900">{{ task.topic }}</p>
                    </div>

                    <!-- Scénario -->
                    <div v-if="task.scenario" class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                      <p class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">
                        {{ t("simulator_subject.task_label") }}
                      </p>
                      <p class="text-sm text-amber-900 leading-relaxed">{{ task.scenario }}</p>
                    </div>

                    <!-- Prompts (communs à topic/scenario) -->
                    <div v-if="task.prompts?.length" class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                      <p v-if="!task.scenario" class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">
                        {{ t("simulator_subject.task_label") }}
                      </p>
                      <ul class="space-y-1">
                        <li v-for="(prompt, pi) in task.prompts" :key="pi" class="flex gap-2 text-sm text-amber-800">
                          <span class="font-bold shrink-0">–</span>
                          <span>{{ prompt }}</span>
                        </li>
                      </ul>
                      <p class="mt-3 text-xs text-amber-600 font-medium">
                        {{ task.word_count_min }}–{{ task.word_count_max }} {{ t("simulator_subject.word_range") }}
                        <span v-if="task.register === 'formell'"> • {{ t("simulator_subject.formal_required") }}</span>
                      </p>
                    </div>
                    <div v-else class="bg-amber-50 border border-amber-200 rounded-xl p-4">
                      <p class="text-xs text-amber-600 font-medium">
                        {{ task.word_count_min }}–{{ task.word_count_max }} {{ t("simulator_subject.word_range") }}
                      </p>
                    </div>
                  </template>

                  <!-- Navigation teile -->
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
                      iconPos="right"
                      size="small"
                      severity="secondary"
                      @click="activeTab = i + 1"
                    />
                  </div>
                </div>
              </div>

              <!-- ── Colonne milieu : rédaction + correction ─── -->
              <div class="lg:w-[55%] overflow-y-auto bg-gray-50">
                <div class="p-6 space-y-4 max-w-2xl mx-auto">

                  <!-- Zone rédaction — verrouillée tant qu'un thème/variante n'est pas choisi -->
                  <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden focus-within:border-teal-400 transition-colors">
                    <textarea
                      v-if="isWritingUnlocked(i, task)"
                      :ref="(el) => setTextareaRef(el, i)"
                      v-model="answers[i]"
                      :placeholder="t('simulator_subject.write_placeholder')"
                      class="w-full border-0 resize-none p-5 text-sm focus:ring-0 focus:outline-none bg-transparent"
                      rows="12"
                      @focus="activeTextareaIndex = i"
                    />
                    <div v-else class="p-5 text-sm text-gray-400 italic">
                      {{ t("simulator_subject.choose_theme_first") }}
                    </div>
                    <div class="border-t border-gray-100 px-5 py-2 flex items-center justify-between bg-gray-50">
                      <span class="text-xs text-gray-400">{{ wordCount(i) }} {{ t("simulator_subject.words_count") }}</span>
                      <div class="flex items-center gap-2">
                        <div class="w-24 bg-gray-200 rounded-full h-1">
                          <div
                            :class="['h-1 rounded-full transition-all', wordCount(i) >= task.word_count_max ? 'bg-green-500' : 'bg-teal-400']"
                            :style="{ width: `${Math.min((wordCount(i) / task.word_count_max) * 100, 100)}%` }"
                          />
                        </div>
                        <span :class="['text-xs font-medium', wordCount(i) >= task.word_count_min ? 'text-green-600' : 'text-gray-400']">
                          / {{ task.word_count_max }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Récap complétion -->
                  <div class="flex items-center gap-2 flex-wrap">
                    <span
                      v-for="(task2, ti) in subject.tasks"
                      :key="ti"
                      :class="[
                        'text-xs px-2 py-1 rounded-full font-medium',
                        wordCount(ti) >= (task2.word_count_min ?? 0) ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-400',
                      ]"
                    >
                      Teil {{ task2.teil }}: {{ wordCount(ti) }}/{{ task2.word_count_max }}
                    </span>
                  </div>

                  <!-- Solde crédits -->
                  <div class="flex items-center justify-between bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                    <div class="flex items-center gap-2">
                      <i class="pi pi-sparkles text-amber-500"></i>
                      <span class="text-sm font-medium text-amber-800">
                        {{ authStore.aiCredits }}
                        {{ authStore.aiCredits <= 1 ? t('simulator_subject.credit') : t('simulator_subject.credits') }}
                      </span>
                    </div>
                    <NuxtLink
                      v-if="authStore.aiCredits === 0"
                      to="/dashboard/credits"
                      class="text-xs font-semibold text-white bg-amber-500 px-3 py-1.5 rounded-lg hover:bg-amber-600 transition-colors"
                    >
                      {{ t('simulator_subject.buy_credits') }}
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
                    <p v-if="!canCorrect && authStore.aiCredits > 0" class="text-center text-xs text-gray-400 mt-2">
                      {{ t("simulator_subject.correct_hint") }}
                    </p>
                    <p v-if="authStore.aiCredits === 0" class="text-center text-xs text-red-400 mt-2">
                      {{ t('simulator_subject.no_credits_hint') }}
                    </p>
                  </div>

                  <!-- Chargement IA -->
                  <div v-else-if="store.correcting" class="flex flex-col items-center gap-3 py-8 bg-teal-50 border border-teal-200 rounded-2xl">
                    <i class="pi pi-spin pi-spinner text-teal-600 text-2xl"></i>
                    <p class="text-sm font-medium text-teal-700">{{ t("simulator_subject.correcting") }}</p>
                    <p class="text-xs text-teal-500">{{ t("simulator_subject.correcting_sub") }}</p>
                  </div>

                  <!-- Erreur correction -->
                  <div v-else-if="store.correctionError" class="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
                    <i class="pi pi-exclamation-circle text-red-500 mt-0.5 shrink-0"></i>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-red-700">{{ t("simulator_subject.error_title") }}</p>
                      <p class="text-xs text-red-500 mt-1">{{ store.correctionError }}</p>
                    </div>
                    <Button :label="t('simulator_subject.retry')" size="small" outlined severity="danger" @click="launchCorrection" />
                  </div>

                  <!-- Résultat disponible -->
                  <div
                    v-else-if="store.correction"
                    class="p-5 bg-white border-2 rounded-2xl"
                    :class="store.correction.passed ? 'border-green-400' : 'border-orange-400'"
                  >
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-3">
                        <div
                          class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                          :class="store.correction.passed ? 'bg-green-500' : 'bg-orange-500'"
                        >
                          {{ store.scorePercentage }}%
                        </div>
                        <div>
                          <p class="text-sm font-semibold text-gray-800">
                            {{ store.correction.passed ? "Prüfung bestanden ✓" : "Nicht bestanden" }}
                          </p>
                          <p class="text-xs text-gray-500">
                            {{ store.correction.overall_score }} / {{ store.correction.max_score }} points
                          </p>
                        </div>
                      </div>
                      <Button
                        :label="t('simulator_subject.see_results')"
                        icon="pi pi-arrow-right"
                        iconPos="right"
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

        <!-- ── Colonne extrême droite : caractères spéciaux allemands ── -->
        <div class="w-14 shrink-0 bg-white border-l border-gray-200 flex flex-col items-center py-4 gap-1.5 overflow-y-auto">
          <button
            v-for="char in specialChars"
            :key="char"
            type="button"
            class="w-9 h-9 rounded-lg text-sm font-semibold text-gray-700 bg-gray-50 hover:bg-teal-100 hover:text-teal-700 transition-colors border border-gray-200"
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

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
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

const totalWords = computed(() =>
  answers.value.reduce((sum, _, i) => sum + wordCount(i), 0),
);
const canCorrect = computed(() =>
  answers.value.some((_, i) => wordCount(i) > 0),
);

const launchCorrection = async () => {
  store.clearCorrection();
  await store.correct(subjectId, answers.value);
  await authStore.fetchUser();
};

const goToResults = () =>
  router.push(`/dashboard/simulateur/${subjectId}/resultats`);

const providerColor = (p: string) =>
  ({
    goethe: "bg-blue-100 text-blue-700",
    telc: "bg-purple-100 text-purple-700",
    osd: "bg-orange-100 text-orange-700",
  })[p] ?? "bg-gray-100 text-gray-600";

// ── Sprachliche Mittel — dérivé directement des champs typés du sujet,
// pas d'un nom d'examen à parser (contrairement à la session réelle).
const mittelKey = (task: any) =>
  resolveMittelKey({
    provider: subject.value?.provider?.toUpperCase() ?? "",
    cefrCode: subject.value?.level?.toUpperCase() ?? "",
    moduleSlug: "schreiben",
    formatType: task.themes ? "oral_monologue" : undefined, // ADJUST: pas de format_type réel disponible ici, à vérifier contre resolveMittelKey
    teilNumber: task.teil,
  });

// ── Choix de thème / variante d'opinion — un état par index de tâche ──
const selectedThemes = ref<Record<number, string | null>>({});
const selectedVariants = ref<Record<number, string | null>>({});

const isWritingUnlocked = (i: number, task: any): boolean => {
  if (task.themes) return !!selectedThemes.value[i];
  if (task.opinion_variants) return !!selectedVariants.value[i];
  return true;
};

// ── Stimulus — gère le cas où le générateur a produit un objet
// {text, title, author} au lieu d'une simple string.
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
const getStimulusAuthor = (task: any): string =>
  parseStimulus(task.stimulus).author || task.stimulus_author || "";
const getStimulusTitle = (task: any): string => parseStimulus(task.stimulus).title || "";

// ── Caractères spéciaux allemands ─────────────────────────────────

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