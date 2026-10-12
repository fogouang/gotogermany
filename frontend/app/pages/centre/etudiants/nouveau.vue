<!-- pages/centre/etudiants/nouveau.vue -->
<template>
  <div class="mx-auto max-w-2xl space-y-5">
    <NuxtLink
      :to="localePath('/centre/etudiants')"
      class="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-ink"
    >
      <i class="pi pi-arrow-left text-xs" />
      {{ t("centre.student_new.back") }}
    </NuxtLink>

    <div class="rounded-card border border-line bg-card shadow-soft">
      <header class="flex items-center gap-3 border-b border-line px-6 py-4">
        <span
          class="flex size-10 items-center justify-center rounded-leaf bg-primary/10 text-primary"
        >
          <i class="pi pi-user-plus" />
        </span>
        <div>
          <h2 class="font-semibold text-ink">
            {{ t("centre.nav.new_student") }}
          </h2>
          <p class="text-xs text-muted">
            {{ t("centre.student_new.subtitle") }}
          </p>
        </div>
      </header>

      <form class="space-y-5 p-6" @submit.prevent="handleCreate(true)">
        <!-- Identité -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="sm:col-span-2">
            <label class="mb-1.5 block text-sm font-medium text-ink">
              {{ t("auth.full_name") }} <span class="text-red-600">*</span>
            </label>
            <InputText
              v-model="form.full_name"
              class="w-full"
              :placeholder="t('centre.form.name_placeholder')"
            />
          </div>
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

        <!-- Connexion -->
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
          <p class="mt-1 text-xs text-muted">
            {{ t("centre.student_new.password_hint") }}
          </p>
        </div>

        <!-- Examen -->
        <div>
          <label class="mb-1.5 block text-sm font-medium text-ink">
            {{ t("centre.students.col_target") }}
            <span class="text-red-600">*</span>
          </label>
          <Select
            v-model="form.target_level_id"
            :options="allLevels"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('centre.form.level_placeholder')"
            class="w-full"
            filter
          />
        </div>

        <Message v-if="createError" severity="error" :closable="false">{{
          createError
        }}</Message>

        <!-- Actions -->
        <div
          class="flex flex-col-reverse gap-2 border-t border-line pt-5 sm:flex-row sm:justify-end"
        >
          <Button
            type="button"
            :label="t('centre.student_new.create_only')"
            text
            :disabled="creating"
            @click="handleCreate(false)"
          />
          <Button
            type="submit"
            :label="t('centre.student_new.create_and_activate')"
            icon="pi pi-bolt"
            :loading="creating"
          />
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "centre", watermark: "Anmeldung" });

const { t } = useI18n();
const localePath = useLocalePath();
const centerStaffStore = useCenterStaffStore();
const examsStore = useExamsStore();
const toast = useToast();

const creating = ref(false);
const createError = ref<string | null>(null);

const form = ref({
  full_name: "",
  email: "",
  phone: "",
  password: "",
  target_level_id: "",
});

const allLevels = computed(() =>
  examsStore.catalog.flatMap((exam) =>
    (exam.levels ?? []).map((level) => ({
      label: `${exam.name} - ${level.cefr_code}`,
      value: level.id,
    })),
  ),
);

async function handleCreate(thenActivate: boolean) {
  const f = form.value;
  if (
    !f.full_name.trim() ||
    !f.email.trim() ||
    !f.password ||
    !f.target_level_id
  ) {
    createError.value = t("centre.form.required_fields");
    return;
  }
  if (f.password.length < 8) {
    createError.value = t("centre.form.password_min");
    return;
  }

  creating.value = true;
  createError.value = null;

  const result = await centerStaffStore.createStudent({
    email: f.email.trim(),
    password: f.password,
    full_name: f.full_name.trim(),
    phone: f.phone.trim() || null,
    target_level_id: f.target_level_id,
  });

  creating.value = false;

  if (result.success && result.student) {
    toast.add({
      severity: "success",
      summary: t("centre.form.account_created"),
      detail: t("centre.form.credentials", {
        email: f.email.trim(),
        password: f.password,
      }),
      life: 10000,
    });
    await navigateTo(
      thenActivate
        ? {
            path: localePath("/centre/etudiants"),
            query: { activer: result.student.id },
          }
        : localePath("/centre/etudiants"),
    );
  } else {
    createError.value = result.error || t("centre.form.create_error");
  }
}

onMounted(async () => {
  if (examsStore.catalog.length === 0) await examsStore.fetchCatalog();
});
</script>
