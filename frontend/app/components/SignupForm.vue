<!-- components/SignupForm.vue -->
<template>
  <form class="flex flex-col gap-4" novalidate @submit.prevent="handleSignup">
    <div
      v-if="referralCode"
      class="flex items-center gap-2.5 rounded-leaf border border-accent-500/30 bg-accent-500/10 px-3 py-2.5 text-sm font-medium text-accent-800 dark:text-accent-300"
    >
      <i class="pi pi-gift text-sm" />
      {{ t("auth.referred_by_message") }}
    </div>

    <!-- Nom -->
    <div class="space-y-1.5">
      <label for="signup-name" class="text-sm font-medium text-ink">{{
        t("auth.full_name")
      }}</label>
      <InputText
        id="signup-name"
        v-model="form.fullName"
        autocomplete="name"
        placeholder="Jean Dupont"
        fluid
        :invalid="!!errors.fullName"
        @blur="touched.fullName = true"
      />
      <small v-if="errors.fullName" class="block text-xs text-red-600">{{
        errors.fullName
      }}</small>
    </div>

    <!-- Téléphone : sert à se connecter -->
    <div class="space-y-1.5">
      <label for="signup-phone" class="text-sm font-medium text-ink">{{
        t("auth.phone")
      }}</label>
      <PhoneInput
        v-model="form.phone"
        input-id="signup-phone"
        :invalid="!!errors.phone"
        @blur="touched.phone = true"
      />
      <small v-if="errors.phone" class="block text-xs text-red-600">{{
        errors.phone
      }}</small>
    </div>

    <!-- Succursale : inscription via le lien d'un centre -->
    <div v-if="joinToken && branches?.length" class="space-y-1.5">
      <label for="signup-branch" class="text-sm font-medium text-ink">{{
        t("auth.branch")
      }}</label>
      <Select
        v-model="form.branchId"
        input-id="signup-branch"
        :options="branches"
        option-label="name"
        option-value="id"
        :placeholder="t('auth.branch_placeholder')"
        fluid
        :invalid="!!errors.branch"
        @blur="touched.branchId = true"
      />
      <small v-if="errors.branch" class="block text-xs text-red-600">{{
        errors.branch
      }}</small>
    </div>

    <!-- Mot de passe -->
    <div class="space-y-1.5">
      <label for="signup-password" class="text-sm font-medium text-ink">{{
        t("auth.password")
      }}</label>
      <Password
        v-model="form.password"
        input-id="signup-password"
        toggle-mask
        :feedback="false"
        autocomplete="new-password"
        fluid
        :invalid="!!errors.password"
        @blur="touched.password = true"
      />
      <p
        class="flex items-center gap-1.5 pt-0.5 text-xs transition-colors"
        :class="
          passwordValid
            ? 'text-emerald-600'
            : show('password')
              ? 'text-red-600'
              : 'text-faint'
        "
      >
        <i
          class="pi text-[10px]"
          :class="passwordValid ? 'pi-check-circle' : 'pi-circle'"
        />
        {{ passwordRule }}
      </p>
      <small v-if="serverErrors.password" class="block text-xs text-red-600">{{
        serverErrors.password
      }}</small>
    </div>

    <!-- Email : facultatif -->
    <div class="space-y-1.5">
      <label for="signup-email" class="text-sm font-medium text-ink">{{
        t("auth.email_optional")
      }}</label>
      <InputText
        id="signup-email"
        v-model="form.email"
        type="email"
        autocomplete="email"
        inputmode="email"
        placeholder="jean@example.com"
        fluid
        :invalid="!!errors.email"
        @blur="touched.email = true"
      />
      <small v-if="errors.email" class="block text-xs text-red-600">{{
        errors.email
      }}</small>
    </div>

    <!-- Communauté WhatsApp : accord libre, non coché par défaut -->
    <label
      for="signup-whatsapp"
      class="flex cursor-pointer items-start gap-3 rounded-leaf border p-3 transition-colors"
      :class="
        form.whatsappOptIn
          ? 'border-emerald-500/40 bg-emerald-500/10'
          : 'border-line bg-card-2/50 hover:border-emerald-500/30'
      "
    >
      <Checkbox
        v-model="form.whatsappOptIn"
        input-id="signup-whatsapp"
        binary
        class="mt-0.5"
      />
      <span class="min-w-0 text-sm">
        <span class="flex items-center gap-1.5 font-medium text-ink">
          <i class="pi pi-whatsapp text-emerald-600" />
          {{ t("auth.whatsapp_opt_in") }}
        </span>
        <span class="mt-0.5 block text-xs text-muted">{{
          t("auth.whatsapp_opt_in_hint")
        }}</span>
      </span>
    </label>
    <small
      v-if="errors.whatsappOptIn"
      class="-mt-2 block text-xs text-red-600"
      >{{ errors.whatsappOptIn }}</small
    >

    <AppButton
      type="submit"
      variant="gradient"
      block
      :label="t('auth.signup_btn')"
      :loading="submitting"
      class="mt-1"
    />

    <slot name="footer" />
  </form>
</template>

<script setup lang="ts">
const props = defineProps<{
  referralCode?: string | null;
  /** Inscription via le lien d'un centre */
  joinToken?: string | null;
  branches?: { id: string; name: string }[];
}>();

const emit = defineEmits<{
  success: [];
}>();

const { t, locale, setLocale } = useI18n();
const authStore = useAuthStore();
const notify = useNotify();
const { fieldErrors } = useApiError();

const PASSWORD_MIN = 6;

const emptyForm = () => ({
  fullName: "",
  phone: "",
  password: "",
  email: "",
  branchId: null as string | null,
  whatsappOptIn: false,
});

const form = ref(emptyForm());
const touched = ref({
  fullName: false,
  phone: false,
  password: false,
  email: false,
  branchId: false,
});
const submitted = ref(false);
const submitting = ref(false);

/** Erreurs renvoyées par le serveur, par champ (effacées dès que l'étudiant corrige) */
const serverErrors = ref<Record<string, string>>({});

// Une seule succursale : présélectionnée
watch(
  () => props.branches,
  (list) => {
    if (list?.length === 1 && !form.value.branchId)
      form.value.branchId = list[0]!.id;
  },
  { immediate: true },
);

// ── Règles locales ──
const nameValid = computed(() => form.value.fullName.trim().length >= 2);

/** PhoneInput renvoie "" ou un numéro international "+XXXXXXXX" : obligatoire */
const phoneValid = computed(() => {
  const digits = form.value.phone.replace(/\D/g, "");
  return digits.length >= 8 && digits.length <= 15;
});

/** Facultatif : vide accepté */
const emailValid = computed(() => {
  const email = form.value.email.trim();
  return !email || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
});

const passwordValid = computed(
  () => form.value.password.length >= PASSWORD_MIN,
);
const passwordRule = computed(() =>
  t("api_errors.rules.min_length", {
    field: t("api_errors.fields.password"),
    n: PASSWORD_MIN,
  }),
);

const branchValid = computed(() => !props.joinToken || !!form.value.branchId);

// Une erreur ne s'affiche qu'après avoir quitté le champ ou tenté l'envoi
const show = (field: keyof typeof touched.value) =>
  touched.value[field] || submitted.value;

const errors = computed(() => ({
  fullName:
    serverErrors.value.full_name ||
    (show("fullName") && !nameValid.value
      ? t("api_errors.rules.required", {
          field: t("api_errors.fields.full_name"),
        })
      : ""),
  phone:
    serverErrors.value.phone ||
    (show("phone") && !phoneValid.value
      ? form.value.phone
        ? t("auth.phone_invalid")
        : t("auth.phone_required")
      : ""),
  email:
    serverErrors.value.email ||
    (show("email") && !emailValid.value ? t("api_errors.rules.email") : ""),
  branch:
    serverErrors.value.branch_id ||
    (show("branchId") && !branchValid.value ? t("auth.branch_required") : ""),
  password: serverErrors.value.password || "",
  whatsappOptIn: serverErrors.value.whatsapp_opt_in || "",
}));

const formValid = computed(
  () =>
    nameValid.value &&
    phoneValid.value &&
    emailValid.value &&
    passwordValid.value &&
    branchValid.value,
);

// L'étudiant corrige un champ : on retire l'erreur serveur de ce champ
watch(
  () => form.value.fullName,
  () => delete serverErrors.value.full_name,
);
watch(
  () => form.value.email,
  () => delete serverErrors.value.email,
);
watch(
  () => form.value.phone,
  () => delete serverErrors.value.phone,
);
watch(
  () => form.value.password,
  () => delete serverErrors.value.password,
);
watch(
  () => form.value.branchId,
  () => delete serverErrors.value.branch_id,
);
watch(
  () => form.value.whatsappOptIn,
  () => delete serverErrors.value.whatsapp_opt_in,
);

// ── Envoi ──
const handleSignup = async () => {
  submitted.value = true;
  if (!formValid.value || submitting.value) return;

  submitting.value = true;
  serverErrors.value = {};
  const savedLocale = locale.value;

  const result = await authStore.register({
    fullName: form.value.fullName.trim(),
    phone: form.value.phone,
    password: form.value.password,
    email: form.value.email.trim() || null,
    referralCode: props.referralCode ?? null,
    whatsappOptIn: form.value.whatsappOptIn,
    centerJoinToken: props.joinToken ?? null,
    branchId: form.value.branchId,
  });

  submitting.value = false;

  if (result.success) {
    const firstName = form.value.fullName.trim().split(/\s+/)[0];
    form.value = emptyForm();
    touched.value = {
      fullName: false,
      phone: false,
      password: false,
      email: false,
      branchId: false,
    };
    submitted.value = false;
    await setLocale(savedLocale);
    notify.success(
      t("toast.welcome", { name: firstName }),
      t("toast.welcome_detail"),
    );
    emit("success");
    return;
  }

  // Erreur liée à un champ (422) : affichée sous le champ concerné
  serverErrors.value = fieldErrors((result as any).apiError);

  // Sinon (numéro déjà utilisé, réseau, serveur...) : toast explicite
  if (Object.keys(serverErrors.value).length === 0) {
    notify.apiError((result as any).apiError, "api_errors.register");
  }
};
</script>
