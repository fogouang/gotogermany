<!-- pages/centre/secretaires.vue -->
<template>
  <div class="space-y-5">
    <!-- ── En-tête ── -->
    <div
      v-if="authStore.isDirector"
      class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <p class="text-sm text-muted">
        {{ t("centre.secretaries.count", secretaries.length) }}
      </p>
      <Button
        :label="t('centre.secretaries.new')"
        icon="pi pi-user-plus"
        class="w-full sm:w-auto"
        @click="openCreateDialog"
      />
    </div>

    <!-- ── Chargement ── -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="n in 3"
        :key="n"
        class="h-16 animate-pulse rounded-card bg-card-2"
      />
    </div>

    <!-- ── Erreur ── -->
    <div
      v-else-if="errorMessage"
      class="rounded-card border border-red-500/30 bg-red-500/5 p-6 text-center text-sm text-red-600"
    >
      {{ errorMessage }}
    </div>

    <!-- ── Vide ── -->
    <div
      v-else-if="secretaries.length === 0"
      class="flex flex-col items-center gap-2 rounded-card border border-dashed border-line bg-card px-6 py-12 text-center"
    >
      <span
        class="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary"
      >
        <i class="pi pi-users" />
      </span>
      <p class="text-sm font-medium text-ink">
        {{ t("centre.secretaries.empty_title") }}
      </p>
      <p class="max-w-sm text-xs text-muted">
        {{ t("centre.secretaries.empty_text") }}
      </p>
    </div>

    <!-- ── Liste ── -->
    <ul
      v-else
      class="divide-y divide-line overflow-hidden rounded-card border border-line bg-card shadow-soft"
    >
      <li
        v-for="sec in secretaries"
        :key="sec.id"
        class="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-4"
        :class="{ 'opacity-60': !sec.is_active }"
      >
        <span
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
        >
          {{ initials(sec.full_name) }}
        </span>
        <div class="min-w-0 flex-1">
          <p class="truncate font-medium text-ink">{{ sec.full_name }}</p>
          <p class="truncate text-xs text-muted">{{ sec.email }}</p>
        </div>
        <span class="inline-flex items-center gap-1.5 text-xs text-muted">
          <i class="pi pi-map-marker text-[11px]" />
          {{ branchName(sec.branch_id) }}
        </span>
        <span
          class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
          :class="
            sec.is_active
              ? 'bg-emerald-500/10 text-emerald-600'
              : 'bg-red-500/10 text-red-600'
          "
        >
          {{
            sec.is_active
              ? t("centre.account.active")
              : t("centre.account.disabled")
          }}
        </span>
      </li>
    </ul>

    <!-- ── Création ── -->
    <Dialog
      v-model:visible="showCreateDialog"
      :header="t('centre.secretaries.new')"
      modal
      :style="{ width: '95vw', maxWidth: '30rem' }"
    >
      <form class="space-y-4" @submit.prevent="handleCreate">
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("auth.full_name") }} <span class="text-red-600">*</span>
          </label>
          <InputText
            v-model="form.full_name"
            class="w-full"
            :placeholder="t('centre.form.name_placeholder')"
          />
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("auth.email") }} <span class="text-red-600">*</span>
            </label>
            <InputText
              v-model="form.email"
              type="email"
              class="w-full"
              :placeholder="t('centre.form.email_placeholder')"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-ink">{{
              t("profile.phone")
            }}</label>
            <InputText
              v-model="form.phone"
              class="w-full"
              placeholder="+237 6XX XXX XXX"
            />
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.form.temp_password") }}
            <span class="text-red-600">*</span>
          </label>
          <div class="flex gap-2">
            <Password
              v-model="form.password"
              class="flex-1"
              inputClass="w-full"
              :feedback="false"
              toggleMask
              :placeholder="t('centre.form.password_placeholder')"
            />
            <Button
              type="button"
              icon="pi pi-refresh"
              outlined
              v-tooltip.top="t('centre.form.generate_password')"
              :aria-label="t('centre.form.generate_password')"
              @click="form.password = genererMotDePasse()"
            />
          </div>
        </div>
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.form.branch") }} <span class="text-red-600">*</span>
          </label>
          <Select
            v-model="form.branch_id"
            :options="branches"
            optionLabel="name"
            optionValue="id"
            :placeholder="t('centre.form.branch_placeholder')"
            class="w-full"
          />
        </div>
        <Message v-if="createError" severity="error" :closable="false">{{
          createError
        }}</Message>
      </form>
      <template #footer>
        <Button
          :label="t('common.cancel')"
          text
          @click="showCreateDialog = false"
        />
        <Button
          :label="t('common.create')"
          icon="pi pi-check"
          :loading="creating"
          @click="handleCreate"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import type { UserAdminResponse, BranchResponse } from "#shared/api";

definePageMeta({ layout: "centre", watermark: "Sekretariat" });

const { t } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const centerStaffStore = useCenterStaffStore();
const toast = useToast();

const loading = ref(true);
const secretaries = ref<UserAdminResponse[]>([]);
const branches = ref<BranchResponse[]>([]);
const errorMessage = ref<string | null>(null);

const showCreateDialog = ref(false);
const creating = ref(false);
const createError = ref<string | null>(null);
const formVide = () => ({
  full_name: "",
  email: "",
  phone: "",
  password: "",
  branch_id: "",
});
const form = ref(formVide());

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function branchName(branchId: string | null) {
  if (!branchId) return "-";
  return branches.value.find((b) => b.id === branchId)?.name ?? "-";
}

function openCreateDialog() {
  form.value = formVide();
  // Une seule succursale : on la présélectionne
  if (branches.value.length === 1) form.value.branch_id = branches.value[0]!.id;
  createError.value = null;
  showCreateDialog.value = true;
}

async function loadData() {
  loading.value = true;
  const [secResult, branchResult] = await Promise.all([
    centerStaffStore.fetchSecretaries(),
    centerStaffStore.fetchMyBranches(),
  ]);

  if (secResult.success) {
    secretaries.value = secResult.secretaries ?? [];
    errorMessage.value = null;
  } else {
    errorMessage.value = secResult.error || t("common.load_error");
  }

  if (branchResult.success) {
    branches.value = branchResult.branches ?? [];
  }

  loading.value = false;
}

async function handleCreate() {
  const f = form.value;
  if (!f.full_name.trim() || !f.email.trim() || !f.password || !f.branch_id) {
    createError.value = t("centre.form.required_fields");
    return;
  }
  if (f.password.length < 8) {
    createError.value = t("centre.form.password_min");
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await centerStaffStore.createSecretary({
    email: f.email.trim(),
    password: f.password,
    full_name: f.full_name.trim(),
    phone: f.phone.trim() || null,
    branch_id: f.branch_id,
  });

  creating.value = false;

  if (result.success) {
    showCreateDialog.value = false;
    toast.add({
      severity: "success",
      summary: t("centre.form.account_created"),
      detail: t("centre.form.credentials", {
        email: f.email.trim(),
        password: f.password,
      }),
      life: 10000,
    });
    await loadData();
  } else {
    createError.value = result.error || t("centre.form.create_error");
  }
}

onMounted(async () => {
  // Page reservee au directeur : la secretaire est renvoyee vers ses eleves
  if (!authStore.isDirector) {
    await navigateTo(localePath("/centre/etudiants"), { replace: true });
    return;
  }
  await loadData();
});
</script>
