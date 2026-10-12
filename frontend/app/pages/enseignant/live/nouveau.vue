<!-- pages/enseignant/live/nouveau.vue -->
<template>
  <div class="mx-auto max-w-4xl space-y-5 pb-24">
    <p class="text-sm text-muted">{{ t("teacher.launch.intro") }}</p>

    <!-- ══ Étape 1 : élève ══ -->
    <section class="rounded-card border border-line bg-card p-5 shadow-soft">
      <h2 class="mb-3 flex items-center gap-2 text-sm font-semibold text-ink">
        <span class="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">1</span>
        {{ t("teacher.launch.step_student") }}
      </h2>

      <div v-if="loadingStudents" class="h-11 animate-pulse rounded-leaf bg-card-2" />

      <p v-else-if="myStudents.length === 0" class="text-sm text-muted">
        {{ t("teacher.launch.no_students") }}
      </p>

      <Select
        v-else
        v-model="selectedStudentId"
        :options="myStudents"
        optionLabel="full_name"
        optionValue="id"
        filter
        :placeholder="t('teacher.launch.choose_student')"
        class="w-full sm:w-96"
      >
        <template #option="{ option }">
          <div class="flex min-w-0 flex-col">
            <span class="truncate">{{ option.full_name }}</span>
            <span class="truncate text-xs text-muted">{{ option.class_label }}</span>
          </div>
        </template>
      </Select>
    </section>

    <!-- ══ Étape 2 : sujet ══ -->
    <section class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft">
      <h2 class="flex items-center gap-2 text-sm font-semibold text-ink">
        <span class="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">2</span>
        {{ t("teacher.launch.step_subject") }}
      </h2>

      <p v-if="studentLevelHint" class="flex items-center gap-1.5 text-xs text-muted">
        <i class="pi pi-info-circle text-[11px]" />
        {{ studentLevelHint }}
      </p>

      <!-- Filtres : examen puis niveau -->
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="p in availableProviders"
          :key="p"
          type="button"
          class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
          :class="
            selectedProvider === p
              ? 'border-primary bg-primary/10 text-primary'
              : 'border-line bg-card text-muted hover:border-primary/30'
          "
          @click="selectProvider(p)"
        >
          {{ p.toUpperCase() }}
        </button>
        <span class="mx-1 h-6 w-px bg-line" />
        <button
          v-for="l in availableLevels"
          :key="l"
          type="button"
          class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
          :class="
            selectedLevel === l
              ? 'border-ink bg-ink text-card'
              : 'border-line bg-card text-muted hover:border-ink/30'
          "
          @click="selectedLevel = selectedLevel === l ? '' : l"
        >
          {{ l }}
        </button>
      </div>

      <!-- Sujets -->
      <div v-if="examsStore.loading" class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div v-for="n in 4" :key="n" class="h-20 animate-pulse rounded-leaf bg-card-2" />
      </div>

      <div
        v-else-if="!sprechenSubjects.length"
        class="rounded-leaf border border-dashed border-line py-8 text-center text-sm text-muted"
      >
        {{ selectedProvider ? t("teacher.launch.no_subjects") : t("teacher.launch.subjects_hint") }}
      </div>

      <div v-else class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          v-for="subject in sprechenSubjects"
          :key="subject.id"
          type="button"
          class="rounded-leaf border p-4 text-left transition-colors"
          :class="
            selectedSubjectId === subject.id
              ? 'border-primary bg-primary/5 ring-1 ring-primary/30'
              : 'border-line hover:border-primary/30'
          "
          @click="selectedSubjectId = subject.id"
        >
          <p class="text-sm font-semibold text-ink">{{ subject.title }}</p>
          <div class="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
            <span class="rounded-full bg-card-2 px-2 py-0.5 font-semibold text-muted">
              {{ subject.provider.toUpperCase() }}
            </span>
            <span class="rounded-full bg-primary/10 px-2 py-0.5 font-semibold text-primary">
              {{ subject.level }}
            </span>
            <span class="text-muted">{{ t("teacher.launch.teile", subject.teilCount) }}</span>
          </div>
        </button>
      </div>
    </section>

    <!-- ══ Barre de lancement (toujours visible en bas) ══ -->
    <div class="sticky bottom-0 z-10 -mx-1">
      <div
        class="flex flex-col gap-3 rounded-card border border-line bg-card/95 p-4 shadow-soft backdrop-blur sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="min-w-0 text-sm">
          <p v-if="canLaunch" class="truncate text-ink">
            <i class="pi pi-check-circle mr-1 text-emerald-600" />
            {{ selectedStudent?.full_name }} · {{ selectedSubject?.title }}
          </p>
          <p v-else class="text-muted">{{ t("teacher.launch.summary_missing") }}</p>
          <p v-if="launchError" class="mt-1 text-xs text-red-600">{{ launchError }}</p>
        </div>
        <Button
          :label="t('teacher.launch.launch')"
          icon="pi pi-play"
          class="shrink-0"
          :disabled="!canLaunch"
          :loading="liveSessionStore.loading"
          @click="handleLaunch"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "enseignant" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const teacherPortalStore = useTeacherPortalStore();
const examsStore = useExamsStore();
const liveSessionStore = useLiveSessionStore();

const loadingStudents = ref(true);
const selectedStudentId = ref<string | null>(null);

// Élèves actifs (ended_at vide) de toutes les classes de l'enseignant, sans doublon.
// On garde le niveau de leur classe pour présélectionner les sujets.
const myStudents = computed(() => {
  const map = new Map<string, { id: string; full_name: string; class_label: string; level_id: string | null }>();
  for (const session of teacherPortalStore.mySessions) {
    const levelId = (session as { level_id?: string | null }).level_id ?? null;
    const classLabel = session.label ? `${session.level_name} · ${session.label}` : session.level_name;
    for (const s of session.students) {
      if (!s.ended_at && !map.has(s.student_id)) {
        map.set(s.student_id, {
          id: s.student_id,
          full_name: s.student_name,
          class_label: classLabel,
          level_id: levelId,
        });
      }
    }
  }
  return [...map.values()].sort((a, b) => a.full_name.localeCompare(b.full_name));
});

const selectedStudent = computed(
  () => myStudents.value.find((s) => s.id === selectedStudentId.value) ?? null,
);

// ── Filtres examen / niveau ──
const selectedProvider = ref("");
const selectedLevel = ref("");

// Un clic manuel sur un examen remet le niveau à zéro
function selectProvider(p: string) {
  selectedProvider.value = selectedProvider.value === p ? "" : p;
  selectedLevel.value = "";
}

const selectedSubjectId = ref<string | null>(null);
const launchError = ref<string | null>(null);

const availableProviders = computed(() => [
  ...new Set(examsStore.catalog.map((e: any) => e.provider as string)),
]);

const availableLevels = computed(() => {
  const set = new Set<string>();
  examsStore.catalog
    .filter((e: any) => !selectedProvider.value || e.provider === selectedProvider.value)
    .forEach((e: any) => e.levels?.forEach((l: any) => set.add(l.cefr_code)));
  return [...set];
});

// ── Présélection d'après la classe de l'élève ──
const studentLevelHint = ref<string | null>(null);

function presetFromStudent() {
  studentLevelHint.value = null;
  const levelId = selectedStudent.value?.level_id;
  if (!levelId) return;
  for (const exam of examsStore.catalog as any[]) {
    const level = (exam.levels ?? []).find((l: any) => l.id === levelId);
    if (level) {
      selectedProvider.value = exam.provider;
      selectedLevel.value = level.cefr_code;
      studentLevelHint.value = t("teacher.launch.level_hint", {
        level: `${exam.name} - ${level.cefr_code}`,
      });
      return;
    }
  }
}

watch(selectedStudentId, presetFromStudent);

interface SprechenSubjectCard {
  id: string;
  provider: string;
  level: string;
  title: string;
  teilCount: number;
}

const sprechenSubjects = computed<SprechenSubjectCard[]>(() => {
  const exam = examsStore.currentExam;
  if (!exam || exam.provider !== selectedProvider.value) return [];

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
        title: subject.name || t("teacher.launch.subject_fallback", { n: subject.subject_number }),
        teilCount: sprechenModule.teile?.length ?? 0,
      });
    }
  }
  return cards;
});

const selectedSubject = computed(
  () => sprechenSubjects.value.find((s) => s.id === selectedSubjectId.value) ?? null,
);

// Examen à charger pour le couple examen + niveau choisi
const targetExamSlug = computed(() => {
  if (!selectedProvider.value) return null;
  const candidates = examsStore.catalog.filter((e: any) => e.provider === selectedProvider.value);
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

// Le sujet choisi disparaît de la liste filtrée : on le désélectionne
watch(sprechenSubjects, (list) => {
  if (selectedSubjectId.value && !list.find((s) => s.id === selectedSubjectId.value)) {
    selectedSubjectId.value = null;
  }
});

const canLaunch = computed(() => !!selectedStudentId.value && !!selectedSubjectId.value);

async function handleLaunch() {
  if (!selectedStudentId.value || !selectedSubjectId.value) return;
  launchError.value = null;

  const result = await liveSessionStore.createSession({
    student_id: selectedStudentId.value,
    subject_id: selectedSubjectId.value,
  });

  if (result.success && result.session) {
    await navigateTo(localePath(`/enseignant/live/${result.session.id}`));
  } else {
    launchError.value = result.error || t("teacher.launch.launch_error");
  }
}

onMounted(async () => {
  await Promise.all([
    teacherPortalStore.mySessions.length === 0 ? teacherPortalStore.fetchMySessions() : Promise.resolve(),
    examsStore.catalog.length === 0 ? examsStore.fetchCatalog() : Promise.resolve(),
  ]);
  loadingStudents.value = false;

  // Arrivée depuis « Mes classes » (?student_id=...) : élève + niveau présélectionnés
  const preselect = route.query.student_id;
  if (typeof preselect === "string" && myStudents.value.some((s) => s.id === preselect)) {
    selectedStudentId.value = preselect;
    await nextTick(); // laisse presetFromStudent poser examen et niveau
  }

  // Sans élève présélectionné (ou classe sans niveau connu) : Goethe par défaut, sinon le premier examen
  if (!selectedProvider.value) {
    const goethe = availableProviders.value.find((p) => p.toLowerCase() === "goethe");
    selectedProvider.value = goethe ?? availableProviders.value[0] ?? "";
  }
});
</script>