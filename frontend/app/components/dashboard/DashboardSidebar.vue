<template>
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-50 bg-white border-r border-gray-100 lg:block transition-all duration-300',
      props.collapsed ? 'w-16' : 'w-64',
    ]"
  >
    <div class="flex flex-col h-full">
      <!-- Logo -->
      <div
        class="flex items-center px-4 py-5 border-b border-gray-100 overflow-hidden h-14"
      >
        <img
          v-if="!props.collapsed"
          src="/images/logo.png"
          alt="DeutschTest"
          class="h-7 object-contain"
        />
        <div
          v-else
          class="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center mx-auto"
        >
          <i class="pi pi-graduation-cap text-white text-sm"></i>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
        <template v-if="!props.collapsed">
          <p
            class="text-xs font-semibold text-gray-400 uppercase tracking-widest px-3 mb-2"
          >
            {{ t("sidebar.main") }}
          </p>
        </template>

        <NuxtLink
          v-for="item in mainItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'flex items-center rounded-lg text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors font-medium group',
            props.collapsed
              ? 'justify-center px-0 py-2.5 mx-1'
              : 'gap-3 px-3 py-2.5',
          ]"
          active-class="!bg-teal-50 !text-teal-700 font-semibold"
          v-tooltip.right="props.collapsed ? item.label : undefined"
          @click="$emit('navigate')"
        >
          <i :class="['pi text-base', item.icon]"></i>
          <span v-if="!props.collapsed">{{ item.label }}</span>
        </NuxtLink>

        <template v-if="!props.collapsed">
          <p
            class="text-xs font-semibold text-gray-400 uppercase tracking-widest px-3 mt-5 mb-2"
          >
            {{ t("sidebar.account") }}
          </p>
        </template>
        <div v-else class="my-3 mx-2 h-px bg-gray-100" />

        <NuxtLink
          v-for="item in accountItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'flex items-center rounded-lg text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors font-medium group',
            props.collapsed
              ? 'justify-center px-0 py-2.5 mx-1'
              : 'gap-3 px-3 py-2.5',
          ]"
          active-class="!bg-teal-50 !text-teal-700 font-semibold"
          v-tooltip.right="props.collapsed ? item.label : undefined"
          @click="$emit('navigate')"
        >
          <i :class="['pi text-base', item.icon]"></i>
          <span v-if="!props.collapsed">{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <!-- User -->
      <div class="border-t border-gray-100 p-2">
        <div
          v-if="!props.collapsed"
          class="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-50 mb-1"
        >
          <div
            class="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white text-sm font-bold shrink-0"
          >
            {{ authStore.userName?.[0]?.toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-gray-900 truncate">
              {{ authStore.userName }}
            </p>
            <p class="text-xs text-gray-400 truncate">
              {{ authStore.userEmail }}
            </p>
          </div>
        </div>

        <button
          :class="[
            'w-full flex items-center rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors font-medium',
            props.collapsed ? 'justify-center py-2.5' : 'gap-2 px-3 py-2',
          ]"
          v-tooltip.right="props.collapsed ? t('sidebar.logout') : undefined"
          @click="handleLogout"
        >
          <i class="pi pi-sign-out text-sm"></i>
          <span v-if="!props.collapsed">{{ t("sidebar.logout") }}</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
const props = defineProps<{ collapsed?: boolean }>();
const authStore = useAuthStore();
const { t } = useI18n();
defineEmits(["navigate"]);

const mainItems = computed(() => [
  {
    label: t("dashboard.pages.dashboard"),
    icon: "pi-th-large",
    to: "/dashboard",
  },
  {
    label: t("dashboard.pages.examens"),
    icon: "pi-book",
    to: "/dashboard/examens",
  },
  {
    label: t("dashboard.pages.simulateur"),
    icon: "pi-pen-to-square",
    to: "/dashboard/simulateur",
  },
  {
    label: t("dashboard.pages.methodologie"),
    icon: "pi-book",
    to: "/dashboard/methodologie",
  },
  {
    label: t("dashboard.quick_actions.results"),
    icon: "pi-chart-line",
    to: "/dashboard/resultats",
  },
]);

const accountItems = computed(() => [
  {
    label: t("dashboard.pages.profil"),
    icon: "pi-user",
    to: "/dashboard/profil",
  },
  {
    label: t("dashboard.pages.factures"),
    icon: "pi-receipt",
    to: "/dashboard/factures",
  },
  {
    label: t("dashboard.pages.credits"),
    icon: "pi-credit-card",
    to: "/dashboard/credits",
  },
]);

const handleLogout = async () => {
  authStore.logout();
  await navigateTo("/");
};
</script>
