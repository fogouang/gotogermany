<!-- app/error.vue : page d'erreur globale (404, 500...) -->
<template>
  <div
    class="relative flex min-h-screen items-center justify-center overflow-hidden bg-canvas px-4"
  >
    <!-- Filigrane -->
    <p
      class="pointer-events-none absolute select-none font-heading text-[40vw] font-extrabold leading-none text-ink/3 sm:text-[28vw]"
      aria-hidden="true"
    >
      {{ statusCode }}
    </p>

    <div
      class="relative w-full max-w-md rounded-card border border-line bg-card p-8 text-center shadow-soft"
    >
      <div
        class="flag-stripe absolute inset-x-0 top-0 h-1 rounded-t-card"
        aria-hidden="true"
      />

      <span
        class="mx-auto flex size-14 items-center justify-center rounded-full"
        :class="
          isNotFound
            ? 'bg-primary/10 text-primary'
            : 'bg-red-500/10 text-red-600'
        "
      >
        <i
          :class="isNotFound ? 'pi pi-compass' : 'pi pi-exclamation-triangle'"
          class="text-2xl"
        />
      </span>

      <p
        class="mt-5 font-heading text-5xl font-extrabold tracking-tight text-ink"
      >
        {{ statusCode }}
      </p>
      <h1 class="mt-2 text-xl font-bold text-ink">
        {{
          isNotFound
            ? t("error_page.not_found_title")
            : t("error_page.error_title")
        }}
      </h1>
      <p class="mt-2 text-sm text-muted">
        {{
          isNotFound
            ? t("error_page.not_found_text")
            : t("error_page.error_text")
        }}
      </p>

      <!-- Détail technique : en développement uniquement -->
      <p
        v-if="isDev && error?.message"
        class="mt-4 rounded-leaf bg-card-2 px-3 py-2 text-left font-mono text-xs text-muted"
      >
        {{ error.message }}
      </p>

      <div class="mt-7 flex flex-col gap-2 sm:flex-row sm:justify-center">
        <AppButton
          variant="accent"
          icon="pi pi-home"
          :label="
            authStore.isAuthenticated
              ? t('error_page.my_space')
              : t('error_page.home')
          "
          @click="goHome"
        />
        <AppButton
          variant="ghost"
          icon="pi pi-arrow-left"
          :label="t('error_page.back')"
          @click="goBack"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { NuxtError } from "#app";

const props = defineProps<{ error: NuxtError }>();

const { t } = useI18n();
const localePath = useLocalePath();
const authStore = useAuthStore();
const isDev = import.meta.dev;

const statusCode = computed(() => props.error?.statusCode ?? 500);
const isNotFound = computed(() => statusCode.value === 404);

useHead({
  title: computed(() =>
    isNotFound.value
      ? t("error_page.not_found_title")
      : t("error_page.error_title"),
  ),
});

function goHome() {
  const target = authStore.isAuthenticated ? espaceAccueil(authStore) : "/";
  clearError({ redirect: localePath(target) });
}

function goBack() {
  if (import.meta.client && window.history.length > 1) {
    clearError();
    window.history.back();
  } else {
    goHome();
  }
}
</script>
