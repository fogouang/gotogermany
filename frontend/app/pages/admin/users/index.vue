<template>
  <div class="space-y-6">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <div class="flex-1 max-w-sm">
        <IconField iconPosition="left">
          <InputIcon class="pi pi-search text-gray-400" />
          <InputText
            v-model="search"
            placeholder="Rechercher un utilisateur..."
            class="w-full"
          />
        </IconField>
      </div>
      <Select
        v-model="filterStatus"
        :options="statusOptions"
        optionLabel="label"
        optionValue="value"
        class="w-40"
      />
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-12">
      <ProgressSpinner style="width:48px;height:48px" strokeWidth="3" />
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="text-left px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wide">
              Utilisateur
            </th>
            <th class="text-left px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wide hidden sm:table-cell">
              Email
            </th>
            <th class="text-left px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wide hidden md:table-cell">
              Inscription
            </th>
            <th class="text-left px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wide">
              Statut
            </th>
            <th class="text-right px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wide">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="user in paginatedUsers"
            :key="user.id"
            class="hover:bg-gray-50/70 transition-colors"
          >
            <!-- Nom -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-xl bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-sm shrink-0">
                  {{ user.full_name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="font-semibold text-gray-900">{{ user.full_name }}</p>
                  <p class="text-xs text-gray-400 sm:hidden">{{ user.email }}</p>
                  <Tag v-if="user.is_admin" value="Admin" severity="danger" class="mt-1" />
                </div>
              </div>
            </td>

            <!-- Email -->
            <td class="px-5 py-4 text-gray-500 hidden sm:table-cell text-xs">
              {{ user.email }}
            </td>

            <!-- Date -->
            <td class="px-5 py-4 text-gray-400 hidden md:table-cell text-xs">
              {{ formatDate(user.created_at) }}
            </td>

            <!-- Statut -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-1.5 flex-wrap">
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
                <Button
                  icon="pi pi-key"
                  text rounded size="small"
                  severity="secondary"
                  v-tooltip.top="'Gérer les accès'"
                  @click="openGrantAccess(user)"
                />
                <Button
                  :icon="user.is_active ? 'pi pi-ban' : 'pi pi-check-circle'"
                  text rounded size="small"
                  :severity="user.is_active ? 'warn' : 'success'"
                  v-tooltip.top="user.is_active ? 'Désactiver' : 'Activer'"
                  :loading="togglingId === user.id"
                  :disabled="user.is_admin"
                  @click="handleToggle(user)"
                />
                <Button
                  icon="pi pi-trash"
                  text rounded size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  :disabled="user.is_admin"
                  @click="confirmDelete(user)"
                />
              </div>
            </td>
          </tr>

          <!-- Empty -->
          <tr v-if="paginatedUsers.length === 0">
            <td colspan="5" class="px-5 py-16 text-center">
              <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center">
                  <i class="pi pi-users text-2xl text-gray-300"></i>
                </div>
                <p class="text-gray-400 font-medium text-sm">Aucun utilisateur trouvé</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer pagination -->
      <div class="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
        <span class="text-xs text-gray-400">
          {{ filteredUsers.length }} utilisateur(s) · page {{ currentPage }} / {{ totalPages }}
        </span>
        <div class="flex items-center gap-1">
          <Button
            icon="pi pi-chevron-left"
            text rounded size="small"
            severity="secondary"
            :disabled="currentPage === 1"
            @click="currentPage--"
          />
          <span class="text-xs text-gray-500 px-2 font-medium">{{ currentPage }}</span>
          <Button
            icon="pi pi-chevron-right"
            text rounded size="small"
            severity="secondary"
            :disabled="currentPage >= totalPages"
            @click="currentPage++"
          />
        </div>
      </div>
    </div>

    <!-- ── Dialog accorder accès ── -->
    <Dialog
      v-model:visible="grantDialog"
      header="Gérer les accès"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '480px' }"
    >
      <div v-if="selectedUser" class="space-y-5 mt-2">

        <!-- User info -->
        <div class="flex items-center gap-3 p-4 bg-gray-50 rounded-xl">
          <div class="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center text-teal-700 font-bold shrink-0">
            {{ selectedUser.full_name.charAt(0).toUpperCase() }}
          </div>
          <div>
            <p class="font-semibold text-gray-900">{{ selectedUser.full_name }}</p>
            <p class="text-xs text-gray-500">{{ selectedUser.email }}</p>
          </div>
        </div>

        <!-- Grant all -->
        <div class="bg-teal-50 border border-teal-100 rounded-xl p-4 flex items-center justify-between gap-4">
          <div>
            <p class="text-sm font-semibold text-teal-800">Accès complet</p>
            <p class="text-xs text-teal-600 mt-0.5">Donner accès à tous les niveaux disponibles</p>
          </div>
          <Button
            label="Tout accorder"
            icon="pi pi-star"
            size="small"
            severity="info"
            :loading="grantingAll"
            @click="handleGrantAll"
          />
        </div>

        <!-- Séparateur -->
        <div class="flex items-center gap-3">
          <div class="flex-1 h-px bg-gray-100"></div>
          <span class="text-xs text-gray-400 font-medium">ou par niveau</span>
          <div class="flex-1 h-px bg-gray-100"></div>
        </div>

        <!-- Select level -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Niveau spécifique</label>
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

    <!-- ── Dialog suppression ── -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer l'utilisateur ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '400px' }"
    >
      <div v-if="selectedUser" class="flex items-start gap-3 mt-2">
        <div class="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center shrink-0">
          <i class="pi pi-exclamation-triangle text-red-500"></i>
        </div>
        <div>
          <p class="font-semibold text-gray-900">{{ selectedUser.full_name }}</p>
          <p class="text-sm text-gray-500 mt-1">
            Cette action est irréversible. Toutes les données de cet utilisateur seront supprimées.
          </p>
        </div>
      </div>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button label="Supprimer" severity="danger" :loading="deleting" @click="handleDelete" />
      </template>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import type { UserAdminResponse } from '#shared/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const store      = useAdminUsersStore()
const examsStore = useExamsStore()
const toast      = useToast()

// ── Filters ──────────────────────────────────────────────
const search       = ref('')
const filterStatus = ref('')
const currentPage  = ref(1)
const pageSize     = 15

const statusOptions = [
  { label: 'Tous',       value: ''         },
  { label: 'Actifs',     value: 'active'   },
  { label: 'Désactivés', value: 'inactive' },
  { label: 'Admins',     value: 'admin'    },
]

const filteredUsers = computed(() => {
  let list = [...store.users]
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(u =>
      u.full_name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q)
    )
  }
  if (filterStatus.value === 'active')   list = list.filter(u => u.is_active)
  if (filterStatus.value === 'inactive') list = list.filter(u => !u.is_active)
  if (filterStatus.value === 'admin')    list = list.filter(u => u.is_admin)
  return list
})

const totalPages   = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize)))
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

// Reset page quand filtre change
watch([search, filterStatus], () => { currentPage.value = 1 })

// ── State ─────────────────────────────────────────────────
const togglingId    = ref<string | null>(null)
const deleting      = ref(false)
const granting      = ref(false)
const grantingAll   = ref(false)
const grantError    = ref('')
const grantDialog   = ref(false)
const deleteDialog  = ref(false)
const selectedUser  = ref<UserAdminResponse | null>(null)
const selectedLevelId = ref<string>('')

// ── Levels list ──────────────────────────────────────────
const allLevels = computed(() =>
  examsStore.catalog.flatMap(exam =>
    (exam.levels ?? []).map(level => ({
      label: `${exam.name} — ${level.cefr_code}`,
      value: level.id,
    }))
  )
)

// ── Helpers ──────────────────────────────────────────────
const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })

// ── Actions ──────────────────────────────────────────────
const handleToggle = async (user: UserAdminResponse) => {
  togglingId.value = user.id
  const res = await store.toggleActive(user.id)
  togglingId.value = null
  if (!res.success) toast.add({ severity: 'error', summary: 'Erreur', detail: res.error, life: 3000 })
}

const confirmDelete = (user: UserAdminResponse) => {
  selectedUser.value = user
  deleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedUser.value) return
  deleting.value = true
  const res = await store.deleteUser(selectedUser.value.id)
  deleting.value = false
  deleteDialog.value = false
  if (!res.success) toast.add({ severity: 'error', summary: 'Erreur', detail: res.error, life: 3000 })
}

const openGrantAccess = (user: UserAdminResponse) => {
  selectedUser.value  = user
  selectedLevelId.value = ''
  grantError.value    = ''
  grantDialog.value   = true
}

const handleGrantAccess = async () => {
  if (!selectedUser.value || !selectedLevelId.value) return
  granting.value   = true
  grantError.value = ''
  const res = await store.grantAccess(selectedUser.value.id, selectedLevelId.value)
  granting.value   = false
  if (res.success) {
    grantDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Accès accordé',
      detail: `${selectedUser.value.full_name} a accès au niveau sélectionné.`,
      life: 3000,
    })
  } else {
    grantError.value = res.error || "Erreur lors de l'attribution"
  }
}

const handleGrantAll = async () => {
  if (!selectedUser.value) return
  grantingAll.value = true
  grantError.value  = ''
  const res = await store.grantAllAccess(selectedUser.value.id)
  grantingAll.value = false
  if (res.success) {
    grantDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Accès complet accordé',
      detail: `${selectedUser.value.full_name} a maintenant accès à tous les niveaux.`,
      life: 3000,
    })
  } else {
    grantError.value = res.error || "Erreur lors de l'attribution globale"
  }
}

onMounted(async () => {
  await store.fetchUsers()
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog()
})
</script>