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
        <!-- Reprendre -->
        <button
          v-if="inProgress"
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
              >{{ t("dashboard.resume_title") }}</span
            >
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

        <!-- Mes niveaux -->
        <section
          class="overflow-hidden rounded-card border border-line bg-card shadow-soft"
        >
          <header
            class="flex items-center justify-between gap-3 border-b border-line px-5 py-4"
          >
            <h2 class="font-semibold text-ink">
              {{ t("dashboard.my_levels") }}
            </h2>
            <NuxtLink
              :to="localePath('/dashboard/examens/catalogue')"
              class="text-sm font-medium text-primary hover:underline"
            >
              {{ t("dashboard.see_all") }}
            </NuxtLink>
          </header>

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
            v-else-if="levelRows.length === 0"
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
            <li v-for="row in levelRows" :key="row.level.id">
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
                    {{ row.level.subject_count ?? 0 }} {{ t("payment.subjet") }}
                  </span>
                </span>

                <span
                  v-if="row.level.id === activeLevelId"
                  class="inline-flex shrink-0 items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary"
                >
                  <i class="pi pi-bookmark-fill text-[9px]" />
                  {{ t("exam_detail.active_level") }}
                </span>
                <span
                  v-if="!row.level.subject_count"
                  class="shrink-0 rounded-full bg-card-2 px-2 py-0.5 text-[11px] font-semibold text-muted"
                >
                  {{ t("dashboard_exams.coming_soon") }}
                </span>
                <span
                  v-else-if="row.level.has_access || row.level.is_free"
                  class="shrink-0 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600"
                >
                  {{
                    row.level.is_free
                      ? t("dashboard.level_free")
                      : t("dashboard.level_active")
                  }}
                </span>
                <template v-else>
                  <span
                    class="shrink-0 rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
                  >
                    {{ t("dashboard.level_preview") }}
                  </span>
                  <span
                    v-if="!isCenterStudent"
                    class="hidden shrink-0 text-xs font-semibold text-primary sm:inline"
                  >
                    {{ t("dashboard.unlock") }}
                  </span>
                </template>
                <i
                  class="pi pi-chevron-right shrink-0 text-xs text-faint transition-transform group-hover:translate-x-0.5"
                />
              </button>
            </li>
          </ul>
        </section>

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
              @click="navigateTo(localePath('/dashboard/examens'))"
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
        <!-- Progression -->
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
  // Niveau actif d'abord, puis niveaux avec sujets, puis accès ouverts
  return rows.sort(
    (a, b) =>
      Number(b.level.id === activeLevelId.value) -
        Number(a.level.id === activeLevelId.value) ||
      Number((b.level.subject_count ?? 0) > 0) -
        Number((a.level.subject_count ?? 0) > 0) ||
      Number(b.level.has_access) - Number(a.level.has_access) ||
      a.level.display_order - b.level.display_order,
  );
});

const openLevel = (row: LevelRow) => {
  if (!row.level.subject_count) return;

  if (row.level.has_access || row.level.is_free || isCenterStudent.value) {
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

const inProgress = computed(
  () => sessions.value.find((s) => s.status !== "COMPLETED") ?? null,
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

// ── Raccourcis ──
const shortcuts = computed(() => {
  const list = [
    {
      to: "/dashboard/examens",
      label: t("dashboard.quick_actions.exam"),
      sub: t("dashboard.quick_actions.exam_sub"),
      icon: "pi pi-book",
      iconClass: "bg-primary/10 text-primary",
    },
    {
      to: "/dashboard/sprechen",
      label: t("dashboard.pages.sprechen"),
      sub: t("dashboard.quick_actions.sprechen_sub"),
      icon: "pi pi-microphone",
      iconClass: "bg-rose-500/10 text-rose-600",
    },
    {
      to: "/dashboard/simulateur",
      label: t("dashboard.quick_actions.simulator"),
      sub: t("dashboard.quick_actions.simulator_sub"),
      icon: "pi pi-pen-to-square",
      iconClass: "bg-indigo-500/10 text-indigo-600",
    },
    {
      to: "/dashboard/start-deutsch",
      label: t("dashboard.quick_actions.start_deutsch"),
      sub: t("dashboard.quick_actions.start_deutsch_sub"),
      icon: "pi pi-graduation-cap",
      iconClass: "bg-sky-500/10 text-sky-600",
      hideForCenter: true,
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
  return list.filter((a) => !(a.hideForCenter && isCenterStudent.value));
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

  // Étudiant individuel qui n'a pas encore choisi son niveau : accueil d'abord
  if (needsOnboarding.value) {
    await navigateTo(localePath("/dashboard/bienvenue"), { replace: true });
    return;
  }

  const tasks: Promise<unknown>[] = [];
  if (examsStore.catalog.length === 0) tasks.push(examsStore.fetchCatalog());
  if (isCenterStudent.value) tasks.push(loadAssignments());
  tasks.push(
    sessionStore.getMySessions(0, 10).then((result: any) => {
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
