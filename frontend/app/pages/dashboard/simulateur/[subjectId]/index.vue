<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Loading -->
    <div
      v-if="store.loading"
      class="flex items-center justify-center min-h-screen"
    >
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Erreur -->
    <div
      v-else-if="store.error"
      class="max-w-lg mx-auto pt-20 px-6 text-center space-y-4"
    >
      <i class="pi pi-exclamation-circle text-red-400 text-4xl"></i>
      <p class="text-red-600 font-medium">{{ store.error }}</p>
      <Button
        :label="t('simulator_subject.back')"
        outlined
        @click="router.back()"
      />
    </div>

    <!-- Contenu -->
    <div v-else-if="subject">
      <!-- Barre de navigation -->
      <div
        class="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3"
      >
        <Button icon="pi pi-arrow-left" text rounded @click="router.back()" />
        <div class="flex items-center gap-2">
          <span
            :class="[
              'text-xs font-bold px-2 py-0.5 rounded-full uppercase',
              providerColor(subject.provider),
            ]"
          >
            {{ subject.provider }}
          </span>
          <span
            class="text-xs font-bold px-2 py-0.5 rounded-full uppercase bg-indigo-100 text-indigo-700"
          >
            {{ subject.level }}
          </span>
        </div>
        <h1 class="text-sm font-semibold text-gray-800 truncate">
          {{ subject.title }}
        </h1>
        <span class="ml-auto text-xs text-gray-400">
          {{ totalWords }} {{ t("simulator_subject.words_written") }}
        </span>
      </div>

      <!-- Tabs -->
      <div class="max-w-3xl mx-auto px-4 pt-6 pb-2">
        <Tabs v-model:value="activeTab">
          <TabList>
            <Tab
              v-for="(task, i) in subject.tasks"
              :key="i"
              :value="i"
              class="flex items-center gap-2"
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
              <span class="text-xs text-gray-400 hidden sm:inline"
                >({{ wordCount(i) }}/{{ task.word_count_max }})</span
              >
            </Tab>
          </TabList>

          <TabPanels>
            <TabPanel
              v-for="(task, i) in subject.tasks"
              :key="i"
              :value="i"
              class="space-y-4 py-6"
            >
              <!-- Context ad -->
              <div
                v-if="task.context_ad"
                class="bg-white border border-gray-200 rounded-xl overflow-hidden"
              >
                <div class="bg-gray-50 border-b border-gray-200 px-5 py-3">
                  <p
                    class="text-xs font-semibold text-gray-500 uppercase tracking-wide"
                  >
                    {{ t("simulator_subject.ad_context") }}
                  </p>
                </div>
                <div class="px-5 py-4">
                  <p
                    class="text-sm text-gray-800 whitespace-pre-line leading-relaxed"
                  >
                    {{ task.context_ad }}
                  </p>
                </div>
              </div>

              <!-- Opinion quote -->
              <div
                v-if="task.opinion_quote"
                class="bg-gray-50 border border-gray-200 rounded-xl p-5 flex gap-3"
              >
                <i class="pi pi-comment text-gray-400 mt-0.5 shrink-0"></i>
                <p class="text-sm text-gray-700 italic">
                  {{ task.opinion_quote }}
                </p>
              </div>

              <!-- Scénario + prompts -->
              <div class="bg-amber-50 border border-amber-200 rounded-xl p-5">
                <p
                  class="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2"
                >
                  {{ t("simulator_subject.task_label") }}
                </p>
                <p class="text-sm text-amber-900 leading-relaxed">
                  {{ task.scenario }}
                </p>
                <ul v-if="task.prompts?.length" class="mt-3 space-y-1">
                  <li
                    v-for="(prompt, pi) in task.prompts"
                    :key="pi"
                    class="flex gap-2 text-sm text-amber-800"
                  >
                    <span class="font-bold shrink-0">–</span>
                    <span>{{ prompt }}</span>
                  </li>
                </ul>
                <p class="mt-3 text-xs text-amber-600 font-medium">
                  {{ task.word_count_min }}–{{ task.word_count_max }}
                  {{ t("simulator_subject.word_range") }}
                </p>
              </div>

              <!-- Zone rédaction -->
              <div
                class="bg-white border-2 border-gray-200 rounded-xl overflow-hidden focus-within:border-teal-400 transition-colors"
              >
                <Textarea
                  v-model="answers[i]"
                  :placeholder="t('simulator_subject.write_placeholder')"
                  class="w-full border-0 resize-none p-5 text-sm focus:ring-0 focus:outline-none"
                  :rows="12"
                />
                <div
                  class="border-t border-gray-100 px-5 py-2 flex items-center justify-between bg-gray-50"
                >
                  <span class="text-xs text-gray-400"
                    >{{ wordCount(i) }}
                    {{ t("simulator_subject.words_count") }}</span
                  >
                  <div class="flex items-center gap-3">
                    <div class="flex items-center gap-2">
                      <div class="w-24 bg-gray-200 rounded-full h-1">
                        <div
                          :class="[
                            'h-1 rounded-full transition-all',
                            wordCount(i) >= task.word_count_max
                              ? 'bg-green-500'
                              : 'bg-teal-400',
                          ]"
                          :style="{
                            width: `${Math.min((wordCount(i) / task.word_count_max) * 100, 100)}%`,
                          }"
                        />
                      </div>
                      <span
                        :class="[
                          'text-xs font-medium',
                          wordCount(i) >= task.word_count_min
                            ? 'text-green-600'
                            : 'text-gray-400',
                        ]"
                      >
                        / {{ task.word_count_max }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Navigation tabs -->
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
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>

      <!-- Zone correction -->
      <div class="max-w-3xl mx-auto px-4 pb-10">
        <!-- Récap complétion -->
        <div class="flex items-center gap-2 mb-4 flex-wrap">
          <span
            v-for="(task, i) in subject.tasks"
            :key="i"
            :class="[
              'text-xs px-2 py-1 rounded-full font-medium',
              wordCount(i) >= task.word_count_min
                ? 'bg-teal-100 text-teal-700'
                : 'bg-gray-100 text-gray-400',
            ]"
          >
            Teil {{ task.teil }}: {{ wordCount(i) }}/{{ task.word_count_max }}
          </span>
        </div>

        <!-- Solde crédits -->
        <div
          class="flex items-center justify-between mb-4 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3"
        >
          <div class="flex items-center gap-2">
            <i class="pi pi-sparkles text-amber-500"></i>
            <span class="text-sm font-medium text-amber-800">
              {{ authStore.aiCredits }}
              {{
                authStore.aiCredits <= 1
                  ? "crédit IA disponible"
                  : "crédits IA disponibles"
              }}
            </span>
          </div>
          <NuxtLink
            v-if="authStore.aiCredits === 0"
            to="/dashboard/credits"
            class="text-xs font-semibold text-white bg-amber-500 px-3 py-1.5 rounded-lg hover:bg-amber-600 transition-colors"
          >
            Acheter des crédits
          </NuxtLink>
        </div>

        <!-- Pas encore soumis -->
        <div
          v-if="
            !store.correction && !store.correcting && !store.correctionError
          "
        >
          <Button
            :label="
              authStore.aiCredits > 0
                ? t('simulator_subject.correct_btn')
                : 'Crédits insuffisants'
            "
            icon="pi pi-sparkles"
            :disabled="!canCorrect || authStore.aiCredits <= 0"
            class="w-full"
            size="large"
            @click="launchCorrection"
          />
          <p
            v-if="!canCorrect && authStore.aiCredits > 0"
            class="text-center text-xs text-gray-400 mt-2"
          >
            {{ t("simulator_subject.correct_hint") }}
          </p>
          <p
            v-if="authStore.aiCredits === 0"
            class="text-center text-xs text-red-400 mt-2"
          >
            Vous n'avez plus de crédits IA. Achetez des crédits pour continuer.
          </p>
        </div>

        <!-- Chargement IA -->
        <div
          v-else-if="store.correcting"
          class="flex flex-col items-center gap-3 py-8 bg-teal-50 border border-teal-200 rounded-2xl"
        >
          <i class="pi pi-spin pi-spinner text-teal-600 text-2xl"></i>
          <p class="text-sm font-medium text-teal-700">
            {{ t("simulator_subject.correcting") }}
          </p>
          <p class="text-xs text-teal-500">
            {{ t("simulator_subject.correcting_sub") }}
          </p>
        </div>

        <!-- Erreur correction -->
        <div
          v-else-if="store.correctionError"
          class="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3"
        >
          <i class="pi pi-exclamation-circle text-red-500 mt-0.5 shrink-0"></i>
          <div class="flex-1">
            <p class="text-sm font-medium text-red-700">
              {{ t("simulator_subject.error_title") }}
            </p>
            <p class="text-xs text-red-500 mt-1">{{ store.correctionError }}</p>
          </div>
          <Button
            :label="t('simulator_subject.retry')"
            size="small"
            outlined
            severity="danger"
            @click="launchCorrection"
          />
        </div>

        <!-- Résultat disponible -->
        <div
          v-else-if="store.correction"
          class="p-5 bg-white border-2 rounded-2xl"
          :class="
            store.correction.passed ? 'border-green-400' : 'border-orange-400'
          "
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                :class="
                  store.correction.passed ? 'bg-green-500' : 'bg-orange-500'
                "
              >
                {{ store.scorePercentage }}%
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-800">
                  {{
                    store.correction.passed
                      ? "Prüfung bestanden ✓"
                      : "Nicht bestanden"
                  }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ store.correction.overall_score }} /
                  {{ store.correction.max_score }} points
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
