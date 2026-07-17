<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 bg-black/40 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed top-0 left-0 z-50 w-64 h-screen bg-gray-900 text-white transition-transform duration-200',
        'lg:translate-x-0',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="h-full px-4 py-6 overflow-y-auto pb-32">
        <!-- Logo + close button mobile -->
        <div class="flex items-center justify-between gap-3 mb-8">
          <div>
            <span class="text-lg font-bold">GoToGermany</span>
            <p class="text-xs text-green-400 leading-none">Espace Ambassadeur</p>
          </div>
          <button
            class="lg:hidden p-2 text-gray-400 hover:text-white"
            @click="sidebarOpen = false"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="space-y-1">
          <NuxtLink
            v-for="item in nav"
            :key="item.name"
            :to="item.href"
            class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            active-class="!bg-amber-600 !text-white"
            @click="sidebarOpen = false"
          >
            <i :class="['pi text-sm', item.icon]"></i>
            <span class="text-sm font-medium">{{ item.name }}</span>
          </NuxtLink>

          <div class="h-px bg-gray-800 my-4" />

          <NuxtLink
            to="/dashboard"
            class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition-colors"
            @click="sidebarOpen = false"
          >
            <i class="pi pi-arrow-left text-sm"></i>
            <span class="text-sm font-medium">Espace étudiant</span>
          </NuxtLink>
        </nav>
      </div>

      <!-- User info -->
      <div
        class="absolute bottom-0 left-0 right-0 p-4 bg-gray-900 border-t border-gray-800"
      >
        <div class="p-3 bg-gray-800 rounded-lg">
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 bg-amber-600 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
            >
              {{ userInitial }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold truncate">
                {{ authStore.userName || "Ambassadeur" }}
              </p>
              <p class="text-xs text-gray-400 truncate">
                {{ authStore.userEmail }}
              </p>
            </div>
          </div>
          <Button
            label="Déconnexion"
            icon="pi pi-sign-out"
            text
            size="small"
            class="w-full justify-center! text-red-400! text-xs!"
            @click="handleLogout"
          />
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="lg:ml-64 min-h-screen flex flex-col">
      <header
        class="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 sm:px-6 py-4"
      >
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-3 min-w-0">
            <button
              class="lg:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-50 rounded-lg shrink-0"
              @click="sidebarOpen = true"
            >
              <i class="pi pi-bars"></i>
            </button>
            <div class="min-w-0">
              <h1 class="text-lg sm:text-xl font-bold text-gray-900 truncate">
                {{ pageTitle }}
              </h1>
              <p class="text-xs text-gray-400 mt-0.5 truncate">{{ pageSubtitle }}</p>
            </div>
          </div>
          <Tag value="Ambassadeur" severity="warning" icon="pi pi-star" class="shrink-0" />
        </div>
      </header>

      <main class="flex-1 p-4 sm:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const authStore = useAuthStore();

const sidebarOpen = ref(false);

const nav = [
  {
    name: "Programme de parrainage",
    href: "/referrals",
    icon: "pi-users",
  },
];

const pageMeta: Record<string, { title: string; subtitle: string }> = {
  "/dashboard/parrainage": {
    title: "Programme de parrainage",
    subtitle: "Votre lien, vos filleuls, vos gains",
  },
};

const pageTitle = computed(() => pageMeta[route.path]?.title || "Ambassadeur");
const pageSubtitle = computed(() => pageMeta[route.path]?.subtitle || "");
const userInitial = computed(() =>
  (authStore.userName || "A").charAt(0).toUpperCase(),
);

const handleLogout = async () => {
  authStore.logout();
  await navigateTo("/");
};
</script>