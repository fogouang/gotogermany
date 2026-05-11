<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">
        Bonjour, {{ authStore.userName }} 👋
      </h1>
      <p class="text-gray-600 mt-2">Bienvenue sur votre tableau de bord</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Examens disponibles -->
      <Card class="lg:col-span-2">
        <template #title>
          <div class="flex items-center justify-between">
            <span>Commencer un examen</span>
            <Button
              label="Voir tout"
              text
              size="small"
              @click="navigateTo('/dashboard/examens')"
            />
          </div>
        </template>
        <template #content>
          <div v-if="examsStore.loading" class="text-center py-8">
            <ProgressSpinner style="width: 50px; height: 50px" />
          </div>

          <div
            v-else-if="examsStore.catalog.length === 0"
            class="text-center py-8 text-gray-500"
          >
            <i class="pi pi-inbox text-4xl mb-4 block"></i>
            <p>Aucun examen disponible</p>
          </div>

          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              v-for="exam in examsStore.catalog.slice(0, 4)"
              :key="exam.id"
              class="border border-gray-100 rounded-xl p-4 hover:shadow-md hover:border-primary-200 transition-all cursor-pointer"
              @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="flex-1 min-w-0">
                  <h3 class="font-semibold text-gray-900 truncate">
                    {{ exam.name }}
                  </h3>
                  <p class="text-xs text-primary-600 font-medium mt-0.5">
                    {{ exam.provider.toUpperCase() }}
                  </p>
                </div>
                <Tag
                  :value="`${exam.levels?.length || 0} niveaux`"
                  severity="secondary"
                  class="shrink-0 ml-2"
                />
              </div>
              <p class="text-sm text-gray-500 line-clamp-2">
                {{
                  exam.description ||
                  "Préparez-vous efficacement pour cet examen"
                }}
              </p>
              <div class="flex flex-wrap gap-1 mt-3">
                <Tag
                  v-for="level in exam.levels?.slice(0, 3)"
                  :key="level.id"
                  :value="level.cefr_code"
                  size="small"
                  severity="info"
                />
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Sessions récentes -->
      <Card>
        <template #title>Sessions récentes</template>
        <template #content>
          <div v-if="sessionsLoading" class="text-center py-8">
            <ProgressSpinner style="width: 40px; height: 40px" />
          </div>

          <div v-else-if="recentSessions.length === 0" class="text-center py-8">
            <i class="pi pi-history text-4xl text-gray-300 mb-3 block"></i>
            <p class="text-sm text-gray-500">Aucune session pour le moment</p>
            <Button
              label="Commencer un examen"
              text
              size="small"
              class="mt-3"
              @click="navigateTo('/dashboard/examens')"
            />
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="s in recentSessions"
              :key="s.id"
              class="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div
                :class="[
                  'w-9 h-9 rounded-lg flex items-center justify-center shrink-0',
                  s.status === 'COMPLETED'
                    ? 'bg-success-100'
                    : 'bg-secondary-100',
                ]"
              >
                <i
                  :class="[
                    'pi text-sm',
                    s.status === 'COMPLETED'
                      ? 'pi-check text-success-600'
                      : 'pi-clock text-secondary-600',
                  ]"
                ></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ s.exam_name }}
                </p>
                <p class="text-xs text-gray-500">
                  Sujet {{ s.subject_number }} •
                  {{ formatDate(s.started_at) }}
                </p>
              </div>
              <span
                v-if="s.score_percentage != null"
                :class="[
                  'text-sm font-semibold shrink-0',
                  s.score_percentage >= 60
                    ? 'text-success-600'
                    : 'text-danger-600',
                ]"
              >
                {{ s.score_percentage }}%
              </span>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const authStore = useAuthStore();
const examsStore = useExamsStore();
const sessionStore = useSessionStore();

const sessionsLoading = ref(false);
const recentSessions = ref<any[]>([]);

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
};

onMounted(async () => {
  if (examsStore.catalog.length === 0) {
    await examsStore.fetchCatalog();
  }

  sessionsLoading.value = true;
  const result = await sessionStore.getMySessions(0, 5);
  if (result.success) recentSessions.value = result.data || [];
  sessionsLoading.value = false;
});
</script>
