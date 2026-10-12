<!-- pages/admin/start-deutsch/index.vue -->
<template>
  <div class="space-y-5 pb-10">
    <!-- ── Tuiles ── -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <div v-for="tile in tiles" :key="tile.label" class="rounded-card border border-line bg-card p-4 shadow-soft">
        <div class="mb-3 flex size-9 items-center justify-center rounded-leaf" :class="tile.iconClass">
          <i :class="tile.icon" class="text-sm" />
        </div>
        <p class="text-xl font-bold leading-none text-ink">{{ tile.value }}</p>
        <p class="mt-1.5 text-xs text-muted">{{ tile.label }}</p>
      </div>
    </div>

    <!-- ── Barre d'outils ── -->
    <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in levelOptions"
          :key="opt.value"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="filterLevel === opt.value ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="filterLevel = opt.value"
        >
          {{ opt.label }} · {{ opt.count }}
        </button>
        <span class="mx-1 hidden h-7 w-px bg-line sm:block" />
        <button
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="onlyInactive ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="onlyInactive = !onlyInactive"
        >
          Inactifs · {{ inactiveCount }}
        </button>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row">
        <IconField class="w-full sm:w-64">
          <InputIcon class="pi pi-search" />
          <InputText v-model="search" class="w-full" placeholder="Rechercher un sujet" />
        </IconField>
        <Button
          label="Nouveau sujet"
          icon="pi pi-plus"
          class="w-full shrink-0 sm:w-auto"
          @click="navigateTo('/admin/start-deutsch/import')"
        />
      </div>
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div v-for="n in 4" :key="n" class="h-16 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="filteredSubjects.length === 0"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <i class="pi pi-inbox" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{ subjects.length === 0 ? "Aucun sujet pour l'instant." : "Aucun sujet ne correspond aux filtres." }}
      </p>
      <Button
        v-if="subjects.length === 0"
        label="Créer le premier sujet"
        icon="pi pi-plus"
        outlined
        size="small"
        @click="navigateTo('/admin/start-deutsch/import')"
      />
    </div>

    <!-- ── Liste groupée par niveau ── -->
    <div v-else class="space-y-5">
      <section v-for="group in groups" :key="group.level" class="space-y-2">
        <h3 class="flex items-center gap-2 text-sm font-semibold text-ink">
          Niveau {{ group.level }}
          <span class="font-normal text-muted">· {{ group.items.length }}</span>
        </h3>

        <ul class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft">
          <li
            v-for="subject in group.items"
            :key="subject.id"
            class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3.5 sm:px-5"
            :class="{ 'opacity-70': !subject.is_active }"
          >
            <span class="flex size-11 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary">
              {{ subject.level }}
            </span>

            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <p class="truncate font-medium text-ink">{{ subject.title }}</p>
                <span
                  class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="subject.is_active ? 'bg-emerald-500/10 text-emerald-600' : 'bg-card-2 text-muted'"
                >
                  {{ subject.is_active ? "Actif" : "Inactif" }}
                </span>
              </div>
              <p class="mt-0.5 truncate text-xs text-faint">
                Sujet n°{{ subject.subject_number }}
                <span class="hidden sm:inline">· {{ subject.id }}</span>
              </p>
              <p v-if="subject.description" class="mt-1 line-clamp-1 text-xs text-muted">{{ subject.description }}</p>
            </div>

            <div class="flex shrink-0 items-center gap-1">
              <Button
                icon="pi pi-images"
                label="Audio et images"
                size="small"
                outlined
                class="hidden! sm:inline-flex!"
                @click="goToMedia(subject)"
              />
              <Button
                icon="pi pi-images"
                text
                rounded
                size="small"
                class="sm:hidden!"
                aria-label="Audio et images"
                @click="goToMedia(subject)"
              />
              <Button
                icon="pi pi-trash"
                text
                rounded
                size="small"
                severity="danger"
                v-tooltip.top="'Supprimer'"
                aria-label="Supprimer"
                @click="openDelete(subject)"
              />
            </div>
          </li>
        </ul>
      </section>
    </div>

    <!-- ══════════ Dialogue suppression ══════════ -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le sujet ?"
      modal
      :style="{ width: '28rem', maxWidth: '95vw' }"
    >
      <div class="space-y-3">
        <Message severity="error" :closable="false">
          Cette action est <strong>irréversible</strong>. Toutes les questions, sessions et corrections liées à ce sujet
          seront supprimées.
        </Message>
        <div class="flex items-center gap-3 rounded-leaf bg-card-2 p-3">
          <span class="flex size-9 shrink-0 items-center justify-center rounded-leaf bg-primary/10 text-sm font-bold text-primary">
            {{ selectedSubject?.level }}
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-ink">{{ selectedSubject?.title }}</p>
            <p class="text-xs text-muted">Sujet n°{{ selectedSubject?.subject_number }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Annuler" text severity="secondary" @click="deleteDialog = false" />
        <Button label="Supprimer" severity="danger" icon="pi pi-trash" :loading="deleting" @click="handleDelete" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "admin", watermark: "Start Deutsch" });

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
const loading = ref(true);

async function fetchSubjects() {
  loading.value = true;
  const result = await store.adminListSubjects();
  if (result.success) {
    subjects.value = result.data as AdminSubject[];
  } else {
    toast.add({ severity: "error", summary: "Impossible de charger les sujets", detail: result.error, life: 4000 });
  }
  loading.value = false;
}

// ── Tuiles ──
const countLevel = (lvl: string) => subjects.value.filter((s) => s.level === lvl).length;
const inactiveCount = computed(() => subjects.value.filter((s) => !s.is_active).length);

const tiles = computed(() => [
  { label: "Sujets", value: subjects.value.length, icon: "pi pi-book", iconClass: "bg-primary/10 text-primary" },
  { label: "Sujets A1", value: countLevel("A1"), icon: "pi pi-flag", iconClass: "bg-sky-500/10 text-sky-600" },
  { label: "Sujets A2", value: countLevel("A2"), icon: "pi pi-flag-fill", iconClass: "bg-violet-500/10 text-violet-600" },
  {
    label: "Actifs",
    value: subjects.value.length - inactiveCount.value,
    icon: "pi pi-check-circle",
    iconClass: "bg-emerald-500/10 text-emerald-600",
  },
]);

// ── Filtres ──
const filterLevel = ref<"A1" | "A2" | "">("");
const onlyInactive = ref(false);
const search = ref("");

const levelOptions = computed(() => [
  { label: "Tous", value: "" as const, count: subjects.value.length },
  { label: "A1", value: "A1" as const, count: countLevel("A1") },
  { label: "A2", value: "A2" as const, count: countLevel("A2") },
]);

const filteredSubjects = computed(() => {
  const q = search.value.trim().toLowerCase();
  return subjects.value
    .filter((s) => !filterLevel.value || s.level === filterLevel.value)
    .filter((s) => !onlyInactive.value || !s.is_active)
    .filter((s) => !q || `${s.title} ${s.subject_number} ${s.description ?? ""}`.toLowerCase().includes(q))
    .sort((a, b) => a.level.localeCompare(b.level) || a.subject_number - b.subject_number);
});

const groups = computed(() => {
  const map = new Map<string, AdminSubject[]>();
  for (const s of filteredSubjects.value) {
    if (!map.has(s.level)) map.set(s.level, []);
    map.get(s.level)!.push(s);
  }
  return [...map.entries()].map(([level, items]) => ({ level, items }));
});

const goToMedia = (subject: AdminSubject) => navigateTo(`/admin/start-deutsch/import?subjectId=${subject.id}`);

// ── Suppression ──
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

  const id = selectedSubject.value.id;
  const result = await store.adminDeleteSubject(id);
  if (result.success) {
    subjects.value = subjects.value.filter((s) => s.id !== id);
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Sujet supprimé", life: 3000 });
  } else {
    toast.add({ severity: "error", summary: result.error || "Erreur", life: 4000 });
  }
  deleting.value = false;
};

onMounted(fetchSubjects);
</script>