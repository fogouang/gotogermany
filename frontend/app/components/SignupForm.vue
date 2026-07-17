<!-- components/SignupForm.vue -->
<template>
  <div class="flex flex-col gap-5">
    <Message v-if="signupError" severity="error" :closable="false">{{
      signupError
    }}</Message>

    <div v-if="referralCode" class="text-center text-sm text-teal-700 bg-teal-50 rounded-lg py-2 px-3">
      {{ t("auth.referred_by_message") }}
    </div>

    <div>
      <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
        t("auth.full_name")
      }}</label>
      <InputText v-model="signupForm.fullName" class="w-full" placeholder="Jean Dupont" />
    </div>
    <div>
      <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
        t("auth.email")
      }}</label>
      <InputText v-model="signupForm.email" type="email" class="w-full" placeholder="jean@example.com" />
    </div>
    <div>
      <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
        t("auth.phone")
      }}</label>
      <InputText v-model="signupForm.phone" class="w-full" placeholder="+237 6XX XXX XXX" />
    </div>
    <div>
      <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
        t("auth.password")
      }}</label>
      <Password v-model="signupForm.password" class="w-full" toggleMask />
    </div>
    <Button
      :label="t('auth.signup_btn')"
      :loading="authStore.loading"
      class="w-full mt-1"
      style="background-color: #076152; border: none"
      @click="handleSignup"
    />

    <slot name="footer" />
  </div>
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