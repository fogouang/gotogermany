<template>
  <section class="py-20 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section Header -->
      <div class="text-center mb-16">
        <div
          class="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200 mb-4"
        >
          <i class="pi pi-flag text-yellow-500"></i>
          <span class="text-sm font-semibold text-gray-700"
            >Examens officiels</span
          >
        </div>
        <h2 class="text-4xl font-bold text-gray-900 mb-4">
          Choisissez votre certification
        </h2>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          Simulations conformes aux examens Goethe-Institut et ÖSD
        </p>
      </div>

      <!-- Grid des examens -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <Card
          v-for="exam in availableExams"
          :key="exam.id"
          class="shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer transform hover:-translate-y-2 border-0 overflow-hidden group"
          @click="startExam(exam.id)"
        >
          <template #header>
            <!-- Header avec drapeau allemand (noir, rouge, jaune) -->
            <div
              class="relative bg-gradient-to-br from-gray-900 via-red-700 to-yellow-500 p-8 text-white overflow-hidden"
            >
              <!-- Pattern background -->
              <div class="absolute inset-0 opacity-10">
                <div class="absolute top-0 left-0 w-full h-1/3 bg-black"></div>
                <div
                  class="absolute top-1/3 left-0 w-full h-1/3 bg-red-600"
                ></div>
                <div
                  class="absolute bottom-0 left-0 w-full h-1/3 bg-yellow-400"
                ></div>
              </div>

              <div class="relative z-10">
                <div class="flex items-center justify-between mb-3">
                  <Tag
                    :value="exam.cefr_level"
                    class="!bg-yellow-400 !text-gray-900 !font-bold !px-4 !py-2"
                  />
                  <i class="pi pi-award text-3xl text-yellow-400"></i>
                </div>
                <h3 class="text-2xl font-bold leading-tight">
                  {{ exam.name }}
                </h3>
              </div>
            </div>
          </template>

          <template #content>
            <div class="space-y-5 p-2">
              <!-- Description -->
              <p class="text-gray-600 leading-relaxed">
                {{ exam.description }}
              </p>

              <!-- Modules avec icônes -->
              <div>
                <h4
                  class="font-semibold text-gray-900 mb-3 flex items-center gap-2"
                >
                  <i class="pi pi-book text-red-600"></i>
                  Modules
                </h4>
                <div class="flex flex-wrap gap-2">
                  <Tag
                    v-for="module in exam.modules"
                    :key="module"
                    :value="module"
                    severity="contrast"
                    class="!bg-gray-100 !text-gray-800 !font-medium"
                  />
                </div>
              </div>

              <!-- Statistiques -->
              <div class="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div class="text-center p-3 bg-yellow-50 rounded-lg">
                  <i class="pi pi-clock text-yellow-600 text-xl mb-2"></i>
                  <p class="text-sm text-gray-600 mb-1">Durée</p>
                  <p class="font-bold text-gray-900 text-lg">
                    {{ exam.duration }} min
                  </p>
                </div>
                <div class="text-center p-3 bg-red-50 rounded-lg">
                  <i class="pi pi-list text-red-600 text-xl mb-2"></i>
                  <p class="text-sm text-gray-600 mb-1">Questions</p>
                  <p class="font-bold text-gray-900 text-lg">
                    {{ exam.totalQuestions }}
                  </p>
                </div>
              </div>
            </div>
          </template>

          <template #footer>
            <div class="flex gap-3 p-2">
              <Button
                label="Commencer"
                icon="pi pi-play"
                class="flex-1 !bg-gradient-to-r !from-yellow-400 !to-yellow-500 !border-0 !text-gray-900 !font-bold hover:!from-yellow-500 hover:!to-yellow-600 shadow-lg"
                @click.stop="startExam(exam.id)"
              />
              <Button
                icon="pi pi-info-circle"
                outlined
                severity="secondary"
                class="!border-2 hover:!bg-gray-100"
                @click.stop="showExamInfo(exam)"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Dialog info examen -->
    <Dialog
      v-model:visible="showInfoDialog"
      :header="selectedExam?.name"
      :modal="true"
      :style="{ width: '50rem' }"
      class="exam-dialog"
    >
      <div v-if="selectedExam" class="space-y-6">
        <!-- À propos -->
        <div class="bg-gray-50 p-4 rounded-lg">
          <h3 class="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <i class="pi pi-info-circle text-yellow-600"></i>
            À propos de cet examen
          </h3>
          <p class="text-gray-700 leading-relaxed">
            {{ selectedExam.description }}
          </p>
        </div>

        <Divider />

        <!-- Structure de l'examen -->
        <div>
          <h3 class="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <i class="pi pi-list text-red-600"></i>
            Structure de l'examen
          </h3>
          <div class="space-y-3">
            <div
              v-for="(module, index) in selectedExam.moduleDetails"
              :key="module.name"
              class="flex justify-between items-center p-4 rounded-lg border-l-4 transition-all hover:shadow-md"
              :class="[
                index === 0 ? 'bg-gray-50 border-gray-900' : '',
                index === 1 ? 'bg-red-50 border-red-600' : '',
                index === 2 ? 'bg-yellow-50 border-yellow-500' : '',
                index === 3 ? 'bg-gray-100 border-gray-700' : '',
              ]"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center"
                >
                  <i
                    :class="[
                      'text-xl',
                      index === 0 ? 'pi pi-book text-gray-900' : '',
                      index === 1 ? 'pi pi-volume-up text-red-600' : '',
                      index === 2 ? 'pi pi-pencil text-yellow-600' : '',
                      index === 3 ? 'pi pi-comments text-gray-700' : '',
                    ]"
                  ></i>
                </div>
                <div>
                  <p class="font-bold text-gray-900">{{ module.name }}</p>
                  <p class="text-sm text-gray-600">
                    {{ module.parts }} parties
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p
                  class="font-bold text-lg"
                  :class="[
                    index === 0 ? 'text-gray-900' : '',
                    index === 1 ? 'text-red-600' : '',
                    index === 2 ? 'text-yellow-600' : '',
                    index === 3 ? 'text-gray-700' : '',
                  ]"
                >
                  {{ module.duration }} min
                </p>
                <p class="text-sm text-gray-600">
                  {{ module.questions }} questions
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Info supplémentaire -->
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
          <div class="flex items-start gap-3">
            <i class="pi pi-lightbulb text-yellow-600 text-xl mt-1"></i>
            <div>
              <p class="font-semibold text-gray-900 mb-1">Conseil</p>
              <p class="text-sm text-gray-700">
                Assurez-vous d'avoir environ
                {{ selectedExam.duration + 30 }} minutes devant vous pour
                compléter l'examen dans de bonnes conditions.
              </p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-3">
          <Button
            label="Annuler"
            outlined
            severity="secondary"
            @click="showInfoDialog = false"
          />
          <Button
            label="Commencer l'examen"
            icon="pi pi-play"
            iconPos="right"
            class="!bg-gradient-to-r !from-yellow-400 !to-yellow-500 !border-0 !text-gray-900 !font-bold"
            @click="startExamFromDialog"
          />
        </div>
      </template>
    </Dialog>
  </section>
</template>

<style scoped>
/* Animation pour les cards */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.group:hover {
  animation: slideUp 0.3s ease-out;
}
</style>

<script setup lang="ts">
const router = useRouter();
const showInfoDialog = ref(false);
const selectedExam = ref<any>(null);

const availableExams = ref([
  {
    id: "goethe_osd_b1",
    name: "Goethe-ÖSD Zertifikat B1",
    cefr_level: "B1",
    description:
      "Certification reconnue internationalement pour le niveau B1. Valide pour études, immigration et emploi.",
    modules: ["Lesen", "Hören", "Schreiben", "Sprechen"],
    moduleDetails: [
      { name: "Lesen", duration: 65, questions: 30, parts: 5 },
      { name: "Hören", duration: 40, questions: 30, parts: 4 },
      { name: "Schreiben", duration: 60, questions: 3, parts: 3 },
      { name: "Sprechen", duration: 15, questions: 3, parts: 3 },
    ],
    duration: 180,
    totalQuestions: 66,
  },
  {
    id: "goethe_osd_b2",
    name: "Goethe-ÖSD Zertifikat B2",
    cefr_level: "B2",
    description: "Certification pour niveau avancé B2",
    modules: ["Lesen", "Hören", "Schreiben", "Sprechen"],
    moduleDetails: [
      { name: "Lesen", duration: 70, questions: 35, parts: 5 },
      { name: "Hören", duration: 45, questions: 35, parts: 4 },
      { name: "Schreiben", duration: 75, questions: 2, parts: 2 },
      { name: "Sprechen", duration: 15, questions: 3, parts: 3 },
    ],
    duration: 210,
    totalQuestions: 70,
  },
]);

const startExam = (examId: string) => {
  router.push(`/exam/${examId}`);
};

const showExamInfo = (exam: any) => {
  selectedExam.value = exam;
  showInfoDialog.value = true;
};

const startExamFromDialog = () => {
  if (selectedExam.value) {
    showInfoDialog.value = false;
    startExam(selectedExam.value.id);
  }
};
</script>
