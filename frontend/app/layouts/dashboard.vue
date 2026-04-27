<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Desktop -->
    <DashboardSidebar class="hidden lg:block" />

    <!-- Main Content -->
    <div class="lg:pl-64">
      <!-- Top Header -->
      <header class="bg-white shadow-sm sticky top-0 z-40">
        <div class="flex items-center justify-between px-4 py-4">
          <Button
            icon="pi pi-bars"
            text
            rounded
            class="lg:hidden"
            @click="sidebarOpen = true"
          />

          <h2 class="text-lg font-semibold text-gray-900 lg:hidden">
            {{ pageTitle }}
          </h2>

          <div class="flex items-center gap-4 ml-auto">
            <span class="text-sm text-gray-600 hidden sm:inline">
              {{ authStore.userName }}
            </span>
            <Avatar
              :label="authStore.userName[0]?.toUpperCase()"
              shape="circle"
              class="bg-teal-600 text-white"
            />
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>

    <!-- Mobile Sidebar -->
    <Drawer v-model:visible="sidebarOpen" position="left" class="lg:hidden">
      <template #header>
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 bg-linear-to-br from-yellow-400 to-orange-400 rounded-xl flex items-center justify-center"
          >
            <i class="pi pi-graduation-cap text-xl text-gray-900"></i>
          </div>
          <span class="text-xl font-bold">DeutschTest</span>
        </div>
      </template>

      <DashboardSidebar @navigate="sidebarOpen = false" />
    </Drawer>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore();
const sidebarOpen = ref(false);
const route = useRoute();

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    "/dashboard": "Tableau de bord",
    "/dashboard/examens": "Examens",
    "/dashboard/resultats": "Résultats",
    "/dashboard/profil": "Profil",
    "/dashboard/settings": "Paramètres",
    "/dashboard/factures": "Factures",
  };
  return titles[route.path] || "Dashboard";
});
</script>
