<!-- pages/referrals/index.vue -->
<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t("referrals.title") }}
      </h1>
      <p class="text-sm text-gray-500">{{ t("referrals.subtitle") }}</p>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-12">
      <ProgressSpinner style="width: 50px; height: 50px" />
    </div>

    <!-- Erreur -->
    <div
      v-else-if="store.error"
      class="max-w-lg mx-auto text-center py-12 space-y-4"
    >
      <i class="pi pi-exclamation-circle text-red-400 text-4xl"></i>
      <p class="text-red-600 font-medium">{{ store.error }}</p>
    </div>

    <template v-else-if="store.dashboard">
      <!-- Lien de parrainage -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
        <p class="text-sm font-semibold text-gray-700 mb-3">
          {{ t("referrals.your_link") }}
        </p>
        <div class="flex items-center gap-2">
          <input
            :value="store.referralLink"
            readonly
            class="flex-1 text-sm bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-gray-700"
          />
          <Button
            :label="copied ? t('referrals.copied') : t('referrals.copy')"
            :icon="copied ? 'pi pi-check' : 'pi pi-copy'"
            :severity="copied ? 'success' : 'secondary'"
            @click="copyLink"
          />
        </div>
        <div class="flex gap-2 mt-3">
          <a
            :href="whatsappShareUrl"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-2 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 hover:bg-green-100 transition-colors"
          >
            <i class="pi pi-whatsapp"></i>
            {{ t("referrals.share_whatsapp") }}
          </a>
        </div>
      </div>

      <!-- Statistiques -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">
            {{ t("referrals.referred_count") }}
          </p>
          <p class="text-2xl font-bold text-gray-900">
            {{ store.referredCount }}
          </p>
        </div>
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <p class="text-xs text-gray-500 mb-1">
            {{ t("referrals.total_earnings") }}
          </p>
          <p class="text-2xl font-bold text-teal-700">
            {{ store.totalEarnings }} FCFA
          </p>
        </div>
      </div>

      <!-- Liste des filleuls -->
      <div
        class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <div class="px-5 py-4 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800 text-sm">
            {{ t("referrals.your_referrals") }}
          </h2>
        </div>

        <div v-if="!store.referredUsers.length" class="text-center py-12 px-4">
          <i class="pi pi-users text-4xl text-gray-200 mb-3 block"></i>
          <p class="text-sm text-gray-500">
            {{ t("referrals.no_referrals_yet") }}
          </p>
        </div>

        <div v-else class="divide-y divide-gray-50">
          <div
            v-for="ru in store.referredUsers"
            :key="ru.user_id"
            class="flex items-center gap-3 px-5 py-4"
          >
            <div
              :class="[
                'w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold shrink-0',
                ru.has_paid
                  ? 'bg-teal-100 text-teal-700'
                  : 'bg-gray-100 text-gray-400',
              ]"
            >
              {{ ru.name.charAt(0).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ ru.name }}
              </p>
              <p class="text-xs text-gray-400">
                {{ formatDate(ru.joined_at) }}
              </p>
            </div>
            <div class="text-right shrink-0 flex items-center gap-2">
              <div>
                <Tag
                  :value="
                    ru.has_paid
                      ? t('referrals.paid')
                      : t('referrals.not_paid_yet')
                  "
                  :severity="ru.has_paid ? 'success' : 'warning'"
                />
                <p
                  v-if="ru.has_paid"
                  class="text-xs font-semibold text-teal-700 mt-1"
                >
                  +{{ ru.total_earned_from_this_user }} FCFA
                </p>
              </div>
              <Button
                v-if="!ru.has_paid"
                :label="t('referrals.validate_payment')"
                icon="pi pi-check-circle"
                size="small"
                severity="secondary"
                @click="openValidateDialog(ru)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Dialog validation manuelle de paiement ── -->
    <Dialog
      v-model:visible="validateDialog"
      :header="
        t('referrals.validate_payment_for', { name: selectedReferral?.name })
      "
      :modal="true"
      :style="{ width: '90vw', maxWidth: '480px' }"
    >
      <div class="space-y-4 mt-2">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t("referrals.level") }}
          </label>
          <Select
            v-model="selectedLevelId"
            :options="allLevels"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('referrals.select_level')"
            class="w-full"
            filter
          />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t("referrals.plan") }}
          </label>
          <Select
            v-model="selectedPlanId"
            :options="allPlans"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('referrals.select_plan')"
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t("referrals.note_optional") }}
          </label>
          <Textarea
            v-model="paymentNote"
            rows="2"
            class="w-full"
            :placeholder="t('referrals.note_placeholder')"
          />
        </div>
        <Message
          v-if="store.ambassadorError"
          severity="error"
          :closable="false"
        >
          {{ store.ambassadorError }}
        </Message>
      </div>
      <template #footer>
        <Button
          :label="t('referrals.cancel')"
          text
          @click="validateDialog = false"
        />
        <Button
          :label="t('referrals.confirm_validation')"
          icon="pi pi-check"
          :loading="store.settingAmbassador"
          :disabled="!selectedLevelId || !selectedPlanId"
          @click="handleValidatePayment"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useReferralsStore } from "~/stores/referrals";

definePageMeta({ layout: "ambassador", middleware: "ambassador" });

const { t } = useI18n();
useHead({ title: t("referrals.page_title") });

const store = useReferralsStore();
const examsStore = useExamsStore();
// ADJUST: nom réel du store des plans si différent — en attente de
// confirmation, voir plans.value ci-dessous.
const plansStore = usePlansStore();

const copied = ref(false);

const whatsappShareUrl = computed(() => {
  const text = t("referrals.whatsapp_message", { link: store.referralLink });
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
});

const copyLink = async () => {
  await navigator.clipboard.writeText(store.referralLink);
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
};

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

// ── Validation manuelle de paiement ─────────────────────────────

const validateDialog = ref(false);
const selectedReferral = ref<{ user_id: string; name: string } | null>(null);
const selectedLevelId = ref("");
const selectedPlanId = ref("");
const paymentNote = ref("");

const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} — ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

const allPlans = computed(() =>
  plansStore.sortedPlans.map((plan) => ({
    label: plan.name,
    value: plan.id,
  })),
);;

const openValidateDialog = (ru: { user_id: string; name: string }) => {
  selectedReferral.value = { user_id: ru.user_id, name: ru.name };
  selectedLevelId.value = "";
  selectedPlanId.value = "";
  paymentNote.value = "";
  store.ambassadorError = null;
  validateDialog.value = true;
};

const handleValidatePayment = async () => {
  if (!selectedReferral.value) return;
  const res = await store.validateManualPayment(
    selectedReferral.value.user_id,
    selectedLevelId.value,
    selectedPlanId.value,
    paymentNote.value,
  );
  if (res.success) {
    validateDialog.value = false;
  }
};

onMounted(async () => {
  await store.fetchDashboard();
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
  if (plansStore.plans.length === 0) await plansStore.fetchPlans();
});
</script>
