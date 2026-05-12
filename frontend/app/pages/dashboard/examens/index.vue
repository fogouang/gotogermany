<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Examens disponibles</h1>
      <p class="text-gray-600">Choisissez un examen et commencez votre préparation</p>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-8">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <IconField iconPosition="left">
            <InputIcon class="pi pi-search" />
            <InputText v-model="searchQuery" placeholder="Rechercher un examen..." class="w-full" />
          </IconField>
        </div>
        <Select
          v-model="selectedProvider"
          :options="providers"
          optionLabel="label"
          optionValue="value"
          placeholder="Provider"
          class="w-full sm:w-44"
        />
        <Select
          v-model="selectedLevel"
          :options="cefrLevels"
          optionLabel="label"
          optionValue="value"
          placeholder="Niveau"
          class="w-full sm:w-44"
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
    <div v-if="examsStore.loading" class="flex justify-center py-20">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Empty -->
    <div v-else-if="filteredExams.length === 0" class="text-center py-20">
      <i class="pi pi-inbox text-5xl text-gray-300 mb-4 block"></i>
      <h3 class="text-lg font-semibold text-gray-700 mb-2">Aucun examen trouvé</h3>
      <p class="text-gray-500 mb-6">Essayez avec d'autres critères de recherche</p>
      <Button label="Réinitialiser" text @click="resetFilters" />
    </div>

    <!-- Exams grouped by provider -->
    <div v-else class="space-y-10">
      <div v-for="(exams, provider) in groupedExams" :key="provider">

        <!-- Provider header -->
        <div class="flex items-center gap-3 mb-5">
          <div class="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
            <i class="pi pi-bookmark text-primary-600 text-sm"></i>
          </div>
          <h2 class="text-lg font-bold text-gray-900">{{ getProviderName(String(provider)) }}</h2>
          <div class="flex-1 h-px bg-gray-100"></div>
          <span class="text-xs text-gray-400">{{ exams.length }} examen(s)</span>
        </div>

        <!-- Exam cards grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="exam in exams"
            :key="exam.id"
            class="group bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg hover:border-primary-200 transition-all duration-200 overflow-hidden cursor-pointer"
            @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
          >
            <!-- Top gradient band -->
            <div class="h-2 bg-linear-to-r from-primary-500 to-primary-400"></div>

            <div class="p-5">
              <!-- Provider badge + niveau tags -->
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-bold text-primary-600 uppercase tracking-widest">
                  {{ exam.provider }}
                </span>
                <div class="flex gap-1.5">
                  <Tag
                    v-for="level in exam.levels"
                    :key="level.id"
                    :value="level.cefr_code"
                    :severity="getLevelSeverity(level.cefr_code)"
                  />
                </div>
              </div>

              <!-- Nom examen -->
              <h3 class="text-lg font-bold text-gray-900 group-hover:text-primary-700 transition-colors mb-1">
                {{ exam.name }}
              </h3>

              <!-- Description -->
              <p class="text-sm text-gray-500 line-clamp-2 mb-4">
                {{ exam.description || "Préparez-vous efficacement pour cet examen d'allemand." }}
              </p>

              <!-- Accès par niveau -->
              <div class="flex flex-wrap gap-2 mb-5">
                <div
                  v-for="level in exam.levels"
                  :key="level.id"
                  class="flex items-center gap-1.5"
                >
                  <span v-if="level.has_access" class="text-xs text-success-600 font-medium flex items-center gap-1 bg-success-50 px-2 py-0.5 rounded-full">
                    <i class="pi pi-check-circle text-xs"></i> {{ level.cefr_code }} — Accès actif
                  </span>
                  <span v-else-if="level.is_free" class="text-xs text-primary-600 font-medium flex items-center gap-1 bg-primary-50 px-2 py-0.5 rounded-full">
                    <i class="pi pi-lock-open text-xs"></i> {{ level.cefr_code }} — Gratuit
                  </span>
                  <span v-else class="text-xs text-gray-500 font-medium flex items-center gap-1 bg-gray-100 px-2 py-0.5 rounded-full">
                    <i class="pi pi-lock text-xs"></i> {{ level.cefr_code }} — Premium
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-2">
                <Button
                  label="Commencer"
                  icon="pi pi-play"
                  class="flex-1 bg-gradient-primary! border-none! text-white!"
                  @click.stop="startExam(exam)"
                />
                <Button
                  icon="pi pi-info-circle"
                  outlined
                  severity="secondary"
                  v-tooltip.top="'Voir les détails'"
                  @click.stop="navigateTo(`/dashboard/examens/${exam.slug}`)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamCatalogResponse } from "#shared/api";

definePageMeta({
  layout: "dashboard",
  middleware: "auth",
});

const examsStore = useExamsStore();

const searchQuery = ref("");
const selectedProvider = ref("");
const selectedLevel = ref("");

const providers = computed(() => [
  { label: "Tous les providers", value: "" },
  { label: "Goethe", value: "Goethe" },
  { label: "ÖSD", value: "ÖSD" },
  { label: "TELC", value: "TELC" },
]);

const cefrLevels = [
  { label: "Tous les niveaux", value: "" },
  { label: "B1", value: "B1" },
  { label: "B2", value: "B2" },
];

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
  if (selectedProvider.value) {
    exams = exams.filter((e) => e.provider === selectedProvider.value);
  }
  if (selectedLevel.value) {
    exams = exams.filter((e) =>
      e.levels?.some((l) => l.cefr_code === selectedLevel.value),
    );
  }
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

const getProviderName = (provider: string) => {
  const names: Record<string, string> = {
    Goethe: "Goethe-Institut",
    ÖSD: "Österreichisches Sprachdiplom",
    TELC: "TELC Deutsch",
  };
  return names[provider] || provider;
};

const getLevelSeverity = (cefrCode: string) => {
  const s: Record<string, any> = {
    A1: "success", A2: "success",
    B1: "info", B2: "info",
    C1: "warning", C2: "danger",
  };
  return s[cefrCode] || "secondary";
};

const resetFilters = () => {
  searchQuery.value = "";
  selectedProvider.value = "";
  selectedLevel.value = "";
};

const startExam = (exam: ExamCatalogResponse) => {
  navigateTo(`/dashboard/examens/${exam.slug}`);
};

onMounted(async () => {
  if (examsStore.catalog.length === 0) {
    await examsStore.fetchCatalog();
  }
});
</script>