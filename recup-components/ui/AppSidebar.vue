<script setup lang="ts">
import type { NavSectionResolue } from "~/composables/useNavigation";

const props = withDefaults(
  defineProps<{
    /** Sections déjà traduites, fournies par useNavigation() */
    sections: NavSectionResolue[];
    appName?: string;
    /** Sous-titre sous le nom, ex. "Espace Centre" */
    subtitle?: string;
    /** Logo image (sinon : initiale sur pastille de marque) */
    logo?: string;
    collapsibleGroups?: boolean;
    collapseLabel?: string;
  }>(),
  {
    appName: "GoToGermany",
    collapsibleGroups: false,
    collapseLabel: "Réduire",
  },
);

const { collapsed, mobileOpen, toggleCollapsed } = useSidebar();
const route = useRoute();

const initial = computed(() => props.appName.charAt(0).toUpperCase());

// Sur mobile, on ferme le tiroir après avoir cliqué un lien
watch(
  () => route.path,
  () => {
    mobileOpen.value = false;
  },
);
</script>

<template>
  <!-- Desktop : prend toute la hauteur de l'AppShell (écran figé) -->
  <aside
    class="hidden h-full shrink-0 flex-col border-r border-line bg-card transition-[width] duration-300 ease-spring lg:flex"
    :class="collapsed ? 'w-20' : 'w-64'"
  >
    <div class="relative shrink-0">
      <div
        class="flex h-16 items-center gap-3 px-5"
        :class="{ 'justify-center px-0': collapsed }"
      >
        <span
          v-if="!logo || collapsed"
          class="brand-gradient flex size-10 shrink-0 items-center justify-center rounded-leaf font-heading font-bold shadow-brand"
        >
          {{ initial }}
        </span>
        <img
          v-else
          :src="logo"
          :alt="appName"
          class="h-8 w-auto shrink-0 object-contain"
        />
        <div v-if="!collapsed" class="min-w-0">
          <span
            v-if="!logo"
            class="block truncate font-heading text-lg font-semibold text-ink"
          >
            {{ appName }}
          </span>
          <span v-if="subtitle" class="block truncate text-xs text-faint">
            {{ subtitle }}
          </span>
        </div>
      </div>
      <!-- Liseré noir-rouge-or -->
      <div class="flag-stripe h-0.5 w-full opacity-80" />
    </div>

    <!-- Seul le menu défile s'il est trop long -->
    <div class="min-h-0 flex-1 overflow-y-auto px-3 py-4">
      <AppSidebarNav
        :sections="sections"
        :collapsed="collapsed"
        :collapsible="collapsibleGroups"
      />
    </div>

    <div class="flex shrink-0 flex-col gap-2 border-t border-line p-3">
      <slot name="footer" :collapsed="collapsed" />
      <AppButton
        variant="ghost"
        size="small"
        block
        :icon="
          collapsed ? 'pi pi-angle-double-right' : 'pi pi-angle-double-left'
        "
        :label="collapsed ? undefined : collapseLabel"
        @click="toggleCollapsed"
      />
    </div>
  </aside>

  <!-- Mobile -->
  <Drawer v-model:visible="mobileOpen" position="left" class="w-72">
    <template #header>
      <div class="flex items-center gap-3">
        <span
          v-if="!logo"
          class="brand-gradient flex size-10 items-center justify-center rounded-leaf font-heading font-bold shadow-brand"
        >
          {{ initial }}
        </span>
        <img
          v-else
          :src="logo"
          :alt="appName"
          class="h-8 w-auto object-contain"
        />
        <div class="min-w-0">
          <span
            v-if="!logo"
            class="block font-heading text-lg font-semibold text-ink"
          >
            {{ appName }}
          </span>
          <span v-if="subtitle" class="block text-xs text-faint">{{
            subtitle
          }}</span>
        </div>
      </div>
    </template>

    <AppSidebarNav :sections="sections" :collapsible="collapsibleGroups" />

    <template #footer>
      <slot name="footer" :collapsed="false" />
    </template>
  </Drawer>
</template>