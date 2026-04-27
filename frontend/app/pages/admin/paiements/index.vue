<template>
  <div class="space-y-6">
    <!-- Header + stats -->
    <div>
      <h2 class="text-lg font-semibold text-gray-900">Paiements</h2>
      <p class="text-sm text-gray-500">Historique et gestion des paiements</p>
    </div>

    <!-- Stats -->
    <div v-if="summary" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <p class="text-2xl font-bold text-gray-900">{{ summary.total_completed }}</p>
        <p class="text-xs text-gray-500 mt-1">Paiements réussis</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <p class="text-2xl font-bold text-green-700">{{ summary.total_revenue.toLocaleString('fr-FR') }}</p>
        <p class="text-xs text-gray-500 mt-1">Revenus FCFA</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <p class="text-2xl font-bold text-amber-600">{{ summary.total_commissions_due.toLocaleString('fr-FR') }}</p>
        <p class="text-xs text-gray-500 mt-1">Commissions dues FCFA</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <p class="text-2xl font-bold text-gray-900">{{ summary.total_payments }}</p>
        <p class="text-xs text-gray-500 mt-1">Total paiements</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <p class="text-2xl font-bold text-red-500">{{ summary.total_failed }}</p>
        <p class="text-xs text-gray-500 mt-1">Paiements échoués</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <p class="text-2xl font-bold text-blue-600">{{ summary.total_discounts.toLocaleString('fr-FR') }}</p>
        <p class="text-xs text-gray-500 mt-1">Réductions accordées FCFA</p>
      </div>
    </div>

    <!-- Table paiements -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-semibold text-gray-900">Tous les paiements</h3>
        <div class="flex gap-2">
          <Select
            v-model="filterStatus"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Tous les statuts"
            class="w-44"
          />
        </div>
      </div>

      <div v-if="loadingPayments" class="flex justify-center py-8">
        <ProgressSpinner style="width: 40px; height: 40px" />
      </div>

      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Référence</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden md:table-cell">Date</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Montant</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase hidden sm:table-cell">Opérateur</th>
            <th class="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Statut</th>
            <th class="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="payment in filteredPayments" :key="payment.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-5 py-4">
              <p class="font-mono text-xs text-gray-700">{{ payment.transaction_reference }}</p>
              <p v-if="payment.promo_code_id" class="text-xs text-amber-600 mt-0.5">
                <i class="pi pi-tag mr-1"></i>Code promo
              </p>
            </td>
            <td class="px-5 py-4 hidden md:table-cell text-xs text-gray-500">
              {{ formatDate(payment.created_at) }}
            </td>
            <td class="px-5 py-4">
              <p class="font-semibold text-gray-900">{{ payment.amount_paid.toLocaleString('fr-FR') }} FCFA</p>
              <p v-if="payment.discount_amount > 0" class="text-xs text-green-600">
                -{{ payment.discount_amount.toLocaleString('fr-FR') }} FCFA
              </p>
            </td>
            <td class="px-5 py-4 hidden sm:table-cell text-xs text-gray-500">{{ payment.operator || '—' }}</td>
            <td class="px-5 py-4">
              <Tag
                :value="formatStatus(payment.payment_status)"
                :severity="payment.payment_status === 'COMPLETED' ? 'success' : payment.payment_status === 'FAILED' ? 'danger' : 'warn'"
              />
            </td>
            <td class="px-5 py-4">
              <div class="flex items-center justify-end gap-1">
                <Button
                  v-if="payment.payment_status === 'COMPLETED'"
                  icon="pi pi-file-pdf"
                  text rounded size="small"
                  severity="secondary"
                  v-tooltip.top="'Voir la facture'"
                  @click="openInvoice(payment.id)"
                />
              </div>
            </td>
          </tr>
          <tr v-if="filteredPayments.length === 0">
            <td colspan="6" class="px-5 py-10 text-center text-gray-400">
              Aucun paiement trouvé
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ─── Dialog Facture ──────────────────────────── -->
    <Dialog
      v-model:visible="invoiceDialog"
      header="Détail facture"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '540px' }"
    >
      <div v-if="invoiceLoading" class="flex justify-center py-8">
        <ProgressSpinner style="width: 40px; height: 40px" />
      </div>

      <div v-else-if="currentInvoice" class="space-y-4 mt-2 text-sm">
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-400">Client</p>
            <p class="font-medium text-gray-900">{{ currentInvoice.customer_name }}</p>
            <p class="text-xs text-gray-500">{{ currentInvoice.customer_email }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-400">Date</p>
            <p class="font-medium text-gray-900">{{ formatDate(currentInvoice.payment_date) }}</p>
          </div>
        </div>

        <div class="bg-gray-50 rounded-lg p-3">
          <p class="text-xs text-gray-400 mb-1">Produit</p>
          <p class="font-medium text-gray-900">{{ currentInvoice.product_description }}</p>
        </div>

        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-500">Montant brut</span>
            <span>{{ currentInvoice.amount_gross.toLocaleString('fr-FR') }} FCFA</span>
          </div>
          <div v-if="currentInvoice.discount_amount > 0" class="flex justify-between text-green-600">
            <span>Réduction</span>
            <span>- {{ currentInvoice.discount_amount.toLocaleString('fr-FR') }} FCFA</span>
          </div>
          <div class="flex justify-between font-bold text-base border-t border-gray-100 pt-2">
            <span>Total payé</span>
            <span class="text-green-700">{{ currentInvoice.amount_paid.toLocaleString('fr-FR') }} FCFA</span>
          </div>
        </div>

        <!-- Partenaire -->
        <div v-if="currentInvoice.partner_info" class="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <p class="text-xs font-semibold text-amber-800 mb-2">Code partenaire utilisé</p>
          <div class="flex justify-between text-xs">
            <span class="text-amber-700">Code : <strong>{{ currentInvoice.partner_info.code }}</strong></span>
            <span class="text-amber-700">Partenaire : {{ currentInvoice.partner_info.partner_name }}</span>
          </div>
          <div class="flex justify-between text-xs mt-1">
            <span class="text-amber-700">Commission due :</span>
            <span class="font-bold text-amber-800">{{ currentInvoice.partner_info.commission_due.toLocaleString('fr-FR') }} FCFA</span>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Fermer" text @click="invoiceDialog = false" />
        <Button
          v-if="currentInvoice?.invoice_url"
          label="Télécharger PDF"
          icon="pi pi-download"
          @click="downloadInvoice(currentInvoice.invoice_url!, `facture-${currentInvoice.transaction_reference}.pdf`)"
        />
        <Button
          v-else-if="currentInvoice"
          label="Générer PDF"
          icon="pi pi-refresh"
          outlined
          :loading="invoiceLoading"
          @click="handleGenerate"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { PaymentSummaryResponse } from '#shared/api'

definePageMeta({ layout: 'admin', middleware: 'admin' })

const toast = useToast()
const { currentInvoice, fetchInvoice, generateInvoice, downloadInvoice, formatDate } = useInvoices()

// ── Stats ─────────────────────────────────────────────
const summary = ref<PaymentSummaryResponse | null>(null)

// ── Paiements ─────────────────────────────────────────
const payments = ref<any[]>([])
const loadingPayments = ref(false)
const filterStatus = ref('')

const statusOptions = [
  { label: 'Tous les statuts', value: '' },
  { label: 'Payés', value: 'COMPLETED' },
  { label: 'En attente', value: 'PENDING' },
  { label: 'Échoués', value: 'FAILED' },
]

const filteredPayments = computed(() => {
  if (!filterStatus.value) return payments.value
  return payments.value.filter(p => p.payment_status === filterStatus.value)
})

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    COMPLETED: 'Payé', FAILED: 'Échoué', PENDING: 'En attente'
  }
  return map[status] || status
}

const loadData = async () => {
  loadingPayments.value = true
  try {
    const { PaymentsService, OpenAPI } = await import('#shared/api')
    const config = useRuntimeConfig()
    OpenAPI.BASE = config.public.apiBaseUrl || 'http://localhost:8001'
    const tokenCookie = useCookie('access_token')
    OpenAPI.TOKEN = tokenCookie.value ?? undefined

    const [sum] = await Promise.all([
      PaymentsService.getSummaryApiV1PaymentsAdminSummaryGet(),
    ])
    summary.value = sum
  } catch (e: any) {
    toast.add({ severity: 'error', summary: e.body?.detail || 'Erreur', life: 3000 })
  } finally {
    loadingPayments.value = false
  }
}

// ── Facture ───────────────────────────────────────────
const invoiceDialog = ref(false)
const invoiceLoading = ref(false)

const openInvoice = async (paymentId: string) => {
  invoiceDialog.value = true
  invoiceLoading.value = true
  await fetchInvoice(paymentId)
  invoiceLoading.value = false
}

const handleGenerate = async () => {
  if (!currentInvoice.value) return
  invoiceLoading.value = true
  await generateInvoice(currentInvoice.value.payment_id)
  invoiceLoading.value = false
}

onMounted(loadData)
</script>