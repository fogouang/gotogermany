<template>
  <div class="space-y-6">
    <!-- Toolbar -->
    <div
      class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between"
    >
      <InputText
        v-model="search"
        placeholder="Rechercher un sujet..."
        class="w-full sm:w-72"
      />
      <div class="flex gap-2">
        <Select
          v-model="filterProvider"
          :options="providerOptions"
          optionLabel="label"
          optionValue="value"
          class="w-40"
          @change="reload"
        />
        <Select
          v-model="filterLevel"
          :options="levelOptions"
          optionLabel="label"
          optionValue="value"
          class="w-32"
          @change="reload"
        />
        <div
          class="flex items-center gap-2 px-3 bg-white border border-gray-200 rounded-lg"
        >
          <label class="text-sm text-gray-500 whitespace-nowrap"
            >Inactifs</label
          >
          <InputSwitch v-model="showInactive" @change="reload" />
        </div>
        <Button
          label="Nouveau sujet"
          icon="pi pi-plus"
          @click="router.push('/admin/simulateur/nouveau')"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Table -->
    <div
      v-else
      class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
    >
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Titre
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell"
            >
              Provider
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell"
            >
              Niveau
            </th>
            <th
              class="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell"
            >
              Tâches
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Statut
            </th>
            <th
              class="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="s in filtered"
            :key="s.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- Titre -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-3">
                <div
                  class="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0"
                  :class="providerBg(s.provider)"
                >
                  {{ s.provider.slice(0, 2).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ s.title }}</p>
                  <p
                    v-if="s.description"
                    class="text-xs text-gray-400 truncate max-w-xs"
                  >
                    {{ s.description }}
                  </p>
                  <div class="flex gap-1 mt-1 sm:hidden">
                    <Tag
                      :value="s.provider.toUpperCase()"
                      :class="providerTagClass(s.provider)"
                    />
                    <Tag :value="s.level.toUpperCase()" severity="info" />
                  </div>
                </div>
              </div>
            </td>

            <!-- Provider -->
            <td class="px-5 py-4 hidden sm:table-cell">
              <Tag
                :value="s.provider.toUpperCase()"
                :class="providerTagClass(s.provider)"
              />
            </td>

            <!-- Niveau -->
            <td class="px-5 py-4 hidden md:table-cell">
              <Tag :value="s.level.toUpperCase()" severity="info" />
            </td>

            <!-- Tâches -->
            <td
              class="px-5 py-4 text-center text-gray-500 hidden md:table-cell"
            >
              {{ s.tasks.length }}
            </td>

            <!-- Statut -->
            <td class="px-5 py-4">
              <Tag
                :value="s.is_active ? 'Actif' : 'Inactif'"
                :severity="s.is_active ? 'success' : 'danger'"
              />
            </td>

            <!-- Actions -->
            <td class="px-5 py-4">
              <div class="flex items-center justify-end gap-1">
                <Button
                  icon="pi pi-pencil"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  v-tooltip.top="'Modifier'"
                  @click="router.push(`/admin/simulateur/${s.id}`)"
                />
                <Button
                  :icon="s.is_active ? 'pi pi-eye-slash' : 'pi pi-eye'"
                  text
                  rounded
                  size="small"
                  :severity="s.is_active ? 'warn' : 'success'"
                  v-tooltip.top="s.is_active ? 'Désactiver' : 'Activer'"
                  :loading="togglingId === s.id"
                  @click="handleToggle(s)"
                />
                <Button
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  @click="openDeleteDialog(s)"
                />
              </div>
            </td>
          </tr>

          <!-- Empty -->
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="px-5 py-12 text-center text-gray-400">
              <i class="pi pi-inbox text-3xl mb-2 block"></i>
              Aucun sujet trouvé
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer count -->
      <div class="px-5 py-3 border-t border-gray-100 text-xs text-gray-400">
        {{ filtered.length }} sujet(s) affiché(s) sur
        {{ store.subjects.length }}
      </div>
    </div>

    <!-- Dialog suppression -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer ce sujet ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '400px' }"
    >
      <p v-if="selectedSubject">
        Supprimer <strong>{{ selectedSubject.title }}</strong> ? Cette action
        est irréversible.
      </p>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button
          label="Supprimer"
          severity="danger"
          :loading="deleting"
          @click="handleDelete"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useSimulatorStore } from "~/stores/simulator";
import type { SchreibenSubjectResponse } from "#shared/api";

definePageMeta({ layout: "admin", middleware: ["auth", "admin"] });
useHead({ title: "Admin — Sujets simulateur" });

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
  { label: "Tous les providers", value: null },
  { label: "Goethe", value: "goethe" },
  { label: "TELC", value: "telc" },
  { label: "ÖSD", value: "osd" },
];
const levelOptions = [
  { label: "Tous niveaux", value: null },
  { label: "B1", value: "b1" },
  { label: "B2", value: "b2" },
];

// ── Filtrage local par search ────────────────────────────
const filtered = computed(() => {
  if (!search.value.trim()) return store.subjects;
  const q = search.value.toLowerCase();
  return store.subjects.filter(
    (s) =>
      s.title.toLowerCase().includes(q) ||
      s.description?.toLowerCase().includes(q),
  );
});

// ── Chargement ───────────────────────────────────────────
const reload = async () => {
  const res = await store.fetchAllSubjects(
    filterProvider.value,
    filterLevel.value,
    !showInactive.value,
  );
  if (!res.success) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: store.error,
      life: 3000,
    });
  }
};

// ── Toggle actif/inactif ─────────────────────────────────
const handleToggle = async (s: SchreibenSubjectResponse) => {
  togglingId.value = s.id;
  const res = await store.toggleActive(s.id);
  togglingId.value = null;
  if (!res.success) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: res.error,
      life: 3000,
    });
  }
};

// ── Suppression ──────────────────────────────────────────
const openDeleteDialog = (s: SchreibenSubjectResponse) => {
  selectedSubject.value = s;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!selectedSubject.value) return;
  deleting.value = true;
  const res = await store.deleteSubject(selectedSubject.value.id);
  deleting.value = false;
  deleteDialog.value = false;
  if (res.success) {
    toast.add({
      severity: "success",
      summary: "Supprimé",
      detail: `« ${selectedSubject.value.title} » supprimé.`,
      life: 3000,
    });
  } else {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: res.error,
      life: 3000,
    });
  }
};

// ── Style helpers ────────────────────────────────────────
const providerBg = (p: string) =>
  ({ goethe: "bg-blue-500", telc: "bg-purple-500", osd: "bg-orange-500" })[p] ??
  "bg-gray-400";
const providerTagClass = (p: string) =>
  ({
    goethe: "bg-blue-100 text-blue-700",
    telc: "bg-purple-100 text-purple-700",
    osd: "bg-orange-100 text-orange-700",
  })[p] ?? "bg-gray-100 text-gray-600";

onMounted(() => reload());
</script>
