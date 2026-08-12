<!-- pages/admin/start-deutsch/index.vue -->
<template>
  <div class="space-y-6 pb-10">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-ink">Sujets Start Deutsch</h1>
        <p class="text-sm text-ink-secondary mt-1">
          Gestion des sujets A1/A2 importés.
        </p>
      </div>
      <Button
        label="Nouveau sujet"
        icon="pi pi-plus"
        @click="navigateTo('/admin/start-deutsch/import')"
      />
    </div>

    <!-- Filtre niveau -->
    <div class="flex gap-2">
      <button
        v-for="opt in levelOptions"
        :key="opt.value"
        class="rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
        :class="
          filterLevel === opt.value
            ? 'border-primary-500 bg-primary-500 text-white'
            : 'border-line bg-card text-ink-secondary hover:bg-hover'
        "
        @click="filterLevel = opt.value"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="filteredSubjects.length === 0"
      class="text-center py-16 bg-card rounded-xl border border-line"
    >
      <i class="pi pi-inbox text-4xl text-ink-tertiary mb-3 block"></i>
      <p class="text-sm text-ink-secondary mb-4">Aucun sujet pour l'instant.</p>
      <Button
        label="Créer le premier sujet"
        icon="pi pi-plus"
        outlined
        size="small"
        @click="navigateTo('/admin/start-deutsch/import')"
      />
    </div>

    <!-- Liste -->
    <div
      v-else
      class="bg-card border border-line rounded-xl overflow-hidden divide-y divide-line"
    >
      <div
        v-for="subject in filteredSubjects"
        :key="subject.id"
        class="flex items-center gap-4 px-5 py-4"
      >
        <span
          class="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-secondary-50 text-secondary-700 font-bold text-sm shrink-0"
        >
          {{ subject.level }}
        </span>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <p class="font-semibold text-ink truncate">{{ subject.title }}</p>
            <span
              class="text-xs font-bold px-2 py-0.5 rounded-full shrink-0"
              :class="
                subject.is_active
                  ? 'bg-success-100 text-success-700'
                  : 'bg-hover text-ink-tertiary'
              "
            >
              {{ subject.is_active ? "Actif" : "Inactif" }}
            </span>
          </div>
          <p class="text-xs text-ink-tertiary mt-0.5">
            Sujet n°{{ subject.subject_number }} · {{ subject.id }}
          </p>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <Button
            icon="pi pi-volume-up"
            text
            rounded
            size="small"
            v-tooltip.top="'Importer audio pour ce sujet'"
            @click="
              navigateTo(`/admin/start-deutsch/import?subjectId=${subject.id}`)
            "
          />
          <Button
            icon="pi pi-trash"
            text
            rounded
            size="small"
            severity="danger"
            v-tooltip.top="'Supprimer'"
            @click="openDelete(subject)"
          />
        </div>
      </div>
    </div>

    <!-- ─── Dialog Supprimer ──────────────────────────── -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le sujet ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '420px' }"
    >
      <div class="space-y-3 mt-2">
        <Message severity="error" :closable="false">
          Cette action est <strong>irréversible</strong>. Toutes les questions,
          sessions et corrections liées à ce sujet seront supprimées.
        </Message>
        <div class="bg-hover rounded-lg p-3 flex items-center gap-3">
          <div
            class="w-9 h-9 bg-secondary-600 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0"
          >
            {{ selectedSubject?.level }}
          </div>
          <div class="min-w-0">
            <p class="font-medium text-sm text-ink truncate">
              {{ selectedSubject?.title }}
            </p>
            <p class="text-xs text-ink-tertiary">
              Sujet n°{{ selectedSubject?.subject_number }}
            </p>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button
          label="Supprimer"
          severity="danger"
          icon="pi pi-trash"
          :loading="deleting"
          @click="handleDelete"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: "admin" });

const toast = useToast();
const store = useStartDeutschSessionStore();

interface AdminSubject {
  id: string;
  level: string;
  subject_number: number;
  title: string;
  description: string | null;
  is_active: boolean;
}

const subjects = ref<AdminSubject[]>([]);
const loading = ref(false);

const filterLevel = ref<"A1" | "A2" | "">("");
const levelOptions = [
  { label: "Tous niveaux", value: "" as const },
  { label: "A1", value: "A1" as const },
  { label: "A2", value: "A2" as const },
];

const filteredSubjects = computed(() =>
  filterLevel.value
    ? subjects.value.filter((s) => s.level === filterLevel.value)
    : subjects.value,
);

async function fetchSubjects() {
  loading.value = true;
  const result = await store.adminListSubjects();
  if (result.success) {
    subjects.value = result.data as AdminSubject[];
  } else {
    console.error("Impossible de charger les sujets", result.error);
  }
  loading.value = false;
}

// ── Supprimer ─────────────────────────────────────────
const deleteDialog = ref(false);
const deleting = ref(false);
const selectedSubject = ref<AdminSubject | null>(null);

const openDelete = (subject: AdminSubject) => {
  selectedSubject.value = subject;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!selectedSubject.value) return;
  deleting.value = true;

  const result = await store.adminDeleteSubject(selectedSubject.value.id);
  if (result.success) {
    subjects.value = subjects.value.filter(
      (s) => s.id !== selectedSubject.value?.id,
    );
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Sujet supprimé", life: 3000 });
  } else {
    toast.add({
      severity: "error",
      summary: result.error || "Erreur",
      life: 4000,
    });
  }
  deleting.value = false;
};

onMounted(fetchSubjects);
</script>
