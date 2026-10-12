<!-- pages/enseignant/sessions.vue -->
<template>
  <div class="space-y-5">
    <p v-if="!loading && !errorMessage" class="text-sm text-muted">
      {{ t("teacher.classes.count", { n: sessions.length }, sessions.length) }}
    </p>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-4">
      <div v-for="n in 2" :key="n" class="h-40 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="sessions.length === 0"
      class="rounded-card border border-dashed border-line bg-card p-10 text-center"
    >
      <i class="pi pi-users mb-3 text-3xl text-faint" />
      <p class="text-sm text-muted">{{ t("teacher.classes.empty") }}</p>
    </div>

    <template v-else>
      <!-- ── Classes en cours et à venir ── -->
      <article
        v-for="session in activeSessions"
        :key="session.id"
        class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <header class="flex flex-col gap-3 border-b border-line px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
          <div class="min-w-0 flex-1">
            <!-- Titre + statut -->
            <div class="flex items-start justify-between gap-3">
              <h3 class="min-w-0 font-semibold text-ink">
                <span class="block truncate">{{ session.level_name }}</span>
                <span v-if="session.label" class="block truncate text-sm font-normal text-muted">
                  {{ session.label }}
                </span>
              </h3>
              <span
                class="shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold sm:hidden"
                :class="statusBadge(session).class"
              >
                {{ statusBadge(session).label }}
              </span>
            </div>

            <!-- Période + élèves -->
            <div class="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
              <span class="flex items-center gap-1.5">
                <i class="pi pi-calendar text-[11px]" />
                {{ period(session) }}
              </span>
              <span class="flex items-center gap-1.5">
                <i class="pi pi-users text-[11px]" />
                {{ t("teacher.classes.active_students", { n: activeStudents(session).length }, activeStudents(session).length) }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span
              class="hidden shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold sm:inline-flex"
              :class="statusBadge(session).class"
            >
              {{ statusBadge(session).label }}
            </span>
            <Button
              :label="t('teacher.classes.give_assignment')"
              icon="pi pi-file-edit"
              size="small"
              outlined
              class="w-full sm:w-auto"
              @click="navigateTo({ path: localePath('/enseignant/devoirs/nouveau'), query: { class_id: session.id } })"
            />
          </div>
        </header>

        <p v-if="activeStudents(session).length === 0" class="px-5 py-4 text-sm text-muted">
          {{ t("teacher.classes.no_active") }}
        </p>

        <ul v-else class="divide-y divide-line">
          <li
            v-for="s in activeStudents(session)"
            :key="s.student_id"
            class="flex items-center gap-3 px-4 py-2.5 sm:px-5"
          >
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-xs font-bold text-primary"
            >
              {{ initials(s.student_name) }}
            </span>
            <span class="min-w-0 flex-1 truncate text-sm font-medium text-ink">{{ s.student_name }}</span>

            <div class="flex shrink-0 items-center gap-1 sm:gap-2">
              <!-- Mobile : icônes seules -->
              <Button
                icon="pi pi-chart-line"
                text
                rounded
                size="small"
                class="sm:hidden!"
                v-tooltip.top="t('teacher.classes.detail')"
                :aria-label="t('teacher.classes.detail')"
                @click="goToDetail(s.student_id)"
              />
              <Button
                icon="pi pi-microphone"
                rounded
                size="small"
                class="sm:hidden!"
                v-tooltip.top="t('teacher.classes.launch_live')"
                :aria-label="t('teacher.classes.launch_live')"
                @click="goToLaunchLive(s.student_id)"
              />

              <!-- À partir de sm : avec libellés -->
              <Button
                :label="t('teacher.classes.detail')"
                icon="pi pi-chart-line"
                text
                size="small"
                class="hidden! sm:inline-flex!"
                @click="goToDetail(s.student_id)"
              />
              <Button
                :label="t('teacher.classes.launch_live')"
                icon="pi pi-microphone"
                size="small"
                class="hidden! sm:inline-flex!"
                @click="goToLaunchLive(s.student_id)"
              />
            </div>
          </li>
        </ul>
      </article>

      <!-- ── Classes terminées (repliées) ── -->
      <section v-if="finishedSessions.length" class="space-y-3">
        <button
          type="button"
          class="flex items-center gap-2 text-sm font-medium text-muted transition-colors hover:text-ink"
          :aria-expanded="showFinished"
          @click="showFinished = !showFinished"
        >
          <i class="pi pi-chevron-right text-xs transition-transform" :class="{ 'rotate-90': showFinished }" />
          {{ t("teacher.classes.finished_toggle", { n: finishedSessions.length }, finishedSessions.length) }}
        </button>

        <template v-if="showFinished">
          <div
            v-for="session in finishedSessions"
            :key="session.id"
            class="flex items-center justify-between gap-3 rounded-card border border-line bg-card px-4 py-4 opacity-75 sm:px-5"
          >
            <div class="min-w-0">
              <p class="truncate font-medium text-ink">{{ session.level_name }}</p>
              <p v-if="session.label" class="truncate text-sm text-muted">{{ session.label }}</p>
              <p class="mt-0.5 text-xs text-muted">{{ period(session) }}</p>
            </div>
            <span class="shrink-0 rounded-full bg-card-2 px-2.5 py-1 text-xs font-semibold text-muted">
              {{ t("centre.classes.status.finished") }}
            </span>
          </div>
        </template>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { NormalizedTrainingSession } from "~/stores/trainingSessions";

definePageMeta({ layout: "enseignant" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const teacherPortalStore = useTeacherPortalStore();

const loading = ref(true);
const errorMessage = ref<string | null>(null);
const showFinished = ref(false);

const sessions = computed(() => teacherPortalStore.mySessions);

type Statut = "upcoming" | "ongoing" | "finished";

function statusOf(session: NormalizedTrainingSession): Statut {
  const now = Date.now();
  if (session.end_date && new Date(session.end_date).getTime() < now)
    return "finished";
  if (new Date(session.start_date).getTime() > now) return "upcoming";
  return "ongoing";
}

function statusBadge(session: NormalizedTrainingSession) {
  return statusOf(session) === "upcoming"
    ? {
        label: t("centre.classes.status.upcoming"),
        class: "bg-sky-500/10 text-sky-600",
      }
    : {
        label: t("centre.classes.status.ongoing"),
        class: "bg-emerald-500/10 text-emerald-600",
      };
}

// En cours d'abord, puis à venir ; dans chaque groupe, la plus récente en premier
const activeSessions = computed(() =>
  sessions.value
    .filter((s) => statusOf(s) !== "finished")
    .sort(
      (a, b) =>
        (statusOf(a) === "ongoing" ? 0 : 1) -
          (statusOf(b) === "ongoing" ? 0 : 1) ||
        new Date(b.start_date).getTime() - new Date(a.start_date).getTime(),
    ),
);

const finishedSessions = computed(() =>
  sessions.value
    .filter((s) => statusOf(s) === "finished")
    .sort(
      (a, b) =>
        new Date(b.end_date!).getTime() - new Date(a.end_date!).getTime(),
    ),
);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function period(session: NormalizedTrainingSession) {
  const start = formatDate(session.start_date);
  return session.end_date
    ? t("centre.classes.period", { start, end: formatDate(session.end_date) })
    : t("centre.classes.period_open", { start });
}

function activeStudents(session: NormalizedTrainingSession) {
  return session.students.filter((s) => !s.ended_at);
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

function goToDetail(studentId: string) {
  navigateTo(localePath(`/enseignant/etudiants/${studentId}`));
}

function goToLaunchLive(studentId: string) {
  navigateTo({
    path: localePath("/enseignant/live/nouveau"),
    query: { student_id: studentId },
  });
}

async function loadData() {
  loading.value = true;
  errorMessage.value = null;
  const result = await teacherPortalStore.fetchMySessions();
  if (!result.success) {
    errorMessage.value = result.error || t("common.load_error");
  }
  loading.value = false;
}

onMounted(loadData);
</script>
