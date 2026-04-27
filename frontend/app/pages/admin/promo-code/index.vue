<template>
  <div class="space-y-6">

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div class="flex gap-3">
        <InputText
          v-model="search"
          placeholder="Rechercher un code..."
          class="w-64"
        />
        <Select
          v-model="filterStatus"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          class="w-36"
        />
      </div>
      <Button
        label="Nouveau code"
        icon="pi pi-plus"
        @click="openCreate"
      />
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Code</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell">Réduction</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell">Partenaire</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell">Utilisations</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell">Expiration</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Statut</th>
            <th class="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="code in filteredCodes"
            :key="code.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- Code -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-2">
                <code class="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs font-mono font-bold">
                  {{ code.code }}
                </code>
                <button
                  class="text-gray-400 hover:text-gray-600"
                  v-tooltip.top="'Copier'"
                  @click="copyCode(code.code)"
                >
                  <i class="pi pi-copy text-xs"></i>
                </button>
              </div>
            </td>

            <!-- Réduction -->
            <td class="px-5 py-4 hidden sm:table-cell">
              <span class="font-semibold text-primary-600">
                {{ formatDiscount(code) }}
              </span>
              <span class="text-xs text-gray-400 ml-1">
                · comm. {{ code.commission_rate }}%
              </span>
            </td>

            <!-- Partenaire -->
            <td class="px-5 py-4 hidden md:table-cell text-gray-600">
              {{ getPartnerName(code.partner_id) }}
            </td>

            <!-- Utilisations -->
            <td class="px-5 py-4 hidden md:table-cell">
              <div class="flex items-center gap-2">
                <span class="font-medium text-gray-900">{{ code.used_count }}</span>
                <span v-if="code.max_uses" class="text-gray-400">/ {{ code.max_uses }}</span>
                <span v-else class="text-xs text-gray-400">illimité</span>
              </div>
              <div v-if="code.max_uses" class="w-16 bg-gray-200 rounded-full h-1 mt-1">
                <div
                  class="h-1 rounded-full bg-primary-500"
                  :style="{ width: `${Math.min((code.used_count / code.max_uses) * 100, 100)}%` }"
                />
              </div>
            </td>

            <!-- Expiration -->
            <td class="px-5 py-4 hidden lg:table-cell text-gray-500">
              <span v-if="code.expires_at" :class="isExpired(code.expires_at) ? 'text-red-500' : ''">
                {{ formatDate(code.expires_at) }}
              </span>
              <span v-else class="text-gray-400">—</span>
            </td>

            <!-- Statut -->
            <td class="px-5 py-4">
              <Tag
                :value="getStatusLabel(code)"
                :severity="getStatusSeverity(code)"
              />
            </td>

            <!-- Actions -->
            <td class="px-5 py-4">
              <div class="flex items-center justify-end gap-1">
                <Button
                  :icon="code.is_active ? 'pi pi-pause' : 'pi pi-play'"
                  text
                  rounded
                  size="small"
                  :severity="code.is_active ? 'warn' : 'success'"
                  v-tooltip.top="code.is_active ? 'Désactiver' : 'Activer'"
                  @click="handleToggle(code)"
                />
                <Button
                  icon="pi pi-pencil"
                  text
                  rounded
                  size="small"
                  severity="secondary"
                  v-tooltip.top="'Modifier'"
                  @click="openEdit(code)"
                />
                <Button
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  @click="confirmDelete(code)"
                />
              </div>
            </td>
          </tr>

          <!-- Empty -->
          <tr v-if="filteredCodes.length === 0">
            <td colspan="7" class="px-5 py-12 text-center text-gray-400">
              <i class="pi pi-tag text-3xl mb-2 block"></i>
              Aucun code promo trouvé
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer -->
      <div class="px-5 py-3 border-t border-gray-100 text-xs text-gray-400">
        {{ filteredCodes.length }} code(s) affiché(s) sur {{ store.codes.length }}
      </div>
    </div>

    <!-- Dialog créer -->
    <Dialog
      v-model:visible="createDialog"
      header="Nouveau code promo"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '500px' }"
    >
      <div class="space-y-4 mt-2">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Code *</label>
            <InputText
              v-model="createForm.code"
              class="w-full font-mono uppercase"
              placeholder="GOETHE20"
              @input="createForm.code = createForm.code.toUpperCase()"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Partenaire</label>
            <Select
              v-model="createForm.partner_id"
              :options="partnerOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Sans partenaire"
              class="w-full"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Type de réduction *</label>
            <Select
              v-model="createForm.discount_type"
              :options="discountTypeOptions"
              optionLabel="label"
              optionValue="value"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Valeur *
              <span class="text-gray-400 font-normal">
                ({{ createForm.discount_type === 'percent' ? '%' : 'FCFA' }})
              </span>
            </label>
            <InputNumber
              v-model="createForm.discount_value"
              class="w-full"
              :min="0"
              :max="createForm.discount_type === 'percent' ? 100 : undefined"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Commission (%)</label>
            <InputNumber v-model="createForm.commission_rate" class="w-full" :min="0" :max="100" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Max utilisations</label>
            <InputNumber v-model="createForm.max_uses" class="w-full" :min="1" placeholder="Illimité" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date d'expiration</label>
          <DatePicker v-model="createForm.expires_at" class="w-full" dateFormat="dd/mm/yy" showIcon />
        </div>

        <Message v-if="createError" severity="error" :closable="false">
          {{ createError }}
        </Message>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="createDialog = false" />
        <Button
          label="Créer"
          icon="pi pi-check"
          :loading="creating"
          :disabled="!createForm.code || !createForm.discount_value"
          @click="handleCreate"
        />
      </template>
    </Dialog>

    <!-- Dialog modifier -->
    <Dialog
      v-model:visible="editDialog"
      header="Modifier le code promo"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '450px' }"
    >
      <div v-if="editingCode" class="space-y-4 mt-2">
        <div class="p-3 bg-gray-50 rounded-lg">
          <code class="font-mono font-bold text-gray-800">{{ editingCode.code }}</code>
          <span class="text-gray-400 text-sm ml-2">— {{ formatDiscount(editingCode) }}</span>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Commission (%)</label>
            <InputNumber v-model="editForm.commission_rate" class="w-full" :min="0" :max="100" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Max utilisations</label>
            <InputNumber v-model="editForm.max_uses" class="w-full" :min="1" placeholder="Illimité" />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date d'expiration</label>
          <DatePicker v-model="editForm.expires_at" class="w-full" dateFormat="dd/mm/yy" showIcon />
        </div>

        <div class="flex items-center gap-3">
          <ToggleSwitch v-model="editForm.is_active" />
          <span class="text-sm text-gray-700">Code actif</span>
        </div>

        <Message v-if="editError" severity="error" :closable="false">
          {{ editError }}
        </Message>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="editDialog = false" />
        <Button
          label="Enregistrer"
          icon="pi pi-check"
          :loading="editing"
          @click="handleEdit"
        />
      </template>
    </Dialog>

    <!-- Dialog supprimer -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le code ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '400px' }"
    >
      <p v-if="selectedCode">
        Supprimer le code <strong>{{ selectedCode.code }}</strong> ? Cette action est irréversible.
      </p>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button label="Supprimer" severity="danger" :loading="deleting" @click="handleDelete" />
      </template>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import type { PromoCodeResponse } from '#shared/api'
import { PromoCodeCreateRequest } from '#shared/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const store = useAdminPromoCodesStore()
const partnersStore = useAdminPartnersStore()
const toast = useToast()

const search = ref('')
const filterStatus = ref('')
const createDialog = ref(false)
const editDialog = ref(false)
const deleteDialog = ref(false)
const creating = ref(false)
const editing = ref(false)
const deleting = ref(false)
const createError = ref('')
const editError = ref('')
const editingCode = ref<PromoCodeResponse | null>(null)
const selectedCode = ref<PromoCodeResponse | null>(null)

const statusOptions = [
  { label: 'Tous', value: '' },
  { label: 'Actifs', value: 'active' },
  { label: 'Inactifs', value: 'inactive' },
  { label: 'Expirés', value: 'expired' },
]

const discountTypeOptions = [
  { label: 'Pourcentage (%)', value: 'percent' },
  { label: 'Montant fixe (FCFA)', value: 'fixed' },
]

const defaultCreateForm = () => ({
  code: '',
  partner_id: null as string | null,
  discount_type: PromoCodeCreateRequest.discount_type.PERCENT,
  discount_value: 10,
  commission_rate: 0,
  max_uses: null as number | null,
  expires_at: null as Date | null,
  is_active: true,
})

const createForm = ref(defaultCreateForm())

const editForm = ref({
  commission_rate: 0,
  max_uses: null as number | null,
  expires_at: null as Date | null,
  is_active: true,
})

const partnerOptions = computed(() => [
  { label: 'Sans partenaire', value: null },
  ...partnersStore.partners.map(p => ({ label: p.name, value: p.id })),
])

const filteredCodes = computed(() => {
  let list = [...store.codes]

  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(c => c.code.toLowerCase().includes(q))
  }

  if (filterStatus.value === 'active') list = list.filter(c => c.is_active && !isExpired(c.expires_at))
  if (filterStatus.value === 'inactive') list = list.filter(c => !c.is_active)
  if (filterStatus.value === 'expired') list = list.filter(c => isExpired(c.expires_at))

  return list
})

const getPartnerName = (partnerId: string | null) => {
  if (!partnerId) return '—'
  return partnersStore.partners.find(p => p.id === partnerId)?.name || '—'
}

const formatDiscount = (code: PromoCodeResponse) => {
  return code.discount_type === 'percent'
    ? `${code.discount_value}%`
    : `${code.discount_value} FCFA`
}

const isExpired = (expiresAt: string | null) => {
  if (!expiresAt) return false
  return new Date(expiresAt) < new Date()
}

const formatDate = (d: string | null) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

const getStatusLabel = (code: PromoCodeResponse) => {
  if (isExpired(code.expires_at)) return 'Expiré'
  if (!code.is_active) return 'Inactif'
  if (code.max_uses && code.used_count >= code.max_uses) return 'Épuisé'
  return 'Actif'
}

const getStatusSeverity = (code: PromoCodeResponse) => {
  if (isExpired(code.expires_at)) return 'danger'
  if (!code.is_active) return 'secondary'
  if (code.max_uses && code.used_count >= code.max_uses) return 'warn'
  return 'success'
}

const copyCode = async (code: string) => {
  await navigator.clipboard.writeText(code)
  toast.add({ severity: 'success', summary: 'Copié !', detail: code, life: 2000 })
}

const openCreate = () => {
  createForm.value = defaultCreateForm()
  createError.value = ''
  createDialog.value = true
}

const handleCreate = async () => {
  creating.value = true
  createError.value = ''

  const payload = {
    code: createForm.value.code,
    partner_id: createForm.value.partner_id || null,
    discount_type: createForm.value.discount_type,
    discount_value: createForm.value.discount_value,
    commission_rate: createForm.value.commission_rate,
    max_uses: createForm.value.max_uses || null,
    expires_at: createForm.value.expires_at
      ? (createForm.value.expires_at as Date).toISOString()
      : null,
    is_active: true,
  }

  const res = await store.createCode(payload)
  creating.value = false

  if (res.success) {
    createDialog.value = false
    toast.add({ severity: 'success', summary: 'Code créé', detail: `Code ${payload.code} créé.`, life: 3000 })
  } else {
    createError.value = res.error || 'Erreur lors de la création'
  }
}

const openEdit = (code: PromoCodeResponse) => {
  editingCode.value = code
  editForm.value = {
    commission_rate: code.commission_rate,
    max_uses: code.max_uses,
    expires_at: code.expires_at ? new Date(code.expires_at) : null,
    is_active: code.is_active,
  }
  editError.value = ''
  editDialog.value = true
}

const handleEdit = async () => {
  if (!editingCode.value) return
  editing.value = true
  editError.value = ''

  const payload = {
    commission_rate: editForm.value.commission_rate,
    max_uses: editForm.value.max_uses || null,
    expires_at: editForm.value.expires_at
      ? (editForm.value.expires_at as Date).toISOString()
      : null,
    is_active: editForm.value.is_active,
  }

  const res = await store.updateCode(editingCode.value.id, payload)
  editing.value = false

  if (res.success) {
    editDialog.value = false
    toast.add({ severity: 'success', summary: 'Modifié', detail: 'Code mis à jour.', life: 3000 })
  } else {
    editError.value = res.error || 'Erreur lors de la modification'
  }
}

const handleToggle = async (code: PromoCodeResponse) => {
  await store.updateCode(code.id, { is_active: !code.is_active })
}

const confirmDelete = (code: PromoCodeResponse) => {
  selectedCode.value = code
  deleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedCode.value) return
  deleting.value = true
  const res = await store.deleteCode(selectedCode.value.id)
  deleting.value = false
  deleteDialog.value = false
  if (!res.success) {
    toast.add({ severity: 'error', summary: 'Erreur', detail: res.error, life: 3000 })
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchCodes(),
    partnersStore.partners.length === 0 ? partnersStore.fetchPartners() : Promise.resolve(),
  ])
})
</script>