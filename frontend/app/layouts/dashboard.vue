<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Desktop -->
    <DashboardSidebar :collapsed="sidebarCollapsed" class="hidden lg:block" />

    <!-- Main Content -->
    <div
      :class="[
        'transition-all duration-300',
        sidebarCollapsed ? 'lg:pl-16' : 'lg:pl-64',
      ]"
    >
      <!-- Top Header Desktop -->
      <header class="bg-white border-b border-gray-100 sticky top-0 z-40">
        <div class="flex items-center gap-3 px-4 h-14">
          <!-- Burger desktop → collapse sidebar -->
          <button
            class="hidden lg:flex w-8 h-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            @click="sidebarCollapsed = !sidebarCollapsed"
          >
            <i class="pi pi-bars text-sm"></i>
          </button>

          <!-- Burger mobile → ouvre drawer -->
          <button
            class="lg:hidden w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 transition-colors"
            @click="sidebarOpen = true"
          >
            <i class="pi pi-bars text-sm"></i>
          </button>

          <!-- Titre page mobile -->
          <span class="lg:hidden text-sm font-semibold text-gray-800">
            {{ pageTitle }}
          </span>

          <!-- Spacer -->
          <div class="flex-1" />

          <!-- User info desktop -->
          <div class="hidden lg:flex items-center gap-2">
            <span class="text-sm text-gray-500">{{ authStore.userName }}</span>
            <div
              class="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white text-xs font-bold"
            >
              {{ authStore.userName?.[0]?.toUpperCase() }}
            </div>
          </div>

          <!-- User avatar mobile -->
          <div
            class="lg:hidden w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white text-xs font-bold"
          >
            {{ authStore.userName?.[0]?.toUpperCase() }}
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>

    <!-- Mobile Drawer -->
    <Drawer
      v-model:visible="sidebarOpen"
      position="left"
      class="lg:hidden"
      style="width: 256px"
    >
      <template #header>
        <img
          src="/images/logo.png"
          alt="DeutschTest"
          class="h-7 object-contain"
        />
      </template>
      <DashboardSidebar @navigate="sidebarOpen = false" />
    </Drawer>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore();
const sidebarOpen = ref(false);
const sidebarCollapsed = ref(false);
const route = useRoute();

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    "/dashboard": "Tableau de bord",
    "/dashboard/examens": "Examens",
    "/dashboard/simulateur": "Simulateur",
    "/dashboard/methodologie": "Méthodologie",
    "/dashboard/resultats": "Résultats",
    "/dashboard/profil": "Profil",
    "/dashboard/factures": "Factures",
     "/dashboard/credits": "Crédits",
  };
  return titles[route.path] || "Dashboard";
});
</script>
