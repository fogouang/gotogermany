<script setup lang="ts">
import { SITE } from "~/config/site";
import type { NavRole } from "~/types/navigation";

const props = defineProps<{
  /** Rôle imposé par le layout ; absent = déduit du store (espace Centre) */
  role?: NavRole;
}>();

const { t } = useI18n();
const route = useRoute();
const authStore = useAuthStore();
const { openMobile } = useSidebar();
const { espace, sections, pageMeta, initiale, seDeconnecter } = useNavigation(
  props.role,
);

// Seule la zone de contenu défile : on la remet en haut à chaque changement de page
const zoneContenu = ref<HTMLElement | null>(null);
watch(
  () => route.path,
  () => zoneContenu.value?.scrollTo({ top: 0 }),
);

const deconnexionEnCours = ref(false);
async function deconnecter() {
  deconnexionEnCours.value = true;
  try {
    await seDeconnecter();
  } finally {
    deconnexionEnCours.value = false;
  }
}
</script>

<template>
  <div class="flex h-dvh overflow-hidden bg-canvas text-ink">
    <AppSidebar
      :sections="sections"
      :app-name="SITE.name"
      :subtitle="espace.label"
      :collapse-label="t('sidebar.collapse', 'Réduire')"
    >
      <template #footer="{ collapsed }">
        <!-- Utilisateur -->
        <div
          class="flex items-center gap-3 rounded-leaf bg-card-2 p-2"
          :class="{ 'justify-center': collapsed }"
        >
          <span
            class="brand-gradient flex size-9 shrink-0 items-center justify-center rounded-full font-heading text-sm font-bold"
          >
            {{ initiale }}
          </span>
          <div v-if="!collapsed" class="min-w-0 flex-1">
            <p class="truncate text-sm font-semibold text-ink">
              {{ authStore.userName || espace.roleLabel }}
            </p>
            <p class="truncate text-xs text-faint">
              {{ authStore.userEmail || espace.roleLabel }}
            </p>
          </div>
        </div>

        <!-- Déconnexion -->
        <button
          type="button"
          v-tooltip.right="{ value: t('sidebar.logout'), disabled: !collapsed }"
          class="flex h-9 w-full items-center gap-2 rounded-leaf text-sm font-medium text-red-600 transition-colors hover:bg-red-500/10 disabled:opacity-60 dark:text-red-400"
          :class="collapsed ? 'justify-center' : 'px-3'"
          :disabled="deconnexionEnCours"
          @click="deconnecter"
        >
          <i
            :class="
              deconnexionEnCours ? 'pi pi-spin pi-spinner' : 'pi pi-sign-out'
            "
            class="text-sm"
          />
          <span v-if="!collapsed">{{ t("sidebar.logout") }}</span>
        </button>
      </template>
    </AppSidebar>

    <div class="flex min-w-0 flex-1 flex-col">
      <!-- Header -->
      <header
        class="z-30 flex h-16 shrink-0 items-center gap-3 border-b border-line bg-card/85 px-4 backdrop-blur-md sm:px-6"
      >
        <button
          type="button"
          class="flex size-10 shrink-0 items-center justify-center rounded-leaf text-muted transition-colors hover:bg-card-2 hover:text-ink lg:hidden"
          aria-label="Menu"
          @click="openMobile"
        >
          <i class="pi pi-bars" />
        </button>

        <div class="min-w-0 flex-1">
          <p
            class="truncate font-heading text-base font-semibold text-ink sm:text-lg"
          >
            {{ pageMeta.title }}
          </p>
          <p
            v-if="pageMeta.subtitle"
            class="hidden truncate text-xs text-faint sm:block"
          >
            {{ pageMeta.subtitle }}
          </p>
        </div>

        <div class="flex shrink-0 items-center gap-2">
          <slot name="header-actions" />
          <AppLangSwitcher />
          <ThemeToggle />
          <span
            class="hidden items-center gap-1.5 rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700 sm:inline-flex"
          >
            <i :class="espace.icon" class="text-[11px]" />
            {{ espace.roleLabel }}
          </span>
        </div>
      </header>

      <!-- Contenu : seule zone qui défile -->
      <main
        ref="zoneContenu"
        class="isolate flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8"
      >
        <div class="mx-auto w-full max-w-400">
          <PageWatermark />
          <slot />
        </div>
      </main>
    </div>

    <ConfirmDialog />
  </div>
</template>
