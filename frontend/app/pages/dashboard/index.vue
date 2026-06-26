<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t("dashboard.greeting") }}, {{ authStore.userName }} 👋
      </h1>
      <p class="text-gray-500 mt-1 text-sm">{{ t("dashboard.subtitle") }}</p>
    </div>

    <!-- ── Actions rapides ────────────────────────────── -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <button
        class="group flex items-center gap-4 bg-white border border-gray-100 rounded-xl p-5 hover:border-teal-400 hover:shadow-md transition-all text-left"
        @click="navigateTo('/dashboard/examens')"
      >
        <div
          class="w-12 h-12 rounded-xl bg-teal-50 flex items-center justify-center shrink-0 group-hover:bg-teal-100 transition-colors"
        >
          <i class="pi pi-book text-teal-600 text-xl"></i>
        </div>
        <div>
          <p
            class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors"
          >
            {{ t("dashboard.quick_actions.exam") }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ t("dashboard.quick_actions.exam_sub") }}
          </p>
        </div>
        <i
          class="pi pi-arrow-right text-gray-300 group-hover:text-teal-500 ml-auto transition-all group-hover:translate-x-1"
        ></i>
      </button>

      <button
        class="group flex items-center gap-4 bg-white border border-gray-100 rounded-xl p-5 hover:border-indigo-400 hover:shadow-md transition-all text-left"
        @click="navigateTo('/dashboard/simulateur')"
      >
        <div
          class="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center shrink-0 group-hover:bg-indigo-100 transition-colors"
        >
          <i class="pi pi-pen-to-square text-indigo-600 text-xl"></i>
        </div>
        <div>
          <p
            class="font-semibold text-gray-900 group-hover:text-indigo-700 transition-colors"
          >
            {{ t("dashboard.quick_actions.simulator") }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ t("dashboard.quick_actions.simulator_sub") }}
          </p>
        </div>
        <i
          class="pi pi-arrow-right text-gray-300 group-hover:text-indigo-500 ml-auto transition-all group-hover:translate-x-1"
        ></i>
      </button>

      <button
        class="group flex items-center gap-4 bg-white border border-gray-100 rounded-xl p-5 hover:border-orange-400 hover:shadow-md transition-all text-left"
        @click="navigateTo('/dashboard/resultats')"
      >
        <div
          class="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center shrink-0 group-hover:bg-orange-100 transition-colors"
        >
          <i class="pi pi-chart-line text-orange-500 text-xl"></i>
        </div>
        <div>
          <p
            class="font-semibold text-gray-900 group-hover:text-orange-700 transition-colors"
          >
            {{ t("dashboard.quick_actions.results") }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ t("dashboard.quick_actions.results_sub") }}
          </p>
        </div>
        <i
          class="pi pi-arrow-right text-gray-300 group-hover:text-orange-500 ml-auto transition-all group-hover:translate-x-1"
        ></i>
      </button>
    </div>

    <!-- ── Contenu principal ──────────────────────────── -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Examens disponibles -->
      <div
        class="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <div
          class="flex items-center justify-between px-6 py-4 border-b border-gray-100"
        >
          <h2 class="font-semibold text-gray-800">
            {{ t("dashboard.choose_exam") }}
          </h2>
          <button
            class="text-sm text-teal-600 font-medium hover:underline"
            @click="navigateTo('/dashboard/examens')"
          >
            {{ t("dashboard.see_all") }}
          </button>
        </div>

        <div v-if="examsStore.loading" class="flex justify-center py-10">
          <ProgressSpinner style="width: 40px; height: 40px" />
        </div>

        <div
          v-else-if="examsStore.catalog.length === 0"
          class="text-center py-10 text-gray-400"
        >
          <i class="pi pi-inbox text-4xl mb-3 block"></i>
          <p class="text-sm">{{ t("dashboard.no_exams") }}</p>
        </div>

        <div v-else class="divide-y divide-gray-50">
          <button
            v-for="exam in examsStore.catalog.slice(0, 4)"
            :key="exam.id"
            class="w-full flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors text-left group"
            @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
          >
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center text-white text-xs font-bold shrink-0"
              :class="providerBg(exam.provider)"
            >
              {{ exam.provider.slice(0, 2).toUpperCase() }}
            </div>

            <div class="flex-1 min-w-0">
              <p
                class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors truncate"
              >
                {{ exam.name }}
              </p>
              <div class="flex items-center gap-2 mt-1">
                <span
                  class="text-xs font-medium"
                  :class="providerText(exam.provider)"
                >
                  {{ exam.provider.toUpperCase() }}
                </span>
                <span class="text-gray-300 text-xs">•</span>
                <div class="flex gap-1">
                  <Tag
                    v-for="level in exam.levels?.slice(0, 3)"
                    :key="level.id"
                    :value="level.cefr_code"
                    size="small"
                    severity="info"
                  />
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <span
                class="text-xs text-teal-600 font-semibold opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {{ t("dashboard.start") }}
              </span>
              <i
                class="pi pi-arrow-right text-gray-300 group-hover:text-teal-500 group-hover:translate-x-1 transition-all text-sm"
              ></i>
            </div>
          </button>
        </div>
      </div>

      <!-- Sessions récentes -->
      <div
        class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <div class="px-6 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800">
            {{ t("dashboard.recent_sessions") }}
          </h2>
        </div>

        <div v-if="sessionsLoading" class="flex justify-center py-10">
          <ProgressSpinner style="width: 40px; height: 40px" />
        </div>

        <div
          v-else-if="recentSessions.length === 0"
          class="text-center py-10 px-4"
        >
          <i class="pi pi-history text-4xl text-gray-200 mb-3 block"></i>
          <p class="text-sm text-gray-500 mb-3">
            {{ t("dashboard.no_sessions") }}
          </p>
          <button
            class="text-sm text-teal-600 font-medium hover:underline"
            @click="navigateTo('/dashboard/examens')"
          >
            {{ t("dashboard.start_exam") }}
          </button>
        </div>

        <div v-else class="divide-y divide-gray-50">
          <div
            v-for="s in recentSessions"
            :key="s.id"
            class="flex items-center gap-3 px-5 py-4"
          >
            <div
              :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
                s.status === 'COMPLETED' ? 'bg-green-100' : 'bg-amber-100',
              ]"
            >
              <i
                :class="[
                  'pi text-xs',
                  s.status === 'COMPLETED'
                    ? 'pi-check text-green-600'
                    : 'pi-clock text-amber-600',
                ]"
              ></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ s.exam_name }}
              </p>
              <p class="text-xs text-gray-400">
                {{ t("dashboard.subject") }} {{ s.subject_number }} ·
                {{ formatDate(s.started_at) }}
              </p>
            </div>
            <span
              v-if="s.score_percentage != null"
              :class="[
                'text-sm font-bold shrink-0',
                s.score_percentage >= 60 ? 'text-green-600' : 'text-red-500',
              ]"
            >
              {{ s.score_percentage }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t, locale } = useI18n();
const authStore = useAuthStore();
const examsStore = useExamsStore();
const sessionStore = useSessionStore();

const sessionsLoading = ref(false);
const recentSessions = ref<any[]>([]);

const formatDate = (dateStr: string) => {
  const localeMap: Record<string, string> = {
    fr: "fr-FR",
    en: "en-GB",
    de: "de-DE",
  };
  return new Date(dateStr).toLocaleDateString(
    localeMap[locale.value] ?? "fr-FR",
    {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    },
  );
};

const providerBg = (p: string) =>
  ({
    goethe: "bg-blue-500",
    telc: "bg-purple-500",
    osd: "bg-orange-500",
  })[p?.toLowerCase()] ?? "bg-gray-400";

const providerText = (p: string) =>
  ({
    goethe: "text-blue-600",
    telc: "text-purple-600",
    osd: "text-orange-600",
  })[p?.toLowerCase()] ?? "text-gray-500";

onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
  sessionsLoading.value = true;
  const result = await sessionStore.getMySessions(0, 5);
  if (result.success) recentSessions.value = result.data || [];
  sessionsLoading.value = false;
});
</script>
