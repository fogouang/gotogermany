<!-- pages/dashboard/start-deutsch/index.vue -->
<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t("start_deutsch.title") }}
      </h1>
      <p class="text-gray-500 mt-1 text-sm">
        {{ t("start_deutsch.subtitle") }}
      </p>
    </div>

    <!-- Bandeau explicatif : entraînement inclus, pas un vrai examen -->
    <div
      class="flex items-start gap-3 bg-emerald-50 border border-emerald-100 rounded-xl px-5 py-4"
    >
      <i class="pi pi-info-circle text-emerald-500 mt-0.5 shrink-0"></i>
      <p class="text-sm text-emerald-800">
        {{ t("start_deutsch.info_banner") }}
      </p>
    </div>

    <!-- Filtre niveau -->
    <div class="flex gap-2">
      <button
        v-for="opt in levelOptions"
        :key="opt.value"
        class="rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
        :class="
          filterLevel === opt.value
            ? 'border-emerald-500 bg-emerald-500 text-white'
            : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
        "
        @click="setLevelFilter(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.subjectsLoading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 48px; height: 48px" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="filteredSubjects.length === 0"
      class="text-center py-16 bg-white rounded-xl border border-gray-100"
    >
      <i class="pi pi-inbox text-4xl text-gray-200 mb-3 block"></i>
      <p class="text-sm text-gray-500">{{ t("start_deutsch.empty") }}</p>
    </div>

    <!-- Cartes sujets -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <button
        v-for="subject in filteredSubjects"
        :key="subject.id"
        class="group flex flex-col items-start gap-3 bg-white border border-gray-100 rounded-xl p-5 text-left hover:border-emerald-400 hover:shadow-md transition-all"
        @click="startSubject(subject.id)"
      >
        <div class="flex w-full items-center justify-between">
          <span
            class="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 font-bold text-sm group-hover:bg-emerald-100 transition-colors"
          >
            {{ subject.level }}
          </span>
          <i
            class="pi pi-arrow-right text-gray-300 group-hover:text-emerald-500 group-hover:translate-x-1 transition-all"
          ></i>
        </div>

        <div>
          <p
            class="font-semibold text-gray-900 group-hover:text-emerald-700 transition-colors"
          >
            {{ subject.title }}
          </p>
          <p
            v-if="subject.description"
            class="text-xs text-gray-400 mt-1 line-clamp-2"
          >
            {{ subject.description }}
          </p>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const store = useStartDeutschSessionStore();

const filterLevel = ref<"A1" | "A2" | "">("");

const levelOptions = computed(() => [
  { label: t("start_deutsch.all_levels"), value: "" as const },
  { label: "A1", value: "A1" as const },
  { label: "A2", value: "A2" as const },
]);

const filteredSubjects = computed(() =>
  filterLevel.value
    ? store.subjects.filter((s) => s.level === filterLevel.value)
    : store.subjects,
);

function setLevelFilter(value: "A1" | "A2" | "") {
  filterLevel.value = value;
}

function startSubject(subjectId: string) {
  navigateTo(`/dashboard/start-deutsch/${subjectId}/session`);
}

onMounted(async () => {
  if (store.subjects.length === 0) await store.fetchSubjects();
});
</script>
