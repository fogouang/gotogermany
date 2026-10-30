<!-- pages/enseignant/devoirs/nouveau.vue -->
<template>
  <div class="space-y-5">
    <NuxtLink
      :to="localePath('/enseignant/devoirs')"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("teacher.assignments.form.back") }}
    </NuxtLink>

    <div v-if="loading" class="grid gap-5 lg:grid-cols-3">
      <div class="h-96 animate-pulse rounded-card bg-card-2 lg:col-span-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <div v-else class="grid items-start gap-5 lg:grid-cols-3">
      <!-- ══════════ Colonne gauche : choisir ══════════ -->
      <div class="space-y-5 lg:col-span-2">
        <!-- Étape 1 : pour qui -->
        <section
          class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <h2 class="flex items-center gap-2 text-sm font-semibold text-ink">
            <span
              class="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
              >1</span
            >
            {{ t("teacher.assignments.form.step_targets") }}
          </h2>

          <p v-if="openClasses.length === 0" class="text-sm text-muted">
            {{ t("teacher.assignments.form.no_classes") }}
          </p>

          <template v-else>
            <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">
              <button
                v-for="c in openClasses"
                :key="c.id"
                type="button"
                class="flex items-center gap-3 rounded-leaf border px-4 py-3 text-left transition-colors"
                :class="
                  selectedClassIds.includes(c.id)
                    ? 'border-primary bg-primary/5 ring-1 ring-primary/30'
                    : 'border-line hover:border-primary/30'
                "
                @click="toggleClass(c.id)"
              >
                <i
                  class="pi text-sm"
                  :class="
                    selectedClassIds.includes(c.id)
                      ? 'pi-check-square text-primary'
                      : 'pi-stop text-muted'
                  "
                />
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium text-ink">
                    {{ c.label || c.level_name }}
                  </p>
                  <p class="truncate text-xs text-muted">
                    {{ c.label ? `${c.level_name} · ` : ""
                    }}{{
                      t(
                        "teacher.classes.active_students",
                        { n: c.active.length },
                        c.active.length,
                      )
                    }}
                  </p>
                </div>
              </button>
            </div>

            <!-- Élèves en plus -->
            <div>
              <label class="mb-1.5 block text-xs font-medium text-muted">
                {{ t("teacher.assignments.form.extra_students") }}
              </label>
              <MultiSelect
                v-if="studentOptions.length"
                v-model="selectedStudentIds"
                :options="studentOptions"
                optionLabel="label"
                optionValue="value"
                filter
                :showToggleAll="false"
                display="chip"
                :placeholder="
                  t('teacher.assignments.form.students_placeholder')
                "
                class="w-full"
              >
                <template #option="{ option }">
                  <div class="flex min-w-0 flex-col">
                    <span class="truncate">{{ option.label }}</span>
                    <span class="truncate text-xs text-muted">{{
                      option.classLabel
                    }}</span>
                  </div>
                </template>
              </MultiSelect>
              <p v-else class="flex items-center gap-1.5 text-sm text-muted">
                <i class="pi pi-check-circle text-xs text-emerald-600" />
                {{ t("teacher.assignments.form.all_covered") }}
              </p>
            </div>
          </template>
        </section>

        <!-- Étape 2 : sujet -->
        <section
          class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <h2 class="flex items-center gap-2 text-sm font-semibold text-ink">
            <span
              class="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
              >2</span
            >
            {{ t("teacher.assignments.form.step_subject") }}
          </h2>

          <div v-if="bankLevels.length > 1" class="flex flex-wrap gap-2">
            <button
              v-for="lvl in bankLevels"
              :key="lvl.id"
              type="button"
              class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
              :class="
                levelFilter === lvl.id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-line bg-card text-muted hover:border-primary/30'
              "
              @click="levelFilter = levelFilter === lvl.id ? null : lvl.id"
            >
              {{ lvl.label }}
            </button>
          </div>

          <div
            v-if="visibleSubjects.length === 0"
            class="rounded-leaf border border-dashed border-line py-8 text-center text-sm text-muted"
          >
            {{ t("teacher.assignments.form.no_subjects") }}
          </div>

          <div
            v-else
            class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3"
          >
            <button
              v-for="s in visibleSubjects"
              :key="s.subject_id"
              type="button"
              class="rounded-leaf border p-4 text-left transition-colors"
              :class="
                selectedSubjectId === s.subject_id
                  ? 'border-primary bg-primary/5 ring-1 ring-primary/30'
                  : 'border-line hover:border-primary/30'
              "
              @click="selectSubject(s.subject_id)"
            >
              <p class="text-sm font-semibold text-ink">
                {{
                  s.subject_name ||
                  t("teacher.launch.subject_fallback", { n: s.subject_number })
                }}
              </p>
              <div class="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
                <span
                  class="rounded-full bg-card-2 px-2 py-0.5 font-semibold text-muted"
                  >{{ s.exam_name }}</span
                >
                <span
                  class="rounded-full bg-primary/10 px-2 py-0.5 font-semibold text-primary"
                  >{{ s.cefr_code }}</span
                >
              </div>
              <p
                v-if="s.modules?.length"
                class="mt-2 truncate text-xs text-muted"
              >
                {{ s.modules.map(moduleLabel).join(" · ") }}
              </p>
            </button>
          </div>

          <p
            v-if="levelMismatch"
            class="flex items-start gap-1.5 rounded-leaf bg-amber-500/10 px-3 py-2 text-xs text-amber-600"
          >
            <i class="pi pi-exclamation-triangle mt-0.5 text-[11px]" />
            {{ t("teacher.assignments.form.level_mismatch") }}
          </p>
        </section>
      </div>

      <!-- ══════════ Colonne droite : détails + envoi ══════════ -->
      <div class="space-y-5 lg:sticky lg:top-0">
        <!-- Étape 3 : détails -->
        <section
          class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <h2 class="flex items-center gap-2 text-sm font-semibold text-ink">
            <span
              class="flex size-6 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
              >3</span
            >
            {{ t("teacher.assignments.form.step_details") }}
          </h2>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("teacher.assignments.form.title") }}
              <span class="text-red-600">*</span>
            </label>
            <InputText
              v-model="title"
              class="w-full"
              :placeholder="t('teacher.assignments.form.title_placeholder')"
              @input="titleTouched = true"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("teacher.assignments.form.instructions") }}
              <span class="font-normal text-muted">{{
                t("centre.form.optional")
              }}</span>
            </label>
            <Textarea
              v-model="instructions"
              rows="4"
              autoResize
              class="w-full"
              :placeholder="
                t('teacher.assignments.form.instructions_placeholder')
              "
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("teacher.assignments.form.due_at") }}
              <span class="font-normal text-muted">{{
                t("centre.form.optional")
              }}</span>
            </label>
            <DatePicker
              v-model="dueAt"
              showTime
              hourFormat="24"
              dateFormat="dd/mm/yy"
              showIcon
              :minDate="new Date()"
              class="w-full"
            />
            <p class="mt-1 text-xs text-muted">
              {{ t("teacher.assignments.form.due_hint") }}
            </p>
          </div>
        </section>

        <!-- Récapitulatif + envoi -->
        <section
          class="space-y-4 rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <div v-if="canSubmit" class="space-y-2 text-sm">
            <p class="flex items-center gap-2 text-ink">
              <i class="pi pi-users text-xs text-muted" />
              {{
                t(
                  "teacher.assignments.form.summary",
                  { n: concernedCount },
                  concernedCount,
                )
              }}
            </p>
            <p class="flex items-center gap-2 text-ink">
              <i class="pi pi-file text-xs text-muted" />
              <span class="truncate">{{ selectedSubject?.subject_name }}</span>
            </p>
          </div>
          <p v-else class="text-sm text-muted">
            {{ t("teacher.assignments.form.summary_missing") }}
          </p>

          <Message v-if="submitError" severity="error" :closable="false">{{
            submitError
          }}</Message>

          <Button
            :label="t('teacher.assignments.form.create')"
            icon="pi pi-send"
            class="w-full"
            :disabled="!canSubmit"
            :loading="submitting"
            @click="handleSubmit"
          />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NormalizedTrainingSession } from "~/stores/trainingSessions";
import type { AssignmentCreate } from "~~/shared/api";

definePageMeta({ layout: "enseignant", watermark: "Hausaufgaben" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const toast = useToast();
const teacherPortalStore = useTeacherPortalStore();
const assignmentsStore = useAssignmentsStore();

const loading = ref(true);

// ── Classes ouvertes (non terminées) avec leurs élèves actifs ──
function isFinished(s: NormalizedTrainingSession) {
  return !!s.end_date && new Date(s.end_date).getTime() < Date.now();
}

const openClasses = computed(() =>
  teacherPortalStore.mySessions
    .filter((s) => !isFinished(s))
    .map((s) => ({
      ...s,
      // Clé de niveau : level_id pour les B, « sd:A1 » / « sd:A2 » pour Start Deutsch
      level_id: classLevelKey(s),
      active: s.students.filter((x) => !x.ended_at),
    })),
);

function classLevelKey(s: NormalizedTrainingSession): string | null {
  const x = s as { level_id?: string | null; sd_level?: string | null };
  if (x.level_id) return x.level_id;
  return x.sd_level ? `sd:${x.sd_level}` : null;
}

// ── Cibles ──
const selectedClassIds = ref<string[]>([]);
const selectedStudentIds = ref<string[]>([]);

function toggleClass(id: string) {
  const i = selectedClassIds.value.indexOf(id);
  if (i >= 0) selectedClassIds.value.splice(i, 1);
  else selectedClassIds.value.push(id);
}

const selectedClasses = computed(() =>
  openClasses.value.filter((c) => selectedClassIds.value.includes(c.id)),
);

// Élèves déjà couverts par une classe cochée
const coveredIds = computed(
  () =>
    new Set(
      selectedClasses.value.flatMap((c) => c.active.map((x) => x.student_id)),
    ),
);

// Un élève couvert par une classe cochée n'a pas besoin d'être ajouté en plus
watch(coveredIds, (covered) => {
  selectedStudentIds.value = selectedStudentIds.value.filter(
    (id) => !covered.has(id),
  );
});

// Élèves actifs de l'enseignant qui ne sont pas déjà couverts par une classe cochée
const studentOptions = computed(() => {
  const map = new Map<
    string,
    { value: string; label: string; classLabel: string; levelId: string | null }
  >();
  for (const c of openClasses.value) {
    for (const s of c.active) {
      if (map.has(s.student_id) || coveredIds.value.has(s.student_id)) continue;
      map.set(s.student_id, {
        value: s.student_id,
        label: s.student_name,
        classLabel: c.label || c.level_name,
        levelId: c.level_id,
      });
    }
  }
  return [...map.values()].sort((a, b) => a.label.localeCompare(b.label));
});

const concernedCount = computed(
  () => new Set([...coveredIds.value, ...selectedStudentIds.value]).size,
);

// Niveaux des cibles choisies (classes + classe des élèves ajoutés)
const targetLevelIds = computed(() => {
  const ids = new Set<string>();
  selectedClasses.value.forEach((c) => c.level_id && ids.add(c.level_id));
  selectedStudentIds.value.forEach((id) => {
    const lvl = studentOptions.value.find((o) => o.value === id)?.levelId;
    if (lvl) ids.add(lvl);
  });
  return ids;
});

// ── Banque de sujets ──
const levelFilter = ref<string | null>(null);
const selectedSubjectId = ref<string | null>(null);

// Même clé côté banque de sujets
type BankItem = (typeof assignmentsStore.bank)[number];
function bankLevelKey(s: BankItem): string {
  return s.level_id ?? `sd:${s.cefr_code}`;
}

const bankLevels = computed(() => {
  const map = new Map<string, string>();
  for (const s of assignmentsStore.bank)
    map.set(bankLevelKey(s), `${s.exam_name} · ${s.cefr_code}`);
  return [...map.entries()]
    .map(([id, label]) => ({ id, label }))
    .sort((a, b) => a.label.localeCompare(b.label));
});

// Une seule classe ciblée (ou un seul niveau) : on filtre directement sur son niveau
watch(targetLevelIds, (ids) => {
  if (ids.size === 1) levelFilter.value = [...ids][0]!;
});

const visibleSubjects = computed(() =>
  assignmentsStore.bank
    .filter((s) => !levelFilter.value || bankLevelKey(s) === levelFilter.value)
    .sort(
      (a, b) =>
        a.exam_name.localeCompare(b.exam_name) ||
        a.subject_number - b.subject_number,
    ),
);

const selectedSubject = computed(
  () =>
    assignmentsStore.bank.find(
      (s) => s.subject_id === selectedSubjectId.value,
    ) ?? null,
);

const levelMismatch = computed(
  () =>
    !!selectedSubject.value &&
    targetLevelIds.value.size > 0 &&
    !targetLevelIds.value.has(bankLevelKey(selectedSubject.value)),
);

// Les noms de modules arrivent en slug (« lesen », « muendlicher_ausdruck »…)
function moduleLabel(slug: string) {
  return slug.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

// ── Détails ──
const title = ref("");
const titleTouched = ref(false);
const instructions = ref("");
const dueAt = ref<Date | null>(null);

function selectSubject(id: string) {
  selectedSubjectId.value = id;
  // Titre prérempli avec le nom du sujet tant que l'enseignant ne l'a pas modifié
  if (!titleTouched.value) {
    const s = assignmentsStore.bank.find((x) => x.subject_id === id);
    if (s)
      title.value =
        s.subject_name ||
        t("teacher.launch.subject_fallback", { n: s.subject_number });
  }
}

// ── Envoi ──
const submitting = ref(false);
const submitError = ref<string | null>(null);

const canSubmit = computed(
  () =>
    concernedCount.value > 0 &&
    !!selectedSubjectId.value &&
    !!title.value.trim(),
);

async function handleSubmit() {
  if (!canSubmit.value || !selectedSubjectId.value) return;
  submitting.value = true;
  submitError.value = null;

  const result = await assignmentsStore.create({
    kind: (selectedSubject.value?.kind ?? "exam") as AssignmentCreate["kind"],
    subject_id: selectedSubjectId.value,
    title: title.value.trim(),
    instructions: instructions.value.trim() || null,
    due_at: dueAt.value ? dueAt.value.toISOString() : null,
    class_ids: selectedClassIds.value,
    student_ids: selectedStudentIds.value,
  });

  submitting.value = false;

  if (result.success) {
    toast.add({
      severity: "success",
      summary: t("teacher.assignments.form.created"),
      life: 3000,
    });
    await navigateTo(localePath("/enseignant/devoirs"));
  } else {
    submitError.value =
      result.error || t("teacher.assignments.form.create_error");
  }
}

// ── Chargement ──
onMounted(async () => {
  await Promise.all([
    teacherPortalStore.mySessions.length === 0
      ? teacherPortalStore.fetchMySessions()
      : Promise.resolve(),
    assignmentsStore.fetchBank(),
  ]);
  loading.value = false;

  // Arrivée depuis « Mes classes » (?class_id=) ou la banque de sujets (?subject_id=)
  const classId = route.query.class_id;
  if (
    typeof classId === "string" &&
    openClasses.value.some((c) => c.id === classId)
  ) {
    selectedClassIds.value = [classId];
  }
  const subjectId = route.query.subject_id;
  if (
    typeof subjectId === "string" &&
    assignmentsStore.bank.some((s) => s.subject_id === subjectId)
  ) {
    await nextTick();
    const s = assignmentsStore.bank.find((x) => x.subject_id === subjectId)!;
    levelFilter.value = bankLevelKey(s);
    selectSubject(subjectId);
  }
});
</script>
