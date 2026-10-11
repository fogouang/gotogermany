<template>
  <div
    class="fixed inset-x-0 top-0 z-50 border-b transition-all duration-300"
    :class="
      scrolled || mobileMenuOpen
        ? 'border-line bg-card/85 shadow-soft backdrop-blur-md'
        : 'border-transparent bg-card/60 backdrop-blur-sm'
    "
  >
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between gap-4">
        <!-- Logo -->
        <NuxtLink
          :to="localePath('/')"
          class="group flex shrink-0 items-center gap-2.5"
          :aria-label="SITE.name"
        >
          <span class="flex flex-col leading-none">
            <span
              class="font-heading text-lg font-bold tracking-tight text-ink"
            >
              GoTo<span class="text-accent-500">Germany</span>
            </span>
            <span class="flag-stripe mt-1 h-0.5 w-full rounded-full" />
          </span>
        </NuxtLink>

        <!-- Desktop nav -->
        <nav class="hidden items-center gap-1 md:flex">
          <NuxtLink
            v-for="item in mainItems"
            :key="item.key"
            :to="localePath(item.to)"
            class="relative px-3.5 py-2 text-sm font-medium transition-colors"
            :class="
              isActive(item.to) ? 'text-ink' : 'text-muted hover:text-ink'
            "
          >
            {{ item.label }}
            <span
              class="absolute inset-x-3.5 -bottom-0.5 h-0.5 origin-left rounded-full bg-accent-500 transition-transform duration-300 ease-spring"
              :class="isActive(item.to) ? 'scale-x-100' : 'scale-x-0'"
            />
          </NuxtLink>
        </nav>

        <!-- Right side desktop -->
        <div class="hidden items-center gap-2 md:flex">
          <!-- Langues -->
          <div
            class="flex items-center rounded-leaf border border-line bg-card p-0.5"
          >
            <button
              v-for="loc in locales"
              :key="loc.code"
              type="button"
              class="rounded-lg px-2 py-1 text-[11px] font-bold uppercase transition-colors"
              :class="
                locale === loc.code
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-faint hover:text-ink'
              "
              @click="changeLocale(loc.code)"
            >
              {{ loc.code }}
            </button>
          </div>

          <ThemeToggle />

          <!-- Connecté -->
          <template v-if="authStore.isAuthenticated">
            <AppButton
              variant="gradient"
              size="small"
              icon="pi pi-th-large"
              :label="t('nav.dashboard')"
              @click="navigateTo(dashboardPath)"
            />
            <button
              v-tooltip.bottom="t('nav.logout')"
              type="button"
              class="flex size-10 items-center justify-center rounded-leaf text-red-600 transition-colors hover:bg-red-500/10 dark:text-red-400"
              :aria-label="t('nav.logout')"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out text-sm" />
            </button>
          </template>

          <!-- Invité -->
          <template v-else>
            <AppButton
              variant="ghost"
              size="small"
              :label="t('nav.login')"
              @click="openLogin"
            />
            <AppButton
              variant="gradient"
              size="small"
              icon="pi pi-arrow-right"
              icon-pos="right"
              :label="t('nav.signup')"
              @click="openSignup"
            />
          </template>
        </div>

        <!-- Mobile : thème + menu -->
        <div class="flex items-center gap-2 md:hidden">
          <ThemeToggle />
          <button
            type="button"
            class="flex size-10 items-center justify-center rounded-leaf border border-line bg-card text-ink"
            :aria-label="mobileMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'"
            :aria-expanded="mobileMenuOpen"
            @click="toggleMobileMenu"
          >
            <i :class="mobileMenuOpen ? 'pi pi-times' : 'pi pi-bars'" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition name="slide-down">
      <div v-if="mobileMenuOpen" class="border-t border-line bg-card md:hidden">
        <nav class="space-y-1 px-4 py-4">
          <NuxtLink
            v-for="item in mainItems"
            :key="item.key"
            :to="localePath(item.to)"
            class="flex items-center gap-3 rounded-leaf px-4 py-3 text-sm font-medium transition-colors"
            :class="
              isActive(item.to)
                ? 'bg-primary-50 text-primary-700'
                : 'text-muted hover:bg-card-2 hover:text-ink'
            "
          >
            <i :class="[item.icon, 'text-sm']" />
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>

        <div class="space-y-4 border-t border-line px-4 pt-4 pb-5">
          <!-- Langues -->
          <div class="flex gap-2">
            <button
              v-for="loc in locales"
              :key="loc.code"
              type="button"
              class="flex-1 rounded-leaf border px-3 py-2 text-xs font-bold uppercase transition-colors"
              :class="
                locale === loc.code
                  ? 'border-primary/30 bg-primary-50 text-primary-700'
                  : 'border-line text-faint hover:text-ink'
              "
              @click="changeLocale(loc.code)"
            >
              {{ loc.code }}
            </button>
          </div>

          <!-- Connecté -->
          <div v-if="authStore.isAuthenticated" class="space-y-2">
            <div class="flex items-center gap-3 rounded-leaf bg-card-2 p-3">
              <span
                class="brand-gradient flex size-9 items-center justify-center rounded-full font-heading text-sm font-bold"
              >
                {{ authStore.userName?.[0]?.toUpperCase() }}
              </span>
              <span class="truncate text-sm font-semibold text-ink">
                {{ authStore.userName }}
              </span>
            </div>
            <AppButton
              variant="gradient"
              block
              icon="pi pi-th-large"
              :label="t('nav.dashboard')"
              @click="navigateTo(dashboardPath)"
            />
            <button
              type="button"
              class="flex h-11 w-full items-center justify-center gap-2 rounded-leaf text-sm font-medium text-red-600 transition-colors hover:bg-red-500/10 dark:text-red-400"
              @click="handleLogout"
            >
              <i class="pi pi-sign-out text-sm" />
              {{ t("nav.logout") }}
            </button>
          </div>

          <!-- Invité -->
          <div v-else class="space-y-2">
            <AppButton
              variant="secondary"
              block
              :label="t('nav.login')"
              @click="
                openLogin();
                closeMobileMenu();
              "
            />
            <AppButton
              variant="gradient"
              block
              icon="pi pi-arrow-right"
              icon-pos="right"
              :label="t('nav.signup')"
              @click="
                openSignup();
                closeMobileMenu();
              "
            />
          </div>
        </div>
      </div>
    </Transition>

    <!-- Connexion -->
    <AppDialog
      v-model:visible="loginVisible"
      :title="t('auth.login_title')"
      icon="pi pi-sign-in"
      width="26rem"
      hide-footer
    >
      <form class="flex flex-col gap-4" @submit.prevent="handleLogin">
        <Message v-if="loginError" severity="error" :closable="false">
          {{ loginError }}
        </Message>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-ink">{{
            t("auth.email")
          }}</label>
          <InputText
            v-model="loginForm.email"
            type="email"
            autocomplete="email"
            placeholder="jean@example.com"
            fluid
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-ink">{{
            t("auth.password")
          }}</label>
          <Password
            v-model="loginForm.password"
            :feedback="false"
            toggle-mask
            autocomplete="current-password"
            fluid
          />
        </div>

        <AppButton
          type="submit"
          variant="gradient"
          block
          :label="t('auth.login_btn')"
          :loading="authStore.loading"
        />

        <p class="text-center text-xs text-muted">
          {{ t("auth.no_account") }}
          <a
            href="#"
            class="font-semibold text-primary hover:underline"
            @click.prevent="openSignup"
          >
            {{ t("auth.register_link") }}
          </a>
        </p>
      </form>
    </AppDialog>

    <!-- Inscription -->
    <AppDialog
      v-model:visible="signupVisible"
      :title="t('auth.signup_title')"
      icon="pi pi-user-plus"
      width="26rem"
      hide-footer
    >
      <SignupForm
        @success="
          () => {
            signupVisible = false;
            navigateTo(cheminApresConnexion());
          }
        "
      >
        <template #footer>
          <p class="text-center text-xs text-muted">
            {{ t("auth.have_account") }}
            <a
              href="#"
              class="font-semibold text-primary hover:underline"
              @click.prevent="openLogin"
            >
              {{ t("auth.login_link") }}
            </a>
          </p>
        </template>
      </SignupForm>
    </AppDialog>
  </div>

  <!-- Spacer -->
  <div class="h-16" />
</template>

<script setup lang="ts">
import { useAuthDialog } from "~/composables/useAuthDialog";
import { SITE } from "~/config/site";

const { t, locale, locales, setLocale } = useI18n();
const localePath = useLocalePath();
const route = useRoute();
const authStore = useAuthStore();
const { loginVisible, signupVisible, openLogin, openSignup } = useAuthDialog();
const { cheminApresConnexion } = useChoixExamen();

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

// Chemin sans préfixe de langue (/fr/tarifs -> /tarifs) pour l'état actif
const cheminSansLangue = computed(
  () => route.path.replace(/^\/(fr|de)(?=\/|$)/, "").replace(/\/$/, "") || "/",
);

function isActive(to: string) {
  if (to === "/") return cheminSansLangue.value === "/";
  return (
    cheminSansLangue.value === to || cheminSansLangue.value.startsWith(`${to}/`)
  );
}

// Espace de l'utilisateur connecté (même logique que la redirection après connexion)
const dashboardPath = computed(() => espaceAccueil(authStore));

// Ombre de la barre uniquement après défilement
const scrolled = ref(false);
function surScroll() {
  scrolled.value = window.scrollY > 8;
}
onMounted(() => {
  surScroll();
  window.addEventListener("scroll", surScroll, { passive: true });
});
onBeforeUnmount(() => window.removeEventListener("scroll", surScroll));

// Fermer le menu mobile au changement de page
watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false;
  },
);

const localeCookie = useCookie("app_locale", { maxAge: 60 * 60 * 24 * 365 });

type AppLocale = "en" | "fr" | "de";

const changeLocale = async (code: string) => {
  localeCookie.value = code;
  await setLocale(code as AppLocale);
};

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};
const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

const handleLogin = async () => {
  loginError.value = "";
  const savedLocale = locale.value;
  const result = await authStore.login(
    loginForm.value.email,
    loginForm.value.password,
  );
  if (result.success) {
    loginVisible.value = false;
    loginForm.value = { email: "", password: "" };
    await setLocale(savedLocale);

    if (authStore.isAdmin) {
      navigateTo("/admin");
    } else if (authStore.isDirector) {
      navigateTo("/centre/dashboard");
    } else if (authStore.isSecretary) {
      navigateTo("/centre/etudiants");
    } else if (authStore.isAmbassador) {
      navigateTo("/referrals");
    } else if (authStore.isTeacher) {
      navigateTo("/enseignant/sessions");
    } else {
      navigateTo(cheminApresConnexion());
    }
  } else {
    loginError.value = result.error || t("auth.login_error");
  }
};

const handleSignup = async () => {
  signupError.value = "";
  const savedLocale = locale.value; // ← sauvegarder avant navigation
  const result = await authStore.register(
    signupForm.value.email,
    signupForm.value.password,
    signupForm.value.fullName,
    signupForm.value.phone,
  );
  if (result.success) {
    signupVisible.value = false;
    signupForm.value = { email: "", password: "", fullName: "", phone: "" };
    await setLocale(savedLocale); // ← restaurer après signup
    navigateTo("/dashboard");
  } else {
    signupError.value = result.error || t("auth.signup_error");
  }
};

const handleLogout = async () => {
  await authStore.logout();
  closeMobileMenu();
  await navigateTo("/");
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
