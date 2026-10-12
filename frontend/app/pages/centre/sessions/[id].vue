<!-- pages/centre/sessions/[id].vue -->
<template>
  <div class="space-y-5">
    <NuxtLink
      :to="localePath('/centre/sessions')"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("centre.classes.detail.back") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-4">
      <div class="h-36 animate-pulse rounded-card bg-card-2" />
      <div class="h-72 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur / introuvable ── -->
    <div
      v-else-if="errorMessage || !session"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage || t("centre.classes.detail.not_found") }}
    </div>

    <template v-else>
      <!-- ══ En-tête ══ -->
      <section class="relative isolate overflow-hidden rounded-card border border-line bg-card p-6 shadow-soft">
        <CardWatermark
          :text="cefrOf(session.level_name)"
          icon="pi pi-users"
          tone="amber"
          placement="center"
          glow="full"
        />

        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h1 class="truncate text-xl font-bold text-ink">{{ session.label || session.level_name }}</h1>
              <span class="rounded-full px-2 py-0.5 text-[11px] font-semibold" :class="statusBadge.class">
                {{ statusBadge.label }}
              </span>
            </div>
            <p v-if="session.label" class="mt-0.5 text-sm text-muted">{{ session.level_name }}</p>
            <div class="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted">
              <span class="flex items-center gap-1.5">
                <i class="pi pi-calendar text-[11px]" />
                {{ period }}
              </span>
              <span v-if="session.branch_name" class="flex items-center gap-1.5">
                <i class="pi pi-map-marker text-[11px]" />
                {{ session.branch_name }}
              </span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <Button
              :label="t('centre.classes.detail.edit')"
              icon="pi pi-pencil"
              outlined
              size="small"
              @click="openEditDialog"
            />
            <Button
              v-if="status !== 'finished'"
              :label="t('centre.classes.detail.end_class')"
              icon="pi pi-flag"
              severity="danger"
              outlined
              size="small"
              @click="confirmEndClass"
            />
          </div>
        </div>

        <!-- Chiffres -->
        <div class="mt-6 grid grid-cols-2 gap-3 border-t border-line pt-5 sm:grid-cols-4">
          <div v-for="s in stats" :key="s.label">
            <p class="text-2xl font-bold" :class="s.tone ?? 'text-ink'">{{ s.value }}</p>
            <p class="text-xs text-muted">{{ s.label }}</p>
          </div>
        </div>
      </section>

      <Message v-if="actionError" severity="error" :closable="false">{{ actionError }}</Message>

      <div class="grid gap-5 lg:grid-cols-3">
        <!-- ══ Élèves ══ -->
        <section class="overflow-hidden rounded-card border border-line bg-card shadow-soft lg:col-span-2">
          <header class="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
            <h2 class="font-semibold text-ink">
              {{ t("centre.nav.students") }}
              <span class="font-normal text-muted">· {{ activeStudents.length }}</span>
            </h2>
          </header>

          <p v-if="activeStudents.length === 0" class="px-5 py-8 text-center text-sm text-muted">
            {{ t("centre.classes.no_student") }}
          </p>

          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-line text-left text-xs text-muted">
                  <th class="px-5 py-3 font-medium">{{ t("centre.classes.detail.col_student") }}</th>
                  <th class="px-5 py-3 font-medium">{{ t("centre.students.col_access") }}</th>
                  <th class="px-5 py-3 font-medium">{{ t("centre.progress.average") }}</th>
                  <th class="px-5 py-3 font-medium">{{ t("centre.classes.detail.col_activity") }}</th>
                  <th class="px-5 py-3" />
                </tr>
              </thead>
              <tbody class="divide-y divide-line">
                <tr v-for="row in activeStudents" :key="row.student_id" class="hover:bg-card-2/50">
                  <td class="px-5 py-3">
                    <div class="flex items-center gap-3">
                      <span
                        class="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary"
                      >
                        {{ initials(row.student_name) }}
                      </span>
                      <div class="min-w-0">
                        <p class="truncate font-medium text-ink">{{ row.student_name }}</p>
                        <p class="truncate text-xs text-muted">
                          {{ row.email }}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="px-5 py-3">
                    <span
                      class="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2 py-0.5 text-[11px] font-semibold"
                      :class="accessBadge(row.access_expires_at).class"
                    >
                      <i :class="accessBadge(row.access_expires_at).icon" class="text-[10px]" />
                      {{ accessBadge(row.access_expires_at).label }}
                    </span>
                  </td>
                  <td class="px-5 py-3 font-semibold" :class="scoreTone(row.average_score)">
                    {{ row.average_score !== null ? `${Math.round(row.average_score)}/100` : "-" }}
                  </td>
                  <td
                    class="whitespace-nowrap px-5 py-3 text-xs"
                    :class="isInactive(row.last_session_at) ? 'text-amber-600' : 'text-muted'"
                  >
                    {{ lastActivity(row.last_session_at) }}
                  </td>
                  <td class="px-5 py-3">
                    <div class="flex items-center justify-end gap-1">
                      <Button
                        v-if="!hasAccess(row.access_expires_at)"
                        :label="t('centre.students.activate')"
                        icon="pi pi-bolt"
                        size="small"
                        @click="goToActivation(row.student_id)"
                      />
                      <Button
                        icon="pi pi-chart-line"
                        text
                        rounded
                        size="small"
                        severity="secondary"
                        v-tooltip.top="t('centre.classes.detail.progress')"
                        :aria-label="t('centre.classes.detail.progress')"
                        @click="navigateTo(localePath(`/centre/progression/${row.student_id}`))"
                      />
                      <Button
                        icon="pi pi-sign-out"
                        text
                        rounded
                        size="small"
                        severity="danger"
                        v-tooltip.top="t('centre.classes.end_student')"
                        :aria-label="t('centre.classes.end_student')"
                        @click="confirmEndStudent(row.student_id, row.student_name)"
                      />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Inscrire -->
          <div class="flex gap-2 border-t border-line px-5 py-4">
            <Select
              v-model="studentToAdd"
              :options="availableStudents"
              optionLabel="full_name"
              optionValue="id"
              :placeholder="t('centre.classes.add_student')"
              class="min-w-0 flex-1"
              filter
            />
            <Button
              :label="t('centre.classes.enroll')"
              icon="pi pi-user-plus"
              :disabled="!studentToAdd"
              :loading="busy"
              @click="handleEnrollStudent"
            />
          </div>

          <!-- Élèves sortis (repliés) -->
          <div v-if="endedStudents.length" class="border-t border-line px-5 py-3">
            <button
              type="button"
              class="flex items-center gap-2 text-xs font-medium text-muted transition-colors hover:text-ink"
              :aria-expanded="showEnded"
              @click="showEnded = !showEnded"
            >
              <i class="pi pi-chevron-right text-[10px] transition-transform" :class="{ 'rotate-90': showEnded }" />
              {{ t("centre.classes.detail.ended_toggle", { n: endedStudents.length }, endedStudents.length) }}
            </button>
            <ul v-if="showEnded" class="mt-2 divide-y divide-line">
              <li
                v-for="s in endedStudents"
                :key="s.student_id"
                class="flex items-center justify-between gap-3 py-2 text-sm"
              >
                <span class="truncate text-muted">{{ s.student_name }}</span>
                <span class="shrink-0 text-xs text-muted">
                  {{ t("centre.classes.left_on", { date: formatDate(s.ended_at!) }) }}
                </span>
              </li>
            </ul>
          </div>
        </section>

        <!-- ══ Enseignants ══ -->
        <section class="h-fit rounded-card border border-line bg-card p-5 shadow-soft">
          <h2 class="mb-3 font-semibold text-ink">{{ t("centre.nav.teachers") }}</h2>

          <p v-if="session.teachers.length === 0" class="mb-3 text-sm text-amber-600">
            {{ t("centre.classes.no_teacher") }}
          </p>

          <ul v-else class="mb-3 space-y-2">
            <li
              v-for="tch in session.teachers"
              :key="tch.teacher_id"
              class="flex items-center gap-3 rounded-leaf bg-card-2 px-3 py-2"
            >
              <span
                class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-bold text-primary"
              >
                {{ initials(tch.teacher_name) }}
              </span>
              <span class="min-w-0 flex-1 truncate text-sm text-ink">{{ tch.teacher_name }}</span>
              <Button
                icon="pi pi-times"
                text
                rounded
                size="small"
                severity="danger"
                v-tooltip.top="t('centre.classes.remove_teacher', { name: tch.teacher_name })"
                :aria-label="t('centre.classes.remove_teacher', { name: tch.teacher_name })"
                @click="confirmRemoveTeacher(tch.teacher_id, tch.teacher_name)"
              />
            </li>
          </ul>

          <div class="flex gap-2">
            <Select
              v-model="teacherToAdd"
              :options="availableTeachers"
              optionLabel="full_name"
              optionValue="id"
              :placeholder="t('centre.classes.add_teacher')"
              class="min-w-0 flex-1"
              filter
            />
            <Button
              icon="pi pi-plus"
              :aria-label="t('common.add')"
              :disabled="!teacherToAdd"
              :loading="busy"
              @click="handleAssignTeacher"
            />
          </div>
        </section>
      </div>
    </template>

    <!-- ══ Modifier ══ -->
    <Dialog
      v-model:visible="showEditDialog"
      :header="t('centre.classes.detail.edit_title')"
      modal
      :style="{ width: '95vw', maxWidth: '28rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleUpdate">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("centre.classes.name") }}</label>
          <InputText v-model="editForm.label" class="w-full" :placeholder="t('centre.classes.name_placeholder')" />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.classes.end_date") }}
            <span class="font-normal text-muted">{{ t("centre.form.optional") }}</span>
          </label>
          <DatePicker
            v-model="editForm.end_date"
            class="w-full"
            dateFormat="dd/mm/yy"
            showIcon
            :minDate="session ? new Date(session.start_date) : undefined"
          />
        </div>
        <p class="flex items-start gap-1.5 text-xs text-muted">
          <i class="pi pi-info-circle mt-0.5 text-[11px]" />
          {{ t("centre.classes.detail.edit_hint") }}
        </p>
        <Message v-if="editError" severity="error" :closable="false">{{ editError }}</Message>
      </form>
      <template #footer>
        <Button :label="t('common.cancel')" text @click="showEditDialog = false" />
        <Button :label="t('centre.classes.detail.save')" icon="pi pi-check" :loading="busy" @click="handleUpdate" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { StudentProgressResponse, StudentResponse, UserAdminResponse } from "#shared/api";
import type { NormalizedTrainingSession } from "~/stores/trainingSessions";

definePageMeta({ layout: "centre", watermark: "Klassen" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const trainingSessionsStore = useTrainingSessionsStore();
const confirm = useConfirm();
const toast = useToast();
const { accessBadge, hasAccess } = useAccessStatus();

const sessionId = route.params.id as string;

const loading = ref(true);
const busy = ref(false);
const errorMessage = ref<string | null>(null);
const actionError = ref<string | null>(null);

const session = ref<NormalizedTrainingSession | null>(null);
const teachers = ref<UserAdminResponse[]>([]);
const students = ref<StudentResponse[]>([]);
const progress = ref<StudentProgressResponse[]>([]);

const DAY = 24 * 60 * 60 * 1000;

// ── Utilitaires ──
function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function cefrOf(levelName: string) {
  return levelName.match(/\b([ABC][12])\b/)?.[1] ?? null;
}

function scoreTone(score: number | null) {
  if (score === null) return "text-muted";
  if (score >= 60) return "text-emerald-600";
  if (score >= 45) return "text-amber-600";
  return "text-red-600";
}

function isInactive(dateStr: string | null) {
  if (!dateStr) return true;
  return Date.now() - new Date(dateStr).getTime() > 7 * DAY;
}

function lastActivity(dateStr: string | null) {
  if (!dateStr) return t("centre.progress.never");
  const jours = Math.round((new Date(dateStr).getTime() - Date.now()) / DAY);
  return new Intl.RelativeTimeFormat(locale.value, { numeric: "auto" }).format(jours, "day");
}

// ── Statut ──
type Statut = "upcoming" | "ongoing" | "finished";

const status = computed<Statut>(() => {
  const s = session.value;
  if (!s) return "ongoing";
  const now = Date.now();
  if (s.end_date && new Date(s.end_date).getTime() < now) return "finished";
  if (new Date(s.start_date).getTime() > now) return "upcoming";
  return "ongoing";
});

const statusBadge = computed(() => {
  if (status.value === "finished")
    return { label: t("centre.classes.status.finished"), class: "bg-card-2 text-muted" };
  if (status.value === "upcoming")
    return { label: t("centre.classes.status.upcoming"), class: "bg-sky-500/10 text-sky-600" };
  return { label: t("centre.classes.status.ongoing"), class: "bg-emerald-500/10 text-emerald-600" };
});

const watermarkTone = computed(() =>
  status.value === "finished" ? "neutral" : status.value === "upcoming" ? "sky" : "emerald",
);

const period = computed(() => {
  if (!session.value) return "";
  const start = formatDate(session.value.start_date);
  return session.value.end_date
    ? t("centre.classes.period", { start, end: formatDate(session.value.end_date) })
    : t("centre.classes.period_open", { start });
});

// ── Élèves : inscription + accès + progression ──
const activeStudents = computed(() => {
  if (!session.value) return [];
  return session.value.students
    .filter((s) => !s.ended_at)
    .map((s) => {
      const account = students.value.find((x) => x.id === s.student_id);
      const prog = progress.value.find((p) => p.student_id === s.student_id);
      return {
        ...s,
        email: account?.email ?? "",
        access_expires_at: account?.access_expires_at ?? null,
        average_score: prog?.average_score ?? null,
        last_session_at: prog?.last_session_at ?? null,
      };
    })
    .sort((a, b) => a.student_name.localeCompare(b.student_name));
});

const endedStudents = computed(() =>
  (session.value?.students ?? [])
    .filter((s) => !!s.ended_at)
    .sort((a, b) => new Date(b.ended_at!).getTime() - new Date(a.ended_at!).getTime()),
);

const showEnded = ref(false);

// Score moyen de la classe : moyenne des élèves actifs qui ont déjà un score
const classAverage = computed(() => {
  const scores = activeStudents.value
    .map((s) => s.average_score)
    .filter((v): v is number => v !== null);
  return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
});

const stats = computed(() => {
  if (!session.value) return [];
  const noAccess = activeStudents.value.filter((s) => !hasAccess(s.access_expires_at)).length;
  return [
    { label: t("centre.classes.detail.stat_active"), value: String(activeStudents.value.length) },
    {
      label: t("centre.classes.detail.stat_no_access"),
      value: String(noAccess),
      tone: noAccess > 0 ? "text-red-600" : undefined,
    },
    {
      label: t("centre.classes.detail.stat_teachers"),
      value: String(session.value.teachers.length),
      tone: session.value.teachers.length ? undefined : "text-amber-600",
    },
    {
      label: t("centre.classes.detail.stat_average"),
      value: classAverage.value !== null ? `${Math.round(classAverage.value)}/100` : "-",
      tone: scoreTone(classAverage.value),
    },
  ];
});

const studentToAdd = ref("");
const teacherToAdd = ref("");

const availableStudents = computed(() => {
  const enrolled = new Set(activeStudents.value.map((s) => s.student_id));
  return students.value.filter((s) => s.is_active && !enrolled.has(s.id));
});

const availableTeachers = computed(() => {
  const assigned = new Set((session.value?.teachers ?? []).map((x) => x.teacher_id));
  return teachers.value.filter((x) => x.is_active && !assigned.has(x.id));
});

function goToActivation(studentId: string) {
  navigateTo({ path: localePath("/centre/etudiants"), query: { activer: studentId } });
}

// ── Chargement ──
async function refreshSession() {
  const result = authStore.isDirector
    ? await trainingSessionsStore.fetchByCenter()
    : await trainingSessionsStore.fetchByBranch();
  if (result.success) {
    session.value = trainingSessionsStore.sessions.find((s) => s.id === sessionId) ?? null;
  }
  return result;
}

async function loadData() {
  loading.value = true;
  const [sessionResult, teacherResult, studentResult, progressResult] = await Promise.all([
    refreshSession(),
    centerStaffStore.fetchTeachers(),
    authStore.isDirector ? centerStaffStore.fetchStudentsByCenter() : centerStaffStore.fetchStudentsByBranch(),
    centerStaffStore.fetchStudentProgress(),
  ]);

  errorMessage.value = sessionResult.success ? null : trainingSessionsStore.error || t("common.load_error");
  teachers.value = teacherResult.success ? (teacherResult.teachers ?? []) : [];
  students.value = studentResult.success ? (studentResult.students ?? []) : [];
  progress.value = progressResult.success ? (progressResult.progress ?? []) : [];
  loading.value = false;
}

// ── Actions enseignants / élèves ──
async function run(action: () => Promise<{ success: boolean; error?: string | null }>, fallbackKey: string) {
  busy.value = true;
  actionError.value = null;
  const result = await action();
  if (result.success) {
    await refreshSession();
  } else {
    actionError.value = result.error || t(fallbackKey);
  }
  busy.value = false;
  return result.success;
}

async function handleAssignTeacher() {
  if (!teacherToAdd.value) return;
  const ok = await run(
    () => trainingSessionsStore.assignTeacher(sessionId, { teacher_id: teacherToAdd.value }),
    "centre.classes.assign_error",
  );
  if (ok) teacherToAdd.value = "";
}

function confirmRemoveTeacher(teacherId: string, name: string) {
  confirm.require({
    header: t("centre.classes.remove_teacher", { name }),
    message: t("centre.classes.detail.remove_teacher_confirm", { name }),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: t("centre.classes.detail.remove"),
    rejectLabel: t("common.cancel"),
    acceptClass: "p-button-danger",
    accept: () => run(() => trainingSessionsStore.removeTeacher(sessionId, teacherId), "centre.classes.remove_error"),
  });
}

async function handleEnrollStudent() {
  if (!studentToAdd.value) return;
  const ok = await run(
    () => trainingSessionsStore.enrollStudent(sessionId, { student_id: studentToAdd.value }),
    "centre.classes.enroll_error",
  );
  if (ok) studentToAdd.value = "";
}

function confirmEndStudent(studentId: string, name: string) {
  confirm.require({
    header: t("centre.classes.end_student"),
    message: t("centre.classes.end_confirm", { name }),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: t("centre.classes.end_student"),
    rejectLabel: t("common.cancel"),
    acceptClass: "p-button-danger",
    accept: () =>
      run(() => trainingSessionsStore.endStudent(sessionId, studentId, { ended_at: null }), "centre.classes.end_error"),
  });
}

// ── Modifier / terminer la classe ──
const showEditDialog = ref(false);
const editError = ref<string | null>(null);
const editForm = ref<{ label: string; end_date: Date | null }>({ label: "", end_date: null });

function openEditDialog() {
  if (!session.value) return;
  editForm.value = {
    label: session.value.label ?? "",
    end_date: session.value.end_date ? new Date(session.value.end_date) : null,
  };
  editError.value = null;
  showEditDialog.value = true;
}

async function handleUpdate() {
  if (!session.value) return;
  const f = editForm.value;
  if (f.end_date && f.end_date <= new Date(session.value.start_date)) {
    editError.value = t("centre.classes.dates_error");
    return;
  }
  busy.value = true;
  editError.value = null;
  const result = await trainingSessionsStore.updateSession(sessionId, {
    label: f.label.trim() || null,
    end_date: f.end_date ? f.end_date.toISOString() : null,
  });
  if (result.success) {
    await refreshSession();
    showEditDialog.value = false;
    toast.add({ severity: "success", summary: t("centre.classes.detail.updated"), life: 3000 });
  } else {
    editError.value = result.error || t("centre.classes.detail.update_error");
  }
  busy.value = false;
}

function confirmEndClass() {
  confirm.require({
    header: t("centre.classes.detail.end_class"),
    message: t("centre.classes.detail.end_class_confirm"),
    icon: "pi pi-exclamation-triangle",
    acceptLabel: t("centre.classes.detail.end_class"),
    rejectLabel: t("common.cancel"),
    acceptClass: "p-button-danger",
    accept: () =>
      run(
        () => trainingSessionsStore.updateSession(sessionId, { end_date: new Date().toISOString() }),
        "centre.classes.detail.update_error",
      ),
  });
}

onMounted(loadData);
</script>