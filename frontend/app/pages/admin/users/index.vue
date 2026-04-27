<template>
  <div class="space-y-6">
    <!-- Toolbar -->
    <div
      class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between"
    >
      <InputText
        v-model="search"
        placeholder="Rechercher un utilisateur..."
        class="w-full sm:w-72"
      >
        <template><i class="pi pi-search text-gray-400"></i></template>
      </InputText>

      <div class="flex gap-2">
        <Select
          v-model="filterStatus"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          class="w-40"
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
              Utilisateur
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell"
            >
              Email
            </th>
            <th
              class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell"
            >
              Inscription
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
            v-for="user in filteredUsers"
            :key="user.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- Nom -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-3">
                <div
                  class="w-9 h-9 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-sm shrink-0"
                >
                  {{ user.full_name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ user.full_name }}</p>
                  <p class="text-xs text-gray-400 sm:hidden">
                    {{ user.email }}
                  </p>
                  <Tag
                    v-if="user.is_admin"
                    value="Admin"
                    severity="danger"
                    class="mt-1"
                  />
                </div>
              </div>
            </td>

            <!-- Email -->
            <td class="px-5 py-4 text-gray-600 hidden sm:table-cell">
              {{ user.email }}
            </td>

            <!-- Date -->
            <td class="px-5 py-4 text-gray-500 hidden md:table-cell">
              {{ formatDate(user.created_at) }}
            </td>

            <!-- Statut -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-2">
                <Tag
                  :value="user.is_active ? 'Actif' : 'Désactivé'"
                  :severity="user.is_active ? 'success' : 'danger'"
                />
                <Tag v-if="user.is_verified" value="Vérifié" severity="info" />
              </div>
            </td>

            <!-- Actions -->
            <td class="px-5 py-4">
              <div class="flex items-center justify-end gap-1">
                <!-- Accorder accès -->
                <Button
                  icon="pi pi-key"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  v-tooltip.top="'Accorder accès exam'"
                  @click="openGrantAccess(user)"
                />

                <!-- Toggle actif -->
                <Button
                  :icon="user.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
                  text
                  rounded
                  size="small"
                  :severity="user.is_active ? 'warn' : 'success'"
                  :v-tooltip.top="user.is_active ? 'Désactiver' : 'Activer'"
                  :loading="togglingId === user.id"
                  :disabled="user.is_admin"
                  @click="handleToggle(user)"
                />

                <!-- Supprimer -->
                <Button
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  :disabled="user.is_admin"
                  @click="confirmDelete(user)"
                />
              </div>
            </td>
          </tr>

          <!-- Empty -->
          <tr v-if="filteredUsers.length === 0">
            <td colspan="5" class="px-5 py-12 text-center text-gray-400">
              <i class="pi pi-users text-3xl mb-2 block"></i>
              Aucun utilisateur trouvé
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer count -->
      <div class="px-5 py-3 border-t border-gray-100 text-xs text-gray-400">
        {{ filteredUsers.length }} utilisateur(s) affiché(s) sur
        {{ store.users.length }}
      </div>
    </div>

    <!-- Dialog accorder accès -->
    <Dialog
      v-model:visible="grantDialog"
      header="Accorder accès à un examen"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '450px' }"
    >
      <div v-if="selectedUser" class="space-y-4 mt-2">
        <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          <div
            class="w-9 h-9 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-sm"
          >
            {{ selectedUser.full_name.charAt(0).toUpperCase() }}
          </div>
          <div>
            <p class="font-medium text-gray-900">
              {{ selectedUser.full_name }}
            </p>
            <p class="text-xs text-gray-500">{{ selectedUser.email }}</p>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >Examen</label
          >
          <Select
            v-model="selectedExamId"
            :options="examsStore.catalog"
            optionLabel="name"
            optionValue="id"
            placeholder="Sélectionner un examen"
            class="w-full"
          />
        </div>

        <Message v-if="grantError" severity="error" :closable="false">
          {{ grantError }}
        </Message>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="grantDialog = false" />
        <Button
          label="Accorder l'accès"
          icon="pi pi-key"
          :loading="granting"
          :disabled="!selectedExamId"
          @click="handleGrantAccess"
        />
      </template>
    </Dialog>

    <!-- Dialog confirmer suppression -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer l'utilisateur ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '400px' }"
    >
      <p v-if="selectedUser">
        Supprimer <strong>{{ selectedUser.full_name }}</strong> ? Cette action
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
import type { UserAdminResponse } from "#shared/api";

definePageMeta({ layout: "admin", middleware: "admin" });

const store = useAdminUsersStore();
const examsStore = useExamsStore();
const toast = useToast();

const search = ref("");
const filterStatus = ref("");
const togglingId = ref<string | null>(null);
const deleting = ref(false);
const granting = ref(false);
const grantError = ref("");

const grantDialog = ref(false);
const deleteDialog = ref(false);
const selectedUser = ref<UserAdminResponse | null>(null);
const selectedExamId = ref<string>("");

const statusOptions = [
  { label: "Tous", value: "" },
  { label: "Actifs", value: "active" },
  { label: "Désactivés", value: "inactive" },
  { label: "Admins", value: "admin" },
];

const filteredUsers = computed(() => {
  let list = [...store.users];

  if (search.value) {
    const q = search.value.toLowerCase();
    list = list.filter(
      (u) =>
        u.full_name.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q),
    );
  }

  if (filterStatus.value === "active") list = list.filter((u) => u.is_active);
  if (filterStatus.value === "inactive")
    list = list.filter((u) => !u.is_active);
  if (filterStatus.value === "admin") list = list.filter((u) => u.is_admin);

  return list;
});

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

const handleToggle = async (user: UserAdminResponse) => {
  togglingId.value = user.id;
  const res = await store.toggleActive(user.id);
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

const confirmDelete = (user: UserAdminResponse) => {
  selectedUser.value = user;
  deleteDialog.value = true;
};

const handleDelete = async () => {
  if (!selectedUser.value) return;
  deleting.value = true;
  const res = await store.deleteUser(selectedUser.value.id);
  deleting.value = false;
  deleteDialog.value = false;
  if (!res.success) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: res.error,
      life: 3000,
    });
  }
};

const openGrantAccess = (user: UserAdminResponse) => {
  selectedUser.value = user;
  selectedExamId.value = "";
  grantError.value = "";
  grantDialog.value = true;
};

const handleGrantAccess = async () => {
  if (!selectedUser.value || !selectedExamId.value) return;
  granting.value = true;
  grantError.value = "";
  const res = await store.grantAccess(
    selectedUser.value.id,
    selectedExamId.value,
  );
  granting.value = false;
  if (res.success) {
    grantDialog.value = false;
    toast.add({
      severity: "success",
      summary: "Accès accordé",
      detail: `${selectedUser.value.full_name} peut maintenant accéder à l'examen.`,
      life: 3000,
    });
  } else {
    grantError.value = res.error || "Erreur lors de l'attribution";
  }
};

onMounted(async () => {
  await store.fetchUsers();
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
});
</script>
