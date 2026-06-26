<template>
  <div class="space-y-6 pb-10">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t("dashboard_exams.title") }}
      </h1>
      <p class="text-sm text-gray-400 mt-1">
        {{ t("dashboard_exams.subtitle") }}
      </p>
    </div>

    <!-- Filtres -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <IconField iconPosition="left">
            <InputIcon class="pi pi-search text-gray-400" />
            <InputText
              v-model="searchQuery"
              :placeholder="t('dashboard_exams.search_placeholder')"
              class="w-full"
            />
          </IconField>
        </div>
        <Select
          v-model="selectedProvider"
          :options="providers"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('dashboard_exams.provider_placeholder')"
          class="w-full sm:w-44"
        />
        <Select
          v-model="selectedLevel"
          :options="cefrLevels"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('dashboard_exams.level_placeholder')"
          class="w-full sm:w-36"
        />
        <Button
          v-if="searchQuery || selectedProvider || selectedLevel"
          icon="pi pi-times"
          text
          rounded
          severity="secondary"
          @click="resetFilters"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="examsStore.loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
    </div>

    <!-- Vide -->
    <div
      v-else-if="filteredExams.length === 0"
      class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-gray-100"
    >
      <div
        class="w-14 h-14 rounded-2xl bg-gray-50 flex items-center justify-center mb-4"
      >
        <i class="pi pi-inbox text-2xl text-gray-300"></i>
      </div>
      <p class="font-semibold text-gray-600">
        {{ t("dashboard_exams.empty_title") }}
      </p>
      <p class="text-sm text-gray-400 mb-5 mt-1">
        {{ t("dashboard_exams.empty_subtitle") }}
      </p>
      <Button
        :label="t('dashboard_exams.reset')"
        text
        size="small"
        @click="resetFilters"
      />
    </div>

    <!-- Liste groupée par provider -->
    <div v-else class="space-y-8">
      <div v-for="(exams, provider) in groupedExams" :key="provider">
        <!-- Provider header -->
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-sm"
            :class="providerBg(String(provider))"
          >
            {{ String(provider).slice(0, 2).toUpperCase() }}
          </div>
          <h2 class="text-xs font-bold text-gray-400 uppercase tracking-widest">
            {{ getProviderName(String(provider)) }}
          </h2>
          <div class="flex-1 h-px bg-gray-100"></div>
          <span class="text-xs text-gray-300 font-medium"
            >{{ exams.length }} {{ t("dashboard_exams.exam_count") }}</span
          >
        </div>

        <!-- Cards examens — grid au lieu de liste -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            v-for="exam in exams"
            :key="exam.id"
            class="group relative bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md hover:border-teal-200 transition-all text-left overflow-hidden"
            @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
          >
            <!-- Accent couleur provider en haut -->
            <div
              class="absolute top-0 left-0 right-0 h-1 rounded-t-2xl"
              :class="providerBg(exam.provider)"
            ></div>

            <!-- Header card -->
            <div class="flex items-start gap-3 mt-1">
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center text-white text-xs font-bold shrink-0"
                :class="providerBg(exam.provider)"
              >
                {{ exam.provider.slice(0, 2).toUpperCase() }}
              </div>
              <div class="flex-1 min-w-0">
                <p
                  class="font-bold text-gray-900 group-hover:text-teal-700 transition-colors leading-tight"
                >
                  {{ exam.name }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5 line-clamp-1">
                  {{ exam.description || t("dashboard_exams.default_desc") }}
                </p>
              </div>
              <i
                class="pi pi-arrow-right text-gray-200 group-hover:text-teal-400 group-hover:translate-x-1 transition-all shrink-0 mt-1"
              ></i>
            </div>

            <!-- Niveaux -->
            <div class="flex flex-wrap items-center gap-2 mt-4">
              <span
                v-for="level in exam.levels"
                :key="level.id"
                :class="[
                  'inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full border transition-colors',
                  level.has_access
                    ? 'bg-green-50 text-green-700 border-green-100'
                    : 'bg-gray-50 text-gray-500 border-gray-100',
                ]"
              >
                <i
                  :class="[
                    'pi text-xs',
                    level.has_access ? 'pi-check-circle' : 'pi-lock',
                  ]"
                ></i>
                {{ level.cefr_code }}
                <span v-if="!level.has_access" class="text-teal-500 font-medium"
                  >· 3 gratuits</span
                >
                <span v-else class="text-green-600 font-medium">· Complet</span>
              </span>
            </div>

            <!-- Footer card -->
            <div
              class="flex items-center justify-between mt-4 pt-3 border-t border-gray-50"
            >
              <span class="text-xs text-gray-400">
                {{
                  exam.levels?.reduce((s, l) => s + (l.subject_count || 0), 0)
                }}
                sujets au total
              </span>
              <span
                class="text-xs font-semibold text-teal-600 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {{ t("dashboard_exams.see_subjects") }} →
              </span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamCatalogResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const examsStore = useExamsStore();

const searchQuery = ref("");
const selectedProvider = ref("");
const selectedLevel = ref("");

const providers = computed(() => [
  { label: t("dashboard_exams.all_providers"), value: "" },
  { label: "Goethe", value: "Goethe" },
  { label: "ÖSD", value: "ÖSD" },
  { label: "TELC", value: "TELC" },
]);

const cefrLevels = computed(() => [
  { label: t("dashboard_exams.all_levels"), value: "" },
  { label: "B1", value: "B1" },
  { label: "B2", value: "B2" },
]);

const filteredExams = computed(() => {
  let exams = examsStore.catalog;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    exams = exams.filter(
      (e) =>
        e.name.toLowerCase().includes(q) ||
        e.description?.toLowerCase().includes(q) ||
        e.provider.toLowerCase().includes(q),
    );
  }
  if (selectedProvider.value)
    exams = exams.filter((e) => e.provider === selectedProvider.value);
  if (selectedLevel.value)
    exams = exams.filter((e) =>
      e.levels?.some((l) => l.cefr_code === selectedLevel.value),
    );
  return exams;
});

const groupedExams = computed(() => {
  const grouped: Record<string, ExamCatalogResponse[]> = {};
  filteredExams.value.forEach((exam) => {
    const p = exam.provider || "Autre";
    if (!grouped[p]) grouped[p] = [];
    grouped[p].push(exam);
  });
  return grouped;
});

const getProviderName = (provider: string) =>
  ({
    Goethe: "Goethe-Institut",
    ÖSD: "Österreichisches Sprachdiplom",
    TELC: "TELC Deutsch",
  })[provider] ?? provider;

const providerBg = (p: string) =>
  ({
    Goethe: "bg-green-500",
    ÖSD: "bg-blue-500",
    TELC: "bg-red-500",
  })[p] ?? "bg-gray-400";

const resetFilters = () => {
  searchQuery.value = "";
  selectedProvider.value = "";
  selectedLevel.value = "";
};

onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
});
</script>
