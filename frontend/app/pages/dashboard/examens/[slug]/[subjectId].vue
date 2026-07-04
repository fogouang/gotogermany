<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <div
      v-else-if="!subject"
      class="text-center py-16 bg-white rounded-xl border border-gray-100"
    >
      <i
        class="pi pi-exclamation-triangle text-4xl text-red-400 mb-3 block"
      ></i>
      <p class="font-medium text-gray-700">
        {{ t("subject_detail.not_found") }}
      </p>
      <Button
        :label="t('subject_detail.back')"
        outlined
        class="mt-4"
        @click="router.back()"
      />
    </div>

    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-3">
        <Button icon="pi pi-arrow-left" text rounded @click="router.back()" />
        <div>
          <p class="text-xs text-gray-400">{{ examName }}</p>
          <h1 class="text-lg font-bold text-gray-900">
            {{
              subject.name ||
              `${t("subject_detail.subject_default")} ${subject.subject_number}`
            }}
          </h1>
        </div>
      </div>

      <!-- Intro -->
      <div class="text-center">
        <h2 class="text-base font-semibold text-gray-800">
          {{ t("subject_detail.how_to_work") }}
        </h2>
        <p class="text-sm text-gray-400 mt-0.5">
          {{ t("subject_detail.choose_module") }}
        </p>
      </div>

      <!-- Modules -->
      <div>
        <p
          class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3"
        >
          {{ t("subject_detail.work_module") }}
        </p>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <button
            v-for="module in displayModules"
            :key="module.id"
            class="group bg-white border-2 border-gray-100 rounded-xl p-4 text-center hover:border-teal-400 hover:shadow-md transition-all"
            @click="startModule(module)"
          >
            <div
              :class="[
                'w-12 h-12 mx-auto rounded-xl flex items-center justify-center mb-3 transition-colors',
                getModuleBg(module.slug),
              ]"
            >
              <i
                :class="[
                  'pi text-xl',
                  getModuleIcon(module.slug),
                  getModuleIconColor(module.slug),
                ]"
              ></i>
            </div>
            <p
              class="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors text-sm mb-2"
            >
              {{ module.name }}
            </p>
            <div class="space-y-0.5 text-xs text-gray-400">
              <p
                v-if="module.time_limit_minutes > 0"
                class="flex items-center justify-center gap-1"
              >
                <i class="pi pi-clock text-xs"></i>
                {{ module.time_limit_minutes }}{{ t("subject_detail.minutes") }}
              </p>
              <p class="flex items-center justify-center gap-1">
                <i class="pi pi-star text-xs"></i>
                {{ module.max_score }}{{ t("subject_detail.points") }}
              </p>
            </div>
          </button>
        </div>
      </div>

      <!-- Séparateur -->
      <div class="flex items-center gap-4">
        <div class="flex-1 h-px bg-gray-100"></div>
        <span
          class="text-xs text-gray-400 font-medium uppercase tracking-widest"
        >
          {{ t("subject_detail.or") }}
        </span>
        <div class="flex-1 h-px bg-gray-100"></div>
      </div>

      <!-- Mode examen complet -->
      <div
        class="bg-white border-2 border-gray-100 rounded-xl p-5 hover:border-teal-400 hover:shadow-md transition-all"
      >
        <div class="flex items-start gap-4">
          <div
            class="w-12 h-12 rounded-xl bg-teal-50 flex items-center justify-center shrink-0"
          >
            <i class="pi pi-graduation-cap text-2xl text-teal-600"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-900">
              {{ t("subject_detail.full_exam_title") }}
            </p>
            <p class="text-xs text-gray-500 mt-0.5">
              {{ t("subject_detail.full_exam_desc") }}
            </p>
            <div class="flex flex-wrap gap-3 mt-2">
              <span class="flex items-center gap-1 text-xs text-gray-400">
                <i class="pi pi-clock text-xs"></i>
                {{ totalMinutes }} {{ t("subject_detail.minutes") }}
              </span>
              <span class="flex items-center gap-1 text-xs text-gray-400">
                <i class="pi pi-list text-xs"></i>
                {{ subject.modules?.length }} {{ t("subject_detail.modules") }}
              </span>
              <span class="flex items-center gap-1 text-xs text-gray-400">
                <i class="pi pi-star text-xs"></i>
                {{ totalPoints }} {{ t("subject_detail.points") }}
              </span>
            </div>
          </div>
        </div>

        <button
          class="mt-4 w-full flex items-center justify-center gap-2 py-3 rounded-xl text-white text-sm font-semibold transition-all hover:opacity-90"
          style="background-color: #1cb098"
          @click="startFullExam"
        >
          <i class="pi pi-play text-xs"></i>
          {{ t("subject_detail.start_full_exam") }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const examsStore = useExamsStore();

const slug = route.params.slug as string;
const subjectId = route.params.subjectId as string;
const examId = route.query.examId as string;

const loading = ref(true);
const subject = ref<any>(null);
const examName = ref("");

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
});

// ── Modules à afficher (fusion Leseverstehen + Sprachbausteine) ──────
// Ces deux modules TELC partagent un temps commun (90min) selon la
// grille officielle. Quand l'un des deux a time_limit_minutes = 0
// (temps non individualisé côté génération), on les fusionne en une
// seule carte cliquable pour éviter un lancement avec un timer à 0.
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
    slug: "lese", // garde le slug lese pour hériter de l'icône/couleur Leseverstehen
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

const startModule = (module: any) => {
  if (module._mergedSlugs) {
    navigateTo({
      path: `/dashboard/examens/${slug}/session`,
      query: {
        examId,
        subjectId,
        moduleSlugs: module._mergedSlugs.join(","),
      },
    });
    return;
  }
  navigateTo({
    path: `/dashboard/examens/${slug}/session`,
    query: { examId, subjectId, moduleSlug: module.slug },
  });
};

const startFullExam = () => {
  navigateTo({
    path: `/dashboard/examens/${slug}/session`,
    query: { examId, subjectId },
  });
};

const getModuleIcon = (s: string) => {
  const slug = (s || "").toLowerCase();
  if (slug.includes("lese")) return "pi-book";
  if (slug.includes("hoer") || slug.includes("hör")) return "pi-volume-up";
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return "pi-pencil";
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return "pi-microphone";
  if (slug.includes("sprachbaustein")) return "pi-language";
  return "pi-file";
};

const getModuleBg = (s: string) => {
  const slug = (s || "").toLowerCase();
  if (slug.includes("lese")) return "bg-blue-50 group-hover:bg-blue-100";
  if (slug.includes("hoer") || slug.includes("hör"))
    return "bg-purple-50 group-hover:bg-purple-100";
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return "bg-green-50 group-hover:bg-green-100";
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return "bg-orange-50 group-hover:bg-orange-100";
  if (slug.includes("sprachbaustein"))
    return "bg-pink-50 group-hover:bg-pink-100";
  return "bg-gray-50 group-hover:bg-gray-100";
};

const getModuleIconColor = (s: string) => {
  const slug = (s || "").toLowerCase();
  if (slug.includes("lese")) return "text-blue-600";
  if (slug.includes("hoer") || slug.includes("hör")) return "text-purple-600";
  if (slug.includes("schreib") || slug.includes("schriftlich"))
    return "text-green-600";
  if (
    slug.includes("sprech") ||
    slug.includes("muendlich") ||
    slug.includes("mündlich")
  )
    return "text-orange-600";
  if (slug.includes("sprachbaustein")) return "text-pink-600";
  return "text-gray-600";
};
</script>
