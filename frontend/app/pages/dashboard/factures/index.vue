<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Mes paiements</h1>
      <p class="text-sm text-gray-500">Historique de vos achats et factures</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Vide -->
    <div v-else-if="myPayments.length === 0" class="text-center py-16 bg-white rounded-xl border border-gray-100">
      <i class="pi pi-receipt text-4xl text-gray-300 mb-3 block"></i>
      <p class="font-medium text-gray-600">Aucun paiement</p>
      <p class="text-sm text-gray-400 mb-4">Vous n'avez pas encore effectué d'achat</p>
      <Button label="Voir les tarifs" icon="pi pi-tag" @click="navigateTo('/tarifs')" />
    </div>

    <!-- Liste paiements -->
    <div v-else class="space-y-3">
      <div
        v-for="payment in myPayments"
        :key="payment.id"
        class="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between gap-4">
          <!-- Infos paiement -->
          <div class="flex items-start gap-4">
            <!-- Icône statut -->
            <div :class="[
              'w-10 h-10 rounded-full flex items-center justify-center shrink-0',
              payment.payment_status === 'COMPLETED' ? 'bg-green-100' :
              payment.payment_status === 'FAILED' ? 'bg-red-100' : 'bg-amber-100'
            ]">
              <i :class="[
                'pi text-sm',
                payment.payment_status === 'COMPLETED' ? 'pi-check text-green-600' :
                payment.payment_status === 'FAILED' ? 'pi-times text-red-600' : 'pi-clock text-amber-600'
              ]"></i>
            </div>

            <div>
              <p class="font-semibold text-gray-900">{{ payment.amount_paid.toLocaleString('fr-FR') }} FCFA</p>
              <p class="text-xs text-gray-400 mt-0.5">Réf. {{ payment.transaction_reference }}</p>
              <p class="text-xs text-gray-400">{{ formatDate(payment.created_at) }}</p>
              <div class="flex items-center gap-2 mt-2">
                <Tag
                  :value="formatStatus(payment.payment_status)"
                  :severity="payment.payment_status === 'COMPLETED' ? 'success' : payment.payment_status === 'FAILED' ? 'danger' : 'warn'"
                />
                <span v-if="payment.operator" class="text-xs text-gray-400">{{ payment.operator }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 shrink-0">
            <Button
              v-if="payment.payment_status === 'COMPLETED'"
              icon="pi pi-file-pdf"
              label="Facture"
              size="small"
              outlined
              severity="secondary"
              :loading="loadingInvoice === payment.id"
              @click="openInvoice(payment.id)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Dialog Facture ──────────────────────────── -->
    <Dialog
      v-model:visible="invoiceDialog"
      header="Facture"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '520px' }"
    >
      <div v-if="invoiceLoading" class="flex justify-center py-8">
        <ProgressSpinner style="width: 40px; height: 40px" />
      </div>

      <div v-else-if="currentInvoice" class="space-y-4 mt-2">
        <!-- Header facture -->
        <div class="bg-gradient-primary text-white rounded-xl p-4 text-center">
          <i class="pi pi-check-circle text-3xl mb-2 block"></i>
          <p class="font-bold text-lg">Paiement confirmé</p>
          <p class="text-white/80 text-sm">{{ currentInvoice.transaction_reference }}</p>
        </div>

        <!-- Détails -->
        <div class="space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">Client</span>
            <span class="font-medium text-gray-900">{{ currentInvoice.customer_name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Produit</span>
            <span class="font-medium text-gray-900 text-right max-w-48">{{ currentInvoice.product_description }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Date</span>
            <span class="font-medium text-gray-900">{{ formatDate(currentInvoice.payment_date) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Opérateur</span>
            <span class="font-medium text-gray-900">{{ currentInvoice.operator || '—' }}</span>
          </div>
          <Divider />
          <div v-if="currentInvoice.discount_amount > 0" class="flex justify-between text-green-600">
            <span>Réduction</span>
            <span>- {{ currentInvoice.discount_amount.toLocaleString('fr-FR') }} FCFA</span>
          </div>
          <div class="flex justify-between font-bold text-base">
            <span class="text-gray-900">Total payé</span>
            <span class="text-green-700">{{ currentInvoice.amount_paid.toLocaleString('fr-FR') }} FCFA</span>
          </div>
        </div>

        <!-- Partenaire -->
        <div v-if="currentInvoice.partner_info" class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
          <i class="pi pi-tag mr-1"></i>
          Code partenaire <strong>{{ currentInvoice.partner_info.code }}</strong> — {{ currentInvoice.partner_info.partner_name }}
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
definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const { myPayments, loading, fetchMyPayments, formatAmount } = usePayments()
const { currentInvoice, fetchInvoice, generateInvoice, downloadInvoice, formatDate } = useInvoices()

const invoiceDialog = ref(false)
const invoiceLoading = ref(false)
const loadingInvoice = ref<string | null>(null)

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    COMPLETED: 'Payé', FAILED: 'Échoué', PENDING: 'En attente'
  }
  return map[status] || status
}

const openInvoice = async (paymentId: string) => {
  loadingInvoice.value = paymentId
  invoiceDialog.value = true
  invoiceLoading.value = true
  await fetchInvoice(paymentId)
  invoiceLoading.value = false
  loadingInvoice.value = null
}

const handleGenerate = async () => {
  if (!currentInvoice.value) return
  invoiceLoading.value = true
  await generateInvoice(currentInvoice.value.payment_id)
  invoiceLoading.value = false
}

onMounted(fetchMyPayments)
</script>