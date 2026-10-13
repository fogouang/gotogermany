<!-- pages/dashboard/start-deutsch/index.vue -->
<template>
  <div class="space-y-6">
    <!-- ── En-tête ── -->
    <header>
      <h1 class="text-2xl font-bold text-ink">{{ t("start_deutsch.title") }}</h1>
      <p class="mt-1 text-sm text-muted">{{ t("start_deutsch.subtitle") }}</p>
    </header>

    <!-- ── Bandeau : entraînement inclus, pas un vrai examen ── -->
    <div class="flex items-start gap-3 rounded-card border border-primary/30 bg-primary/10 px-5 py-4">
      <i class="pi pi-info-circle mt-0.5 shrink-0 text-primary" />
      <p class="text-sm text-ink">{{ t("start_deutsch.info_banner") }}</p>
    </div>

    <!-- ── Filtre niveau ── -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="opt in levelOptions"
        :key="opt.value"
        type="button"
        class="rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
        :class="
          filterLevel === opt.value
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-line bg-card text-muted hover:border-primary/30 hover:text-ink'
        "
        @click="setLevelFilter(opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- ── Chargement ── -->
    <div v-if="store.subjectsLoading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="i in 6" :key="i" class="h-32 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="filteredSubjects.length === 0"
      class="rounded-card border border-line bg-card py-16 text-center shadow-soft"
    >
      <i class="pi pi-inbox mb-3 block text-4xl text-faint" />
      <p class="text-sm text-muted">{{ t("start_deutsch.empty") }}</p>
    </div>

    <!-- ── Cartes sujets ── -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="subject in filteredSubjects"
        :key="subject.id"
        type="button"
        class="group flex flex-col items-start gap-3 rounded-card border border-line bg-card p-5 text-left shadow-soft transition-all hover:border-primary/40"
        @click="startSubject(subject.id)"
      >
        <div class="flex w-full items-center justify-between">
          <span
            class="inline-flex size-10 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary"
          >
            {{ subject.level }}
          </span>
          <i
            class="pi pi-arrow-right text-faint transition-all group-hover:translate-x-1 group-hover:text-primary"
          />
        </div>

        <div class="min-w-0">
          <p class="font-semibold text-ink transition-colors group-hover:text-primary">
            {{ subject.title }}
          </p>
          <p v-if="subject.description" class="mt-1 line-clamp-2 text-xs text-muted">
            {{ subject.description }}
          </p>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard" });

const { t } = useI18n();
const localePath = useLocalePath();
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
  navigateTo(localePath(`/dashboard/start-deutsch/${subjectId}/session`));
}

onMounted(async () => {
  if (store.subjects.length === 0) await store.fetchSubjects();
});
</script>