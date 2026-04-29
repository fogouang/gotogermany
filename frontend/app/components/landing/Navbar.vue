<template>
  <div class="fixed top-0 left-0 right-0 z-50 bg-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <NuxtLink
          to="/"
          class="flex items-center gap-3 hover:opacity-80 transition-opacity"
        >
          <img
            src="/images/logo.png"
            alt="GoToGermany"
            class="h-36 object-contain"
          />
        </NuxtLink>

        <!-- Desktop Menu -->
        <nav class="hidden md:flex items-center gap-1">
          <NuxtLink
            v-for="item in mainItems"
            :key="item.label"
            :to="item.to"
            class="px-4 py-2 rounded-lg text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-colors font-medium flex items-center gap-2"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>

        <!-- Authenticated -->
        <div
          v-if="authStore.isAuthenticated"
          class="hidden md:flex items-center gap-3"
        >
          <Button
            :label="authStore.userName"
            icon="pi pi-user"
            text
            severity="secondary"
            class="font-medium!"
          />
          <Button
            label="Dashboard"
            icon="pi pi-th-large"
            class="bg-linear-to-r! from-teal-600! to-teal-700! border-0! text-white! font-semibold!"
            @click="navigateTo('/dashboard')"
          />
          <Button
            icon="pi pi-sign-out"
            text
            severity="danger"
            rounded
            @click="handleLogout"
            v-tooltip.bottom="'Déconnexion'"
          />
        </div>

        <!-- Guest -->
        <div v-else class="hidden md:flex items-center gap-3">
          <Button
            label="Connexion"
            text
            class="font-semibold!"
            @click="openLogin"
          />
          <Button
            label="Commencer gratuitement"
            icon="pi pi-arrow-right"
            iconPos="right"
            class="bg-linear-to-r! from-teal-600! to-teal-700! border-0! text-white! font-semibold! hover:from-teal-700! hover:to-teal-800!"
            @click="openSignup"
          />
        </div>

        <!-- Mobile Menu Button -->
        <Button
          icon="pi pi-bars"
          text
          rounded
          class="md:hidden text-gray-700!"
          @click="toggleMobileMenu"
        />
      </div>
    </div>

    <!-- Mobile Menu -->
    <Transition name="slide-down">
      <div
        v-if="mobileMenuOpen"
        class="md:hidden bg-white border-t border-gray-200"
      >
        <nav class="px-4 py-4 space-y-1">
          <NuxtLink
            v-for="item in mainItems"
            :key="item.label"
            :to="item.to"
            class="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-colors font-medium"
            @click="closeMobileMenu"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </NuxtLink>

          <Divider v-if="authStore.isAuthenticated" />

          <div v-if="authStore.isAuthenticated" class="space-y-1">
            <div
              class="flex items-center gap-3 px-4 py-3 text-gray-900 font-semibold"
            >
              <i class="pi pi-user"></i>
              <span>{{ authStore.userName }}</span>
            </div>
            <NuxtLink
              to="/dashboard"
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-colors font-medium"
              @click="closeMobileMenu"
            >
              <i class="pi pi-th-large"></i><span>Dashboard</span>
            </NuxtLink>
            <button
              class="flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors font-medium w-full"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out"></i><span>Déconnexion</span>
            </button>
          </div>

          <div v-else class="space-y-2 pt-4">
            <Button
              label="Connexion"
              outlined
              class="w-full font-semibold!"
              @click="
                openLogin();
                closeMobileMenu();
              "
            />
            <Button
              label="Commencer gratuitement"
              icon="pi pi-arrow-right"
              iconPos="right"
              class="bg-linear-to-r! from-teal-600! to-teal-700! border-0! text-white! font-semibold! w-full"
              @click="
                openSignup();
                closeMobileMenu();
              "
            />
          </div>
        </nav>
      </div>
    </Transition>

    <!-- ─── Login Dialog ──────────────────────────────── -->
    <Dialog
      v-model:visible="loginVisible"
      header="Connexion"
      :style="{ width: '90vw', maxWidth: '450px' }"
      :modal="true"
    >
      <Message v-if="loginError" severity="error" :closable="false">{{
        loginError
      }}</Message>
      <div class="flex flex-col gap-4 mt-4">
        <div>
          <label class="block text-sm font-medium mb-2">Email</label>
          <InputText
            v-model="loginForm.email"
            type="email"
            class="w-full"
            placeholder="jean@example.com"
            @keyup.enter="handleLogin"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Mot de passe</label>
          <Password
            v-model="loginForm.password"
            class="w-full"
            :feedback="false"
            toggleMask
            @keyup.enter="handleLogin"
          />
        </div>
        <Button
          label="Se connecter"
          :loading="authStore.loading"
          class="w-full mt-2 bg-linear-to-r! from-teal-600! to-teal-700! border-0!"
          @click="handleLogin"
        />
        <p class="text-xs text-gray-500 text-center">
          Pas encore de compte ?
          <a
            href="#"
            class="text-teal-600 hover:underline font-medium"
            @click.prevent="openSignup"
            >S'inscrire</a
          >
        </p>
      </div>
    </Dialog>

    <!-- ─── Signup Dialog ─────────────────────────────── -->
    <Dialog
      v-model:visible="signupVisible"
      header="Inscription gratuite"
      :style="{ width: '90vw', maxWidth: '450px' }"
      :modal="true"
    >
      <Message v-if="signupError" severity="error" :closable="false">{{
        signupError
      }}</Message>
      <div class="flex flex-col gap-4 mt-4">
        <div>
          <label class="block text-sm font-medium mb-2">Nom complet</label>
          <InputText
            v-model="signupForm.fullName"
            class="w-full"
            placeholder="Jean Dupont"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Email</label>
          <InputText
            v-model="signupForm.email"
            type="email"
            class="w-full"
            placeholder="jean@example.com"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2"
            >Téléphone (optionnel)</label
          >
          <InputText
            v-model="signupForm.phone"
            class="w-full"
            placeholder="+237 6XX XXX XXX"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Mot de passe</label>
          <Password v-model="signupForm.password" class="w-full" toggleMask />
        </div>
        <Button
          label="S'inscrire"
          :loading="authStore.loading"
          class="w-full mt-2 bg-linear-to-r! from-teal-600! to-teal-700! border-0!"
          @click="handleSignup"
        />
        <p class="text-xs text-gray-500 text-center">
          Déjà un compte ?
          <a
            href="#"
            class="text-teal-600 hover:underline font-medium"
            @click.prevent="openLogin"
            >Se connecter</a
          >
        </p>
      </div>
    </Dialog>
  </div>

  <!-- Spacer -->
  <div class="h-16"></div>
</template>

<script setup lang="ts">
import { useAuthDialog } from "~/composables/useAuthDialog";

const authStore = useAuthStore();
const { loginVisible, signupVisible, openLogin, openSignup } = useAuthDialog();

const mobileMenuOpen = ref(false);
const loginError = ref("");
const signupError = ref("");

const loginForm = ref({ email: "", password: "" });
const signupForm = ref({ email: "", password: "", fullName: "", phone: "" });

const mainItems = ref([
  { label: "Accueil", icon: "pi pi-home", to: "/" },
  { label: "Tarifs", icon: "pi pi-tags", to: "/tarifs" },
  { label: "À propos", icon: "pi pi-info-circle", to: "/about" },
  { label: "Contact", icon: "pi pi-envelope", to: "/contact" },
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
    loginError.value = result.error || "Erreur de connexion";
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
    signupError.value = result.error || "Erreur lors de l'inscription";
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
  transition: all 0.3s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>
