<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <NuxtLink to="/">
          <img src="/images/logo.png" alt="DeutschTest" class="h-10 mx-auto mb-6" />
        </NuxtLink>
        <h1 class="text-2xl font-bold text-gray-900">{{ t("auth.signup_title") }}</h1>
        <p class="text-sm text-gray-500 mt-1">{{ t("auth.signup_subtitle") }}</p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
        <SignupForm :referral-code="referralCode" @success="onSuccess">
          <template #footer>
            <p class="text-xs text-gray-500 text-center mt-2">
              {{ t("auth.have_account") }}
              <NuxtLink to="/" class="text-[#076152] hover:underline font-medium">
                {{ t("auth.login_link") }}
              </NuxtLink>
            </p>
          </template>
        </SignupForm>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const { t } = useI18n();

const referralCookie = useCookie<string | null>("referral_code", {
  maxAge: 60 * 60 * 24 * 30,
});

const referralCode = computed(() => referralCookie.value);

onMounted(() => {
  const ref = route.query.ref as string | undefined;
  if (ref) referralCookie.value = ref;
});

const onSuccess = () => {
  referralCookie.value = null;
  navigateTo("/dashboard");
};
</script>