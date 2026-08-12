<!-- pages/dashboard/start-deutsch/[subjectId]/session.vue -->
<template>
  <div class="pb-10">
    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <template v-else>
      <!-- Header réutilisé (examen + Teil courant + timer par module) -->
      <SessionHeader
        :exam-name="store.subjectTitle"
        :module-name="currentModuleLabel"
        :current-teil-index="currentTeilIndexInModule"
        :teile="store.currentModule?.teile ?? []"
        :time-remaining="timeRemainingForCurrentModule"
        @exit="handleExit"
      />

      <div class="px-4 pt-6 space-y-6">
        <!-- Onglets modules -->
        <div class="flex gap-2 overflow-x-auto">
          <button
            v-for="(mod, index) in store.modules"
            :key="mod.id"
            class="shrink-0 rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
            :class="
              store.currentModuleIndex === index
                ? 'border-primary-500 bg-primary-500 text-white'
                : 'border-line bg-card text-ink-secondary hover:bg-hover'
            "
            @click="store.switchToModule(index)"
          >
            {{ moduleLabel(mod.slug) }}
          </button>
        </div>

        <!-- Progression — numérotée PAR MODULE (ex. Lesen : Question 3 of 15), pas globale sur les 35 -->
        <div>
          <p class="text-sm font-semibold text-ink-secondary">
            {{
              t("start_deutsch.session.progress", {
                current: currentQuestionIndexInModule + 1,
                total: questionsInCurrentModule.length,
              })
            }}
          </p>
          <div class="mt-2 h-1.5 rounded-full bg-hover overflow-hidden">
            <div
              class="h-full rounded-full bg-primary-500 transition-[width] duration-300"
              :style="{ width: `${moduleProgressPercent}%` }"
            />
          </div>
        </div>

        <!-- Instructions + audio du Teil courant -->
        <div
          v-if="store.currentTeil"
          class="bg-card border border-line rounded-xl p-4"
        >
          <p
            class="text-xs font-bold text-ink-tertiary uppercase tracking-wide mb-1"
          >
            Teil {{ store.currentTeil.teil_number }}
          </p>
          <p
            v-if="store.currentTeil.instructions"
            class="text-sm text-ink-secondary"
          >
            {{ store.currentTeil.instructions }}
          </p>
          <audio
            v-if="store.currentTeil.audio_file"
            class="mt-3 w-full"
            controls
            :src="resolveAudioUrl(store.currentTeil.audio_file)"
          />
        </div>

        <!-- Question courante -->
        <QuestionRenderer
          v-if="store.currentQuestion && store.currentTeil"
          :question="store.currentQuestion"
          :teil="store.currentTeil"
          :assets-base-url="assetsBaseUrl"
          :level="store.level"
          :subject-number="store.subjectNumber"
          :used-labels="usedLabelsInCurrentTeil"
          :model-value="store.currentAnswer?.user_answer ?? null"
          @update:model-value="onAnswer"
        />

        <!-- Navigation -->
        <div class="flex items-center justify-between gap-3">
          <Button
            :label="t('start_deutsch.session.previous')"
            icon="pi pi-arrow-left"
            outlined
            :disabled="store.isFirstQuestion"
            @click="store.previousQuestion"
          />

          <Button
            v-if="!store.isLastQuestion"
            :label="t('start_deutsch.session.next')"
            icon="pi pi-arrow-right"
            icon-pos="right"
            @click="store.nextQuestion"
          />
          <Button
            v-else
            :label="t('start_deutsch.session.submit')"
            icon="pi pi-check"
            icon-pos="right"
            :loading="store.isSubmitting"
            @click="handleSubmit"
          />
        </div>

        <!-- Téléchargement du devoir Schreiben — visible seulement sur ce module, une fois toutes les tâches remplies -->
        <SchreibenDownloadButton
          v-if="store.currentModule?.slug === 'schreiben'"
          :subject-title="store.subjectTitle"
          :level="store.level"
          :student-name="authStore.userName"
          :teile="store.currentModule?.teile ?? []"
          :answers="store.answers"
        />

        <!-- Navigateur de questions (points cliquables) — scopé au module courant -->
        <div class="flex flex-wrap gap-1.5 justify-center pt-2">
          <button
            v-for="q in questionsInCurrentModule"
            :key="q.id"
            class="h-2.5 w-2.5 rounded-full transition-colors"
            :class="
              q.id === store.currentQuestion?.id
                ? 'bg-primary-500'
                : store.isAnswered(q.id)
                  ? 'bg-primary-200'
                  : 'bg-hover border border-line'
            "
            @click="goToQuestionById(q.id)"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import QuestionRenderer from "~/components/start-deutsch/QuestionRenderer.vue";
import SchreibenDownloadButton from "~/components/start-deutsch/SchreibenDownloadButton.vue";
// ⚠️ À adapter : chemin réel de ton Header/Timer existant (B1/B2)
import SessionHeader from "~/components/session/SessionHeader.vue";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const route = useRoute();
const store = useStartDeutschSessionStore();
const authStore = useAuthStore();
const config = useRuntimeConfig();

const assetsBaseUrl = computed(
  () => `${config.public.apiBaseUrl || "http://localhost:8001"}/start-deutsch`,
);

function resolveAudioUrl(audioFile: string) {
  return `${assetsBaseUrl.value}/${audioFile}`;
}

const moduleLabels: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
};

function moduleLabel(slug: string) {
  return moduleLabels[slug] ?? slug;
}

const currentModuleLabel = computed(() =>
  moduleLabel(store.currentModule?.slug ?? ""),
);

// ── Numérotation PAR MODULE ─────────────────────────────────────────
// Le store garde une liste globale (store.questions, 35 questions pour
// un sujet A1 complet) — on la refiltre ici au niveau de la page pour
// n'afficher/naviguer QUE dans les questions du module actif, sans
// toucher au store (qui reste partagé/générique).

const questionsInCurrentModule = computed(() =>
  (store.currentModule?.teile ?? []).flatMap(
    (teil: any) => teil.questions ?? [],
  ),
);

const currentQuestionIndexInModule = computed(() =>
  questionsInCurrentModule.value.findIndex(
    (q: any) => q.id === store.currentQuestion?.id,
  ),
);

const moduleProgressPercent = computed(() => {
  const total = questionsInCurrentModule.value.length;
  if (!total) return 0;
  return ((currentQuestionIndexInModule.value + 1) / total) * 100;
});

const currentTeilIndexInModule = computed(() =>
  (store.currentModule?.teile ?? []).findIndex(
    (teil: any) => teil.id === store.currentTeil?.id,
  ),
);

function goToQuestionById(questionId: string) {
  const globalIndex = store.questions.findIndex(
    (q: any) => q.id === questionId,
  );
  if (globalIndex !== -1) store.goToQuestion(globalIndex);
}

// ── Timer PAR MODULE ─────────────────────────────────────────────────
// Durées officielles Goethe-Institut (Start Deutsch 1 / Goethe-Zertifikat
// A2, Prüfungsdauer par Fertigkeit) — gérées uniquement côté frontend,
// pas de champ backend pour l'instant. Un décompte indépendant par
// module : changer d'onglet met en pause le décompte du module quitté
// et reprend celui du module rejoint, là où il en était.
const MODULE_DURATIONS_MINUTES: Record<string, Record<string, number>> = {
  A1: { lesen: 25, hoeren: 20, schreiben: 20, sprechen: 15 },
  A2: { lesen: 30, hoeren: 30, schreiben: 30, sprechen: 15 },
};

const secondsRemainingByModule = reactive<Record<number, number>>({});
let timerInterval: ReturnType<typeof setInterval> | null = null;

function initModuleTimers() {
  store.modules.forEach((mod: any, index: number) => {
    if (secondsRemainingByModule[index] === undefined) {
      const minutes = MODULE_DURATIONS_MINUTES[store.level]?.[mod.slug] ?? 20;
      secondsRemainingByModule[index] = minutes * 60;
    }
  });
}

const timeRemainingForCurrentModule = computed(
  () => secondsRemainingByModule[store.currentModuleIndex] ?? 0,
);

function startTimerLoop() {
  timerInterval = setInterval(() => {
    const idx = store.currentModuleIndex;
    const current = secondsRemainingByModule[idx];
    if (current !== undefined && current > 0) {
      secondsRemainingByModule[idx] = current - 1;
    }
  }, 1000);
}

function handleExit() {
  navigateTo("/dashboard/start-deutsch");
}

// Pour image_day_matching : lettres déjà choisies par les AUTRES questions du
// même Teil (chaque image ne doit servir qu'une fois)
const usedLabelsInCurrentTeil = computed(() => {
  const teil = store.currentTeil;
  if (!teil) return [];
  return (teil.questions ?? [])
    .filter((q: any) => q.id !== store.currentQuestion?.id)
    .map((q: any) => store.answers[q.id]?.user_answer?.answer)
    .filter((label: any): label is string => !!label);
});

function onAnswer(value: Record<string, any>) {
  if (!store.currentQuestion) return;
  store.setAnswer(store.currentQuestion.id, value);
}

async function handleSubmit() {
  const result = await store.submitSession();
  if (!result.success) return;

  // Déclenche la correction IA pour chaque Teil free_text répondu — pas
  // automatique côté serveur au submit (contrairement à B1/B2 existant),
  // donc on l'appelle explicitement ici avant de naviguer vers le résultat
  const freeTextTeile = store.modules
    .flatMap((m: any) => m.teile ?? [])
    .filter((t: any) => t.format_type === "free_text");

  for (const teil of freeTextTeile) {
    const question = teil.questions?.[0];
    const text = question
      ? store.answers[question.id]?.user_answer?.text
      : undefined;
    if (question && text) {
      await store.correctSchreiben(teil.id, text);
    }
  }

  if (timerInterval) clearInterval(timerInterval);
  navigateTo(
    `/dashboard/start-deutsch/${route.params.subjectId}/result?sessionId=${store.sessionId}`,
  );
}

onMounted(async () => {
  const subjectId = route.params.subjectId as string;
  if (store.sessionId === null || store.subjectId !== subjectId) {
    await store.startSession(subjectId);
  }
  initModuleTimers();
  startTimerLoop();
});

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval);
});
</script>
