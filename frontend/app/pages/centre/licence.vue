<!-- pages/centre/licence.vue -->
<template>
  <div>
    <div v-if="loading" class="flex justify-center py-12">
      <i class="pi pi-spin pi-spinner text-3xl text-emerald-600"></i>
    </div>

    <div v-else-if="errorMessage" class="text-center py-12">
      <i class="pi pi-times-circle text-4xl text-red-500 mb-3"></i>
      <p class="text-gray-600">{{ errorMessage }}</p>
    </div>

    <div v-else-if="!usage?.license" class="text-center py-12">
      <i class="pi pi-exclamation-triangle text-4xl text-amber-500 mb-3"></i>
      <p class="text-gray-600">Aucune licence active pour votre centre.</p>
      <p class="text-sm text-gray-400 mt-1">Contactez ITIA pour activer ou renouveler votre licence.</p>
    </div>

    <div v-else class="max-w-2xl space-y-6">
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
          <div>
            <h3 class="text-lg font-bold text-gray-900">{{ usage.formula_label }}</h3>
            <p class="text-sm text-gray-400 mt-1">Licence de centre - GoToGermany</p>
          </div>
          <Tag :value="statusLabel" :severity="statusSeverity" class="self-start sm:self-auto" />
        </div>

        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <dt class="text-gray-400">Date de début</dt>
            <dd class="text-gray-900 font-medium mt-0.5">{{ formatDate(usage.license.start_date) }}</dd>
          </div>
          <div>
            <dt class="text-gray-400">Date d'échéance</dt>
            <dd class="text-gray-900 font-medium mt-0.5">{{ formatDate(usage.license.end_date) }}</dd>
          </div>
          <div>
            <dt class="text-gray-400">Places allouées</dt>
            <dd class="text-gray-900 font-medium mt-0.5">{{ usage.license.max_students }} étudiants</dd>
          </div>
          <div>
            <dt class="text-gray-400">Places utilisées</dt>
            <dd class="text-gray-900 font-medium mt-0.5">{{ usage.students_used }}</dd>
          </div>
          <div>
            <dt class="text-gray-400">Mode de paiement</dt>
            <dd class="text-gray-900 font-medium mt-0.5">{{ paymentMethodLabel }}</dd>
          </div>
          <div>
            <dt class="text-gray-400">Référence paiement</dt>
            <dd class="text-gray-900 font-medium mt-0.5">{{ usage.license.payment_reference || '—' }}</dd>
          </div>
        </dl>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h3 class="text-sm font-semibold text-gray-700">Attestation de licence</h3>
          <p class="text-xs text-gray-400 mt-1">Document PDF justificatif à télécharger ou imprimer</p>
        </div>
        <Button
          label="Télécharger le PDF"
          icon="pi pi-download"
          :loading="downloadingCertificate"
          class="w-full sm:w-auto"
          @click="downloadCertificate"
        />
      </div>

      <Message v-if="certificateError" severity="error" :closable="false">{{ certificateError }}</Message>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'centre',
  middleware: 'director',
})

import type { LicenseUsageResponse } from '#shared/api'
import { LicenseStatus, PaymentMethod } from '#shared/api'

const centerStaffStore = useCenterStaffStore()

const loading = ref(true)
const usage = ref<LicenseUsageResponse | null>(null)
const errorMessage = ref<string | null>(null)
const downloadingCertificate = ref(false)
const certificateError = ref<string | null>(null)

const statusLabel = computed(() => {
  switch (usage.value?.license?.status) {
    case LicenseStatus.ACTIVE: return 'Active'
    case LicenseStatus.PENDING: return 'En attente'
    case LicenseStatus.EXPIRED: return 'Expirée'
    case LicenseStatus.CANCELLED: return 'Annulée'
    default: return '—'
  }
})

const statusSeverity = computed(() => {
  switch (usage.value?.license?.status) {
    case LicenseStatus.ACTIVE: return 'success'
    case LicenseStatus.PENDING: return 'warn'
    default: return 'danger'
  }
})

const paymentMethodLabel = computed(() => {
  const method = usage.value?.license?.payment_method
  if (method === PaymentMethod.MOBILE_MONEY) return 'Mobile Money'
  if (method === PaymentMethod.BANK_TRANSFER) return 'Virement bancaire'
  return '—'
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

async function downloadCertificate() {
  downloadingCertificate.value = true
  certificateError.value = null
  const result = await centerStaffStore.fetchMyCertificate()
  downloadingCertificate.value = false
  if (result.success && result.certificateUrl) {
    window.open(result.certificateUrl, '_blank')
  } else {
    certificateError.value = result.error || 'Erreur lors de la génération du document.'
  }
}

onMounted(async () => {
  const result = await centerStaffStore.fetchMyUsage()
  if (result.success) {
    usage.value = result.usage ?? null
  } else {
    errorMessage.value = result.error || 'Erreur de chargement.'
  }
  loading.value = false
})
</script>