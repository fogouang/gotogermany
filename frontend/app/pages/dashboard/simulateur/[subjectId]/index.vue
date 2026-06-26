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
                wordCount(i) >= task.word_count_min
                  ? 'bg-teal-600 text-white'
                  : 'bg-gray-200 text-gray-500',
              ]"
            >
              {{ wordCount(i) >= task.word_count_min ? "✓" : i + 1 }}
            </span>
            <span class="font-medium">Teil {{ task.teil }}</span>
            <span class="text-xs text-gray-400 hidden sm:inline">({{ wordCount(i) }}/{{ task.word_count_max }})</span>
          </button>
        </div>
      </div>

      <!-- Layout deux colonnes -->
      <div class="flex-1 overflow-hidden min-h-0">
        <template v-for="(task, i) in subject.tasks" :key="i">
          <div v-show="activeTab === i" class="h-full flex flex-col lg:flex-row">

            <!-- ── Colonne gauche : consignes ───────────────── -->
            <div class="lg:w-[45%] bg-white border-r border-gray-100 overflow-y-auto">
              <div class="p-6 space-y-4 max-w-xl mx-auto lg:mx-0">

                <!-- Context ad -->
                <div v-if="task.context_ad" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
                  <div class="bg-gray-50 border-b border-gray-200 px-5 py-3">
                    <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      {{ t("simulator_subject.ad_context") }}
                    </p>
                  </div>
                  <div class="px-5 py-4">
                    <p class="text-sm text-gray-800 whitespace-pre-line leading-relaxed">
                      {{ task.context_ad }}
                    </p>
                  </div>
                </div>

                <!-- Opinion quote -->
                <div v-if="task.opinion_quote" class="bg-gray-50 border border-gray-200 rounded-xl p-5 flex gap-3">
                  <i class="pi pi-comment text-gray-400 mt-0.5 shrink-0"></i>
                  <p class="text-sm text-gray-700 italic">{{ task.opinion_quote }}</p>
                </div>

                <!-- Scénario + prompts -->
                <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                  <p class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">
                    {{ t("simulator_subject.task_label") }}
                  </p>
                  <p class="text-sm text-amber-900 leading-relaxed">{{ task.scenario }}</p>
                  <ul v-if="task.prompts?.length" class="mt-3 space-y-1">
                    <li v-for="(prompt, pi) in task.prompts" :key="pi" class="flex gap-2 text-sm text-amber-800">
                      <span class="font-bold shrink-0">–</span>
                      <span>{{ prompt }}</span>
                    </li>
                  </ul>
                  <p class="mt-3 text-xs text-amber-600 font-medium">
                    {{ task.word_count_min }}–{{ task.word_count_max }} {{ t("simulator_subject.word_range") }}
                  </p>
                </div>

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

            <!-- ── Colonne droite : rédaction + correction ─── -->
            <div class="lg:w-[55%] overflow-y-auto bg-gray-50">
              <div class="p-6 space-y-4 max-w-2xl mx-auto">

                <!-- Zone rédaction -->
                <div class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden focus-within:border-teal-400 transition-colors">
                  <Textarea
                    v-model="answers[i]"
                    :placeholder="t('simulator_subject.write_placeholder')"
                    class="w-full border-0 resize-none p-5 text-sm focus:ring-0 focus:outline-none"
                    :rows="12"
                  />
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

                <!-- Zone correction (visible sur tous les teile) -->

                <!-- Récap complétion -->
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    v-for="(task2, ti) in subject.tasks"
                    :key="ti"
                    :class="[
                      'text-xs px-2 py-1 rounded-full font-medium',
                      wordCount(ti) >= task2.word_count_min ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-400',
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
                <div
                  v-else-if="store.correcting"
                  class="flex flex-col items-center gap-3 py-8 bg-teal-50 border border-teal-200 rounded-2xl"
                >
                  <i class="pi pi-spin pi-spinner text-teal-600 text-2xl"></i>
                  <p class="text-sm font-medium text-teal-700">{{ t("simulator_subject.correcting") }}</p>
                  <p class="text-xs text-teal-500">{{ t("simulator_subject.correcting_sub") }}</p>
                </div>

                <!-- Erreur correction -->
                <div
                  v-else-if="store.correctionError"
                  class="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3"
                >
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

    </template>
  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from "~/stores/simulator";

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

onMounted(async () => {
  store.clearCorrection();
  await store.fetchSubject(subjectId);
});

useHead({ title: t("simulator_subject.page_title") });
</script>