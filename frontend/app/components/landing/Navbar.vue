<template>
  <div
    class="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-100"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <NuxtLink
          to="/"
          class="flex items-center hover:opacity-80 transition-opacity shrink-0"
        >
          <img
            src="/images/logo.png"
            alt="DeutschTest"
            class="h-10 object-contain"
          />
        </NuxtLink>

        <!-- Desktop Nav -->
        <nav class="hidden md:flex items-center gap-1">
          <NuxtLink
            v-for="item in mainItems"
            :key="item.key"
            :to="item.to"
            class="px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors font-medium flex items-center gap-2"
            active-class="text-white bg-[#076152]"
          >
            <i :class="[item.icon, 'text-xs']"></i>
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>

        <!-- Right side -->
        <div class="hidden md:flex items-center gap-2">
          <!-- Lang switcher -->
          <div
            class="flex items-center gap-0.5 border border-gray-200 rounded-lg p-0.5"
          >
            <button
              v-for="loc in locales"
              :key="loc.code"
              :class="[
                'text-xs font-bold px-2 py-1 rounded-md transition-colors uppercase',
                locale === loc.code
                  ? 'bg-[#076152] text-white'
                  : 'text-gray-400 hover:text-gray-600',
              ]"
              @click="setLocale(loc.code)"
            >
              {{ loc.code }}
            </button>
          </div>

          <!-- Authenticated -->
          <template v-if="authStore.isAuthenticated">
            <span
              class="text-sm text-gray-600 font-medium flex items-center gap-1.5"
            >
              <i class="pi pi-user text-[#076152] text-xs"></i>
              {{ authStore.userName }}
            </span>
            <div class="w-px h-4 bg-gray-200 mx-1" />
            <Button
              :label="t('nav.dashboard')"
              icon="pi pi-th-large"
              size="small"
              class="bg-teal-600! hover:bg-teal-700! border-0! text-white! font-semibold!"
              @click="navigateTo('/dashboard')"
            />
            <Button
              icon="pi pi-sign-out"
              text
              rounded
              size="small"
              severity="danger"
              v-tooltip.bottom="t('nav.logout')"
              @click="handleLogout"
            />
          </template>

          <!-- Guest -->
          <template v-else>
            <button
              class="px-4 py-2 text-sm font-semibold text-[#076152] hover:bg-teal-50 rounded-lg transition-colors"
              @click="openLogin"
            >
              {{ t("nav.login") }}
            </button>
            <button
              class="flex items-center gap-2 px-5 py-2 rounded-lg text-sm font-semibold text-white transition-all hover:opacity-90"
              style="background-color: #076152"
              @click="openSignup"
            >
              {{ t("nav.signup") }}
              <i class="pi pi-arrow-right text-xs"></i>
            </button>
          </template>
        </div>

        <!-- Mobile toggle -->
        <button
          class="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
          @click="toggleMobileMenu"
        >
          <i :class="mobileMenuOpen ? 'pi pi-times' : 'pi pi-bars'"></i>
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <Transition name="slide-down">
      <div
        v-if="mobileMenuOpen"
        class="md:hidden bg-white border-t border-gray-100 shadow-lg"
      >
        <nav class="px-4 py-4 space-y-1">
          <NuxtLink
            v-for="item in mainItems"
            :key="item.key"
            :to="item.to"
            class="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium text-sm"
            @click="closeMobileMenu"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>

        <div class="px-4 pb-4 border-t border-gray-100 pt-3 space-y-3">
          <!-- Lang switcher mobile -->
          <div class="flex items-center gap-1 px-4">
            <button
              v-for="loc in locales"
              :key="loc.code"
              :class="[
                'text-xs font-bold px-3 py-1.5 rounded-lg border transition-colors uppercase',
                locale === loc.code
                  ? 'bg-[#076152] text-white border-[#076152]'
                  : 'text-gray-400 border-gray-200 hover:text-gray-600',
              ]"
              @click="setLocale(loc.code)"
            >
              {{ loc.code }}
            </button>
          </div>

          <!-- Authenticated mobile -->
          <div v-if="authStore.isAuthenticated" class="space-y-1">
            <div
              class="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-gray-700"
            >
              <i class="pi pi-user text-teal-600"></i>
              {{ authStore.userName }}
            </div>
            <NuxtLink
              to="/dashboard"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium text-sm"
              @click="closeMobileMenu"
            >
              <i class="pi pi-th-large"></i>
              <span>{{ t("nav.dashboard") }}</span>
            </NuxtLink>
            <button
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors font-medium text-sm w-full"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out"></i>
              <span>{{ t("nav.logout") }}</span>
            </button>
          </div>

          <!-- Guest mobile -->
          <div v-else class="space-y-2">
            <button
              class="w-full px-4 py-3 rounded-lg border border-gray-200 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              @click="
                openLogin();
                closeMobileMenu();
              "
            >
              {{ t("nav.login") }}
            </button>
            <button
              class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-semibold text-white transition-all hover:opacity-90"
              style="background-color: #1cb098"
              @click="
                openSignup();
                closeMobileMenu();
              "
            >
              {{ t("nav.signup") }}
              <i class="pi pi-arrow-right text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Login Dialog -->
    <Dialog
      v-model:visible="loginVisible"
      :header="t('auth.login_title')"
      :style="{ width: '90vw', maxWidth: '420px' }"
      :modal="true"
    >
      <Message v-if="loginError" severity="error" :closable="false">{{
        loginError
      }}</Message>
      <div class="flex flex-col gap-4 mt-4">
        <div>
          <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
            t("auth.email")
          }}</label>
          <InputText
            v-model="loginForm.email"
            type="email"
            class="w-full"
            placeholder="jean@example.com"
            @keyup.enter="handleLogin"
          />
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
            t("auth.password")
          }}</label>
          <Password
            v-model="loginForm.password"
            class="w-full"
            :feedback="false"
            toggleMask
            @keyup.enter="handleLogin"
          />
        </div>
        <Button
          :label="t('auth.login_btn')"
          :loading="authStore.loading"
          class="w-full mt-1"
          style="background-color: #076152; border: none"
          @click="handleLogin"
        />
        <p class="text-xs text-gray-500 text-center">
          {{ t("auth.no_account") }}
          <a
            href="#"
            class="text-teal-600 hover:underline font-medium"
            @click.prevent="openSignup"
          >
            {{ t("auth.register_link") }}
          </a>
        </p>
      </div>
    </Dialog>

    <!-- Signup Dialog -->
    <Dialog
      v-model:visible="signupVisible"
      :header="t('auth.signup_title')"
      :style="{ width: '90vw', maxWidth: '420px' }"
      :modal="true"
    >
      <Message v-if="signupError" severity="error" :closable="false">{{
        signupError
      }}</Message>
      <div class="flex flex-col gap-4 mt-4">
        <div>
          <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
            t("auth.full_name")
          }}</label>
          <InputText
            v-model="signupForm.fullName"
            class="w-full"
            placeholder="Jean Dupont"
          />
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
            t("auth.email")
          }}</label>
          <InputText
            v-model="signupForm.email"
            type="email"
            class="w-full"
            placeholder="jean@example.com"
          />
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1.5 text-gray-700">{{
            t("auth.phone")
          }}</label>
          <InputText
            v-model="signupForm.phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
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
        <p class="text-xs text-gray-500 text-center">
          {{ t("auth.have_account") }}
          <a
            href="#"
            class="text-[#076152] hover:underline font-medium"
            @click.prevent="openLogin"
          >
            {{ t("auth.login_link") }}
          </a>
        </p>
      </div>
    </Dialog>
  </div>

  <!-- Spacer -->
  <div class="h-16"></div>
</template>

<script setup lang="ts">
import { useAuthDialog } from "~/composables/useAuthDialog";

const { t, locale, locales, setLocale } = useI18n();
const authStore = useAuthStore();
const { loginVisible, signupVisible, openLogin, openSignup } = useAuthDialog();

const mobileMenuOpen = ref(false);
const loginError = ref("");
const signupError = ref("");
const loginForm = ref({ email: "", password: "" });
const signupForm = ref({ email: "", password: "", fullName: "", phone: "" });

const mainItems = computed(() => [
  { key: "home", label: t("nav.home"), icon: "pi pi-home", to: "/" },
  {
    key: "pricing",
    label: t("nav.pricing"),
    icon: "pi pi-tags",
    to: "/tarifs",
  },
  {
    key: "about",
    label: t("nav.about"),
    icon: "pi pi-info-circle",
    to: "/about",
  },
  {
    key: "contact",
    label: t("nav.contact"),
    icon: "pi pi-envelope",
    to: "/contact",
  },
]);

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};
const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

const handleLogin = async () => {
  loginError.value = "";
  const result = await authStore.login(
    loginForm.value.email,
    loginForm.value.password,
  );
  if (result.success) {
    loginVisible.value = false;
    loginForm.value = { email: "", password: "" };
    navigateTo(authStore.isAdmin ? "/admin" : "/dashboard");
  } else {
    loginError.value = result.error || t("auth.login_error");
  }
};

const handleSignup = async () => {
  signupError.value = "";
  const result = await authStore.register(
    signupForm.value.email,
    signupForm.value.password,
    signupForm.value.fullName,
    signupForm.value.phone,
  );
  if (result.success) {
    signupVisible.value = false;
    signupForm.value = { email: "", password: "", fullName: "", phone: "" };
    navigateTo("/dashboard");
  } else {
    signupError.value = result.error || t("auth.signup_error");
  }
};

const handleLogout = () => {
  authStore.logout();
  closeMobileMenu();
};
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
