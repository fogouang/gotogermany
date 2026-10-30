<template>
  <div class="rounded-card border border-line bg-card shadow-soft">
    <div
      class="flex items-center justify-between gap-3 border-b border-line px-5 py-4"
    >
      <div class="flex items-center gap-2">
        <p class="font-semibold text-ink">
          {{ t("centre_join.requests_title") }}
        </p>
        <span
          v-if="requests.length"
          class="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-bold text-primary"
        >
          {{ requests.length }}
        </span>
      </div>
      <Button
        icon="pi pi-refresh"
        text
        rounded
        size="small"
        severity="secondary"
        :loading="loading"
        :aria-label="t('centre_join.refresh')"
        @click="load"
      />
    </div>

    <div v-if="loading && !requests.length" class="space-y-2 p-4">
      <div
        v-for="n in 2"
        :key="n"
        class="h-14 animate-pulse rounded-leaf bg-card-2"
      />
    </div>

    <p
      v-else-if="!requests.length"
      class="px-5 py-6 text-center text-sm text-muted"
    >
      {{ t("centre_join.requests_empty") }}
    </p>

    <ul v-else class="divide-y divide-line">
      <li
        v-for="req in requests"
        :key="req.id"
        class="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-3"
      >
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-ink">
            {{ req.full_name }}
          </p>
          <p class="mt-0.5 truncate text-xs text-muted">
            {{ req.phone
            }}<template v-if="req.email"> · {{ req.email }}</template>
          </p>
          <p class="mt-0.5 text-xs text-faint">
            {{ req.branch_name }}
            <template v-if="req.requested_at">
              ·
              {{
                t("centre_join.requested_on", {
                  date: formatDate(req.requested_at),
                })
              }}
            </template>
          </p>
        </div>
        <div class="flex gap-2">
          <Button
            :label="t('centre_join.reject')"
            severity="danger"
            text
            size="small"
            :loading="rejectingId === req.id"
            @click="reject(req)"
          />
          <Button
            :label="t('centre_join.approve')"
            icon="pi pi-check"
            size="small"
            @click="openApprove(req)"
          />
        </div>
      </li>
    </ul>

    <!-- Validation : choix du niveau -->
    <Dialog
      v-model:visible="approveVisible"
      :header="
        t('centre_join.approve_title', { name: selected?.full_name ?? '' })
      "
      modal
      :style="{ width: '95vw', maxWidth: '28rem' }"
    >
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-ink">{{
            t("centre_join.level_label")
          }}</label>
          <Select
            v-model="levelId"
            :options="levelOptions"
            option-label="label"
            option-value="value"
            :placeholder="t('centre_join.level_placeholder')"
            fluid
          />
        </div>
        <p class="text-xs text-muted">{{ t("centre_join.approve_hint") }}</p>
      </div>
      <template #footer>
        <Button
          :label="t('centre_join.cancel')"
          text
          @click="approveVisible = false"
        />
        <Button
          :label="t('centre_join.approve')"
          icon="pi pi-check"
          :disabled="!levelId"
          :loading="approving"
          @click="approve"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
interface JoinRequest {
  id: string;
  full_name: string;
  phone: string | null;
  email: string | null;
  branch_id: string;
  branch_name: string;
  requested_at: string | null;
}

const emit = defineEmits<{ approved: [] }>();

const { t, locale } = useI18n();
const toast = useToast();
const examsStore = useExamsStore();
const runtimeConfig = useRuntimeConfig();
const tokenCookie = useCookie("access_token");

const base = runtimeConfig.public.apiBaseUrl || "http://localhost:8001";
const headers = (): Record<string, string> => {
  const h: Record<string, string> = {};
  if (tokenCookie.value) h.Authorization = `Bearer ${tokenCookie.value}`;
  return h;
};

const requests = ref<JoinRequest[]>([]);
const loading = ref(false);

const apiError = (e: any) =>
  typeof e?.data?.detail === "string"
    ? e.data.detail
    : t("centre_join.error_generic");

async function load() {
  loading.value = true;
  try {
    requests.value = await $fetch<JoinRequest[]>(
      `${base}/api/v1/users/join-requests`,
      {
        headers: headers(),
      },
    );
  } catch (e) {
    toast.add({ severity: "error", summary: apiError(e), life: 4000 });
  } finally {
    loading.value = false;
  }
}

// Niveaux du catalogue (le niveau préparé par l'élève), plus Start Deutsch A1/A2
const levelOptions = computed(() => [
  ...examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} · ${level.cefr_code}`,
      value: level.id,
    })),
  ),
  { label: "Start Deutsch · A1", value: "sd:A1" },
  { label: "Start Deutsch · A2", value: "sd:A2" },
]);

// ── Validation ──
const approveVisible = ref(false);
const selected = ref<JoinRequest | null>(null);
const levelId = ref<string | null>(null);
const approving = ref(false);

function openApprove(req: JoinRequest) {
  selected.value = req;
  levelId.value = null;
  approveVisible.value = true;
}

async function approve() {
  if (!selected.value || !levelId.value) return;
  approving.value = true;
  try {
    await $fetch(
      `${base}/api/v1/users/join-requests/${selected.value.id}/approve`,
      {
        method: "POST",
        headers: headers(),
        body: levelId.value.startsWith("sd:")
          ? { target_sd_level: levelId.value.slice(3) }
          : { target_level_id: levelId.value },
      },
    );
    requests.value = requests.value.filter((r) => r.id !== selected.value?.id);
    approveVisible.value = false;
    toast.add({
      severity: "success",
      summary: t("centre_join.approved"),
      life: 3000,
    });
    emit("approved");
  } catch (e) {
    toast.add({ severity: "error", summary: apiError(e), life: 5000 });
  } finally {
    approving.value = false;
  }
}

// ── Refus ──
const rejectingId = ref<string | null>(null);

async function reject(req: JoinRequest) {
  if (!window.confirm(t("centre_join.reject_confirm", { name: req.full_name })))
    return;
  rejectingId.value = req.id;
  try {
    await $fetch(`${base}/api/v1/users/join-requests/${req.id}/reject`, {
      method: "POST",
      headers: headers(),
    });
    requests.value = requests.value.filter((r) => r.id !== req.id);
    toast.add({
      severity: "success",
      summary: t("centre_join.rejected"),
      life: 3000,
    });
  } catch (e) {
    toast.add({ severity: "error", summary: apiError(e), life: 4000 });
  } finally {
    rejectingId.value = null;
  }
}

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString(locale.value, {
    day: "2-digit",
    month: "short",
  });

onMounted(async () => {
  if (!examsStore.catalog.length) await examsStore.fetchCatalog();
  await load();
});
</script>
