<template>
  <div>
    <!-- Loading State -->
    <div v-if="examsStore.loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 60px; height: 60px" />
    </div>

    <!-- Error State -->
    <div v-else-if="!exam" class="text-center py-16">
      <div
        class="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4"
      >
        <i class="pi pi-exclamation-triangle text-3xl text-red-600"></i>
      </div>
      <h3 class="text-lg font-semibold text-gray-900 mb-2">
        Examen introuvable
      </h3>
      <p class="text-gray-600 mb-6">
        Cet examen n'existe pas ou n'est plus disponible.
      </p>
      <Button
        label="Retour aux examens"
        icon="pi pi-arrow-left"
        @click="navigateTo('/dashboard/examens')"
      />
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Breadcrumb -->
      <Breadcrumb :home="homeItem" :model="breadcrumbItems" class="mb-6" />

      <!-- Header -->
      <div
        class="bg-linear-to-br from-teal-600 to-blue-600 rounded-2xl p-8 mb-8 text-white"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div
              class="inline-flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full text-sm mb-4"
            >
              <i class="pi pi-bookmark"></i>
              <span>{{ exam.provider.toUpperCase() }}</span>
            </div>
            <h1 class="text-4xl font-bold mb-3">{{ exam.name }}</h1>
            <p class="text-teal-50 text-lg max-w-3xl">
              {{
                exam.description ||
                "Préparez-vous efficacement pour cet examen d'allemand avec nos tests adaptatifs."
              }}
            </p>
          </div>
          <Button
            icon="pi pi-arrow-left"
            rounded
            text
            class="text-white!"
            @click="navigateTo('/dashboard/examens')"
          />
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-8">
          <div class="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div class="text-2xl font-bold mb-1">
              {{ exam.levels?.length || 0 }}
            </div>
            <div class="text-sm text-teal-100">Niveaux disponibles</div>
          </div>
          <div class="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div class="text-2xl font-bold mb-1">{{ totalSubjects }}</div>
            <div class="text-sm text-teal-100">Sujets disponibles</div>
          </div>
          <div class="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
            <div class="text-2xl font-bold mb-1">{{ freeLevelsCount }}</div>
            <div class="text-sm text-teal-100">Niveaux gratuits</div>
          </div>
        </div>
      </div>

      <!-- Levels List -->
      <div>
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Niveaux et sujets</h2>

        <div
          v-if="!exam.levels || exam.levels.length === 0"
          class="text-center py-12 bg-gray-50 rounded-lg"
        >
          <i class="pi pi-info-circle text-4xl text-gray-400 mb-4"></i>
          <p class="text-gray-600">Aucun niveau disponible pour cet examen</p>
        </div>

        <Accordion v-else :multiple="true" :activeIndex="[0]">
          <AccordionTab v-for="level in sortedLevels" :key="level.id">
            <template #header>
              <div class="flex items-center justify-between w-full pr-4">
                <div class="flex items-center gap-4">
                  <div
                    :class="[
                      'w-12 h-12 rounded-lg flex items-center justify-center',
                      getLevelBgColor(level.cefr_code),
                    ]"
                  >
                    <span
                      :class="[
                        'text-lg font-bold',
                        getLevelTextColor(level.cefr_code),
                      ]"
                    >
                      {{ level.cefr_code }}
                    </span>
                  </div>
                  <div>
                    <h3 class="font-semibold text-gray-900">
                      Niveau {{ level.cefr_code }} -
                      {{ getLevelName(level.cefr_code) }}
                    </h3>
                    <p class="text-sm text-gray-600">
                      {{ level.subjects?.length || 0 }} sujet(s) • Score minimum
                      : {{ level.total_pass_score }}
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <Tag
                    v-if="hasAccess(level)"
                    value="Accès actif"
                    severity="success"
                    icon="pi pi-lock-open"
                  />
                  <Tag
                    v-else-if="level.is_free"
                    value="Gratuit"
                    severity="info"
                    icon="pi pi-lock-open"
                  />
                  <Tag
                    v-else
                    value="Premium"
                    severity="warning"
                    icon="pi pi-lock"
                  />
                </div>
              </div>
            </template>

            <!-- Pas de sujets -->
            <div
              v-if="!level.subjects || level.subjects.length === 0"
              class="text-center py-8 text-gray-500"
            >
              <i class="pi pi-inbox text-3xl mb-2"></i>
              <p>Aucun sujet disponible pour ce niveau</p>
            </div>

            <!-- Sujets -->
            <div v-else class="space-y-6 pt-4">
              <div v-for="subject in level.subjects" :key="subject.id">
                <!-- Sujet header -->
                <div class="flex items-center justify-between mb-3">
                  <h4
                    class="text-sm font-semibold text-gray-700 flex items-center gap-2"
                  >
                    <i class="pi pi-file text-teal-600"></i>
                    {{ subject.name || `Sujet ${subject.subject_number}` }}
                  </h4>
                  <Button
                    :label="
                      hasAccess(level) || level.is_free
                        ? 'Commencer ce sujet'
                        : 'Acheter l\'accès'
                    "
                    :icon="
                      hasAccess(level) || level.is_free
                        ? 'pi pi-play'
                        : 'pi pi-lock'
                    "
                    :severity="
                      hasAccess(level) || level.is_free ? 'primary' : 'warning'
                    "
                    size="small"
                    @click="startSubject(level, subject.id)"
                  />
                </div>

                <!-- Modules du sujet -->
                <div
                  class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                >
                  <Card
                    v-for="module in subject.modules"
                    :key="module.id"
                    class="hover:shadow-md transition-shadow"
                  >
                    <template #title>
                      <div class="flex items-center gap-3">
                        <div
                          :class="[
                            'w-10 h-10 rounded-lg flex items-center justify-center',
                            getModuleColor(module.slug),
                          ]"
                        >
                          <i
                            :class="['pi text-lg', getModuleIcon(module.slug)]"
                          ></i>
                        </div>
                        <div>
                          <h4 class="text-base font-semibold text-gray-900">
                            {{ module.name }}
                          </h4>
                          <p class="text-xs text-gray-500 mt-1">
                            {{ module.slug }}
                          </p>
                        </div>
                      </div>
                    </template>

                    <template #content>
                      <div class="space-y-3">
                        <div class="flex items-center justify-between text-sm">
                          <div class="flex items-center gap-2 text-gray-600">
                            <i class="pi pi-clock"></i>
                            <span>{{ module.time_limit_minutes }} min</span>
                          </div>
                          <div class="flex items-center gap-2 text-gray-600">
                            <i class="pi pi-star"></i>
                            <span>{{ module.max_score }} pts</span>
                          </div>
                        </div>
                        <div v-if="module.teile && module.teile.length > 0">
                          <Divider />
                          <div class="space-y-2">
                            <h5
                              class="text-xs font-semibold text-gray-700 uppercase"
                            >
                              Parties
                            </h5>
                            <div class="flex flex-wrap gap-2">
                              <Tag
                                v-for="teil in module.teile"
                                :key="teil.id"
                                :value="`Teil ${teil.teil_number}`"
                                severity="secondary"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </template>
                  </Card>
                </div>
              </div>
            </div>
          </AccordionTab>
        </Accordion>
      </div>

      <!-- CTA Section -->
      <Card
        class="mt-8 bg-linear-to-br from-teal-50 to-blue-50 border-2 border-teal-200"
      >
        <template #content>
          <div
            class="flex flex-col md:flex-row items-center justify-between gap-6"
          >
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900 mb-2">
                Prêt à commencer votre préparation ?
              </h3>
              <p class="text-gray-700">
                Accédez à tous les niveaux et sujets pour progresser rapidement.
              </p>
            </div>
            <div class="flex gap-3">
              <Button
                label="Commencer gratuitement"
                icon="pi pi-play"
                size="large"
                @click="startFreeLevel"
              />
              <Button
                label="Voir les tarifs"
                icon="pi pi-tag"
                outlined
                size="large"
                @click="navigateTo('/dashboard/tarifs')"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {
  ExamDetailResponse,
  LevelWithSubjectsResponse,
} from "#shared/api";

definePageMeta({ layout: "dashboard", middleware: "auth" });

const route = useRoute();
const examsStore = useExamsStore();
const slug = computed(() => route.params.slug as string);

const homeItem = ref({ icon: "pi pi-home", to: "/dashboard" });
const breadcrumbItems = computed(() => [
  { label: "Examens", to: "/dashboard/examens" },
  { label: exam.value?.name || "Détails" },
]);

const exam = computed<ExamDetailResponse | null>(() => examsStore.currentExam);

const sortedLevels = computed(() => {
  if (!exam.value?.levels) return [];
  return [...exam.value.levels].sort(
    (a, b) => a.display_order - b.display_order,
  );
});

const totalSubjects = computed(() => {
  if (!exam.value?.levels) return 0;
  return exam.value.levels.reduce(
    (sum, level) => sum + (level.subjects?.length || 0),
    0,
  );
});

const freeLevelsCount = computed(() => {
  if (!exam.value?.levels) return 0;
  return exam.value.levels.filter((l) => l.is_free).length;
});

const hasAccess = (level: LevelWithSubjectsResponse): boolean => {
  const catalogExam = examsStore.catalog.find((e) => e.slug === slug.value);
  const catalogLevel = catalogExam?.levels?.find((l) => l.id === level.id);
  return catalogLevel?.has_access ?? level.is_free;
};

const getLevelName = (cefrCode: string) => {
  const names: Record<string, string> = {
    A1: "Débutant",
    A2: "Élémentaire",
    B1: "Intermédiaire",
    B2: "Indépendant",
    C1: "Autonome",
    C2: "Maîtrise",
  };
  return names[cefrCode] || cefrCode;
};

const getLevelBgColor = (cefrCode: string) => {
  const colors: Record<string, string> = {
    A1: "bg-green-100",
    A2: "bg-green-100",
    B1: "bg-blue-100",
    B2: "bg-blue-100",
    C1: "bg-purple-100",
    C2: "bg-purple-100",
  };
  return colors[cefrCode] || "bg-gray-100";
};

const getLevelTextColor = (cefrCode: string) => {
  const colors: Record<string, string> = {
    A1: "text-green-700",
    A2: "text-green-700",
    B1: "text-blue-700",
    B2: "text-blue-700",
    C1: "text-purple-700",
    C2: "text-purple-700",
  };
  return colors[cefrCode] || "text-gray-700";
};

const getModuleIcon = (moduleSlug: string) => {
  const icons: Record<string, string> = {
    horen: "pi-volume-up",
    lesen: "pi-book",
    schreiben: "pi-pencil",
    sprechen: "pi-microphone",
  };
  for (const key in icons) {
    if (moduleSlug.toLowerCase().includes(key)) return icons[key]!;
  }
  return "pi-file";
};

const getModuleColor = (moduleSlug: string) => {
  const colors: Record<string, string> = {
    horen: "bg-purple-100 text-purple-600",
    lesen: "bg-blue-100 text-blue-600",
    schreiben: "bg-green-100 text-green-600",
    sprechen: "bg-orange-100 text-orange-600",
  };
  for (const key in colors) {
    if (moduleSlug.toLowerCase().includes(key)) return colors[key]!;
  }
  return "bg-gray-100 text-gray-600";
};

// Démarrer sur un sujet précis
const startSubject = (level: LevelWithSubjectsResponse, subjectId: string) => {
  if (!exam.value) return;
  if (!hasAccess(level) && !level.is_free) {
    // Rediriger vers paiement avec exam_id
    navigateTo(`/dashboard/paiement?exam_id=${exam.value.id}`);
    return;
  }
  navigateTo({
    path: `/dashboard/examens/${slug.value}/session`,
    query: { examId: exam.value.id, subjectId },
  });
};

// Démarrer sur le premier level accessible (sujet choisi auto par backend)
const startModule = (level: LevelWithSubjectsResponse) => {
  if (!exam.value) return;
  if (!hasAccess(level) && !level.is_free) {
    navigateTo(`/dashboard/paiement?exam_id=${exam.value.id}`);
    return;
  }
  navigateTo({
    path: `/dashboard/examens/${slug.value}/session`,
    query: { examId: exam.value.id },
  });
};

const startFreeLevel = () => {
  const freeLevel = sortedLevels.value.find((l) => l.is_free);
  if (freeLevel) startModule(freeLevel);
};

onMounted(async () => {
  await Promise.all([
    examsStore.fetchExamBySlug(slug.value),
    examsStore.fetchCatalog(),
  ]);
});

onUnmounted(() => examsStore.clearCurrentExam());
</script>
