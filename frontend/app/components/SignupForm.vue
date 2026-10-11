<!-- components/SignupForm.vue -->
<template>
  <form class="flex flex-col gap-4" @submit.prevent="handleSignup">
    <Message v-if="signupError" severity="error" :closable="false">
      {{ signupError }}
    </Message>

    <div
      v-if="referralCode"
      class="flex items-center gap-2.5 rounded-leaf border border-accent-500/30 bg-accent-500/10 px-3 py-2.5 text-sm font-medium text-accent-800 dark:text-accent-300"
    >
      <i class="pi pi-gift text-sm" />
      {{ t("auth.referred_by_message") }}
    </div>

    <div class="space-y-1.5">
      <label class="text-sm font-medium text-ink">{{ t("auth.full_name") }}</label>
      <InputText
        v-model="signupForm.fullName"
        autocomplete="name"
        placeholder="Jean Dupont"
        fluid
      />
    </div>

    <div class="space-y-1.5">
      <label class="text-sm font-medium text-ink">{{ t("auth.email") }}</label>
      <InputText
        v-model="signupForm.email"
        type="email"
        autocomplete="email"
        placeholder="jean@example.com"
        fluid
      />
    </div>

    <div class="space-y-1.5">
      <label class="text-sm font-medium text-ink">{{ t("auth.phone") }}</label>
      <InputText
        v-model="signupForm.phone"
        type="tel"
        autocomplete="tel"
        placeholder="+237 6XX XXX XXX"
        fluid
      />
    </div>

    <div class="space-y-1.5">
      <label class="text-sm font-medium text-ink">{{ t("auth.password") }}</label>
      <Password
        v-model="signupForm.password"
        toggle-mask
        autocomplete="new-password"
        fluid
      />
    </div>

    <AppButton
      type="submit"
      variant="gradient"
      block
      :label="t('auth.signup_btn')"
      :loading="authStore.loading"
      class="mt-1"
    />

    <slot name="footer" />
  </form>
</template>

<script setup lang="ts">
const props = defineProps<{
  referralCode?: string | null;
}>();

const emit = defineEmits<{
  success: [];
}>();

const { t, locale, setLocale } = useI18n();
const authStore = useAuthStore();

const signupError = ref("");
const signupForm = ref({ email: "", password: "", fullName: "", phone: "" });

const handleSignup = async () => {
  signupError.value = "";
  const savedLocale = locale.value;

  const result = await authStore.register(
    signupForm.value.email,
    signupForm.value.password,
    signupForm.value.fullName,
    signupForm.value.phone,
    props.referralCode ?? undefined,
  );

  if (result.success) {
    signupForm.value = { email: "", password: "", fullName: "", phone: "" };
    await setLocale(savedLocale);
    emit("success");
  } else {
    signupError.value = result.error || t("auth.signup_error");
  }
};
</script>