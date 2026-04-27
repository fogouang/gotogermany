<template>
  <div class="space-y-6">

    <!-- Toolbar -->
    <div class="flex items-center justify-between gap-4">
      <InputText
        v-model="search"
        placeholder="Rechercher un partenaire..."
        class="w-72"
      />
      <Button
        label="Nouveau partenaire"
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
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Partenaire</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell">Email</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell">Codes</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell">Utilisations</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden lg:table-cell">Commission due</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Statut</th>
            <th class="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="partner in filteredPartners"
            :key="partner.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- Nom -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 bg-primary-100 rounded-lg flex items-center justify-center shrink-0">
                  <i class="pi pi-building text-primary-600 text-sm"></i>
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ partner.name }}</p>
                  <p class="text-xs text-gray-400">{{ formatDate(partner.created_at) }}</p>
                </div>
              </div>
            </td>

            <!-- Email -->
            <td class="px-5 py-4 text-gray-600 hidden sm:table-cell">
              <div>
                <p>{{ partner.contact_email }}</p>
                <p v-if="partner.phone" class="text-xs text-gray-400">{{ partner.phone }}</p>
              </div>
            </td>

            <!-- Codes -->
            <td class="px-5 py-4 hidden md:table-cell">
              <span class="font-medium text-gray-900">
                {{ stats[partner.id]?.total_codes ?? '—' }}
              </span>
              <span v-if="stats[partner.id]" class="text-xs text-gray-400 ml-1">
                ({{ stats[partner.id]?.active_codes }} actifs)
              </span>
            </td>

            <!-- Utilisations -->
            <td class="px-5 py-4 hidden md:table-cell">
              <span class="font-medium text-gray-900">
                {{ stats[partner.id]?.total_uses ?? '—' }}
              </span>
            </td>

            <!-- Commission -->
            <td class="px-5 py-4 hidden lg:table-cell">
              <span class="font-semibold text-primary-600">
                {{ stats[partner.id]
                  ? stats[partner.id]?.total_commission_due?.toFixed(0) + ' FCFA'
                  : '—' }}
              </span>
            </td>

            <!-- Statut -->
            <td class="px-5 py-4">
              <Tag
                :value="partner.is_active ? 'Actif' : 'Inactif'"
                :severity="partner.is_active ? 'success' : 'danger'"
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
                  @click="openEdit(partner)"
                />
                <Button
                  icon="pi pi-trash"
                  text
                  rounded
                  size="small"
                  severity="danger"
                  v-tooltip.top="'Supprimer'"
                  @click="confirmDelete(partner)"
                />
              </div>
            </td>
          </tr>

          <!-- Empty -->
          <tr v-if="filteredPartners.length === 0">
            <td colspan="7" class="px-5 py-12 text-center text-gray-400">
              <i class="pi pi-building text-3xl mb-2 block"></i>
              Aucun partenaire trouvé
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer -->
      <div class="px-5 py-3 border-t border-gray-100 text-xs text-gray-400">
        {{ filteredPartners.length }} partenaire(s) sur {{ store.partners.length }}
      </div>
    </div>

    <!-- Dialog créer/modifier -->
    <Dialog
      v-model:visible="formDialog"
      :header="editingPartner ? 'Modifier le partenaire' : 'Nouveau partenaire'"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '500px' }"
    >
      <div class="space-y-4 mt-2">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nom *</label>
          <InputText v-model="form.name" class="w-full" placeholder="Centre de langue Berlin" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email de contact *</label>
          <InputText v-model="form.contact_email" type="email" class="w-full" placeholder="contact@centre.com" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
          <InputText v-model="form.phone" class="w-full" placeholder="+237 6XX XXX XXX" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Notes internes</label>
          <Textarea v-model="form.notes" class="w-full" :rows="3" placeholder="Informations internes..." />
        </div>
        <Message v-if="formError" severity="error" :closable="false">{{ formError }}</Message>
      </div>

      <template #footer>
        <Button label="Annuler" text @click="formDialog = false" />
        <Button
          :label="editingPartner ? 'Enregistrer' : 'Créer'"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!form.name || !form.contact_email"
          @click="handleSave"
        />
      </template>
    </Dialog>

    <!-- Dialog supprimer -->
    <Dialog
      v-model:visible="deleteDialog"
      header="Supprimer le partenaire ?"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '400px' }"
    >
      <p v-if="selectedPartner">
        Supprimer <strong>{{ selectedPartner.name }}</strong> ? Les codes promo associés seront aussi supprimés.
      </p>
      <template #footer>
        <Button label="Annuler" text @click="deleteDialog = false" />
        <Button label="Supprimer" severity="danger" :loading="deleting" @click="handleDelete" />
      </template>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import type { PartnerDetailResponse, PartnerStatsResponse } from '#shared/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const store = useAdminPartnersStore()
const toast = useToast()

const search = ref('')
const formDialog = ref(false)
const deleteDialog = ref(false)
const saving = ref(false)
const deleting = ref(false)
const formError = ref('')
const editingPartner = ref<PartnerDetailResponse | null>(null)
const selectedPartner = ref<PartnerDetailResponse | null>(null)
const stats = ref<Record<string, PartnerStatsResponse>>({})

const defaultForm = () => ({
  name: '',
  contact_email: '',
  phone: '',
  notes: '',
})

const form = ref(defaultForm())

const filteredPartners = computed(() => {
  if (!search.value) return store.partners
  const q = search.value.toLowerCase()
  return store.partners.filter(p =>
    p.name.toLowerCase().includes(q) ||
    p.contact_email.toLowerCase().includes(q)
  )
})

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })

const openCreate = () => {
  editingPartner.value = null
  form.value = defaultForm()
  formError.value = ''
  formDialog.value = true
}

const openEdit = (partner: PartnerDetailResponse) => {
  editingPartner.value = partner
  form.value = {
    name: partner.name,
    contact_email: partner.contact_email,
    phone: (partner as any).phone || '',
    notes: partner.notes || '',
  }
  formError.value = ''
  formDialog.value = true
}

const handleSave = async () => {
  saving.value = true
  formError.value = ''

  const payload = {
    name: form.value.name,
    contact_email: form.value.contact_email,
    phone: form.value.phone || null,
    notes: form.value.notes || null,
  }

  let res
  if (editingPartner.value) {
    res = await store.updatePartner(editingPartner.value.id, payload)
  } else {
    res = await store.createPartner(payload)
  }

  saving.value = false

  if (res.success) {
    formDialog.value = false
    toast.add({
      severity: 'success',
      summary: editingPartner.value ? 'Modifié' : 'Créé',
      detail: `Partenaire ${editingPartner.value ? 'mis à jour' : 'créé'} avec succès.`,
      life: 3000,
    })
    if (res.data) loadStats(res.data.id)
  } else {
    formError.value = res.error || 'Erreur lors de la sauvegarde'
  }
}

const confirmDelete = (partner: PartnerDetailResponse) => {
  selectedPartner.value = partner
  deleteDialog.value = true
}

const handleDelete = async () => {
  if (!selectedPartner.value) return
  deleting.value = true
  const res = await store.deletePartner(selectedPartner.value.id)
  deleting.value = false
  deleteDialog.value = false
  if (!res.success) {
    toast.add({ severity: 'error', summary: 'Erreur', detail: res.error, life: 3000 })
  }
}

const loadStats = async (partnerId: string) => {
  const s = await store.getStats(partnerId)
  if (s) stats.value[partnerId] = s
}

onMounted(async () => {
  await store.fetchPartners()
  store.partners.forEach(p => loadStats(p.id))
})
</script>