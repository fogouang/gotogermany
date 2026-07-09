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

      <!-- Pool de crédits IA -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-gray-700">Crédits IA du centre</h3>
          <NuxtLink
            to="/centre/credits-historique"
            class="text-xs text-emerald-600 hover:text-emerald-700 font-medium flex items-center gap-1"
          >
            Voir l'historique
            <i class="pi pi-arrow-right text-xs"></i>
          </NuxtLink>
        </div>

        <div v-if="poolLoading" class="flex justify-center py-6">
          <i class="pi pi-spin pi-spinner text-2xl text-emerald-600"></i>
        </div>

        <div v-else-if="pool" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-xs text-gray-400 mb-1">Solde du pool</p>
              <p class="text-2xl font-bold text-gray-900">{{ pool.ai_credit_pool_balance }}</p>
              <p class="text-xs text-gray-400 mt-1">crédits disponibles</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-xs text-gray-400 mb-1">Défaut par étudiant</p>
              <p class="text-2xl font-bold text-gray-900">{{ pool.default_credits_per_student }}</p>
              <p class="text-xs text-gray-400 mt-1">crédits à la création d'un compte</p>
            </div>
          </div>

          <div
            v-if="pool.ai_credit_pool_balance < pool.default_credits_per_student"
            class="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2"
          >
            <i class="pi pi-exclamation-circle text-red-500 text-sm"></i>
            <p class="text-xs text-red-700">
              Pool insuffisant pour créer un nouvel étudiant. Contactez ITIA pour un rechargement.
            </p>
          </div>

          <div class="flex items-end gap-2 pt-2 border-t border-gray-100">
            <div class="flex-1">
              <label class="text-xs font-medium text-gray-600 mb-1 block">
                Modifier le défaut par étudiant
              </label>
              <InputNumber
                v-model="defaultCreditsForm"
                class="w-full"
                :min="0"
                :max="100"
                showButtons
              />
            </div>
            <Button
              label="Enregistrer"
              size="small"
              :loading="savingDefault"
              :disabled="defaultCreditsForm === pool.default_credits_per_student"
              @click="handleUpdateDefault"
            />
          </div>
          <p v-if="defaultError" class="text-sm text-red-600">{{ defaultError }}</p>
        </div>
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

import type { LicenseUsageResponse, CenterPoolResponse } from '#shared/api'

const centerStaffStore = useCenterStaffStore()

const loading = ref(true)
const usage = ref<LicenseUsageResponse | null>(null)
const errorMessage = ref<string | null>(null)
const downloadingCertificate = ref(false)

const poolLoading = ref(true)
const pool = ref<CenterPoolResponse | null>(null)
const defaultCreditsForm = ref(0)
const savingDefault = ref(false)
const defaultError = ref<string | null>(null)

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

async function loadPool() {
  poolLoading.value = true
  const result = await centerStaffStore.fetchMyPool()
  if (result.success && result.pool) {
    pool.value = result.pool
    defaultCreditsForm.value = result.pool.default_credits_per_student
  }
  poolLoading.value = false
}

async function handleUpdateDefault() {
  savingDefault.value = true
  defaultError.value = null
  const result = await centerStaffStore.updateDefaultCredits(defaultCreditsForm.value)
  savingDefault.value = false
  if (result.success && result.pool) {
    pool.value = result.pool
  } else {
    defaultError.value = result.error || "Erreur lors de la mise à jour."
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

  await loadPool()
})
</script>