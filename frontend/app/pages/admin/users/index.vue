<!-- pages/admin/users/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Tuiles (servent aussi de filtre) ── -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <button
        v-for="tile in tiles"
        :key="tile.key"
        type="button"
        class="flex items-center gap-3 rounded-card border bg-card p-4 text-left shadow-soft transition-colors"
        :class="filterStatus === tile.key ? 'border-primary ring-1 ring-primary/30' : 'border-line hover:border-primary/30'"
        @click="filterStatus = tile.key"
      >
        <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf" :class="tile.iconClass">
          <i :class="tile.icon" />
        </span>
        <div class="min-w-0">
          <p class="text-2xl font-bold leading-none text-ink">{{ tile.count }}</p>
          <p class="mt-1 truncate text-xs text-muted">{{ tile.label }}</p>
        </div>
      </button>
    </div>

    <!-- ── Recherche ── -->
    <IconField class="w-full sm:max-w-sm">
      <InputIcon class="pi pi-search" />
      <InputText v-model="search" placeholder="Rechercher un utilisateur (nom, email)" class="w-full" />
    </IconField>

    <!-- ── Chargement ── -->
    <div v-if="store.loading" class="space-y-3">
      <div v-for="n in 5" :key="n" class="h-16 animate-pulse rounded-card bg-card-2" />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="filteredUsers.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
        <i class="pi pi-users" />
      </span>
      <p class="text-sm font-medium text-ink">Aucun utilisateur trouvé</p>
    </div>

    <!-- ── Liste ── -->
    <template v-else>
      <ul class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft">
        <li
          v-for="user in paginatedUsers"
          :key="user.id"
          class="flex flex-wrap items-center gap-x-4 gap-y-3 px-4 py-3.5 sm:px-5"
        >
          <!-- Identité -->
          <div class="flex min-w-56 flex-1 items-center gap-3" :class="{ 'opacity-60': !user.is_active }">
            <span
              class="flex size-10 shrink-0 items-center justify-center rounded-leaf text-sm font-bold"
              :class="user.is_admin ? 'bg-red-500/10 text-red-600' : 'bg-primary/10 text-primary'"
            >
              {{ initials(user.full_name) }}
            </span>
            <div class="min-w-0">
              <p class="truncate font-medium text-ink">{{ user.full_name }}</p>
              <p class="truncate text-xs text-muted">{{ user.email }}</p>
            </div>
          </div>

          <!-- Inscription -->
          <span class="hidden w-28 text-xs text-muted md:block">{{ formatDate(user.created_at) }}</span>

          <!-- Badges -->
          <div class="flex flex-wrap items-center gap-1.5">
            <span v-if="user.is_admin" class="rounded-full bg-red-500/10 px-2 py-0.5 text-[11px] font-semibold text-red-600">
              Admin
            </span>
            <span
              class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
              :class="user.is_active ? 'bg-emerald-500/10 text-emerald-600' : 'bg-red-500/10 text-red-600'"
            >
              {{ user.is_active ? "Actif" : "Désactivé" }}
            </span>
            <span v-if="user.is_verified" class="rounded-full bg-sky-500/10 px-2 py-0.5 text-[11px] font-semibold text-sky-600">
              Vérifié
            </span>
            <span
              v-if="user.is_ambassador"
              class="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2 py-0.5 text-[11px] font-semibold text-amber-600"
            >
              <i class="pi pi-star-fill text-[9px]" /> Ambassadeur
            </span>
          </div>

          <!-- Actions -->
          <div class="ml-auto flex items-center gap-1">
            <Button
              icon="pi pi-key"
              text
              rounded
              size="small"
              severity="secondary"
              v-tooltip.top="'Gérer les accès'"
              aria-label="Gérer les accès"
              @click="openGrantAccess(user)"
            />
            <Button
              :icon="user.is_ambassador ? 'pi pi-star-fill' : 'pi pi-star'"
              text
              rounded
              size="small"
              :severity="user.is_ambassador ? 'warn' : 'secondary'"
              v-tooltip.top="user.is_ambassador ? 'Retirer le statut ambassadeur' : 'Rendre ambassadeur'"
              :aria-label="user.is_ambassador ? 'Retirer le statut ambassadeur' : 'Rendre ambassadeur'"
              :loading="togglingAmbassadorId === user.id"
              @click="handleToggleAmbassador(user)"
            />
            <Button
              :icon="user.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
              text
              rounded
              size="small"
              :severity="user.is_active ? 'warn' : 'success'"
              v-tooltip.top="user.is_active ? 'Désactiver' : 'Activer'"
              :aria-label="user.is_active ? 'Désactiver' : 'Activer'"
              :loading="togglingId === user.id"
              :disabled="user.is_admin"
              @click="handleToggle(user)"
            />
            <Button
              icon="pi pi-trash"
              text
              rounded
              size="small"
              severity="danger"
              v-tooltip.top="'Supprimer'"
              aria-label="Supprimer"
              :disabled="user.is_admin"
              @click="confirmDelete(user)"
            />
          </div>
        </li>
      </ul>

      <Paginator
        v-if="filteredUsers.length > 15"
        v-model:first="first"
        v-model:rows="rows"
        :totalRecords="filteredUsers.length"
        :rowsPerPageOptions="[15, 30, 60]"
        class="rounded-card border border-line"
      />
    </template>

    <!-- ══ Gérer les accès ══ -->
    <Dialog
      v-model:visible="grantDialog"
      header="Gérer les accès"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <div v-if="selectedUser" class="space-y-5">
        <div class="flex items-center gap-3 rounded-leaf bg-card-2 p-4">
          <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-primary/10 font-bold text-primary">
            {{ initials(selectedUser.full_name) }}
          </span>
          <div class="min-w-0">
            <p class="truncate font-semibold text-ink">{{ selectedUser.full_name }}</p>
            <p class="truncate text-xs text-muted">{{ selectedUser.email }}</p>
          </div>
        </div>

        <!-- Accès complet -->
        <div class="flex items-center justify-between gap-4 rounded-leaf border border-primary/30 bg-primary/5 p-4">
          <div>
            <p class="text-sm font-semibold text-ink">Accès complet</p>
            <p class="mt-0.5 text-xs text-muted">Donner accès à tous les niveaux disponibles</p>
          </div>
          <Button label="Tout accorder" icon="pi pi-star" size="small" :loading="grantingAll" @click="handleGrantAll" />
        </div>

        <div class="flex items-center gap-3">
          <div class="h-px flex-1 bg-line" />
          <span class="text-xs font-medium text-muted">ou par niveau</span>
          <div class="h-px flex-1 bg-line" />
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">Niveau spécifique</label>
          <Select
            v-model="selectedLevelId"
            :options="allLevels"
            optionLabel="label"
            optionValue="value"
            placeholder="Sélectionner un niveau"
            class="w-full"
            filter
          />
        </div>

        <Message v-if="grantError" severity="error" :closable="false">{{ grantError }}</Message>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="grantDialog = false" />
        <Button
          label="Accorder ce niveau"
          icon="pi pi-key"
          :loading="granting"
          :disabled="!selectedLevelId"
          @click="handleGrantAccess"
        />
      </template>
    </Dialog>

    <!-- ══ Suppression ══ -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer l'utilisateur ?"
      modal
      :style="{ width: '95vw', maxWidth: '26rem' }"
    >
      <div v-if="selectedUser" class="flex items-start gap-3">
        <span class="flex size-10 shrink-0 items-center justify-center rounded-leaf bg-red-500/10">
          <i class="pi pi-exclamation-triangle text-red-600" />
        </span>
        <div>
          <p class="font-semibold text-ink">{{ selectedUser.full_name }}</p>
          <p class="mt-1 text-sm text-muted">
            Cette action est irréversible. Toutes les données de cet utilisateur seront supprimées.
          </p>
        </div>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button label="Supprimer" icon="pi pi-trash" severity="danger" :loading="deleting" @click="handleDelete" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { UserAdminResponse } from "#shared/api";

definePageMeta({ layout: "admin" });

const store = useAdminUsersStore();
const examsStore = useExamsStore();
const toast = useToast();

// ── Filtres ──
type FilterKey = "all" | "active" | "inactive" | "admin" | "ambassador";
const search = ref("");
const filterStatus = ref<FilterKey>("all");

function matches(u: UserAdminResponse, key: FilterKey) {
  if (key === "active") return u.is_active;
  if (key === "inactive") return !u.is_active;
  if (key === "admin") return u.is_admin;
  if (key === "ambassador") return u.is_ambassador;
  return true;
}

const tiles = computed(() => {
  const count = (k: FilterKey) => store.users.filter((u) => matches(u, k)).length;
  return [
    { key: "all" as const, label: "Utilisateurs", count: count("all"), icon: "pi pi-users", iconClass: "bg-primary/10 text-primary" },
    { key: "active" as const, label: "Actifs", count: count("active"), icon: "pi pi-check-circle", iconClass: "bg-emerald-500/10 text-emerald-600" },
    { key: "inactive" as const, label: "Désactivés", count: count("inactive"), icon: "pi pi-ban", iconClass: "bg-red-500/10 text-red-600" },
    { key: "admin" as const, label: "Admins", count: count("admin"), icon: "pi pi-shield", iconClass: "bg-red-500/10 text-red-600" },
    { key: "ambassador" as const, label: "Ambassadeurs", count: count("ambassador"), icon: "pi pi-star", iconClass: "bg-amber-500/15 text-amber-600" },
  ];
});

const filteredUsers = computed(() => {
  const q = search.value.trim().toLowerCase();
  return store.users
    .filter((u) => matches(u, filterStatus.value))
    .filter((u) => !q || u.full_name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
});

// ── Pagination ──
const first = ref(0);
const rows = ref(15);
const paginatedUsers = computed(() => filteredUsers.value.slice(first.value, first.value + rows.value));

watch([search, filterStatus], () => {
  first.value = 0;
});

// ── État ──
const togglingId = ref<string | null>(null);
const togglingAmbassadorId = ref<string | null>(null);
const deleting = ref(false);
const granting = ref(false);
const grantingAll = ref(false);
const grantError = ref("");
const grantDialog = ref(false);
const deleteDialog = ref(false);
const selectedUser = ref<UserAdminResponse | null>(null);
const selectedLevelId = ref<string>("");

// ── Niveaux ──
const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

// ── Utilitaires ──
function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });

// ── Actions ──
async function handleToggle(user: UserAdminResponse) {
  togglingId.value = user.id;
  const res = await store.toggleActive(user.id);
  togglingId.value = null;
  if (!res.success) toast.add({ severity: "error", summary: "Erreur", detail: res.error, life: 3000 });
}

async function handleToggleAmbassador(user: UserAdminResponse) {
  const wasAmbassador = user.is_ambassador;
  togglingAmbassadorId.value = user.id;
  const res = await store.toggleAmbassador(user.id, wasAmbassador);
  togglingAmbassadorId.value = null;
  if (res.success) {
    toast.add({
      severity: "success",
      summary: wasAmbassador ? "Statut ambassadeur retiré" : "Statut ambassadeur accordé",
      detail: `${user.full_name} ${wasAmbassador ? "n'est plus" : "est maintenant"} ambassadeur.`,
      life: 3000,
    });
  } else {
    toast.add({ severity: "error", summary: "Erreur", detail: res.error, life: 3000 });
  }
}

function confirmDelete(user: UserAdminResponse) {
  selectedUser.value = user;
  deleteDialog.value = true;
}

async function handleDelete() {
  if (!selectedUser.value) return;
  deleting.value = true;
  const res = await store.deleteUser(selectedUser.value.id);
  deleting.value = false;
  deleteDialog.value = false;
  if (!res.success) toast.add({ severity: "error", summary: "Erreur", detail: res.error, life: 3000 });
}

function openGrantAccess(user: UserAdminResponse) {
  selectedUser.value = user;
  selectedLevelId.value = "";
  grantError.value = "";
  grantDialog.value = true;
}

async function handleGrantAccess() {
  if (!selectedUser.value || !selectedLevelId.value) return;
  granting.value = true;
  grantError.value = "";
  const res = await store.grantAccess(selectedUser.value.id, selectedLevelId.value);
  granting.value = false;
  if (res.success) {
    grantDialog.value = false;
    toast.add({
      severity: "success",
      summary: "Accès accordé",
      detail: `${selectedUser.value.full_name} a accès au niveau sélectionné.`,
      life: 3000,
    });
  } else {
    grantError.value = res.error || "Erreur lors de l'attribution";
  }
}

async function handleGrantAll() {
  if (!selectedUser.value) return;
  grantingAll.value = true;
  grantError.value = "";
  const res = await store.grantAllAccess(selectedUser.value.id);
  grantingAll.value = false;
  if (res.success) {
    grantDialog.value = false;
    toast.add({
      severity: "success",
      summary: "Accès complet accordé",
      detail: `${selectedUser.value.full_name} a maintenant accès à tous les niveaux.`,
      life: 3000,
    });
  } else {
    grantError.value = res.error || "Erreur lors de l'attribution globale";
  }
}

onMounted(async () => {
  await store.fetchUsers();
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
});
</script>