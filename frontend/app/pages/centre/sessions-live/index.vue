<!-- pages/centre/sessions-live.vue -->
<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Session Sprechen en direct</h1>
      <p class="text-sm text-gray-500">
        Choisissez un étudiant et un sujet pour lancer une session d'examen oral
        que vous menez vous-même, en direct.
      </p>
    </div>

    <!-- Étape 1 : étudiant -->
    <div class="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
      <p class="text-sm font-semibold text-gray-700">1. Étudiant</p>
      <div v-if="loadingStudents" class="flex items-center gap-2 text-sm text-gray-400">
        <i class="pi pi-spin pi-spinner" /> Chargement des étudiants…
      </div>
      <Select
        v-else
        v-model="selectedStudentId"
        :options="students"
        optionLabel="full_name"
        optionValue="id"
        filter
        placeholder="Choisir un étudiant"
        class="w-full sm:w-96"
      />
    </div>

    <!-- Étape 2 : sujet (même pattern de filtrage que dashboard/sprechen/index.vue) -->
    <div class="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
      <p class="text-sm font-semibold text-gray-700">2. Sujet Sprechen</p>

      <div class="flex flex-wrap gap-2">
        <button
          v-for="p in availableProviders"
          :key="p"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedProvider === p
              ? 'bg-teal-600 text-white border-teal-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-teal-300',
          ]"
          @click="selectedProvider = selectedProvider === p ? '' : p"
        >
          {{ p.toUpperCase() }}
        </button>
        <div class="w-px bg-gray-200 mx-1" />
        <button
          v-for="l in availableLevels"
          :key="l"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium border transition-all',
            selectedLevel === l
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300',
          ]"
          @click="selectedLevel = selectedLevel === l ? '' : l"
        >
          {{ l }}
        </button>
      </div>

      <div v-if="examsStore.loading" class="flex justify-center py-8">
        <ProgressSpinner style="width: 40px; height: 40px" />
      </div>

      <div
        v-else-if="!sprechenSubjects.length"
        class="text-center py-8 text-sm text-gray-400"
      >
        Sélectionnez un provider et un niveau pour voir les sujets disponibles.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <button
          v-for="subject in sprechenSubjects"
          :key="subject.id"
          :class="[
            'text-left rounded-xl border p-4 transition-all',
            selectedSubjectId === subject.id
              ? 'border-teal-500 ring-2 ring-teal-100 bg-teal-50'
              : 'border-gray-100 hover:border-teal-200',
          ]"
          @click="selectedSubjectId = subject.id"
        >
          <p class="font-semibold text-gray-900 text-sm">{{ subject.title }}</p>
          <div class="flex items-center gap-2 mt-2">
            <Tag :value="subject.provider.toUpperCase()" />
            <Tag :value="subject.level" severity="info" />
            <span class="text-xs text-gray-400">{{ subject.teilCount }} Teile</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Étape 3 : lancer -->
    <div class="flex items-center gap-3">
      <Button
        label="Lancer la session"
        icon="pi pi-play"
        :disabled="!canLaunch"
        :loading="liveSessionStore.loading"
        @click="handleLaunch"
      />
      <p v-if="launchError" class="text-sm text-red-600">{{ launchError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: "centre",
  middleware: "centre-staff", // autorise branch_secretary ET center_director
});

const centerStaffStore = useCenterStaffStore();
const examsStore = useExamsStore();
const liveSessionStore = useLiveSessionStore();
const authStore = useAuthStore();

const loadingStudents = ref(true);
const students = ref<{ id: string; full_name: string }[]>([]);
const selectedStudentId = ref<string | null>(null);

const selectedProvider = ref("");
const selectedLevel = ref("");
const selectedSubjectId = ref<string | null>(null);

const launchError = ref<string | null>(null);

const availableProviders = computed(() => {
  const set = new Set(examsStore.catalog.map((e: any) => e.provider));
  return [...set];
});

const availableLevels = computed(() => {
  const set = new Set<string>();
  examsStore.catalog.forEach((e: any) =>
    e.levels?.forEach((l: any) => set.add(l.cefr_code)),
  );
  return [...set];
});

interface SprechenSubjectCard {
  id: string;
  provider: string;
  level: string;
  title: string;
  teilCount: number;
}

const sprechenSubjects = computed<SprechenSubjectCard[]>(() => {
  const exam = examsStore.currentExam;
  if (!exam) return [];

  const cards: SprechenSubjectCard[] = [];
  for (const level of exam.levels ?? []) {
    if (selectedLevel.value && level.cefr_code !== selectedLevel.value) continue;

    for (const subject of level.subjects ?? []) {
      const sprechenModule = (subject.modules ?? []).find(
        (m: any) => m.slug === "sprechen" || m.slug === "muendlicher_ausdruck",
      );
      if (!sprechenModule) continue;

      cards.push({
        id: subject.id,
        provider: exam.provider,
        level: level.cefr_code,
        title: subject.name || `Sujet ${subject.subject_number}`,
        teilCount: sprechenModule.teile?.length ?? 0,
      });
    }
  }
  return cards;
});

const targetExamSlug = computed(() => {
  if (!selectedProvider.value) return null;
  const candidates = examsStore.catalog.filter(
    (e: any) => e.provider === selectedProvider.value,
  );
  if (!candidates.length) return null;
  if (!selectedLevel.value) return candidates[0]!.slug;
  const match = candidates.find((e: any) =>
    e.levels?.some((l: any) => l.cefr_code === selectedLevel.value),
  );
  return (match ?? candidates[0]!).slug;
});

watch(targetExamSlug, async (slug) => {
  if (!slug) return;
  await examsStore.fetchExamBySlug(slug);
});

// Réinitialise le sujet choisi si la liste filtrée change sous ses pieds
watch(sprechenSubjects, (list) => {
  if (selectedSubjectId.value && !list.find((s) => s.id === selectedSubjectId.value)) {
    selectedSubjectId.value = null;
  }
});

const canLaunch = computed(
  () => !!selectedStudentId.value && !!selectedSubjectId.value,
);

async function handleLaunch() {
  if (!selectedStudentId.value || !selectedSubjectId.value) return;
  launchError.value = null;

  const result = await liveSessionStore.createSession({
    student_id: selectedStudentId.value,
    subject_id: selectedSubjectId.value,
  });

  if (result.success && result.session) {
    // Redirige vers la page "run" de la session (à construire à l'étape
    // suivante — page candidat/examinateur qui utilise useLiveSession()).
    await navigateTo(`/centre/sessions-live/${result.session.id}`);
  } else {
    launchError.value = result.error || "Erreur lors du lancement.";
  }
}

onMounted(async () => {
  const result = authStore.isDirector
    ? await centerStaffStore.fetchStudentsByCenter()
    : await centerStaffStore.fetchStudentsByBranch();
  if (result.success) students.value = result.students ?? [];
  loadingStudents.value = false;

  if (!examsStore.catalog.length) await examsStore.fetchCatalog();
});
</script>