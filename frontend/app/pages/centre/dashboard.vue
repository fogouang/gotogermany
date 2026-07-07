<!-- pages/centre/dashboard.vue -->
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

    <div v-else class="space-y-6">
      <!-- Cartes résumé -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-500">Licence</span>
            <i class="pi pi-verified text-emerald-600"></i>
          </div>
          <p class="text-lg font-bold text-gray-900">{{ usage.formula_label || '—' }}</p>
          <p class="text-xs text-gray-400 mt-1">
            Du {{ formatDate(usage.license.start_date) }} au {{ formatDate(usage.license.end_date) }}
          </p>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-500">Places utilisées</span>
            <i class="pi pi-users text-emerald-600"></i>
          </div>
          <p class="text-lg font-bold text-gray-900">
            {{ usage.students_used }} / {{ usage.license.max_students }}
          </p>
          <div class="w-full bg-gray-100 rounded-full h-2 mt-2">
            <div
              class="h-2 rounded-full transition-all"
              :class="quotaBarColor"
              :style="{ width: quotaPercent + '%' }"
            ></div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-gray-500">Jours restants</span>
            <i class="pi pi-calendar text-emerald-600"></i>
          </div>
          <p class="text-lg font-bold" :class="daysColor">
            {{ usage.days_remaining ?? '—' }}
          </p>
          <p class="text-xs text-gray-400 mt-1">avant expiration de la licence</p>
        </div>
      </div>

      <!-- Alerte quota proche -->
      <div
        v-if="quotaPercent >= 90"
        class="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3"
      >
        <i class="pi pi-exclamation-triangle text-amber-500"></i>
        <p class="text-sm text-amber-800">
          Le quota de votre licence est presque atteint ({{ usage.students_used }}/{{ usage.license.max_students }}).
          Contactez ITIA pour une extension si besoin.
        </p>
      </div>

      <!-- Alerte expiration proche -->
      <div
        v-if="usage.days_remaining !== null && usage.days_remaining <= 7"
        class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3"
      >
        <i class="pi pi-clock text-red-500"></i>
        <p class="text-sm text-red-800">
          Votre licence expire dans {{ usage.days_remaining }} jour(s). Contactez ITIA pour renouveler.
        </p>
      </div>

      <!-- Répartition par succursale -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h3 class="text-sm font-semibold text-gray-700 mb-4">Répartition par succursale</h3>
        <div v-if="branchEntries.length === 0" class="text-sm text-gray-400">
          Aucune succursale enregistrée.
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="[branchName, count] in branchEntries"
            :key="branchName"
            class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
          >
            <span class="text-sm text-gray-700">{{ branchName }}</span>
            <span class="text-sm font-semibold text-gray-900">{{ count }} étudiant(s)</span>
          </div>
        </div>
      </div>

      <!-- Attestation -->
      <div class="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-between">
        <div>
          <h3 class="text-sm font-semibold text-gray-700">Attestation de licence</h3>
          <p class="text-xs text-gray-400 mt-1">Document justificatif à télécharger</p>
        </div>
        <Button
          label="Télécharger"
          icon="pi pi-download"
          size="small"
          :loading="downloadingCertificate"
          @click="downloadCertificate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'centre',
  middleware: 'director',
})

import type { LicenseUsageResponse } from '#shared/api'

const centerStaffStore = useCenterStaffStore()

const loading = ref(true)
const usage = ref<LicenseUsageResponse | null>(null)
const errorMessage = ref<string | null>(null)
const downloadingCertificate = ref(false)

const quotaPercent = computed(() => {
  if (!usage.value?.license?.max_students) return 0
  return Math.min(100, Math.round((usage.value.students_used / usage.value.license.max_students) * 100))
})

const quotaBarColor = computed(() => {
  if (quotaPercent.value >= 90) return 'bg-red-500'
  if (quotaPercent.value >= 70) return 'bg-amber-500'
  return 'bg-emerald-500'
})

const daysColor = computed(() => {
  const days = usage.value?.days_remaining
  if (days === null || days === undefined) return 'text-gray-900'
  if (days <= 7) return 'text-red-600'
  if (days <= 30) return 'text-amber-600'
  return 'text-gray-900'
})

const branchEntries = computed(() => {
  return Object.entries(usage.value?.branches_breakdown || {})
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

async function downloadCertificate() {
  downloadingCertificate.value = true
  const result = await centerStaffStore.fetchMyCertificate()
  downloadingCertificate.value = false
  if (result.success && result.certificateUrl) {
    window.open(result.certificateUrl, '_blank')
  }
}

onMounted(async () => {
  const result = await centerStaffStore.fetchMyUsage()
  if (result.success) {
    usage.value = result.usage ?? null
  } else {
    errorMessage.value = result.error || 'Erreur de chargement de votre licence.'
  }
  loading.value = false
})
</script>