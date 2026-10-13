<template>
  <div class="space-y-5 pb-10">
    <p class="text-sm text-muted">{{ t("profile.subtitle") }}</p>

    <div class="grid items-start gap-5 lg:grid-cols-3">
      <!-- ══════════ Carte identité ══════════ -->
      <aside class="relative isolate overflow-hidden rounded-card border border-line bg-card p-6 text-center shadow-soft lg:sticky lg:top-0">
        <span class="mx-auto mb-4 flex size-24 items-center justify-center rounded-full bg-primary/10 text-3xl font-bold text-primary">
          {{ initials }}
        </span>
        <h2 class="truncate text-lg font-bold text-ink">{{ authStore.userName }}</h2>
        <p class="truncate text-sm text-muted">{{ authStore.userEmail }}</p>

        <span
          class="mt-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
          :class="authStore.isVerified ? 'bg-emerald-500/10 text-emerald-600' : 'bg-amber-500/15 text-amber-600'"
        >
          <i class="pi text-[10px]" :class="authStore.isVerified ? 'pi-check-circle' : 'pi-exclamation-triangle'" />
          {{ authStore.isVerified ? t("profile.email_verified") : t("profile.email_not_verified") }}
        </span>

        <dl class="mt-5 space-y-3 border-t border-line pt-5 text-left text-sm">
          <div class="flex items-center gap-3">
            <span class="flex size-8 shrink-0 items-center justify-center rounded-leaf bg-card-2 text-muted">
              <i class="pi pi-calendar text-xs" />
            </span>
            <div>
              <dt class="text-xs text-muted">{{ t("profile.member_since") }}</dt>
              <dd class="font-medium text-ink">{{ formatDate(memberSince) }}</dd>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="flex size-8 shrink-0 items-center justify-center rounded-leaf bg-card-2 text-muted">
              <i class="pi pi-shield text-xs" />
            </span>
            <div>
              <dt class="text-xs text-muted">{{ t("profile.status") }}</dt>
              <dd class="font-medium text-ink">{{ authStore.isAdmin ? t("profile.admin") : t("profile.user") }}</dd>
            </div>
          </div>
        </dl>
      </aside>

      <!-- ══════════ Formulaires ══════════ -->
      <div class="space-y-5 lg:col-span-2">
        <!-- Infos personnelles -->
        <section class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
          <h2 class="mb-4 font-semibold text-ink">{{ t("profile.personal_info") }}</h2>

          <Message v-if="successMessage" severity="success" closable class="mb-4" @close="successMessage = ''">
            {{ successMessage }}
          </Message>
          <Message v-if="errorMessage" severity="error" closable class="mb-4" @close="errorMessage = ''">
            {{ errorMessage }}
          </Message>

          <form class="space-y-5" @submit.prevent="updateProfile">
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("profile.full_name") }}</label>
                <InputText v-model="profileForm.full_name" fluid autocomplete="name" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("profile.phone") }}</label>
                <InputText v-model="profileForm.phone" fluid inputmode="tel" autocomplete="tel" placeholder="+237 6XX XXX XXX" />
              </div>
              <div class="md:col-span-2">
                <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("profile.email") }}</label>
                <InputText :modelValue="authStore.userEmail" fluid disabled />
                <small class="mt-1 block text-xs text-faint">{{ t("profile.email_readonly") }}</small>
              </div>
            </div>

            <div class="flex flex-col-reverse gap-2 border-t border-line pt-4 sm:flex-row sm:justify-end">
              <Button :label="t('profile.cancel')" severity="secondary" outlined :disabled="!profileDirty" @click="resetForm" />
              <Button
                :label="t('profile.save')"
                icon="pi pi-save"
                type="submit"
                :loading="loading"
                :disabled="!profileDirty || !profileForm.full_name.trim()"
              />
            </div>
          </form>
        </section>

        <!-- Mot de passe -->
        <section class="rounded-card border border-line bg-card p-5 shadow-soft sm:p-6">
          <h2 class="mb-4 font-semibold text-ink">{{ t("profile.change_password") }}</h2>

          <Message v-if="passwordSuccess" severity="success" closable class="mb-4" @close="passwordSuccess = ''">
            {{ passwordSuccess }}
          </Message>
          <Message v-if="passwordError" severity="error" closable class="mb-4" @close="passwordError = ''">
            {{ passwordError }}
          </Message>

          <form class="space-y-5" @submit.prevent="changePassword">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("profile.current_password") }}</label>
              <Password
                v-model="passwordForm.current_password"
                fluid
                toggleMask
                :feedback="false"
                :inputProps="{ autocomplete: 'current-password' }"
              />
            </div>
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("profile.new_password") }}</label>
                <Password
                  v-model="passwordForm.new_password"
                  fluid
                  toggleMask
                  :feedback="false"
                  :invalid="newPasswordTooShort"
                  :inputProps="{ autocomplete: 'new-password' }"
                />
                <small class="mt-1 block text-xs" :class="newPasswordTooShort ? 'text-red-600' : 'text-faint'">
                  {{ t("profile.error_length") }}
                </small>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-ink">{{ t("profile.confirm_password") }}</label>
                <Password
                  v-model="passwordForm.confirm_password"
                  fluid
                  toggleMask
                  :feedback="false"
                  :invalid="passwordMismatch"
                  :inputProps="{ autocomplete: 'new-password' }"
                />
                <small v-if="passwordMismatch" class="mt-1 block text-xs text-red-600">{{ t("profile.error_match") }}</small>
              </div>
            </div>

            <div class="flex flex-col-reverse gap-2 border-t border-line pt-4 sm:flex-row sm:justify-end">
              <Button :label="t('profile.cancel')" severity="secondary" outlined @click="resetPasswordForm" />
              <Button
                :label="t('profile.change_password_btn')"
                icon="pi pi-lock"
                type="submit"
                :loading="passwordLoading"
                :disabled="!passwordReady"
              />
            </div>
          </form>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", watermark: "Profil" });

const { t, locale } = useI18n();
const authStore = useAuthStore();

const loading = ref(false);
const passwordLoading = ref(false);
const successMessage = ref("");
const errorMessage = ref("");
const passwordSuccess = ref("");
const passwordError = ref("");

const userDetails = computed(() => authStore.user as any);

// ── Identité ──
const initials = computed(() =>
  (authStore.userName || authStore.userEmail || "?")
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p: string) => p[0]!.toUpperCase())
    .join(""),
);

const memberSince = computed<string | undefined>(() => userDetails.value?.created_at);

const intlLocale = computed(() => ({ fr: "fr-FR", de: "de-DE" } as Record<string, string>)[locale.value] ?? "en-GB");
const formatDate = (dateString?: string) =>
  dateString
    ? new Date(dateString).toLocaleDateString(intlLocale.value, { year: "numeric", month: "long", day: "numeric" })
    : "-";

// ── Infos personnelles ──
const profileForm = ref({ full_name: "", phone: "" });

const initForm = () => {
  profileForm.value = {
    full_name: authStore.userName || "",
    phone: userDetails.value?.phone || "",
  };
};

const profileDirty = computed(
  () =>
    profileForm.value.full_name.trim() !== (authStore.userName || "") ||
    profileForm.value.phone.trim() !== (userDetails.value?.phone || ""),
);

const updateProfile = async () => {
  if (!profileDirty.value) return;
  loading.value = true;
  successMessage.value = "";
  errorMessage.value = "";
  const result = await authStore.updateProfile(profileForm.value.full_name.trim(), profileForm.value.phone.trim());
  if (result.success) {
    successMessage.value = t("profile.success_update");
    initForm();
  } else {
    errorMessage.value = result.error || t("profile.error_update");
  }
  loading.value = false;
};

const resetForm = () => {
  initForm();
  successMessage.value = "";
  errorMessage.value = "";
};

// ── Mot de passe ──
const passwordForm = ref({ current_password: "", new_password: "", confirm_password: "" });

const newPasswordTooShort = computed(
  () => passwordForm.value.new_password.length > 0 && passwordForm.value.new_password.length < 8,
);
const passwordMismatch = computed(
  () =>
    passwordForm.value.confirm_password.length > 0 &&
    passwordForm.value.new_password !== passwordForm.value.confirm_password,
);
const passwordReady = computed(
  () =>
    !!passwordForm.value.current_password &&
    passwordForm.value.new_password.length >= 8 &&
    passwordForm.value.new_password === passwordForm.value.confirm_password,
);

const changePassword = async () => {
  passwordSuccess.value = "";
  passwordError.value = "";
  if (!passwordForm.value.current_password || !passwordForm.value.new_password) {
    passwordError.value = t("profile.error_fields");
    return;
  }
  if (passwordMismatch.value) {
    passwordError.value = t("profile.error_match");
    return;
  }
  if (passwordForm.value.new_password.length < 8) {
    passwordError.value = t("profile.error_length");
    return;
  }
  passwordLoading.value = true;
  const result = await authStore.changePassword(passwordForm.value.current_password, passwordForm.value.new_password);
  if (result.success) {
    passwordForm.value = { current_password: "", new_password: "", confirm_password: "" };
    passwordSuccess.value = t("profile.success_password");
  } else {
    passwordError.value = result.error || t("profile.error_password");
  }
  passwordLoading.value = false;
};

const resetPasswordForm = () => {
  passwordForm.value = { current_password: "", new_password: "", confirm_password: "" };
  passwordSuccess.value = "";
  passwordError.value = "";
};

onMounted(initForm);
</script>