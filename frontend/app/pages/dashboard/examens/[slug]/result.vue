<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 60px; height: 60px" />
    </div>

    <!-- Erreur -->
    <div v-else-if="!result" class="text-center py-16">
      <i class="pi pi-exclamation-triangle text-5xl text-red-500 mb-4"></i>
      <h2 class="text-xl font-bold mb-2">Résultat introuvable</h2>
      <Button
        label="Retour aux examens"
        @click="navigateTo('/dashboard/examens')"
      />
    </div>

    <!-- Résultat -->
    <div v-else class="max-w-4xl mx-auto space-y-8">
      <!-- Header résultat -->
      <div
        :class="[
          'rounded-2xl p-8 text-white',
          result.passed === true
            ? 'bg-linear-to-br from-green-600 to-teal-600'
            : result.passed === false
              ? 'bg-linear-to-br from-red-500 to-orange-500'
              : 'bg-linear-to-br from-green-600 to-teal-600',
        ]"
      >
        <div class="text-center">
          <i
            :class="[
              'text-6xl mb-4',
              result.passed === true
                ? 'pi pi-check-circle'
                : result.passed === false
                  ? 'pi pi-times-circle'
                  : 'pi pi-clock',
            ]"
          ></i>
          <h1 class="text-3xl font-bold mb-2">{{ result.exam_name }}</h1>
          <p class="text-xl opacity-90 mb-6">{{ result.result_message }}</p>

          <!-- Score global -->
          <div
            class="inline-flex items-center gap-6 bg-white/20 rounded-xl px-8 py-4"
          >
            <div class="text-center">
              <div class="text-4xl font-bold">
                {{ result.score !== null ? result.score?.toFixed(1) : "—" }}
              </div>
              <div class="text-sm opacity-75">Score /100</div>
            </div>
            <div class="w-px h-12 bg-white/30"></div>
            <div class="text-center">
              <div class="text-4xl font-bold">
                {{ result.total_pass_score }}
              </div>
              <div class="text-sm opacity-75">Score requis</div>
            </div>
            <div class="w-px h-12 bg-white/30"></div>
            <div class="text-center">
              <div class="text-4xl font-bold">
                {{
                  result.duration_seconds
                    ? formatDuration(result.duration_seconds)
                    : "—"
                }}
              </div>
              <div class="text-sm opacity-75">Durée</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Score par module -->
      <Card>
        <template #title>
          <h2 class="text-xl font-bold">Résultats par module</h2>
        </template>
        <template #content>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              v-for="module in result.modules"
              :key="module.slug"
              class="bg-gray-50 rounded-xl p-4"
            >
              <div class="flex items-center gap-3 mb-3">
                <div
                  :class="[
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    getModuleColor(module.slug),
                  ]"
                >
                  <i :class="['pi text-lg', getModuleIcon(module.slug)]"></i>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-900">{{ module.name }}</h3>
                  <p class="text-xs text-gray-500">
                    Max : {{ module.max_score }} pts
                  </p>
                </div>
              </div>

              <div
                v-if="!module.is_corrected"
                class="flex items-center gap-2 text-amber-600"
              >
                <i class="pi pi-clock"></i>
                <span class="text-sm">En attente de correction</span>
              </div>
              <div v-else>
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-600">Score</span>
                  <span class="font-bold">
                    {{ module.score_obtained?.toFixed(1) ?? "—" }} / 100
                  </span>
                </div>
                <ProgressBar
                  :value="module.score_obtained ?? 0"
                  :showValue="false"
                  :class="[
                    'h-2',
                    (module.score_obtained ?? 0) >= 60
                      ? '[&_.p-progressbar-value]:bg-green-500'
                      : '[&_.p-progressbar-value]:bg-red-500',
                  ]"
                />
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Détail par module -->
      <div v-for="module in result.modules" :key="`detail-${module.slug}`">
        <Accordion>
          <AccordionTab>
            <template #header>
              <div class="flex items-center gap-3">
                <i :class="['pi', getModuleIcon(module.slug)]"></i>
                <span class="font-semibold"
                  >{{ module.name }} — Détail des réponses</span
                >
              </div>
            </template>

            <div
              v-for="teil in module.teile"
              :key="teil.teil_number"
              class="mb-6"
            >
              <h4 class="font-medium text-gray-700 mb-3">
                Teil {{ teil.teil_number }} —
                {{ teil.score_obtained?.toFixed(1) }} / {{ teil.max_score }} pts
              </h4>

              <div class="space-y-3">
                <div
                  v-for="answer in teil.answers"
                  :key="answer.question_id"
                  :class="[
                    'p-4 rounded-lg border-l-4',
                    answer.is_correct === true
                      ? 'bg-green-50 border-green-500'
                      : answer.is_correct === false
                        ? 'bg-red-50 border-red-500'
                        : 'bg-gray-50 border-gray-300',
                  ]"
                >
                  <div class="flex items-start justify-between gap-4">
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-700 mb-1">
                        Question {{ answer.question_number }}
                      </p>
                      <div class="flex flex-wrap gap-4 text-sm">
                        <span class="text-gray-600">
                          Votre réponse :
                          <strong>{{
                            formatAnswer(answer.user_answer)
                          }}</strong>
                        </span>
                        <span
                          v-if="
                            answer.correct_answer && answer.is_correct === false
                          "
                          class="text-green-700"
                        >
                          Bonne réponse :
                          <strong>{{
                            formatAnswer(answer.correct_answer)
                          }}</strong>
                        </span>
                      </div>
                      <p
                        v-if="answer.feedback"
                        class="text-xs text-gray-500 mt-2"
                      >
                        {{ answer.feedback }}
                      </p>
                    </div>
                    <div class="shrink-0">
                      <i
                        v-if="answer.is_correct === true"
                        class="pi pi-check-circle text-green-600 text-xl"
                      ></i>
                      <i
                        v-else-if="answer.is_correct === false"
                        class="pi pi-times-circle text-red-600 text-xl"
                      ></i>
                      <i v-else class="pi pi-clock text-gray-400 text-xl"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </AccordionTab>
        </Accordion>
      </div>

      <!-- Actions -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center pb-8">
        <Button
          label="Retour aux examens"
          icon="pi pi-arrow-left"
          outlined
          @click="navigateTo('/dashboard/examens')"
        />
        <Button
          label="Voir mes résultats"
          icon="pi pi-list"
          outlined
          @click="navigateTo('/dashboard/resultats')"
        />
        <Button
          label="Recommencer"
          icon="pi pi-refresh"
          @click="navigateTo(`/dashboard/examens`)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SessionResultResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const route = useRoute();
const sessionStore = useSessionStore();

const loading = ref(true);
const result = ref<SessionResultResponse | null>(null);

const sessionId = computed(() => route.params.sessionId as string);

const formatDuration = (seconds: number): string => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m${s.toString().padStart(2, "0")}s`;
};

const formatAnswer = (answer: Record<string, any> | null): string => {
  if (!answer) return "—";
  return answer.answer ?? answer.text ?? JSON.stringify(answer);
};

const getModuleIcon = (slug: string) => {
  const icons: Record<string, string> = {
    horen: "pi-volume-up",
    lesen: "pi-book",
    schreiben: "pi-pencil",
    sprechen: "pi-microphone",
  };
  for (const key in icons) {
    if (slug.toLowerCase().includes(key)) return icons[key];
  }
  return "pi-file";
};

const getModuleColor = (slug: string) => {
  const colors: Record<string, string> = {
    horen: "bg-purple-100 text-purple-600",
    lesen: "bg-blue-100 text-blue-600",
    schreiben: "bg-green-100 text-green-600",
    sprechen: "bg-orange-100 text-orange-600",
  };
  for (const key in colors) {
    if (slug.toLowerCase().includes(key)) return colors[key];
  }
  return "bg-gray-100 text-gray-600";
};

onMounted(async () => {
  // 1. Essayer depuis le store (soumission directe)
  if (sessionStore.result) {
    result.value = sessionStore.result;
    loading.value = false;
    return;
  }

  // 2. Essayer depuis query param ?sessionId=...
  const sessionId = route.query.sessionId as string;
  if (sessionId) {
    const res = await sessionStore.getResult(sessionId);
    if (res.success) result.value = res.result ?? null;
    loading.value = false;
    return;
  }

  // 3. Essayer depuis sessionId du store
  if (sessionStore.sessionId) {
    const res = await sessionStore.getResult(sessionStore.sessionId);
    if (res.success) result.value = res.result ?? null;
    loading.value = false;
    return;
  }

  loading.value = false;
});
</script>
