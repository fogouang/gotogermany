<template>
  <div class="space-y-6 pb-10">
    <NuxtLink
      :to="localePath('/dashboard/examens/catalogue')"
      class="inline-flex items-center gap-2 text-sm text-muted hover:text-ink"
    >
      <i class="pi pi-th-large text-xs" />
      {{ t("level_switch.all_exams") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="pending || examsStore.loading" class="space-y-4">
      <div class="h-32 animate-pulse rounded-card bg-card-2" />
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="n in 6"
          :key="n"
          class="h-24 animate-pulse rounded-card bg-card-2"
        />
      </div>
    </div>

    <!-- ── Introuvable ── -->
    <div
      v-else-if="!exam"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-14 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-red-500/10 text-red-600"
      >
        <i class="pi pi-exclamation-triangle" />
      </span>
      <p class="font-medium text-ink">{{ t("exam_detail.not_found") }}</p>
      <Button
        :label="t('exam_detail.back')"
        outlined
        size="small"
        @click="navigateTo(localePath('/dashboard/examens'))"
      />
    </div>

    <template v-else>
      <!-- ══════════ En-tête examen ══════════ -->
      <section
        class="relative isolate overflow-hidden rounded-card border border-line bg-card p-5 shadow-soft sm:p-6"
      >
        <span
          class="absolute inset-x-0 top-0 h-1"
          :class="providerStyle(exam.provider).bar"
        />
        <div class="flex flex-col gap-5 sm:flex-row sm:items-center">
          <div class="flex min-w-0 flex-1 items-start gap-4">
            <span
              class="flex size-14 shrink-0 items-center justify-center rounded-leaf text-sm font-extrabold"
              :class="providerStyle(exam.provider).badge"
            >
              {{ providerShort(exam.provider) }}
            </span>
            <div class="min-w-0">
              <p
                class="text-xs font-semibold uppercase tracking-wider"
                :class="providerStyle(exam.provider).text"
              >
                {{ providerName(exam.provider) }}
              </p>
              <h1
                class="mt-0.5 text-xl font-bold leading-tight text-ink sm:text-2xl"
              >
                {{ exam.name }}
              </h1>
              <p v-if="exam.description" class="mt-1 text-sm text-muted">
                {{ exam.description }}
              </p>
            </div>
          </div>

          <dl class="grid shrink-0 grid-cols-2 gap-2 text-center sm:w-64">
            <div class="rounded-leaf bg-card-2 px-3 py-2.5">
              <dd class="text-xl font-bold text-ink">{{ totalSubjects }}</dd>
              <dt class="text-[11px] text-muted">
                {{ t("exam_detail.subjects") }}
              </dt>
            </div>
            <div class="rounded-leaf bg-card-2 px-3 py-2.5">
              <dd class="text-xl font-bold text-ink">
                {{ sortedLevels.length }}
              </dd>
              <dt class="text-[11px] text-muted">
                {{ t("exam_detail.levels") }}
              </dt>
            </div>
          </dl>
        </div>
      </section>

      <!-- ══════════ Niveaux ══════════ -->
      <section v-for="level in sortedLevels" :key="level.id" class="space-y-4">
        <!-- En-tête niveau -->
        <div class="flex flex-wrap items-center gap-3">
          <span
            class="flex size-12 shrink-0 items-center justify-center rounded-leaf text-base font-extrabold"
            :class="providerStyle(exam.provider).badge"
          >
            {{ level.cefr_code }}
          </span>
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="font-semibold text-ink">
                {{ t("exam_detail.level_prefix") }} {{ level.cefr_code }}
                <span
                  v-if="levelName(level.cefr_code)"
                  class="font-normal text-muted"
                  >· {{ levelName(level.cefr_code) }}</span
                >
              </h2>
              <span
                v-if="isOpen(level)"
                class="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600"
              >
                <i class="pi pi-check-circle text-[9px]" />
                {{
                  level.is_free
                    ? t("dashboard.level_free")
                    : t("exam_detail.access_active")
                }}
              </span>
              <span
                v-else-if="!isCenterStudent"
                class="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
              >
                <i class="pi pi-lock text-[9px]" />
                {{ t("dashboard.level_preview") }}
              </span>
            </div>
            <p
              v-if="doneCount(level) > 0"
              class="mt-1 text-xs font-medium text-primary"
            >
              {{
                t("exam_detail.done_count", {
                  done: doneCount(level),
                  total: level.subjects?.length ?? 0,
                })
              }}
            </p>
          </div>
          <span
            v-if="canSwitch && activeOption?.level.id === level.id"
            class="inline-flex shrink-0 items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary"
          >
            <i class="pi pi-bookmark-fill text-[10px]" />
            {{ t("exam_detail.active_level") }}
          </span>
          <Button
            v-else-if="canSwitch && level.subjects?.length"
            :label="t('exam_detail.set_active')"
            icon="pi pi-bookmark"
            size="small"
            text
            class="shrink-0"
            :loading="settingActive === level.id"
            @click="makeActive(level)"
          />
        </div>

        <!-- Modules -->
        <div
          v-if="level.subjects?.[0]?.modules?.length"
          class="flex flex-wrap gap-2"
        >
          <span
            v-for="module in level.subjects[0].modules"
            :key="module.id"
            class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
            :class="moduleStyle(module.slug).chip"
          >
            <i class="pi text-[10px]" :class="moduleStyle(module.slug).icon" />
            {{ module.name }}
            <span class="opacity-60"
              >· {{ module.time_limit_minutes }} min</span
            >
          </span>
        </div>

        <!-- Bandeau de déblocage -->
        <div
          v-if="!isOpen(level) && lockedCount(level) > 0"
          class="flex flex-col gap-3 rounded-card border border-primary/30 bg-primary/10 p-4 sm:flex-row sm:items-center"
        >
          <span
            class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-card text-primary"
          >
            <i class="pi" :class="isCenterStudent ? 'pi-lock' : 'pi-unlock'" />
          </span>
          <div class="min-w-0 flex-1">
            <template v-if="isCenterStudent">
              <p class="text-sm font-semibold text-ink">
                {{ t("dashboard.status.not_activated_title") }}
              </p>
              <p class="text-xs text-muted">
                {{ t("dashboard.status.not_activated_text") }}
              </p>
            </template>
            <template v-else>
              <p class="text-sm font-semibold text-ink">
                {{
                  t(
                    "exam_detail.more_subjects",
                    { n: lockedCount(level) },
                    lockedCount(level),
                  )
                }}
              </p>
              <p class="text-xs text-muted">
                {{
                  t("exam_detail.more_subjects_text", {
                    level: level.cefr_code,
                  })
                }}
              </p>
            </template>
          </div>
          <Button
            v-if="!isCenterStudent"
            :label="
              levelPrice(level)
                ? t('dashboard_exams.unlock_price', {
                    price: fcfa(levelPrice(level)!),
                  })
                : t('exam_detail.subscribe')
            "
            icon="pi pi-unlock"
            size="small"
            class="shrink-0"
            @click="goToPayment(level)"
          />
        </div>

        <!-- Sujets -->
        <div
          v-if="level.subjects?.length"
          class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"
        >
          <button
            v-for="subject in level.subjects"
            :key="subject.id"
            type="button"
            class="group relative flex items-center gap-4 rounded-card border bg-card px-4 py-4 text-left shadow-soft transition-colors"
            :class="
              canOpen(level, subject)
                ? 'border-line hover:border-primary/40'
                : 'border-dashed border-line'
            "
            @click="goToSubject(level, subject)"
          >
            <span
              class="flex size-11 shrink-0 items-center justify-center rounded-leaf text-sm font-bold transition-colors"
              :class="
                isDone(subject.id)
                  ? attempts[subject.id]?.passed
                    ? 'bg-emerald-500/10 text-emerald-600'
                    : 'bg-card-2 text-muted'
                  : canOpen(level, subject)
                    ? 'bg-card-2 text-ink group-hover:bg-primary/10 group-hover:text-primary'
                    : 'bg-card-2 text-faint'
              "
            >
              <i v-if="!canOpen(level, subject)" class="pi pi-lock text-xs" />
              <i v-else-if="isDone(subject.id)" class="pi pi-check text-sm" />
              <template v-else>{{ subject.subject_number }}</template>
            </span>

            <span class="min-w-0 flex-1">
              <span
                class="block truncate text-sm font-semibold"
                :class="
                  canOpen(level, subject)
                    ? 'text-ink group-hover:text-primary'
                    : 'text-muted'
                "
              >
                {{
                  subject.name ||
                  `${t("exam_detail.subject_default")} ${subject.subject_number}`
                }}
              </span>
              <span class="mt-0.5 block text-xs text-muted">
                {{
                  t("exam_detail.subject_meta", {
                    modules: subject.modules?.length ?? 0,
                    minutes: subjectMinutes(subject),
                  })
                }}
              </span>
              <span class="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1">
                <span
                  class="inline-flex items-center gap-1 text-[11px] font-semibold"
                  :class="subjectBadge(level, subject).class"
                >
                  <i
                    class="pi text-[9px]"
                    :class="subjectBadge(level, subject).icon"
                  />
                  {{ subjectBadge(level, subject).label }}
                </span>
                <span
                  v-if="attemptBadge(subject.id)"
                  class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="attemptBadge(subject.id)!.class"
                >
                  <i
                    class="pi text-[9px]"
                    :class="attemptBadge(subject.id)!.icon"
                  />
                  {{ attemptBadge(subject.id)!.label }}
                </span>
              </span>
            </span>

            <i
              class="pi shrink-0 text-xs transition-transform"
              :class="
                canOpen(level, subject)
                  ? 'pi-arrow-right text-faint group-hover:translate-x-1 group-hover:text-primary'
                  : 'pi-chevron-right text-line'
              "
            />
          </button>
        </div>
        <p
          v-else
          class="rounded-card border border-dashed border-line bg-card px-4 py-8 text-center text-sm text-muted"
        >
          {{ t("dashboard_exams.coming_soon_text") }}
        </p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import type {
  ExamDetailResponse,
  LevelWithSubjectsResponse,
  SessionListResponse,
} from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Prüfung" });

const { t, te, locale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const examsStore = useExamsStore();
const authStore = useAuthStore();
const slug = computed(() => route.params.slug as string);
const { isCenterStudent, assignedExamSlug } = useVisibleCatalog();

/** Nombre de sujets d'essai gratuits par niveau (miroir de la règle backend check_subject_access) */
const FREE_SUBJECTS = 3;

const { pending } = await useAsyncData(
  `exam-${slug.value}`,
  async () => {
    examsStore.clearCurrentExam();
    await Promise.all([
      examsStore.fetchExamBySlug(slug.value),
      examsStore.catalog.length === 0
        ? examsStore.fetchCatalog()
        : Promise.resolve(),
    ]);

    // Étudiant de centre : blocage si l'URL pointe vers un examen hors de son inscription
    if (
      isCenterStudent.value &&
      assignedExamSlug.value &&
      slug.value !== assignedExamSlug.value
    ) {
      await navigateTo(localePath("/dashboard/examens"));
    }
  },
  { server: false, watch: [slug] },
);

const exam = computed<ExamDetailResponse | null>(() => examsStore.currentExam);

// ── Format ──
const intlLocale = computed(
  () =>
    (({ fr: "fr-FR", de: "de-DE" }) as Record<string, string>)[locale.value] ??
    "en-GB",
);
const fcfa = (n: number) =>
  `${Math.round(n).toLocaleString(intlLocale.value)} FCFA`;

// ── Organismes (même palette que le catalogue) ──
const norm = (p?: string | null) =>
  (p ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

const PROVIDERS: Record<
  string,
  { name: string; short: string; badge: string; bar: string; text: string }
> = {
  goethe: {
    name: "Goethe-Institut",
    short: "GI",
    badge: "bg-emerald-500/10 text-emerald-600",
    bar: "bg-emerald-500",
    text: "text-emerald-600",
  },
  telc: {
    name: "telc",
    short: "TE",
    badge: "bg-red-500/10 text-red-600",
    bar: "bg-red-500",
    text: "text-red-600",
  },
  osd: {
    name: "ÖSD",
    short: "ÖSD",
    badge: "bg-sky-500/10 text-sky-600",
    bar: "bg-sky-500",
    text: "text-sky-600",
  },
  testdaf: {
    name: "TestDaF",
    short: "TD",
    badge: "bg-violet-500/10 text-violet-600",
    bar: "bg-violet-500",
    text: "text-violet-600",
  },
  ecl: {
    name: "ECL",
    short: "ECL",
    badge: "bg-amber-500/15 text-amber-600",
    bar: "bg-amber-500",
    text: "text-amber-600",
  },
};
const providerName = (p: string) => PROVIDERS[norm(p)]?.name ?? p;
const providerShort = (p: string) =>
  PROVIDERS[norm(p)]?.short ?? p.slice(0, 2).toUpperCase();
const providerStyle = (p: string) =>
  PROVIDERS[norm(p)] ?? {
    badge: "bg-primary/10 text-primary",
    bar: "bg-primary",
    text: "text-primary",
  };

const levelName = (code: string) =>
  te(`exam_detail.level_names.${code}`)
    ? t(`exam_detail.level_names.${code}`)
    : "";

const moduleStyle = (slug: string) => {
  const s = slug.toLowerCase();
  if (s.includes("lesen"))
    return { chip: "bg-sky-500/10 text-sky-600", icon: "pi-book" };
  if (s.includes("horen") || s.includes("hören") || s.includes("hoeren"))
    return { chip: "bg-violet-500/10 text-violet-600", icon: "pi-volume-up" };
  if (s.includes("schreiben"))
    return { chip: "bg-emerald-500/10 text-emerald-600", icon: "pi-pencil" };
  if (s.includes("sprechen"))
    return { chip: "bg-orange-500/10 text-orange-600", icon: "pi-microphone" };
  return { chip: "bg-card-2 text-muted", icon: "pi-file" };
};

// ── Niveaux ──
const sortedLevels = computed(() => {
  if (!exam.value?.levels) return [];
  let levels = exam.value.levels;
  // Étudiant de centre : uniquement son niveau assigné
  if (isCenterStudent.value)
    levels = levels.filter((l) => l.id === authStore.targetLevelId);
  return [...levels].sort((a, b) => a.display_order - b.display_order);
});

const totalSubjects = computed(() =>
  sortedLevels.value.reduce((sum, l) => sum + (l.subjects?.length || 0), 0),
);

const catalogLevel = (level: LevelWithSubjectsResponse) =>
  examsStore.catalog
    .find((e) => e.slug === slug.value)
    ?.levels?.find((l) => l.id === level.id);

const hasAccess = (level: LevelWithSubjectsResponse) =>
  catalogLevel(level)?.has_access ?? false;
const levelPrice = (level: LevelWithSubjectsResponse) =>
  catalogLevel(level)?.price ?? null;

/** Niveau entièrement ouvert : accès payé ou niveau gratuit */
const isOpen = (level: LevelWithSubjectsResponse) =>
  hasAccess(level) || level.is_free;

/** Sujet d'essai : aucun pour l'élève de centre (verrouillé sur son niveau, comme le backend) */
const isTrialSubject = (subject: { subject_number: number }) =>
  !isCenterStudent.value && subject.subject_number <= FREE_SUBJECTS;

const canOpen = (
  level: LevelWithSubjectsResponse,
  subject: { subject_number: number },
) => isOpen(level) || isTrialSubject(subject);

const lockedCount = (level: LevelWithSubjectsResponse) =>
  (level.subjects ?? []).filter((s) => !canOpen(level, s)).length;

const subjectMinutes = (subject: any) =>
  (subject.modules ?? []).reduce(
    (s: number, m: any) => s + (m.time_limit_minutes || 0),
    0,
  );

const subjectBadge = (
  level: LevelWithSubjectsResponse,
  subject: { subject_number: number },
) => {
  if (isOpen(level))
    return {
      label: t("exam_detail.available"),
      icon: "pi-check-circle",
      class: "text-emerald-600",
    };
  if (isTrialSubject(subject))
    return {
      label: t("dashboard.level_free"),
      icon: "pi-lock-open",
      class: "text-primary",
    };
  return {
    label: t("exam_detail.premium"),
    icon: "pi-lock",
    class: "text-faint",
  };
};

// ── Navigation ──
const goToPayment = (level: LevelWithSubjectsResponse) => {
  if (isCenterStudent.value) return; // c'est le centre qui active l'accès
  navigateTo(localePath(`/dashboard/paiement?level_id=${level.id}`));
};

const goToSubject = (level: LevelWithSubjectsResponse, subject: any) => {
  if (!exam.value) return;
  if (!canOpen(level, subject)) {
    goToPayment(level);
    return;
  }
  navigateTo(
    localePath({
      path: `/dashboard/examens/${slug.value}/${subject.id}`,
      query: { examId: exam.value.id },
    }),
  );
};

// ══════════ Niveau actif ══════════
const notify = useNotify();
const { info } = useProviders();
const { activeOption, canSwitch, setActiveLevel } = useActiveLevel();
const settingActive = ref<string | null>(null);

async function makeActive(level: LevelWithSubjectsResponse) {
  if (!exam.value) return;
  settingActive.value = level.id;
  const result = await setActiveLevel(level.id);
  settingActive.value = null;
  if (!result.success) {
    notify.error(t("toast.error_title"), result.error || t("onboarding.error"));
    return;
  }
  notify.success(
    t("toast.level_changed", {
      level: `${info(exam.value.provider).brand} ${level.cefr_code}`,
    }),
  );
}

// ══════════ État de chaque sujet (depuis les sessions de l'étudiant) ══════════
const sessionStore = useSessionStore();

type Attempt = {
  best: number | null;
  passed: boolean;
  inProgress: boolean;
  pending: boolean; // rendu, correction (IA ou enseignant) en cours
  done: number;
};
const attempts = ref<Record<string, Attempt>>({});

async function loadAttempts() {
  const res = await sessionStore.getMySessions(0, 100);
  if (!res.success) return;
  const map: Record<string, Attempt> = {};
  for (const s of (res.data ?? []) as SessionListResponse[]) {
    const a = (map[s.subject_id] ??= {
      best: null,
      passed: false,
      inProgress: false,
      pending: false,
      done: 0,
    });
    if (s.status === "IN_PROGRESS") {
      a.inProgress = true;
      continue;
    }
    if (s.status === "ABANDONED") continue;
    a.done++;
    if (s.status === "PENDING_REVIEW") {
      a.pending = true;
      continue;
    }
    if (s.passed) a.passed = true;
    if (s.score != null && (a.best === null || s.score > a.best))
      a.best = s.score;
  }
  attempts.value = map;
}

const isDone = (subjectId: string) =>
  (attempts.value[subjectId]?.done ?? 0) > 0;

const attemptBadge = (subjectId: string) => {
  const a = attempts.value[subjectId];
  if (!a) return null;
  // Rendu mais pas encore noté (aucune tentative notée sur ce sujet)
  if (a.pending && a.best === null && !a.passed) {
    return {
      label: t("exam_detail.done_pending"),
      icon: "pi-hourglass",
      class: "bg-sky-500/10 text-sky-600",
    };
  }
  if (a.done > 0) {
    const verdict = a.passed ? t("dashboard.passed") : t("dashboard.failed");
    return {
      label: a.best !== null ? `${verdict} · ${Math.round(a.best)}` : verdict,
      icon: a.passed ? "pi-check" : "pi-times",
      class: a.passed
        ? "bg-emerald-500/10 text-emerald-600"
        : "bg-red-500/10 text-red-600",
    };
  }
  if (a.inProgress) {
    return {
      label: t("dashboard.in_progress"),
      icon: "pi-clock",
      class: "bg-amber-500/15 text-amber-600",
    };
  }
  return null;
};

const doneCount = (level: LevelWithSubjectsResponse) =>
  (level.subjects ?? []).filter((s) => (attempts.value[s.id]?.done ?? 0) > 0)
    .length;

onMounted(loadAttempts);
</script>
