<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Mes résultats</h1>
      <p class="text-gray-600">Historique de vos sessions d'examen</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 60px; height: 60px" />
    </div>

    <!-- Empty -->
    <div v-else-if="sessions.length === 0" class="text-center py-16">
      <div
        class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4"
      >
        <i class="pi pi-inbox text-3xl text-gray-400"></i>
      </div>
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Aucun résultat</h3>
      <p class="text-gray-600 mb-6">Vous n'avez pas encore passé d'examen.</p>
      <Button
        label="Commencer un examen"
        icon="pi pi-play"
        @click="navigateTo('/dashboard/examens')"
      />
    </div>

    <!-- Liste sessions -->
    <div v-else class="space-y-4">
      <!-- Filtres -->
      <div
        class="bg-white rounded-lg shadow-sm p-4 mb-6 flex flex-col sm:flex-row gap-4"
      >
        <Select
          v-model="filterStatus"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Tous les statuts"
          class="w-full sm:w-48"
        />
        <Select
          v-model="filterSort"
          :options="sortOptions"
          optionLabel="label"
          optionValue="value"
          class="w-full sm:w-48"
        />
        <Button
          v-if="filterStatus"
          label="Réinitialiser"
          icon="pi pi-times"
          text
          @click="filterStatus = ''"
        />
      </div>

      <!-- Stats rapides -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow-sm text-center">
          <div class="text-2xl font-bold text-gray-900">{{ stats.total }}</div>
          <div class="text-sm text-gray-500">Sessions totales</div>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center">
          <div class="text-2xl font-bold text-green-600">
            {{ stats.passed }}
          </div>
          <div class="text-sm text-gray-500">Réussies</div>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center">
          <div class="text-2xl font-bold text-blue-600">
            {{
              stats.avgScore !== null ? stats.avgScore.toFixed(1) + "%" : "—"
            }}
          </div>
          <div class="text-sm text-gray-500">Score moyen</div>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm text-center">
          <div class="text-2xl font-bold text-purple-600">
            {{ stats.pending }}
          </div>
          <div class="text-sm text-gray-500">En correction</div>
        </div>
      </div>

      <!-- Cards sessions -->
      <Card
        v-for="session in filteredSessions"
        :key="session.id"
        class="hover:shadow-md transition-shadow"
      >
        <template #content>
          <div
            class="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <!-- Infos exam -->
            <div class="flex items-center gap-4">
              <!-- Icône statut -->
              <div
                :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center shrink-0',
                  getStatusBg(session.status, session.passed),
                ]"
              >
                <i
                  :class="[
                    'pi text-xl',
                    getStatusIcon(session.status, session.passed),
                  ]"
                ></i>
              </div>

              <div>
                <h3 class="font-semibold text-gray-900">
                  {{ session.exam_name }}
                </h3>
                <div class="flex flex-wrap items-center gap-2 mt-1">
                  <Tag
                    :value="getStatusLabel(session.status, session.passed)"
                    :severity="
                      getStatusSeverity(session.status, session.passed)
                    "
                  />
                  <span class="text-xs text-gray-400">
                    {{ formatDate(session.started_at) }}
                  </span>
                  <span
                    v-if="session.duration_seconds"
                    class="text-xs text-gray-400"
                  >
                    • {{ formatDuration(session.duration_seconds) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Score + actions -->
            <div class="flex items-center gap-6 sm:gap-8">
              <!-- Score -->
              <div class="text-center">
                <div
                  :class="[
                    'text-2xl font-bold',
                    session.passed === true
                      ? 'text-green-600'
                      : session.passed === false
                        ? 'text-red-600'
                        : 'text-gray-500',
                  ]"
                >
                  {{
                    session.score !== null && session.score !== undefined
                      ? session.score.toFixed(1) + "%"
                      : "—"
                  }}
                </div>
                <div class="text-xs text-gray-500">Score</div>
              </div>

              <!-- Actions -->
              <div class="flex gap-2">
                <Button
                  v-if="session.status === 'IN_PROGRESS'"
                  icon="pi pi-play"
                  label="Continuer"
                  size="small"
                  @click="viewResult(session)"
                />
                <Button
                  v-else
                  icon="pi pi-eye"
                  outlined
                  rounded
                  v-tooltip.top="'Voir le détail'"
                  @click="viewResult(session)"
                />
              </div>
            </div>
          </div>

          <!-- Score breakdown si disponible -->
          <div
            v-if="
              session.score !== null &&
              session.score !== undefined &&
              session.status === 'COMPLETED'
            "
            class="mt-4 pt-4 border-t border-gray-100"
          >
            <ProgressBar
              :value="session.score"
              :showValue="false"
              :class="[
                'h-2',
                session.passed
                  ? '[&_.p-progressbar-value]:bg-green-500!'
                  : '[&_.p-progressbar-value]:bg-red-500!',
              ]"
            />
          </div>
        </template>
      </Card>

      <!-- Pagination simple -->
      <div v-if="hasMore" class="text-center pt-4">
        <Button
          label="Charger plus"
          icon="pi pi-chevron-down"
          outlined
          :loading="loadingMore"
          @click="loadMore"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SessionListResponse } from "#shared/api";

definePageMeta({
  layout: "dashboard",
  middleware: "auth",
});

const sessionStore = useSessionStore();

const loading = ref(true);
const loadingMore = ref(false);
const sessions = ref<SessionListResponse[]>([]);
const filterStatus = ref("");
const filterSort = ref("desc");
const skip = ref(0);
const limit = 20;
const hasMore = ref(false);

const statusOptions = [
  { label: "Tous les statuts", value: "" },
  { label: "Réussies", value: "passed" },
  { label: "Échouées", value: "failed" },
  { label: "En correction", value: "PENDING_REVIEW" },
  { label: "En cours", value: "IN_PROGRESS" },
];

const sortOptions = [
  { label: "Plus récentes d'abord", value: "desc" },
  { label: "Plus anciennes d'abord", value: "asc" },
];

// Filtrage local
const filteredSessions = computed(() => {
  let list = [...sessions.value];

  if (filterStatus.value === "passed") {
    list = list.filter((s) => s.passed === true);
  } else if (filterStatus.value === "failed") {
    list = list.filter((s) => s.passed === false);
  } else if (filterStatus.value) {
    list = list.filter((s) => s.status === filterStatus.value);
  }

  if (filterSort.value === "asc") {
    list.sort(
      (a, b) =>
        new Date(a.started_at).getTime() - new Date(b.started_at).getTime(),
    );
  } else {
    list.sort(
      (a, b) =>
        new Date(b.started_at).getTime() - new Date(a.started_at).getTime(),
    );
  }

  return list;
});

// Stats calculées
const stats = computed(() => {
  const total = sessions.value.length;
  const passed = sessions.value.filter((s) => s.passed === true).length;
  const pending = sessions.value.filter(
    (s) => s.status === "PENDING_REVIEW",
  ).length;
  const completed = sessions.value.filter(
    (s) => s.score !== null && s.score !== undefined,
  );
  const avgScore =
    completed.length > 0
      ? completed.reduce((sum, s) => sum + (s.score ?? 0), 0) / completed.length
      : null;

  return { total, passed, pending, avgScore };
});

// Helpers statut
const getStatusIcon = (status: string, passed: boolean | null | undefined) => {
  if (status === "IN_PROGRESS") return "pi-play text-blue-600";
  if (status === "PENDING_REVIEW") return "pi-clock text-amber-600";
  if (passed === true) return "pi-check-circle text-green-600";
  if (passed === false) return "pi-times-circle text-red-600";
  return "pi-circle text-gray-400";
};

const getStatusBg = (status: string, passed: boolean | null | undefined) => {
  if (status === "IN_PROGRESS") return "bg-blue-50";
  if (status === "PENDING_REVIEW") return "bg-amber-50";
  if (passed === true) return "bg-green-50";
  if (passed === false) return "bg-red-50";
  return "bg-gray-50";
};

const getStatusLabel = (status: string, passed: boolean | null | undefined) => {
  if (status === "IN_PROGRESS") return "En cours";
  if (status === "PENDING_REVIEW") return "En correction";
  if (passed === true) return "Réussi";
  if (passed === false) return "Échoué";
  return "Terminé";
};

const getStatusSeverity = (
  status: string,
  passed: boolean | null | undefined,
) => {
  if (status === "IN_PROGRESS") return "info";
  if (status === "PENDING_REVIEW") return "warn";
  if (passed === true) return "success";
  if (passed === false) return "danger";
  return "secondary";
};

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatDuration = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m${s.toString().padStart(2, "0")}s`;
};

const viewResult = (session: SessionListResponse) => {
  if (session.status === "IN_PROGRESS") {
    // Continuer la session
    navigateTo(
      `/dashboard/examens/${session.exam_slug}/session?examId=${session.exam_id}`,
    );
  } else {
    navigateTo(
      `/dashboard/examens/${session.exam_slug}/result?sessionId=${session.id}`,
    );
  }
};

// Chargement
const loadSessions = async () => {
  loading.value = true;
  const res = await sessionStore.getMySessions(0, limit);
  if (res.success && res.data) {
    sessions.value = res.data;
    hasMore.value = res.data.length === limit;
    skip.value = limit;
  }
  loading.value = false;
};

const loadMore = async () => {
  loadingMore.value = true;
  const res = await sessionStore.getMySessions(skip.value, limit);
  if (res.success && res.data) {
    sessions.value.push(...res.data);
    hasMore.value = res.data.length === limit;
    skip.value += limit;
  }
  loadingMore.value = false;
};

onMounted(() => loadSessions());
</script>
