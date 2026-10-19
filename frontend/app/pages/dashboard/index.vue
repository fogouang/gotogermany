<!-- pages/dashboard/index.vue -->
<template>
  <div class="space-y-5 pb-10">
    <!-- ── Accueil ── -->
    <div>
      <p class="text-xl font-bold text-ink sm:text-2xl">
        {{ t("dashboard.greeting") }}, {{ firstName }}
      </p>
      <p class="mt-0.5 text-sm text-muted">{{ t("dashboard.subtitle") }}</p>
    </div>

    <!-- ── Bandeaux d'état ── -->
    <div
      v-for="banner in banners"
      :key="banner.key"
      class="flex flex-col gap-3 rounded-card border p-4 sm:flex-row sm:items-center sm:p-5"
      :class="banner.tone"
    >
      <span
        class="flex size-10 shrink-0 items-center justify-center rounded-full bg-card"
      >
        <i :class="banner.icon" />
      </span>
      <div class="min-w-0 flex-1">
        <p class="font-semibold text-ink">{{ banner.title }}</p>
        <p class="text-sm text-muted">{{ banner.text }}</p>
      </div>
      <Button
        v-if="banner.action"
        :label="banner.action.label"
        size="small"
        class="shrink-0"
        @click="navigateTo(localePath(banner.action.to))"
      />
    </div>

    <div class="grid items-start gap-5 lg:grid-cols-3">
      <!-- ══════════ Colonne principale ══════════ -->
      <div class="space-y-5 lg:col-span-2">
        <!-- Reprendre : session en cours sur un autre examen que l'examen actif -->
        <button
          v-if="
            inProgress &&
            !isStartDeutsch &&
            inProgress.exam_id !== myExam?.exam.id
          "
          type="button"
          class="group flex w-full items-center gap-4 rounded-card border border-primary/30 bg-primary/10 p-5 text-left transition-colors hover:border-primary"
          @click="
            navigateTo(localePath(`/dashboard/examens/${inProgress.exam_slug}`))
          "
        >
          <span
            class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary text-white"
          >
            <i class="pi pi-play" />
          </span>
          <span class="min-w-0 flex-1">
            <span
              class="block text-xs font-semibold uppercase tracking-wide text-primary"
            >
              {{ t("dashboard.resume_title") }}
            </span>
            <span class="block truncate font-semibold text-ink">{{
              inProgress.exam_name
            }}</span>
            <span class="block text-xs text-muted">
              {{ t("dashboard.subject") }} {{ inProgress.subject_number }} ·
              {{ formatDateTime(inProgress.started_at) }}
            </span>
          </span>
          <span
            class="hidden items-center gap-1 text-sm font-semibold text-primary sm:flex"
          >
            {{ t("dashboard.resume_btn") }}
            <i
              class="pi pi-arrow-right text-xs transition-transform group-hover:translate-x-1"
            />
          </span>
        </button>

        <!-- ══ Parcours Start Deutsch ══ -->
        <section
          v-if="isStartDeutsch"
          class="rounded-card border border-primary/30 bg-primary/10 p-5 sm:p-6"
        >
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
            <span
              class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary text-white"
            >
              <i class="pi pi-graduation-cap" />
            </span>
            <div class="min-w-0 flex-1">
              <h2 class="font-semibold text-ink">
                {{ t("dashboard.track.start_title") }}
              </h2>
              <p class="mt-0.5 text-sm text-muted">
                {{ t("dashboard.track.start_text") }}
              </p>
            </div>
            <Button
              :label="t('dashboard.track.start_cta')"
              icon="pi pi-arrow-right"
              icon-pos="right"
              class="shrink-0"
              @click="navigateTo(localePath('/dashboard/start-deutsch'))"
            />
          </div>
          <button
            v-if="canSwitchTrack"
            type="button"
            class="mt-4 text-xs font-medium text-muted hover:text-primary hover:underline"
            @click="navigateTo(localePath('/dashboard/bienvenue?step=level'))"
          >
            {{ t("dashboard.track.switch_to_exam") }}
          </button>
        </section>

        <!-- ══ Parcours examen ══ -->
        <template v-else>
          <!-- Mon examen -->
          <section
            v-if="myExam"
            class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
          >
            <div class="p-5 sm:p-6">
              <div class="flex items-start gap-4">
                <span
                  class="flex size-14 shrink-0 items-center justify-center rounded-leaf text-base font-extrabold"
                  :class="info(myExam.exam.provider).badge"
                >
                  {{ myExam.level.cefr_code }}
                </span>
                <div class="min-w-0 flex-1">
                  <p
                    class="text-xs font-semibold uppercase tracking-wide text-primary"
                  >
                    {{ t("dashboard.my_exam.eyebrow") }}
                  </p>
                  <h2 class="truncate text-lg font-bold text-ink">
                    {{ myExam.exam.name }}
                  </h2>
                  <p class="text-xs text-muted">
                    {{
                      t(
                        "dashboard.subjects_count",
                        { n: totalSubjects },
                        totalSubjects,
                      )
                    }}
                  </p>
                </div>
                <span
                  class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="accessBadge(myExam.level).class"
                >
                  {{ accessBadge(myExam.level).label }}
                </span>
              </div>

              <template v-if="totalSubjects > 0">
                <!-- Sujets terminés -->
                <div class="mt-5">
                  <div class="mb-1.5 flex items-center justify-between text-xs">
                    <span class="text-muted">
                      {{
                        t("dashboard.my_exam.progress", {
                          done: doneCount,
                          total: totalSubjects,
                        })
                      }}
                    </span>
                    <span class="font-semibold tabular-nums text-ink"
                      >{{ progressPct }}%</span
                    >
                  </div>
                  <div class="h-2 overflow-hidden rounded-full bg-card-2">
                    <div
                      class="h-full rounded-full bg-primary transition-[width] duration-500"
                      :style="{ width: `${progressPct}%` }"
                    />
                  </div>
                </div>

                <!-- Avancement par module : meilleur score obtenu dans chaque module -->
                <div v-if="moduleProgress.length" class="mt-5 space-y-2.5">
                  <p
                    class="text-xs font-semibold uppercase tracking-wide text-faint"
                  >
                    {{ t("dashboard.my_exam.modules_title") }}
                  </p>
                  <div
                    v-for="m in moduleProgress"
                    :key="m.slug"
                    class="flex items-center gap-3"
                  >
                    <span class="w-32 shrink-0 truncate text-sm text-ink">{{
                      m.label
                    }}</span>
                    <div
                      class="h-1.5 flex-1 overflow-hidden rounded-full bg-card-2"
                    >
                      <div
                        v-if="m.pct !== null"
                        class="h-full rounded-full transition-[width] duration-500"
                        :class="m.pct >= 60 ? 'bg-emerald-500' : 'bg-amber-500'"
                        :style="{ width: `${m.pct}%` }"
                      />
                    </div>
                    <span
                      class="w-24 shrink-0 text-right text-xs tabular-nums"
                      :class="m.pct === null ? 'text-amber-600' : 'text-muted'"
                    >
                      {{
                        m.pct === null
                          ? t("dashboard.my_exam.module_pending")
                          : `${m.pct} %`
                      }}
                    </span>
                  </div>
                </div>

                <!-- Chiffres -->
                <dl class="mt-5 grid grid-cols-3 gap-2 text-center">
                  <div class="rounded-leaf bg-card-2 px-2 py-3">
                    <dd class="text-lg font-bold tabular-nums text-ink">
                      {{ bestScore !== null ? `${bestScore} %` : "-" }}
                    </dd>
                    <dt class="text-[11px] leading-tight text-muted">
                      {{ t("dashboard.my_exam.best_score") }}
                    </dt>
                  </div>
                  <div class="rounded-leaf bg-card-2 px-2 py-3">
                    <dd class="text-lg font-bold tabular-nums text-emerald-600">
                      {{ examPassed }}/{{ examCompleted.length }}
                    </dd>
                    <dt class="text-[11px] leading-tight text-muted">
                      {{ t("dashboard.my_exam.passed") }}
                    </dt>
                  </div>
                  <div class="rounded-leaf bg-card-2 px-2 py-3">
                    <dd class="truncate text-sm font-bold leading-7 text-ink">
                      {{ lastActivity ? formatShort(lastActivity) : "-" }}
                    </dd>
                    <dt class="text-[11px] leading-tight text-muted">
                      {{ t("dashboard.my_exam.last_activity") }}
                    </dt>
                  </div>
                </dl>

                <!-- Une seule action -->
                <Button
                  v-if="primaryAction"
                  :label="primaryAction.label"
                  :icon="primaryAction.icon"
                  class="mt-5 w-full sm:w-auto"
                  @click="navigateTo(localePath(primaryAction.to))"
                />
              </template>

              <p
                v-else
                class="mt-5 rounded-leaf bg-card-2 px-4 py-3 text-sm text-muted"
              >
                {{ t("dashboard_exams.coming_soon") }}
              </p>
            </div>
          </section>

          <!-- Autres examens : repliés si un examen est actif, sinon étape de choix -->
          <section
            class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
          >
            <button
              v-if="myExam"
              type="button"
              class="flex w-full items-center justify-between gap-3 px-5 py-4 text-left transition-colors hover:bg-card-2/60"
              :aria-expanded="showOthers"
              @click="showOthers = !showOthers"
            >
              <span class="font-semibold text-ink">
                {{ t("dashboard.my_exam.explore", { n: otherRows.length }) }}
              </span>
              <i
                class="pi pi-chevron-down text-xs text-faint transition-transform"
                :class="{ 'rotate-180': showOthers }"
              />
            </button>
            <header
              v-else
              class="flex items-center justify-between gap-3 border-b border-line px-5 py-4"
            >
              <div class="min-w-0">
                <h2 class="font-semibold text-ink">
                  {{ t("dashboard.my_exam.choose_title") }}
                </h2>
                <p class="mt-0.5 text-xs text-muted">
                  {{ t("dashboard.my_exam.choose_text") }}
                </p>
              </div>
              <NuxtLink
                :to="localePath('/dashboard/examens/catalogue')"
                class="shrink-0 text-sm font-medium text-primary hover:underline"
              >
                {{ t("dashboard.see_all") }}
              </NuxtLink>
            </header>

            <div
              v-show="!myExam || showOthers"
              :class="{ 'border-t border-line': myExam }"
            >
              <div
                v-if="examsStore.loading && levelRows.length === 0"
                class="space-y-2 p-5"
              >
                <div
                  v-for="n in 3"
                  :key="n"
                  class="h-14 animate-pulse rounded-leaf bg-card-2"
                />
              </div>

              <div
                v-else-if="otherRows.length === 0"
                class="flex flex-col items-center gap-2 px-6 py-10 text-center"
              >
                <span
                  class="flex size-12 items-center justify-center rounded-full bg-card-2 text-muted"
                >
                  <i class="pi pi-inbox" />
                </span>
                <p class="text-sm text-muted">{{ t("dashboard.no_exams") }}</p>
              </div>

              <ul v-else class="divide-y divide-line">
                <li v-for="row in otherRows" :key="row.level.id">
                  <button
                    type="button"
                    class="group flex w-full items-center gap-4 px-5 py-3.5 text-left transition-colors hover:bg-card-2/60"
                    @click="openLevel(row)"
                  >
                    <span
                      class="flex size-10 shrink-0 items-center justify-center rounded-leaf text-xs font-bold"
                      :class="info(row.exam.provider).badge"
                    >
                      {{ row.level.cefr_code }}
                    </span>
                    <span class="min-w-0 flex-1">
                      <span class="block truncate font-medium text-ink">{{
                        row.exam.name
                      }}</span>
                      <span class="block text-xs text-muted">
                        {{
                          t(
                            "dashboard.subjects_count",
                            { n: row.level.subject_count ?? 0 },
                            row.level.subject_count ?? 0,
                          )
                        }}
                      </span>
                    </span>
                    <span
                      class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                      :class="accessBadge(row.level).class"
                    >
                      {{ accessBadge(row.level).label }}
                    </span>
                    <span
                      v-if="
                        row.level.subject_count &&
                        !hasOpenAccess(row.level) &&
                        !isCenterStudent
                      "
                      class="hidden shrink-0 text-xs font-semibold text-primary sm:inline"
                    >
                      {{ t("dashboard.unlock") }}
                    </span>
                    <i
                      class="pi pi-chevron-right shrink-0 text-xs text-faint transition-transform group-hover:translate-x-0.5"
                    />
                  </button>
                </li>
              </ul>

              <NuxtLink
                v-if="myExam"
                :to="localePath('/dashboard/examens/catalogue')"
                class="block border-t border-line px-5 py-3 text-center text-sm font-medium text-primary hover:underline"
              >
                {{ t("dashboard.see_all") }}
              </NuxtLink>
            </div>
          </section>
        </template>

        <!-- Activité récente -->
        <section
          class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
        >
          <header
            class="flex items-center justify-between gap-3 border-b border-line px-5 py-4"
          >
            <h2 class="font-semibold text-ink">
              {{ t("dashboard.recent_sessions") }}
            </h2>
            <NuxtLink
              v-if="sessions.length"
              :to="localePath('/dashboard/resultats')"
              class="text-sm font-medium text-primary hover:underline"
            >
              {{ t("dashboard.see_all") }}
            </NuxtLink>
          </header>

          <div v-if="sessionsLoading" class="space-y-2 p-5">
            <div
              v-for="n in 3"
              :key="n"
              class="h-12 animate-pulse rounded-leaf bg-card-2"
            />
          </div>

          <div
            v-else-if="sessions.length === 0"
            class="flex flex-col items-center gap-3 px-6 py-10 text-center"
          >
            <span
              class="flex size-12 items-center justify-center rounded-full bg-card-2 text-muted"
            >
              <i class="pi pi-history" />
            </span>
            <p class="text-sm text-muted">{{ t("dashboard.no_sessions") }}</p>
            <Button
              :label="t('dashboard.start')"
              size="small"
              outlined
              @click="
                navigateTo(
                  localePath(
                    isStartDeutsch
                      ? '/dashboard/start-deutsch'
                      : '/dashboard/examens',
                  ),
                )
              "
            />
          </div>

          <ul v-else class="divide-y divide-line">
            <li
              v-for="s in sessions.slice(0, 5)"
              :key="s.id"
              class="flex items-center gap-3 px-5 py-3.5"
            >
              <span
                class="flex size-9 shrink-0 items-center justify-center rounded-leaf"
                :class="sessionStyle(s).bubble"
              >
                <i class="pi text-xs" :class="sessionStyle(s).icon" />
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-ink">
                  {{ s.exam_name }}
                </p>
                <p class="text-xs text-muted">
                  {{ t("dashboard.subject") }} {{ s.subject_number }} ·
                  {{ formatDateTime(s.started_at) }}
                </p>
              </div>
              <span
                class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="sessionStyle(s).badge"
              >
                {{ sessionLabel(s) }}
              </span>
            </li>
          </ul>
        </section>
      </div>

      <!-- ══════════ Colonne latérale ══════════ -->
      <aside class="space-y-5 lg:sticky lg:top-0">
        <!-- Progression globale -->
        <section
          class="rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <h2 class="mb-4 font-semibold text-ink">
            {{ t("dashboard.progress_title") }}
          </h2>
          <div v-if="completed.length === 0" class="text-sm text-muted">
            {{ t("dashboard.no_progress") }}
          </div>
          <div v-else class="grid grid-cols-3 gap-2 text-center">
            <div class="rounded-leaf bg-card-2 px-2 py-3">
              <p class="text-lg font-bold text-ink">{{ completed.length }}</p>
              <p class="text-[11px] leading-tight text-muted">
                {{ t("dashboard.sessions_done") }}
              </p>
            </div>
            <div class="rounded-leaf bg-card-2 px-2 py-3">
              <p class="text-lg font-bold text-emerald-600">
                {{ passedCount }}
              </p>
              <p class="text-[11px] leading-tight text-muted">
                {{ t("dashboard.passed_count") }}
              </p>
            </div>
            <div class="rounded-leaf bg-card-2 px-2 py-3">
              <p class="text-lg font-bold text-ink">
                {{ averageScore ?? "-" }}
              </p>
              <p class="text-[11px] leading-tight text-muted">
                {{ t("dashboard.avg_score") }}
              </p>
            </div>
          </div>
        </section>

        <!-- Communauté WhatsApp -->
        <section
          v-if="showCommunity"
          class="relative overflow-hidden rounded-card border border-emerald-500/30 bg-emerald-500/10 p-5"
        >
          <button
            type="button"
            class="absolute right-3 top-3 flex size-7 items-center justify-center rounded-full text-muted hover:bg-card hover:text-ink"
            :aria-label="t('toast.close')"
            @click="hideCommunity"
          >
            <i class="pi pi-times text-xs" />
          </button>
          <span
            class="mb-3 flex size-10 items-center justify-center rounded-full bg-emerald-600 text-white"
          >
            <i class="pi pi-whatsapp" />
          </span>
          <h2 class="font-semibold text-ink">
            {{ t("dashboard.community_title") }}
          </h2>
          <p class="mt-1 text-sm text-muted">
            {{ t("dashboard.community_text") }}
          </p>
          <a
            :href="SITE.whatsappCommunity"
            target="_blank"
            rel="noopener"
            class="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-leaf bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
            @click="hideCommunity"
          >
            <i class="pi pi-whatsapp" />
            {{ t("dashboard.community_btn") }}
          </a>
        </section>

        <!-- Devoirs (élève de centre) -->
        <section
          v-if="isCenterStudent"
          class="rounded-card border border-line bg-card p-5 shadow-soft"
        >
          <div class="mb-3 flex items-center gap-3">
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-violet-500/10 text-violet-600"
            >
              <i class="pi pi-book" />
            </span>
            <div class="min-w-0">
              <h2 class="font-semibold text-ink">
                {{ t("dashboard.assignments_title") }}
              </h2>
              <p class="text-xs text-muted">
                {{
                  t(
                    "dashboard.assignments_todo",
                    { n: todoAssignments.length },
                    todoAssignments.length,
                  )
                }}
              </p>
            </div>
          </div>
          <p
            v-if="lateCount > 0"
            class="mb-2 text-xs font-semibold text-red-600"
          >
            {{ t("dashboard.assignments_late", { n: lateCount }, lateCount) }}
          </p>
          <p v-if="nextDue" class="mb-3 text-xs text-muted">
            {{ t("dashboard.next_due", { date: formatDate(nextDue) }) }}
          </p>
          <Button
            :label="t('dashboard.see_assignments')"
            size="small"
            outlined
            class="w-full"
            @click="navigateTo(localePath('/dashboard/devoirs'))"
          />
        </section>

        <!-- Raccourcis -->
        <section
          class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
        >
          <ul class="divide-y divide-line">
            <li v-for="a in shortcuts" :key="a.to">
              <NuxtLink
                :to="localePath(a.to)"
                class="group flex items-center gap-3 px-4 py-3 transition-colors hover:bg-card-2/60"
              >
                <span
                  class="flex size-9 shrink-0 items-center justify-center rounded-leaf"
                  :class="a.iconClass"
                >
                  <i :class="a.icon" class="text-sm" />
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block truncate text-sm font-medium text-ink">{{
                    a.label
                  }}</span>
                  <span class="block truncate text-xs text-muted">{{
                    a.sub
                  }}</span>
                </span>
                <i
                  class="pi pi-arrow-right text-xs text-faint transition-transform group-hover:translate-x-1"
                />
              </NuxtLink>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AssignmentsService } from "#shared/api";
import { SITE } from "~/config/site";
import type { LearningTrack } from "~/composables/useLearningTrack";
import type {
  LevelAccessResponse,
  SessionListResponse,
  StudentAssignmentResponse,
  UserMeResponse,
} from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Übersicht" });

const { t, locale } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const examsStore = useExamsStore();
const sessionStore = useSessionStore();
const { visibleCatalog, isCenterStudent } = useVisibleCatalog();
const { needsOnboarding, activeOption } = useActiveLevel();
const { info } = useProviders();
const { track, isStartDeutsch, canSwitchTrack, setTrack } = useLearningTrack();
const activeLevelId = computed(() => activeOption.value?.level.id ?? null);

const me = computed(() => authStore.user as UserMeResponse | null);
const firstName = computed(() => (authStore.userName || "").split(" ")[0]);

// ── Format ──
const intlLocale = computed(
  () =>
    (({ fr: "fr-FR", de: "de-DE" }) as Record<string, string>)[locale.value] ??
    "en-GB",
);
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(intlLocale.value, {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
const formatShort = (d: string) =>
  new Date(d).toLocaleDateString(intlLocale.value, {
    day: "2-digit",
    month: "short",
  });
const formatDateTime = (d: string) =>
  new Date(d).toLocaleDateString(intlLocale.value, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

// ── Niveaux ──
type LevelRow = {
  exam: { name: string; slug: string; provider: string };
  level: LevelAccessResponse;
};

const levelRows = computed<LevelRow[]>(() => {
  const rows = visibleCatalog.value.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({ exam, level })),
  );
  // Niveaux avec sujets d'abord, puis accès ouverts, puis ordre d'affichage
  return rows.sort(
    (a, b) =>
      Number((b.level.subject_count ?? 0) > 0) -
        Number((a.level.subject_count ?? 0) > 0) ||
      Number(b.level.has_access) - Number(a.level.has_access) ||
      a.level.display_order - b.level.display_order,
  );
});

const hasOpenAccess = (level: LevelAccessResponse) =>
  level.has_access || level.is_free || isCenterStudent.value;

const accessBadge = (level: LevelAccessResponse) => {
  if (!level.subject_count)
    return {
      label: t("dashboard_exams.coming_soon"),
      class: "bg-card-2 text-muted",
    };
  if (level.is_free)
    return {
      label: t("dashboard.level_free"),
      class: "bg-emerald-500/10 text-emerald-600",
    };
  if (hasOpenAccess(level))
    return {
      label: t("dashboard.level_active"),
      class: "bg-emerald-500/10 text-emerald-600",
    };
  return {
    label: t("dashboard.level_preview"),
    class: "bg-amber-500/15 text-amber-600",
  };
};

const openLevel = (row: LevelRow) => {
  if (!row.level.subject_count) return;
  if (hasOpenAccess(row.level)) {
    navigateTo(localePath(`/dashboard/examens/${row.exam.slug}`));
  } else {
    navigateTo(localePath(`/dashboard/paiement?level_id=${row.level.id}`));
  }
};

// ── Bandeaux ──
const EXPIRY_WARNING_DAYS = 7;

const banners = computed(() => {
  const list: {
    key: string;
    tone: string;
    icon: string;
    title: string;
    text: string;
    action?: { label: string; to: string };
  }[] = [];

  if (isCenterStudent.value && !authStore.targetLevelId) {
    list.push({
      key: "no_level",
      tone: "border-amber-500/30 bg-amber-500/10",
      icon: "pi pi-info-circle text-amber-600",
      title: t("dashboard.status.no_level_title"),
      text: t("dashboard.status.no_level_text"),
    });
  } else if (
    isCenterStudent.value &&
    levelRows.value.length > 0 &&
    !levelRows.value.some((r) => r.level.has_access)
  ) {
    list.push({
      key: "not_activated",
      tone: "border-amber-500/30 bg-amber-500/10",
      icon: "pi pi-lock text-amber-600",
      title: t("dashboard.status.not_activated_title"),
      text: t("dashboard.status.not_activated_text"),
    });
  }

  const expires = me.value?.access_expires_at;
  if (expires) {
    const daysLeft = Math.ceil(
      (new Date(expires).getTime() - Date.now()) / 86_400_000,
    );
    if (daysLeft >= 0 && daysLeft <= EXPIRY_WARNING_DAYS) {
      list.push({
        key: "expiring",
        tone: "border-red-500/30 bg-red-500/10",
        icon: "pi pi-clock text-red-600",
        title: t("dashboard.status.expiring_title"),
        text: t("dashboard.status.expiring_text", {
          date: formatDate(expires),
        }),
        action: isCenterStudent.value
          ? undefined
          : { label: t("dashboard.status.renew"), to: "/dashboard/examens" },
      });
    }
  }
  return list;
});

// ── Sessions ──
const sessionsLoading = ref(true);
const sessions = ref<SessionListResponse[]>([]);

// Seule une session réellement en cours se reprend (pas une session abandonnée ou en correction)
const inProgress = computed(
  () => sessions.value.find((s) => s.status === "IN_PROGRESS") ?? null,
);
const completed = computed(() =>
  sessions.value.filter((s) => s.status === "COMPLETED"),
);
const passedCount = computed(
  () => completed.value.filter((s) => s.passed).length,
);
const averageScore = computed(() => {
  const scored = completed.value.filter((s) => s.score != null);
  if (!scored.length) return null;
  return Math.round(
    scored.reduce((sum, s) => sum + (s.score ?? 0), 0) / scored.length,
  );
});

const sessionStyle = (s: SessionListResponse) =>
  s.status !== "COMPLETED"
    ? {
        bubble: "bg-amber-500/15",
        icon: "pi-clock text-amber-600",
        badge: "bg-amber-500/15 text-amber-600",
      }
    : s.passed
      ? {
          bubble: "bg-emerald-500/10",
          icon: "pi-check text-emerald-600",
          badge: "bg-emerald-500/10 text-emerald-600",
        }
      : {
          bubble: "bg-red-500/10",
          icon: "pi-times text-red-600",
          badge: "bg-red-500/10 text-red-600",
        };

const sessionLabel = (s: SessionListResponse) => {
  if (s.status !== "COMPLETED") return t("dashboard.in_progress");
  const verdict = s.passed ? t("dashboard.passed") : t("dashboard.failed");
  return s.score != null ? `${verdict} · ${Math.round(s.score)}` : verdict;
};

// ── Mon examen ──
const myExam = computed(() => activeOption.value);
const showOthers = ref(false);

// L'examen actif a sa carte : il n'apparaît pas dans la liste des autres
const otherRows = computed(() =>
  levelRows.value.filter((r) => r.level.id !== activeLevelId.value),
);

const totalSubjects = computed(() => myExam.value?.level.subject_count ?? 0);

// Sessions de l'examen actif, de la plus récente à la plus ancienne
const examSessions = computed(() =>
  myExam.value
    ? sessions.value.filter((s) => s.exam_id === myExam.value!.exam.id)
    : [],
);
const examCompleted = computed(() =>
  examSessions.value.filter((s) => s.status === "COMPLETED"),
);
const examPassed = computed(
  () => examCompleted.value.filter((s) => s.passed).length,
);
const examInProgress = computed(
  () => examSessions.value.find((s) => s.status === "IN_PROGRESS") ?? null,
);

// Un sujet compte comme terminé seulement en examen complet (pas en mode module seul)
const doneSubjects = computed(
  () =>
    new Set(
      examCompleted.value
        .filter((s) => !s.module_slugs?.length)
        .map((s) => s.subject_number),
    ),
);
const doneCount = computed(() =>
  Math.min(doneSubjects.value.size, totalSubjects.value),
);

const progressPct = computed(() =>
  totalSubjects.value
    ? Math.round((doneCount.value / totalSubjects.value) * 100)
    : 0,
);

const bestScore = computed(() => {
  const scores = examCompleted.value
    .map((s) => s.score)
    .filter((v): v is number => v != null);
  return scores.length ? Math.round(Math.max(...scores)) : null;
});

const lastActivity = computed(() => examSessions.value[0]?.started_at ?? null);

// ── Avancement par module ──
// Meilleur score de chaque module, toutes sessions de l'examen confondues
// (examen complet ou module seul). null = en attente de correction.
const MODULE_LABELS: Record<string, string> = {
  lesen: "Lesen",
  hoeren: "Hören",
  horen: "Hören",
  hören: "Hören",
  schreiben: "Schreiben",
  sprechen: "Sprechen",
  sprachbausteine: "Sprachbausteine",
};

const moduleLabel = (slug: string) =>
  MODULE_LABELS[slug.toLowerCase()] ??
  slug.charAt(0).toUpperCase() + slug.slice(1).replace(/_/g, " ");

const breakdownOf = (s: SessionListResponse) =>
  ((
    s as SessionListResponse & {
      score_breakdown?: Record<string, unknown> | null;
    }
  ).score_breakdown ?? {}) as Record<string, unknown>;

const moduleProgress = computed(() => {
  const best = new Map<string, number | null>();
  for (const s of examSessions.value) {
    if (s.status !== "COMPLETED" && s.status !== "PENDING_REVIEW") continue;
    for (const [slug, value] of Object.entries(breakdownOf(s))) {
      const prev = best.get(slug);
      if (typeof value === "number") {
        best.set(slug, prev == null ? value : Math.max(prev, value));
      } else if (!best.has(slug)) {
        best.set(slug, null);
      }
    }
  }
  return [...best.entries()].map(([slug, pct]) => ({
    slug,
    label: moduleLabel(slug),
    pct: pct === null ? null : Math.round(pct),
  }));
});

// Premier sujet pas encore terminé (même logique que le choix automatique du backend)
const nextSubject = computed(() => {
  for (let n = 1; n <= totalSubjects.value; n++)
    if (!doneSubjects.value.has(n)) return n;
  return null;
});

const primaryAction = computed(() => {
  const o = myExam.value;
  if (!o || !totalSubjects.value) return null;
  const examPath = `/dashboard/examens/${o.exam.slug}`;
  if (!hasOpenAccess(o.level)) {
    return {
      label: t("dashboard.my_exam.unlock"),
      icon: "pi pi-lock-open",
      to: `/dashboard/paiement?level_id=${o.level.id}`,
    };
  }
  if (examInProgress.value) {
    return {
      label: t("dashboard.my_exam.resume", {
        n: examInProgress.value.subject_number,
      }),
      icon: "pi pi-play",
      to: examPath,
    };
  }
  if (nextSubject.value) {
    return {
      label: t("dashboard.my_exam.start", { n: nextSubject.value }),
      icon: "pi pi-arrow-right",
      to: examPath,
    };
  }
  return {
    label: t("dashboard.my_exam.redo"),
    icon: "pi pi-refresh",
    to: examPath,
  };
});

// ── Devoirs ──
const assignments = ref<StudentAssignmentResponse[]>([]);
const DONE_STATUSES = ["submitted", "graded"];

const todoAssignments = computed(() =>
  assignments.value.filter(
    (a) => !DONE_STATUSES.includes(a.status.toLowerCase()),
  ),
);
const lateCount = computed(
  () => todoAssignments.value.filter((a) => a.is_late).length,
);
const nextDue = computed(
  () =>
    todoAssignments.value
      .filter((a) => a.due_at && !a.is_late)
      .map((a) => a.due_at!)
      .sort()[0] ?? null,
);

async function loadAssignments() {
  try {
    authStore._ensureApiConfig();
    const res = await AssignmentsService.myAssignmentsApiV1AssignmentsMeGet();
    assignments.value = (
      Array.isArray(res) ? res : ((res as any)?.data ?? [])
    ) as StudentAssignmentResponse[];
  } catch {
    assignments.value = [];
  }
}

// ── Raccourcis : même découpage par parcours que le menu ──
type Shortcut = {
  to: string;
  label: string;
  sub: string;
  icon: string;
  iconClass: string;
  hideForCenter?: boolean;
  /** Absent = visible dans les deux parcours */
  track?: LearningTrack;
};

const shortcuts = computed(() => {
  const list: Shortcut[] = [
    {
      to: "/dashboard/examens",
      label: t("dashboard.quick_actions.exam"),
      sub: t("dashboard.quick_actions.exam_sub"),
      icon: "pi pi-book",
      iconClass: "bg-primary/10 text-primary",
      track: "exam",
    },
    {
      to: "/dashboard/sprechen",
      label: t("dashboard.pages.sprechen"),
      sub: t("dashboard.quick_actions.sprechen_sub"),
      icon: "pi pi-microphone",
      iconClass: "bg-rose-500/10 text-rose-600",
      track: "exam",
    },
    {
      to: "/dashboard/simulateur",
      label: t("dashboard.quick_actions.simulator"),
      sub: t("dashboard.quick_actions.simulator_sub"),
      icon: "pi pi-pen-to-square",
      iconClass: "bg-indigo-500/10 text-indigo-600",
      track: "exam",
    },
    {
      to: "/dashboard/start-deutsch",
      label: t("dashboard.quick_actions.start_deutsch"),
      sub: t("dashboard.quick_actions.start_deutsch_sub"),
      icon: "pi pi-graduation-cap",
      iconClass: "bg-sky-500/10 text-sky-600",
      hideForCenter: true,
      track: "start_deutsch",
    },
    {
      to: "/dashboard/resultats",
      label: t("dashboard.quick_actions.results"),
      sub: t("dashboard.quick_actions.results_sub"),
      icon: "pi pi-chart-line",
      iconClass: "bg-orange-500/10 text-orange-600",
    },
    {
      to: "/dashboard/credits",
      label: t("dashboard.pages.credits"),
      sub: `${authStore.aiCredits} ${t("ai_credits.available", { n: authStore.aiCredits }, authStore.aiCredits)}`,
      icon: "pi pi-sparkles",
      iconClass: "bg-amber-500/15 text-amber-600",
    },
  ];
  return list.filter(
    (a) =>
      !(a.hideForCenter && isCenterStudent.value) &&
      (!a.track || a.track === track.value),
  );
});

// ── Communauté WhatsApp : carte masquée après "Rejoindre" ou la croix (préférence locale) ──
const COMMUNITY_KEY = "gtg_community_hidden";
const showCommunity = ref(false);

function hideCommunity() {
  showCommunity.value = false;
  try {
    localStorage.setItem(COMMUNITY_KEY, "1");
  } catch {
    /* stockage indisponible : la carte réapparaîtra simplement */
  }
}

onMounted(() => {
  try {
    showCommunity.value = localStorage.getItem(COMMUNITY_KEY) !== "1";
  } catch {
    showCommunity.value = true;
  }
});

// ── Chargement ──
onMounted(async () => {
  await authStore.fetchUser();

  // Étudiant individuel qui n'a encore rien choisi : accueil d'abord
  if (needsOnboarding.value) {
    await navigateTo(localePath("/dashboard/bienvenue"), { replace: true });
    return;
  }

  const tasks: Promise<unknown>[] = [];
  if (examsStore.catalog.length === 0) tasks.push(examsStore.fetchCatalog());
  if (isCenterStudent.value) tasks.push(loadAssignments());
  tasks.push(
    // 50 dernières sessions : assez pour calculer l'avancement de l'examen actif
    sessionStore.getMySessions(0, 50).then((result: any) => {
      if (result.success) {
        sessions.value = [
          ...((result.data ?? []) as SessionListResponse[]),
        ].sort((a, b) => b.started_at.localeCompare(a.started_at));
      }
    }),
  );
  await Promise.all(tasks);
  sessionsLoading.value = false;
});
</script>
