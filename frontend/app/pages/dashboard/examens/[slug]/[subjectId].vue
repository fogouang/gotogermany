<template>
  <div class="space-y-6 pb-10">
    <NuxtLink
      :to="localePath(`/dashboard/examens/${slug}`)"
      class="inline-flex items-center gap-2 text-sm text-muted hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ examName || t("subject_detail.back") }}
    </NuxtLink>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="grid gap-5 lg:grid-cols-3">
      <div class="h-64 animate-pulse rounded-card bg-card-2 lg:col-span-2" />
      <div class="h-64 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Introuvable ── -->
    <div
      v-else-if="!subject"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-14 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-red-500/10 text-red-600"
      >
        <i class="pi pi-exclamation-triangle" />
      </span>
      <p class="font-medium text-ink">{{ t("subject_detail.not_found") }}</p>
      <Button
        :label="t('subject_detail.back')"
        outlined
        size="small"
        @click="navigateTo(localePath(`/dashboard/examens/${slug}`))"
      />
    </div>

    <template v-else>
      <!-- ══════════ En-tête ══════════ -->
      <header class="flex items-center gap-4">
        <span
          class="flex size-14 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-xl font-extrabold text-primary"
        >
          {{ subject.subject_number }}
        </span>
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-wider text-muted">
            {{ examName }}
          </p>
          <h1 class="truncate text-xl font-bold text-ink sm:text-2xl">
            {{
              subject.name ||
              `${t("subject_detail.subject_default")} ${subject.subject_number}`
            }}
          </h1>
          <p
            v-if="bestAttempt"
            class="mt-1 inline-flex items-center gap-1.5 text-xs font-medium"
            :class="bestAttempt.class"
          >
            <i class="pi text-[10px]" :class="bestAttempt.icon" />
            {{ t("subject_detail.best_result", { result: bestAttempt.label }) }}
          </p>
        </div>
      </header>

      <div class="grid items-start gap-5 lg:grid-cols-3">
        <!-- ══════════ Colonne principale ══════════ -->
        <div class="space-y-6 lg:col-span-2">
          <!-- Examen blanc complet (recommandé) -->
          <section
            class="relative overflow-hidden rounded-card border-2 border-primary/40 bg-card p-5 shadow-soft sm:p-6"
          >
            <span
              class="absolute right-4 top-4 rounded-full bg-primary px-2.5 py-0.5 text-[11px] font-semibold text-white"
            >
              {{ t("subject_detail.recommended") }}
            </span>
            <div class="flex items-start gap-4 pr-20">
              <span
                class="flex size-12 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-primary"
              >
                <i class="pi pi-graduation-cap text-xl" />
              </span>
              <div class="min-w-0">
                <h2 class="text-lg font-bold text-ink">
                  {{ t("subject_detail.full_exam_title") }}
                </h2>
                <p class="mt-0.5 text-sm text-muted">
                  {{ t("subject_detail.full_exam_desc") }}
                </p>
              </div>
            </div>

            <!-- Déroulé : les modules dans l'ordre de l'examen -->
            <ol class="mt-5 flex flex-wrap items-center gap-2">
              <template v-for="(module, i) in subject.modules" :key="module.id">
                <li
                  class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
                  :class="moduleStyle(module.slug).chip"
                >
                  <i
                    class="pi text-[10px]"
                    :class="moduleStyle(module.slug).icon"
                  />
                  {{ module.name }}
                  <span v-if="module.time_limit_minutes" class="opacity-60"
                    >· {{ module.time_limit_minutes }} {{ minutesLabel }}</span
                  >
                </li>
                <i
                  v-if="Number(i) < subject.modules.length - 1"
                  class="pi pi-angle-right text-[10px] text-faint"
                />
              </template>
            </ol>

            <div
              class="mt-5 flex flex-col gap-4 border-t border-line pt-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <dl class="flex flex-wrap gap-x-5 gap-y-1 text-sm">
                <div class="flex items-center gap-1.5 text-muted">
                  <i class="pi pi-clock text-xs" />
                  <dd class="font-semibold text-ink">
                    {{ totalMinutes }} {{ minutesLabel }}
                  </dd>
                </div>
                <div class="flex items-center gap-1.5 text-muted">
                  <i class="pi pi-list text-xs" />
                  <dd class="font-semibold text-ink">
                    {{ subject.modules?.length ?? 0 }}
                    {{ t("subject_detail.modules") }}
                  </dd>
                </div>
                <div class="flex items-center gap-1.5 text-muted">
                  <i class="pi pi-star text-xs" />
                  <dd class="font-semibold text-ink">
                    {{ totalPoints }} {{ pointsLabel }}
                  </dd>
                </div>
              </dl>
              <Button
                :label="t('subject_detail.start_full_exam')"
                icon="pi pi-play"
                size="large"
                class="w-full sm:w-auto"
                @click="startFullExam"
              />
            </div>
          </section>

          <!-- Entraînement par module -->
          <section class="space-y-3">
            <div>
              <h2 class="font-semibold text-ink">
                {{ t("subject_detail.work_module") }}
              </h2>
              <p class="text-sm text-muted">
                {{ t("subject_detail.choose_module") }}
              </p>
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <button
                v-for="module in displayModules"
                :key="module.id"
                type="button"
                class="group flex items-center gap-4 rounded-card border border-line bg-card p-4 text-left transition-colors hover:border-primary/40"
                @click="startModule(module)"
              >
                <span
                  class="flex size-11 shrink-0 items-center justify-center rounded-leaf"
                  :class="moduleStyle(module.slug).chip"
                >
                  <i class="pi" :class="moduleStyle(module.slug).icon" />
                </span>
                <span class="min-w-0 flex-1">
                  <span
                    class="block truncate font-semibold text-ink transition-colors group-hover:text-primary"
                  >
                    {{ module.name }}
                  </span>
                  <span
                    class="mt-0.5 flex flex-wrap gap-x-3 text-xs text-muted"
                  >
                    <span v-if="module.time_limit_minutes > 0">
                      <i class="pi pi-clock mr-1 text-[10px]" />{{
                        module.time_limit_minutes
                      }}
                      {{ minutesLabel }}
                    </span>
                    <span>
                      <i class="pi pi-star mr-1 text-[10px]" />{{
                        module.max_score
                      }}
                      {{ pointsLabel }}
                    </span>
                  </span>
                </span>
                <i
                  class="pi pi-arrow-right shrink-0 text-xs text-faint transition-transform group-hover:translate-x-1 group-hover:text-primary"
                />
              </button>
            </div>
          </section>
        </div>

        <!-- ══════════ Avant de commencer ══════════ -->
        <aside
          class="rounded-card border border-line bg-card p-5 shadow-soft lg:sticky lg:top-0"
        >
          <h2 class="mb-4 font-semibold text-ink">
            {{ t("subject_detail.before_start") }}
          </h2>
          <ul class="space-y-3 text-sm">
            <li
              v-for="tip in tips"
              :key="tip.key"
              class="flex items-start gap-3"
            >
              <span
                class="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-card-2 text-muted"
              >
                <i class="pi text-xs" :class="tip.icon" />
              </span>
              <span class="text-ink">{{ tip.text }}</span>
            </li>
          </ul>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SessionListResponse } from "#shared/api";

definePageMeta({ layout: "dashboard", watermark: "Prüfung" });

const { t } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const examsStore = useExamsStore();
const sessionStore = useSessionStore();

const slug = route.params.slug as string;
const subjectId = route.params.subjectId as string;
const examId = route.query.examId as string;

const loading = ref(true);
const subject = ref<any>(null);
const examName = ref("");

// Libellés d'unité (les clés existantes peuvent contenir une espace)
const minutesLabel = computed(() => t("subject_detail.minutes").trim());
const pointsLabel = computed(() => t("subject_detail.points").trim());

onMounted(async () => {
  if (!examsStore.currentExam || examsStore.currentExam.id !== examId) {
    await examsStore.fetchExamBySlug(slug);
  }
  const exam = examsStore.currentExam;
  if (exam) {
    examName.value = exam.name;
    for (const level of exam.levels ?? []) {
      const found = level.subjects?.find((s: any) => s.id === subjectId);
      if (found) {
        subject.value = found;
        break;
      }
    }
  }
  loading.value = false;
  loadBestAttempt();
});

// ── Meilleur résultat déjà obtenu sur ce sujet ──
const attempts = ref<SessionListResponse[]>([]);

async function loadBestAttempt() {
  const res = await sessionStore.getMySessions(0, 100);
  if (res.success) {
    attempts.value = ((res.data ?? []) as SessionListResponse[]).filter(
      (s) => s.subject_id === subjectId && s.status === "COMPLETED",
    );
  }
}

const bestAttempt = computed(() => {
  if (!attempts.value.length) return null;
  const best = [...attempts.value].sort(
    (a, b) => (b.score ?? -1) - (a.score ?? -1),
  )[0]!;
  const passed = attempts.value.some((s) => s.passed);
  const verdict = passed ? t("dashboard.passed") : t("dashboard.failed");
  return {
    label:
      best.score != null ? `${verdict} · ${Math.round(best.score)}` : verdict,
    icon: passed ? "pi-check-circle" : "pi-times-circle",
    class: passed ? "text-emerald-600" : "text-red-600",
  };
});

// ── Modules à afficher (fusion Leseverstehen + Sprachbausteine) ──
// Ces deux modules TELC partagent un temps commun (90 min) selon la grille officielle.
// Quand l'un des deux a time_limit_minutes = 0 (temps non individualisé à la génération),
// on les fusionne en une seule carte pour éviter un lancement avec un chronomètre à 0.
const displayModules = computed(() => {
  if (!subject.value?.modules) return [];

  const modules = subject.value.modules;
  const leseModule = modules.find((m: any) =>
    (m.slug || "").toLowerCase().includes("lese"),
  );
  const sprachbausteineModule = modules.find((m: any) =>
    (m.slug || "").toLowerCase().includes("sprachbaustein"),
  );

  const shouldMerge =
    leseModule &&
    sprachbausteineModule &&
    (leseModule.time_limit_minutes === 0 ||
      sprachbausteineModule.time_limit_minutes === 0);

  if (!shouldMerge) return modules;

  const merged = {
    id: `${leseModule.id}__${sprachbausteineModule.id}`,
    slug: "lese", // garde le slug lese pour hériter de l'icône et de la couleur Leseverstehen
    name: `${leseModule.name} + ${sprachbausteineModule.name}`,
    time_limit_minutes:
      (leseModule.time_limit_minutes || 0) +
      (sprachbausteineModule.time_limit_minutes || 0),
    max_score:
      (leseModule.max_score || 0) + (sprachbausteineModule.max_score || 0),
    _mergedSlugs: [leseModule.slug, sprachbausteineModule.slug],
  };

  const leseIndex = modules.findIndex((m: any) => m.id === leseModule.id);
  const others = modules.filter(
    (m: any) => m.id !== leseModule.id && m.id !== sprachbausteineModule.id,
  );
  const result = [...others];
  result.splice(leseIndex, 0, merged);
  return result;
});

const totalMinutes = computed(
  () =>
    subject.value?.modules?.reduce(
      (s: number, m: any) => s + (m.time_limit_minutes || 0),
      0,
    ) ?? 0,
);
const totalPoints = computed(
  () =>
    subject.value?.modules?.reduce(
      (s: number, m: any) => s + (m.max_score || 0),
      0,
    ) ?? 0,
);

// ── Conseils : uniquement des faits vrais pour ce sujet ──
const hasListening = computed(() =>
  (subject.value?.modules ?? []).some((m: any) =>
    /hoer|hör|horen/i.test(m.slug || ""),
  ),
);

const tips = computed(() => [
  { key: "timer", icon: "pi-clock", text: t("subject_detail.tip_timer") },
  { key: "saved", icon: "pi-save", text: t("subject_detail.tip_saved") },
  ...(hasListening.value
    ? [
        {
          key: "audio",
          icon: "pi-headphones",
          text: t("subject_detail.tip_headphones"),
        },
      ]
    : []),
  { key: "quiet", icon: "pi-moon", text: t("subject_detail.tip_quiet") },
]);

// ── Lancement ──
const sessionPath = `/dashboard/examens/${slug}/session`;

const startModule = (module: any) => {
  const query = module._mergedSlugs
    ? { examId, subjectId, moduleSlugs: module._mergedSlugs.join(",") }
    : { examId, subjectId, moduleSlug: module.slug };
  navigateTo(localePath({ path: sessionPath, query }));
};

const startFullExam = () => {
  navigateTo(localePath({ path: sessionPath, query: { examId, subjectId } }));
};

// ── Couleurs des modules (mêmes que la page de l'examen) ──
const moduleStyle = (slug: string) => {
  const s = (slug || "").toLowerCase();
  if (s.includes("sprachbaustein"))
    return { chip: "bg-pink-500/10 text-pink-600", icon: "pi-language" };
  if (s.includes("lese"))
    return { chip: "bg-sky-500/10 text-sky-600", icon: "pi-book" };
  if (s.includes("hoer") || s.includes("hör") || s.includes("horen"))
    return { chip: "bg-violet-500/10 text-violet-600", icon: "pi-volume-up" };
  if (s.includes("schreib") || s.includes("schriftlich"))
    return { chip: "bg-emerald-500/10 text-emerald-600", icon: "pi-pencil" };
  if (s.includes("sprech") || s.includes("muendlich") || s.includes("mündlich"))
    return { chip: "bg-orange-500/10 text-orange-600", icon: "pi-microphone" };
  return { chip: "bg-card-2 text-muted", icon: "pi-file" };
};
</script>
