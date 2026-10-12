<!-- pages/admin/centers/index.vue -->
<template>
  <div class="space-y-5">
    <!-- ── Tuiles (servent aussi de filtre) ── -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <button
        v-for="tile in tiles"
        :key="tile.key"
        type="button"
        class="flex items-center gap-3 rounded-card border bg-card p-4 text-left shadow-soft transition-colors"
        :class="
          statusFilter === tile.key
            ? 'border-primary ring-1 ring-primary/30'
            : 'border-line hover:border-primary/30'
        "
        @click="statusFilter = tile.key"
      >
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-leaf"
          :class="tile.iconClass"
        >
          <i :class="tile.icon" />
        </span>
        <div>
          <p class="text-2xl font-bold leading-none text-ink">
            {{ tile.count }}
          </p>
          <p class="mt-1 text-xs text-muted">{{ tile.label }}</p>
        </div>
      </button>
    </div>

    <!-- ── Barre d'outils ── -->
    <div
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <IconField class="w-full sm:max-w-sm">
        <InputIcon class="pi pi-search" />
        <InputText
          v-model="search"
          class="w-full"
          placeholder="Rechercher un centre (nom, email, téléphone)"
        />
      </IconField>
      <Button
        label="Nouveau centre"
        icon="pi pi-plus"
        class="w-full sm:w-auto"
        @click="openCreateCenterDialog"
      />
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loadingCenters" class="space-y-3">
      <div
        v-for="n in 4"
        :key="n"
        class="h-16 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="filteredCenters.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-building" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{
          adminCenters.centers.length === 0
            ? "Aucun centre pour l'instant."
            : "Aucun centre ne correspond."
        }}
      </p>
    </div>

    <!-- ── Liste ── -->
    <template v-else>
      <ul
        class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
      >
        <li
          v-for="center in paginatedCenters"
          :key="center.id"
          class="flex flex-wrap items-center gap-x-4 gap-y-3 px-4 py-4 sm:px-5"
        >
          <span
            class="flex size-10 shrink-0 items-center justify-center rounded-leaf text-sm font-bold"
            :class="
              center.is_active
                ? 'bg-primary/10 text-primary'
                : 'bg-card-2 text-muted'
            "
          >
            {{ initials(center.name) }}
          </span>

          <div
            class="min-w-48 flex-1"
            :class="{ 'opacity-60': !center.is_active }"
          >
            <p class="truncate font-medium text-ink">{{ center.name }}</p>
            <p class="flex flex-wrap gap-x-3 text-xs text-muted">
              <span
                v-if="center.contact_email"
                class="inline-flex items-center gap-1"
              >
                <i class="pi pi-envelope text-[10px]" />{{
                  center.contact_email
                }}
              </span>
              <span
                v-if="center.contact_phone"
                class="inline-flex items-center gap-1"
              >
                <i class="pi pi-phone text-[10px]" />{{ center.contact_phone }}
              </span>
              <span v-if="!center.contact_email && !center.contact_phone"
                >Aucun contact</span
              >
            </p>
          </div>

          <span
            class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="
              center.is_active
                ? 'bg-emerald-500/10 text-emerald-600'
                : 'bg-red-500/10 text-red-600'
            "
          >
            {{ center.is_active ? "Actif" : "Désactivé" }}
          </span>

          <div class="flex items-center gap-1">
            <Button
              label="Directeur"
              icon="pi pi-user-plus"
              text
              size="small"
              @click="openDirectorDialog(center)"
            />
            <Button
              :icon="center.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
              text
              rounded
              size="small"
              :severity="center.is_active ? 'danger' : 'success'"
              v-tooltip.top="center.is_active ? 'Désactiver' : 'Réactiver'"
              :aria-label="center.is_active ? 'Désactiver' : 'Réactiver'"
              @click="confirmToggleActive(center)"
            />
          </div>
        </li>
      </ul>

      <Paginator
        v-if="filteredCenters.length > 10"
        v-model:first="centersFirst"
        v-model:rows="centersRows"
        :totalRecords="filteredCenters.length"
        :rowsPerPageOptions="[10, 20, 50]"
        class="rounded-card border border-line"
      />
    </template>

    <!-- ══ Création centre ══ -->
    <Dialog
      v-model:visible="showCreateCenterDialog"
      header="Nouveau centre"
      modal
      :style="{ width: '95vw', maxWidth: '28rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleCreateCenter">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            Nom du centre <span class="text-red-600">*</span>
          </label>
          <InputText
            v-model="centerForm.name"
            class="w-full"
            placeholder="ex. Centre Alpha Formation"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            Email de contact
            <span class="font-normal text-muted">(optionnel)</span>
          </label>
          <InputText
            v-model="centerForm.contact_email"
            type="email"
            class="w-full"
            placeholder="contact@centre-alpha.cm"
          />
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            Téléphone <span class="font-normal text-muted">(optionnel)</span>
          </label>
          <InputText
            v-model="centerForm.contact_phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
        </div>
        <Message v-if="centerFormError" severity="error" :closable="false">{{
          centerFormError
        }}</Message>
      </form>
      <template #footer>
        <Button label="Annuler" text @click="showCreateCenterDialog = false" />
        <Button
          label="Créer"
          icon="pi pi-check"
          :loading="creatingCenter"
          @click="handleCreateCenter"
        />
      </template>
    </Dialog>

    <!-- ══ Création directeur ══ -->
    <Dialog
      v-model:visible="showDirectorDialog"
      header="Créer le directeur"
      modal
      :style="{ width: '95vw', maxWidth: '28rem' }"
    >
      <div v-if="selectedCenter" class="space-y-4">
        <div class="flex items-center gap-3 rounded-leaf bg-card-2 px-4 py-3">
          <i class="pi pi-building text-muted" />
          <p class="font-semibold text-ink">{{ selectedCenter.name }}</p>
        </div>

        <!-- Identifiants à transmettre -->
        <div
          v-if="directorCredentials"
          class="space-y-3 rounded-leaf border border-emerald-500/30 bg-emerald-500/10 p-4"
        >
          <p
            class="flex items-center gap-2 text-sm font-semibold text-emerald-600"
          >
            <i class="pi pi-check-circle" /> Compte créé
          </p>
          <p class="text-xs text-muted">
            Transmettez ces identifiants à {{ directorForm.full_name }} :
          </p>
          <div
            class="space-y-1 rounded-leaf bg-card px-3 py-2 font-mono text-sm text-ink"
          >
            <p>{{ directorForm.email }}</p>
            <p>{{ directorForm.password }}</p>
          </div>
          <Button
            label="Copier"
            icon="pi pi-copy"
            size="small"
            outlined
            @click="copyCredentials"
          />
        </div>

        <form v-else class="space-y-4" @submit.prevent="handleCreateDirector">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              Nom complet <span class="text-red-600">*</span>
            </label>
            <InputText
              v-model="directorForm.full_name"
              class="w-full"
              placeholder="ex. M. Jean Talla"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              Email <span class="text-red-600">*</span>
            </label>
            <InputText
              v-model="directorForm.email"
              type="email"
              class="w-full"
              placeholder="directeur@centre.cm"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              Téléphone <span class="font-normal text-muted">(optionnel)</span>
            </label>
            <InputText
              v-model="directorForm.phone"
              class="w-full"
              placeholder="+237 6XX XXX XXX"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              Mot de passe provisoire <span class="text-red-600">*</span>
            </label>
            <div class="flex gap-2">
              <Password
                v-model="directorForm.password"
                class="flex-1"
                inputClass="w-full"
                toggleMask
                :feedback="false"
                placeholder="Min. 8 caractères"
              />
              <Button
                type="button"
                icon="pi pi-refresh"
                outlined
                v-tooltip.top="'Générer un mot de passe'"
                aria-label="Générer un mot de passe"
                @click="directorForm.password = genererMotDePasse()"
              />
            </div>
          </div>
          <Message
            v-if="directorFormError"
            severity="error"
            :closable="false"
            >{{ directorFormError }}</Message
          >
        </form>
      </div>
      <template #footer>
        <Button label="Fermer" text @click="showDirectorDialog = false" />
        <Button
          v-if="!directorCredentials"
          label="Créer"
          icon="pi pi-user-plus"
          :loading="creatingDirector"
          @click="handleCreateDirector"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { CenterResponse } from "#shared/api";

definePageMeta({ layout: "admin" });

const adminCenters = useAdminCentersStore();
const adminUsers = useAdminUsersStore();
const toast = useToast();
const confirm = useConfirm();

const loadingCenters = ref(true);
const selectedCenter = ref<CenterResponse | null>(null);

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

// ── Filtres ──
type StatusFilter = "all" | "active" | "inactive";
const statusFilter = ref<StatusFilter>("all");
const search = ref("");

const tiles = computed(() => {
  const all = adminCenters.centers;
  return [
    {
      key: "all" as const,
      label: "Centres",
      count: all.length,
      icon: "pi pi-building",
      iconClass: "bg-primary/10 text-primary",
    },
    {
      key: "active" as const,
      label: "Actifs",
      count: all.filter((c) => c.is_active).length,
      icon: "pi pi-check-circle",
      iconClass: "bg-emerald-500/10 text-emerald-600",
    },
    {
      key: "inactive" as const,
      label: "Désactivés",
      count: all.filter((c) => !c.is_active).length,
      icon: "pi pi-ban",
      iconClass: "bg-red-500/10 text-red-600",
    },
  ];
});

// Plus récents en tête (le dernier créé est en fin de liste côté store)
const filteredCenters = computed(() => {
  const q = search.value.trim().toLowerCase();
  return [...adminCenters.centers]
    .reverse()
    .filter(
      (c) =>
        statusFilter.value === "all" ||
        (statusFilter.value === "active") === c.is_active,
    )
    .filter(
      (c) =>
        !q ||
        c.name.toLowerCase().includes(q) ||
        (c.contact_email ?? "").toLowerCase().includes(q) ||
        (c.contact_phone ?? "").includes(q),
    );
});

// ── Pagination (client) ──
const centersFirst = ref(0);
const centersRows = ref(10);
const paginatedCenters = computed(() =>
  filteredCenters.value.slice(
    centersFirst.value,
    centersFirst.value + centersRows.value,
  ),
);

watch([statusFilter, search], () => {
  centersFirst.value = 0;
});

// ── Activation / désactivation ──
function confirmToggleActive(center: CenterResponse) {
  confirm.require({
    message: center.is_active
      ? `Désactiver « ${center.name} » ? Tout le personnel et les étudiants de ce centre perdront l'accès immédiatement.`
      : `Réactiver « ${center.name} » ? Le personnel et les étudiants retrouveront l'accès.`,
    header: center.is_active ? "Désactiver le centre" : "Réactiver le centre",
    icon: "pi pi-exclamation-triangle",
    acceptLabel: center.is_active ? "Désactiver" : "Réactiver",
    rejectLabel: "Annuler",
    acceptClass: center.is_active ? "p-button-danger" : undefined,
    accept: async () => {
      const result = await adminCenters.toggleCenterActive(center.id);
      if (result.success) {
        toast.add({
          severity: "success",
          summary: center.is_active ? "Centre désactivé" : "Centre réactivé",
          life: 3000,
        });
      } else {
        toast.add({
          severity: "error",
          summary: result.error || "Erreur",
          life: 4000,
        });
      }
    },
  });
}

// ── Création centre ──
const showCreateCenterDialog = ref(false);
const creatingCenter = ref(false);
const centerFormError = ref<string | null>(null);
const centerForm = ref({ name: "", contact_email: "", contact_phone: "" });

function openCreateCenterDialog() {
  centerForm.value = { name: "", contact_email: "", contact_phone: "" };
  centerFormError.value = null;
  showCreateCenterDialog.value = true;
}

async function handleCreateCenter() {
  if (!centerForm.value.name.trim()) {
    centerFormError.value = "Le nom du centre est requis.";
    return;
  }
  creatingCenter.value = true;
  centerFormError.value = null;
  const result = await adminCenters.createCenter({
    name: centerForm.value.name.trim(),
    contact_email: centerForm.value.contact_email.trim() || null,
    contact_phone: centerForm.value.contact_phone.trim() || null,
  });
  creatingCenter.value = false;
  if (result.success) {
    showCreateCenterDialog.value = false;
    // Le nouveau centre apparaît en tête : on revient à la première page, sans filtre
    statusFilter.value = "all";
    search.value = "";
    centersFirst.value = 0;
    toast.add({
      severity: "success",
      summary: "Centre créé",
      detail: "Créez maintenant son directeur.",
      life: 4000,
    });
  } else {
    centerFormError.value = result.error || "Erreur lors de la création.";
  }
}

// ── Création directeur ──
const showDirectorDialog = ref(false);
const creatingDirector = ref(false);
const directorFormError = ref<string | null>(null);
const directorCredentials = ref(false);
const directorForm = ref({ full_name: "", email: "", phone: "", password: "" });

function openDirectorDialog(center: CenterResponse) {
  selectedCenter.value = center;
  directorForm.value = {
    full_name: "",
    email: "",
    phone: "",
    password: genererMotDePasse(),
  };
  directorFormError.value = null;
  directorCredentials.value = false;
  showDirectorDialog.value = true;
}

async function handleCreateDirector() {
  if (!selectedCenter.value) return;
  const f = directorForm.value;
  if (!f.full_name.trim() || !f.email.trim() || !f.password) {
    directorFormError.value = "Nom, email et mot de passe sont requis.";
    return;
  }
  if (f.password.length < 8) {
    directorFormError.value =
      "Le mot de passe doit faire au moins 8 caractères.";
    return;
  }

  creatingDirector.value = true;
  directorFormError.value = null;

  const result = await adminUsers.createDirector({
    email: f.email.trim(),
    password: f.password,
    full_name: f.full_name.trim(),
    phone: f.phone.trim() || null,
    center_id: selectedCenter.value.id,
  });

  creatingDirector.value = false;

  if (result.success) {
    directorCredentials.value = true;
  } else {
    directorFormError.value =
      result.error || "Erreur lors de la création du directeur.";
  }
}

async function copyCredentials() {
  const f = directorForm.value;
  try {
    await navigator.clipboard.writeText(`${f.email}\n${f.password}`);
    toast.add({
      severity: "success",
      summary: "Identifiants copiés",
      life: 2000,
    });
  } catch {
    toast.add({
      severity: "warn",
      summary: "Copie impossible, notez-les à la main.",
      life: 3000,
    });
  }
}

onMounted(async () => {
  loadingCenters.value = true;
  await adminCenters.fetchCenters();
  loadingCenters.value = false;
});
</script>
