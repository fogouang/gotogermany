<template>
  <div class="space-y-6 pb-10">
    <!-- Loading -->
    <div v-if="pending || examsStore.loading" class="flex justify-center py-24">
      <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="3" />
    </div>

    <!-- Not found -->
    <div
      v-else-if="!exam"
      class="flex flex-col items-center justify-center py-24 gap-4"
    >
      <div
        class="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center"
      >
        <i class="pi pi-exclamation-triangle text-2xl text-red-400"></i>
      </div>
      <p class="font-semibold text-gray-700">
        {{ t("exam_detail.not_found") }}
      </p>
      <Button
        :label="t('exam_detail.back')"
        outlined
        size="small"
        @click="navigateTo('/dashboard/examens')"
      />
    </div>

    <div v-else class="space-y-8">
      <!-- Breadcrumb + Header -->
      <div class="flex items-start gap-3">
        <Button
          icon="pi pi-arrow-left"
          text
          rounded
          severity="secondary"
          @click="navigateTo('/dashboard/examens')"
        />
        <div class="flex-1">
          <span
            class="text-xs font-bold uppercase tracking-widest"
            :class="providerText(exam.provider)"
          >
            {{ exam.provider }}
          </span>
          <h1 class="text-2xl font-bold text-gray-900 mt-0.5">
            {{ exam.name }}
          </h1>
          <p v-if="exam.description" class="text-sm text-gray-400 mt-1">
            {{ exam.description }}
          </p>
        </div>
      </div>

      <!-- Stats cards -->
      <div class="grid grid-cols-3 gap-4">
        <div
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 text-center"
        >
          <p class="text-3xl font-bold text-gray-900">
            {{ exam.levels?.length || 0 }}
          </p>
          <p
            class="text-xs text-gray-400 mt-1 font-medium uppercase tracking-wide"
          >
            {{ t("exam_detail.levels") }}
          </p>
        </div>
        <div
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 text-center"
        >
          <p class="text-3xl font-bold text-gray-900">{{ totalSubjects }}</p>
          <p
            class="text-xs text-gray-400 mt-1 font-medium uppercase tracking-wide"
          >
            {{ t("exam_detail.subjects") }}
          </p>
        </div>
        <div
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 text-center"
        >
          <p class="text-3xl font-bold text-teal-600">3</p>
          <p
            class="text-xs text-gray-400 mt-1 font-medium uppercase tracking-wide"
          >
            {{ t("exam_detail.free_per_level") }}
          </p>
        </div>
      </div>

      <!-- Niveaux -->
      <div class="space-y-10">
        <div v-for="level in sortedLevels" :key="level.id">
          <!-- Level header -->
          <div class="flex items-center gap-4 mb-5">
            <div
              :class="[
                'w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-sm shrink-0',
                getLevelBg(level.cefr_code),
              ]"
            >
              {{ level.cefr_code }}
            </div>
            <div class="flex-1">
              <div class="flex items-center gap-2 flex-wrap">
                <p class="font-bold text-gray-900">
                  {{ t("exam_detail.level_prefix") }} {{ level.cefr_code }} —
                  {{ getLevelName(level.cefr_code) }}
                </p>
                <!-- Badge accès -->
                <Tag
                  v-if="hasAccess(level)"
                  :value="t('exam_detail.access_active')"
                  severity="success"
                  rounded
                />
                <Tag v-else value="3 sujets gratuits" severity="info" rounded />
              </div>
              <p class="text-xs text-gray-400 mt-0.5">
                {{ level.subject_count || level.subjects?.length || 0 }}
                {{ t("exam_detail.subjects_count") }} ·
                {{ t("exam_detail.min_score") }} :
                {{ level.total_pass_score }} pts
              </p>
            </div>

            <!-- Bouton souscrire si pas d'accès -->
            <Button
              v-if="!hasAccess(level)"
              :label="t('exam_detail.subscribe')"
              icon="pi pi-crown"
              size="small"
              class="shrink-0"
              @click="goToPayment(level)"
            />
          </div>

          <!-- Modules pills -->
          <div class="flex flex-wrap gap-2 mb-5 px-1">
            <div
              v-for="module in level.subjects?.[0]?.modules"
              :key="module.id"
              :class="[
                'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold',
                getModuleColor(module.slug),
              ]"
            >
              <i :class="['pi text-xs', getModuleIcon(module.slug)]"></i>
              {{ module.name }}
              <span class="opacity-50 font-normal"
                >· {{ module.time_limit_minutes }}min</span
              >
            </div>
          </div>

          <!-- Sujets grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <button
              v-for="subject in level.subjects"
              :key="subject.id"
              :class="[
                'group relative bg-white border rounded-2xl px-5 py-4 text-left flex items-center gap-4 shadow-sm transition-all duration-200',
                isSubjectFree(subject)
                  ? 'border-gray-100 hover:border-teal-300 hover:shadow-md cursor-pointer'
                  : hasAccess(level)
                    ? 'border-gray-100 hover:border-teal-300 hover:shadow-md cursor-pointer'
                    : 'border-dashed border-gray-200 opacity-70 cursor-pointer hover:opacity-90',
              ]"
              @click="goToSubject(level, subject)"
            >
              <!-- Numéro -->
              <div
                :class="[
                  'w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors border',
                  isSubjectFree(subject) || hasAccess(level)
                    ? 'bg-gray-50 border-gray-100 group-hover:bg-teal-50 group-hover:border-teal-200'
                    : 'bg-gray-50 border-gray-100',
                ]"
              >
                <span
                  :class="[
                    'text-sm font-bold transition-colors',
                    isSubjectFree(subject) || hasAccess(level)
                      ? 'text-gray-400 group-hover:text-teal-600'
                      : 'text-gray-300',
                  ]"
                >
                  {{ subject.subject_number }}
                </span>
              </div>

              <!-- Infos -->
              <div class="flex-1 min-w-0">
                <p
                  :class="[
                    'font-semibold text-sm transition-colors',
                    isSubjectFree(subject) || hasAccess(level)
                      ? 'text-gray-900 group-hover:text-teal-700'
                      : 'text-gray-400',
                  ]"
                >
                  {{
                    subject.name ||
                    `${t("exam_detail.subject_default")} ${subject.subject_number}`
                  }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5">
                  {{ subject.modules?.length || 0 }} modules ·
                  {{
                    subject.modules?.reduce(
                      (s, m) => s + (m.time_limit_minutes || 0),
                      0,
                    )
                  }}
                  min
                </p>

                <!-- Status badge -->
                <span
                  v-if="isSubjectFree(subject)"
                  class="inline-flex items-center gap-1 text-xs font-semibold text-teal-600 mt-1.5"
                >
                  <i class="pi pi-lock-open text-xs"></i> Gratuit
                </span>
                <span
                  v-else-if="hasAccess(level)"
                  class="inline-flex items-center gap-1 text-xs font-semibold text-green-600 mt-1.5"
                >
                  <i class="pi pi-check-circle text-xs"></i>
                  {{ t("exam_detail.available") }}
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1 text-xs font-semibold text-gray-400 mt-1.5"
                >
                  <i class="pi pi-lock text-xs"></i>
                  {{ t("exam_detail.premium") }}
                </span>
              </div>

              <i
                :class="[
                  'pi pi-arrow-right shrink-0 text-sm transition-all',
                  isSubjectFree(subject) || hasAccess(level)
                    ? 'text-gray-200 group-hover:text-teal-400 group-hover:translate-x-1'
                    : 'text-gray-100',
                ]"
              ></i>

              <!-- Lock overlay pour sujets premium sans accès -->
              <div
                v-if="!isSubjectFree(subject) && !hasAccess(level)"
                class="absolute top-3 right-3"
              >
                <div
                  class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center"
                >
                  <i class="pi pi-lock text-xs text-gray-400"></i>
                </div>
              </div>
            </button>
          </div>

          <!-- CTA souscrire si pas d'accès -->
          <div
            v-if="!hasAccess(level) && (level.subjects?.length || 0) > 3"
            class="mt-4 flex items-center gap-4 bg-linear-to-r from-teal-50 to-blue-50 border border-teal-100 rounded-2xl p-4"
          >
            <div
              class="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center shrink-0"
            >
              <i class="pi pi-crown text-teal-600"></i>
            </div>
            <div class="flex-1">
              <p class="text-sm font-semibold text-gray-800">
                {{ (level.subjects?.length || 0) - 3 }} sujets supplémentaires
                disponibles
              </p>
              <p class="text-xs text-gray-500 mt-0.5">
                Souscrivez au niveau {{ level.cefr_code }} pour accéder à tous
                les sujets
              </p>
            </div>
            <Button
              :label="t('exam_detail.subscribe')"
              icon="pi pi-arrow-right"
              iconPos="right"
              size="small"
              severity="info"
              @click="goToPayment(level)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {
  ExamDetailResponse,
  LevelWithSubjectsResponse,
} from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const route = useRoute();
const examsStore = useExamsStore();
const appStore = useAppStore();
const slug = computed(() => route.params.slug as string);

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
  },
  { server: false, watch: [slug] },
);

const exam = computed<ExamDetailResponse | null>(() => examsStore.currentExam);

const sortedLevels = computed(() => {
  if (!exam.value?.levels) return [];
  return [...exam.value.levels].sort(
    (a, b) => a.display_order - b.display_order,
  );
});

const totalSubjects = computed(
  () =>
    exam.value?.levels?.reduce(
      (sum, l) => sum + (l.subjects?.length || 0),
      0,
    ) ?? 0,
);

const hasAccess = (level: LevelWithSubjectsResponse): boolean => {
  const catalogExam = examsStore.catalog.find((e) => e.slug === slug.value);
  const catalogLevel = catalogExam?.levels?.find((l) => l.id === level.id);
  return catalogLevel?.has_access ?? false;
};

const isSubjectFree = (subject: any): boolean => {
  return subject.subject_number <= 3
}

const goToSubject = (level: LevelWithSubjectsResponse, subject: any) => {
  if (!exam.value) return;
  if (!isSubjectFree(subject) && !hasAccess(level)) {
    goToPayment(level);
    return;
  }
  navigateTo({
    path: `/dashboard/examens/${slug.value}/${subject.id}`,
    query: { examId: exam.value.id },
  });
};

const goToPayment = (level: LevelWithSubjectsResponse) => {
  navigateTo(`/dashboard/paiement?level_id=${level.id}`);
};

const getLevelName = (code: string) =>
  t(`exam_detail.level_names.${code}`) ?? code;

const getLevelBg = (code: string) =>
  ({
    B1: "bg-blue-100 text-blue-700",
    B2: "bg-indigo-100 text-indigo-700",
    C1: "bg-purple-100 text-purple-700",
    C2: "bg-violet-100 text-violet-700",
  })[code] ?? "bg-gray-100 text-gray-700";

const providerText = (p: string) =>
  ({
    Goethe: "text-blue-600",
    ÖSD: "text-orange-600",
    TELC: "text-purple-600",
  })[p] ?? "text-gray-500";

const getModuleIcon = (s: string) => {
  if (s.includes("lesen")) return "pi-book";
  if (s.includes("horen") || s.includes("hören")) return "pi-volume-up";
  if (s.includes("schreiben")) return "pi-pencil";
  if (s.includes("sprechen")) return "pi-microphone";
  return "pi-file";
};

const getModuleColor = (s: string) => {
  if (s.includes("lesen")) return "bg-blue-50 text-blue-600";
  if (s.includes("horen") || s.includes("hören"))
    return "bg-purple-50 text-purple-600";
  if (s.includes("schreiben")) return "bg-emerald-50 text-emerald-600";
  if (s.includes("sprechen")) return "bg-orange-50 text-orange-600";
  return "bg-gray-100 text-gray-600";
};
</script>
