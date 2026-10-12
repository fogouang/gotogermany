<!-- pages/centre/succursales.vue -->
<template>
  <div class="space-y-5">
    <!-- ── En-tête ── -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <p class="text-sm text-muted">
        {{ t("centre.branches.count", branches.length) }}
        <span v-if="branches.length" class="text-faint">
          · {{ t("centre.branches.students", totalStudents) }}
        </span>
      </p>
      <Button
        :label="t('centre.branches.new')"
        icon="pi pi-plus"
        class="w-full sm:w-auto"
        @click="openCreateDialog"
      />
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div v-for="n in 3" :key="n" class="h-36 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="branches.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <i class="pi pi-sitemap" />
      </span>
      <p class="text-sm font-medium text-ink">{{ t("centre.branches.empty_title") }}</p>
      <p class="max-w-sm text-xs text-muted">{{ t("centre.branches.empty_text") }}</p>
    </div>

    <!-- ── Succursales ── -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="branch in sortedBranches"
        :key="branch.id"
        class="flex flex-col rounded-card border bg-card p-5 shadow-soft"
        :class="branch.is_main ? 'border-primary/40' : 'border-line'"
      >
        <div class="flex items-start justify-between gap-3">
          <span
            class="flex size-10 shrink-0 items-center justify-center rounded-leaf"
            :class="branch.is_main ? 'bg-primary/10 text-primary' : 'bg-card-2 text-muted'"
          >
            <i :class="branch.is_main ? 'pi pi-building' : 'pi pi-map-marker'" />
          </span>
          <span
            class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="branch.is_main ? 'bg-primary/10 text-primary' : 'bg-card-2 text-muted'"
          >
            {{ branch.is_main ? t("centre.branches.main") : t("centre.branches.secondary") }}
          </span>
        </div>

        <h3 class="mt-4 truncate font-semibold text-ink">{{ branch.name }}</h3>

        <div class="mt-auto flex items-end justify-between gap-3 pt-4">
          <p class="text-2xl font-bold text-ink">
            {{ studentCount(branch.id) }}
            <span class="text-xs font-normal text-muted">
              {{ t("centre.branches.students_label", studentCount(branch.id)) }}
            </span>
          </p>
          <p class="text-xs text-muted">
            {{ t("centre.branches.created_on", { date: formatDate(branch.created_at) }) }}
          </p>
        </div>
      </article>
    </div>

    <!-- ── Création ── -->
    <Dialog
      v-model:visible="showCreateDialog"
      :header="t('centre.branches.new')"
      modal
      :style="{ width: '95vw', maxWidth: '28rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleCreate">
        <div>
          <label for="branch-name" class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.branches.name_label") }}
          </label>
          <InputText
            id="branch-name"
            v-model="newBranchName"
            class="w-full"
            :placeholder="t('centre.branches.name_placeholder')"
            autofocus
          />
        </div>
        <Message v-if="createError" severity="error" :closable="false">{{ createError }}</Message>
      </form>
      <template #footer>
        <Button :label="t('common.cancel')" text @click="showCreateDialog = false" />
        <Button :label="t('common.create')" icon="pi pi-check" :loading="creating" @click="handleCreate" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { BranchResponse } from "#shared/api";

definePageMeta({ layout: "centre", watermark: "Zweigstellen" });

const { t, locale } = useI18n();
const centerStaffStore = useCenterStaffStore();
const toast = useToast();

const loading = ref(true);
const branches = ref<BranchResponse[]>([]);
const countsByBranch = ref<Record<string, number>>({});
const errorMessage = ref<string | null>(null);

// La succursale principale d'abord, puis par ordre alphabétique
const sortedBranches = computed(() =>
  [...branches.value].sort(
    (a, b) => Number(b.is_main) - Number(a.is_main) || a.name.localeCompare(b.name),
  ),
);

const totalStudents = computed(() =>
  Object.values(countsByBranch.value).reduce((sum, n) => sum + n, 0),
);

function studentCount(branchId: string) {
  return countsByBranch.value[branchId] ?? 0;
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

async function loadBranches() {
  loading.value = true;

  const [branchResult, studentsResult] = await Promise.all([
    centerStaffStore.fetchMyBranches(),
    centerStaffStore.fetchStudentsByCenter(),
  ]);

  if (branchResult.success) {
    branches.value = branchResult.branches ?? [];
    errorMessage.value = null;
  } else {
    errorMessage.value = branchResult.error || t("common.load_error");
  }

  if (studentsResult.success) {
    const counts: Record<string, number> = {};
    for (const s of studentsResult.students ?? []) {
      if (s.branch_id) counts[s.branch_id] = (counts[s.branch_id] ?? 0) + 1;
    }
    countsByBranch.value = counts;
  }

  loading.value = false;
}

// ── Création ──
const showCreateDialog = ref(false);
const newBranchName = ref("");
const creating = ref(false);
const createError = ref<string | null>(null);

function openCreateDialog() {
  newBranchName.value = "";
  createError.value = null;
  showCreateDialog.value = true;
}

async function handleCreate() {
  if (!newBranchName.value.trim()) {
    createError.value = t("centre.branches.name_required");
    return;
  }
  creating.value = true;
  createError.value = null;
  const result = await centerStaffStore.createMyBranch({
    name: newBranchName.value.trim(),
  });
  creating.value = false;
  if (result.success) {
    showCreateDialog.value = false;
    toast.add({ severity: "success", summary: t("centre.branches.created"), life: 3000 });
    await loadBranches();
  } else {
    createError.value = result.error || t("centre.branches.create_error");
  }
}

onMounted(loadBranches);
</script>