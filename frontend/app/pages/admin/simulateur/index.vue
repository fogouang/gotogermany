<!-- pages/admin/simulateur/index.vue -->
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
    <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in providerOptions"
          :key="opt.label"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="filterProvider === opt.value ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="setProvider(opt.value)"
        >
          {{ opt.label }}
        </button>
        <span class="mx-1 hidden h-7 w-px bg-line sm:block" />
        <button
          v-for="opt in levelOptions"
          :key="opt.label"
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="filterLevel === opt.value ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="setLevel(opt.value)"
        >
          {{ opt.label }}
        </button>
        <span class="mx-1 hidden h-7 w-px bg-line sm:block" />
        <button
          type="button"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="showInactive ? 'border-primary bg-primary/10 text-primary' : 'border-line bg-card text-muted hover:border-primary/30'"
          @click="toggleInactive"
        >
          <i class="pi mr-1 text-[10px]" :class="showInactive ? 'pi-eye' : 'pi-eye-slash'" />
          Inclure les inactifs
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
          @click="router.push('/admin/simulateur/nouveau')"
        />
      </div>
    </div>

    <!-- ── Chargement ── -->
    <div v-if="store.loading && store.subjects.length === 0" class="space-y-3">
      <div v-for="n in 4" :key="n" class="h-16 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="filtered.length === 0"
      class="flex flex-col items-center gap-3 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <i class="pi pi-inbox" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{ store.subjects.length === 0 ? "Aucun sujet pour ces filtres." : "Aucun sujet ne correspond à la recherche." }}
      </p>
      <Button
        v-if="store.subjects.length === 0 && !filterProvider && !filterLevel"
        label="Créer le premier sujet"
        icon="pi pi-plus"
        outlined
        size="small"
        @click="router.push('/admin/simulateur/nouveau')"
      />
    </div>

    <!-- ── Liste groupée provider + niveau ── -->
    <div v-else class="space-y-5" :class="{ 'opacity-60': store.loading }">
      <section v-for="group in groups" :key="group.key" class="space-y-2">
        <h3 class="flex items-center gap-2 text-sm font-semibold text-ink">
          <span class="size-2 rounded-full" :class="providerStyle(group.provider).dot" />
          {{ providerLabel(group.provider) }} {{ group.level.toUpperCase() }}
          <span class="font-normal text-muted">· {{ group.items.length }}</span>
        </h3>

        <ul class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft">
          <li
            v-for="s in group.items"
            :key="s.id"
            class="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3.5 sm:px-5"
          >
            <button
              type="button"
              class="flex min-w-52 flex-1 items-center gap-3 text-left"
              @click="router.push(`/admin/simulateur/${s.id}`)"
            >
              <span
                class="flex size-10 shrink-0 items-center justify-center rounded-leaf text-xs font-bold"
                :class="providerStyle(s.provider).badge"
              >
                {{ s.level.toUpperCase() }}
              </span>
              <span class="min-w-0">
                <span class="block truncate font-medium text-ink" :class="{ 'text-muted': !s.is_active }">{{ s.title }}</span>
                <span v-if="s.description" class="block truncate text-xs text-muted">{{ s.description }}</span>
              </span>
            </button>

            <div class="flex items-center gap-4 text-xs">
              <span class="text-muted">
                <i class="pi pi-list mr-1 text-[10px]" />{{ s.tasks.length }} tâche(s)
              </span>
              <span class="hidden text-faint sm:inline">Ordre {{ s.display_order }}</span>
            </div>

            <label class="flex cursor-pointer items-center gap-2 text-xs text-muted">
              <ToggleSwitch
                :modelValue="s.is_active"
                :disabled="togglingId === s.id"
                @update:modelValue="handleToggle(s)"
              />
              <span class="w-12">{{ s.is_active ? "Actif" : "Inactif" }}</span>
            </label>

            <div class="flex items-center gap-1">
              <Button
                icon="pi pi-pencil"
                text
                rounded
                size="small"
                severity="secondary"
                v-tooltip.top="'Modifier'"
                aria-label="Modifier"
                @click="router.push(`/admin/simulateur/${s.id}`)"
              />
              <Button
                icon="pi pi-trash"
                text
                rounded
                size="small"
                severity="danger"
                v-tooltip.top="'Supprimer'"
                aria-label="Supprimer"
                @click="openDeleteDialog(s)"
              />
            </div>
          </li>
        </ul>
      </section>

      <p class="text-xs text-faint">{{ filtered.length }} sujet(s) affiché(s) sur {{ store.subjects.length }}</p>
    </div>

    <!-- ══════════ Dialogue suppression ══════════ -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer ce sujet ?"
      modal
      :style="{ width: '28rem', maxWidth: '95vw' }"
    >
      <div v-if="selectedSubject" class="space-y-3">
        <Message severity="error" :closable="false">Cette action est <strong>irréversible</strong>.</Message>
        <div class="flex items-center gap-3 rounded-leaf bg-card-2 p-3">
          <span
            class="flex size-9 shrink-0 items-center justify-center rounded-leaf text-xs font-bold"
            :class="providerStyle(selectedSubject.provider).badge"
          >
            {{ selectedSubject.level.toUpperCase() }}
          </span>
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-ink">{{ selectedSubject.title }}</p>
            <p class="text-xs text-muted">
              {{ providerLabel(selectedSubject.provider) }} · {{ selectedSubject.tasks.length }} tâche(s)
            </p>
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
import { useSimulatorStore } from "~/stores/simulator";
import type { SchreibenSubjectResponse } from "#shared/api";

definePageMeta({ layout: "admin", watermark: "Schreiben" });
useHead({ title: "Admin · Sujets simulateur" });

const router = useRouter();
const toast = useToast();
const store = useSimulatorStore();

const search = ref("");
const filterProvider = ref<string | null>(null);
const filterLevel = ref<string | null>(null);
const showInactive = ref(false);
const togglingId = ref<string | null>(null);
const deleting = ref(false);
const deleteDialog = ref(false);
const selectedSubject = ref<SchreibenSubjectResponse | null>(null);

const providerOptions = [
  { label: "Tous", value: null },
  { label: "Goethe", value: "goethe" },
  { label: "TELC", value: "telc" },
  { label: "ÖSD", value: "osd" },
];
const levelOptions = [
  { label: "Tous niveaux", value: null },
  { label: "B1", value: "b1" },
  { label: "B2", value: "b2" },
];

const providerLabel = (p: string) => ({ goethe: "Goethe", telc: "TELC", osd: "ÖSD" })[p] ?? p.toUpperCase();

const providerStyle = (p: string) =>
  ({
    goethe: { badge: "bg-sky-500/10 text-sky-600", dot: "bg-sky-500" },
    telc: { badge: "bg-violet-500/10 text-violet-600", dot: "bg-violet-500" },
    osd: { badge: "bg-orange-500/10 text-orange-600", dot: "bg-orange-500" },
  })[p] ?? { badge: "bg-card-2 text-muted", dot: "bg-line" };

// ── Tuiles (sur la liste chargée) ──
const tiles = computed(() => {
  const all = store.subjects;
  const active = all.filter((s) => s.is_active).length;
  return [
    { label: "Sujets chargés", value: all.length, icon: "pi pi-pencil", iconClass: "bg-primary/10 text-primary" },
    { label: "Actifs", value: active, icon: "pi pi-check-circle", iconClass: "bg-emerald-500/10 text-emerald-600" },
    { label: "Inactifs", value: all.length - active, icon: "pi pi-eye-slash", iconClass: "bg-card-2 text-muted" },
    {
      label: "Tâches au total",
      value: all.reduce((n, s) => n + s.tasks.length, 0),
      icon: "pi pi-list",
      iconClass: "bg-amber-500/15 text-amber-600",
    },
  ];
});

// ── Recherche locale + groupement ──
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return store.subjects;
  return store.subjects.filter(
    (s) => s.title.toLowerCase().includes(q) || s.description?.toLowerCase().includes(q),
  );
});

const providerOrder = ["goethe", "telc", "osd"];

const groups = computed(() => {
  const map = new Map<string, { key: string; provider: string; level: string; items: SchreibenSubjectResponse[] }>();
  for (const s of filtered.value) {
    const key = `${s.provider}-${s.level}`;
    if (!map.has(key)) map.set(key, { key, provider: s.provider, level: s.level, items: [] });
    map.get(key)!.items.push(s);
  }
  return [...map.values()]
    .sort(
      (a, b) =>
        providerOrder.indexOf(a.provider) - providerOrder.indexOf(b.provider) || a.level.localeCompare(b.level),
    )
    .map((g) => ({ ...g, items: [...g.items].sort((a, b) => a.display_order - b.display_order) }));
});

// ── Chargement ──
const reload = async () => {
  const res = await store.fetchAllSubjects(filterProvider.value, filterLevel.value, !showInactive.value);
  if (!res.success) {
    toast.add({ severity: "error", summary: "Erreur", detail: store.error, life: 3000 });
  }
};

const setProvider = (v: string | null) => {
  if (filterProvider.value === v) return;
  filterProvider.value = v;
  reload();
};
const setLevel = (v: string | null) => {
  if (filterLevel.value === v) return;
  filterLevel.value = v;
  reload();
};
const toggleInactive = () => {
  showInactive.value = !showInactive.value;
  reload();
};

// ── Actif / inactif ──
const handleToggle = async (s: SchreibenSubjectResponse) => {
  togglingId.value = s.id;
  const res = await store.toggleActive(s.id);
  togglingId.value = null;
  if (!res.success) {
    toast.add({ severity: "error", summary: "Erreur", detail: res.error, life: 3000 });
  }
};

// ── Suppression ──
const openDeleteDialog = (s: SchreibenSubjectResponse) => {
  selectedSubject.value = s;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!selectedSubject.value) return;
  const title = selectedSubject.value.title;
  deleting.value = true;
  const res = await store.deleteSubject(selectedSubject.value.id);
  deleting.value = false;
  if (res.success) {
    deleteDialog.value = false;
    toast.add({ severity: "success", summary: "Supprimé", detail: `« ${title} » supprimé.`, life: 3000 });
  } else {
    toast.add({ severity: "error", summary: "Erreur", detail: res.error, life: 3000 });
  }
};

onMounted(reload);
</script>