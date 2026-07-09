<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/40 z-30 md:hidden"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      class="fixed top-0 left-0 z-40 w-64 h-screen bg-slate-900 text-white transition-transform duration-200"
      :class="
        sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      "
    >
      <div class="h-full px-4 py-6 overflow-y-auto pb-32">
        <!-- Logo -->
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 bg-linear-to-br from-emerald-600 to-emerald-800 rounded-xl flex items-center justify-center shrink-0"
            >
              <i class="pi pi-building text-white text-xl"></i>
            </div>
            <div class="min-w-0">
              <span class="text-lg font-bold block truncate">GoToGermany</span>
              <p class="text-xs text-gray-400 leading-none truncate">
                Espace Centre
              </p>
            </div>
          </div>
          <button
            class="md:hidden text-gray-400 hover:text-white p-1"
            @click="sidebarOpen = false"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="space-y-1">
          <p
            class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mb-2"
          >
            Général
          </p>
          <NuxtLink
            v-for="item in navItems"
            :key="item.name"
            :to="item.href"
            class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-300 hover:bg-slate-800 hover:text-white transition-colors"
            active-class="!bg-emerald-600 !text-white"
            @click="sidebarOpen = false"
          >
            <i :class="['pi text-sm shrink-0', item.icon]"></i>
            <span class="text-sm font-medium truncate">{{ item.name }}</span>
          </NuxtLink>
        </nav>
      </div>

      <!-- Infos utilisateur -->
      <div
        class="absolute bottom-0 left-0 right-0 p-4 bg-slate-900 border-t border-slate-800"
      >
        <div class="p-3 bg-slate-800 rounded-lg">
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 bg-emerald-600 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
            >
              {{ userInitial }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold truncate">
                {{ authStore.userName || "Utilisateur" }}
              </p>
              <p class="text-xs text-gray-400 truncate">{{ roleLabel }}</p>
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
    <div class="md:ml-64 min-h-screen flex flex-col">
      <header
        class="sticky top-0 z-20 bg-white border-b border-gray-200 px-4 md:px-6 py-4"
      >
        <div class="flex items-center gap-3">
          <button
            class="md:hidden text-gray-500 hover:text-gray-900 shrink-0"
            @click="sidebarOpen = true"
          >
            <i class="pi pi-bars text-lg"></i>
          </button>
          <div class="flex-1 min-w-0">
            <h1 class="text-lg md:text-xl font-bold text-gray-900 truncate">
              {{ pageTitle }}
            </h1>
            <p class="text-xs text-gray-400 mt-0.5 truncate hidden sm:block">
              {{ pageSubtitle }}
            </p>
          </div>
          <Tag
            :value="roleLabel"
            severity="success"
            icon="pi pi-building"
            class="shrink-0 hidden sm:flex"
          />
        </div>
      </header>

      <main class="flex-1 p-4 md:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const authStore = useAuthStore();

const sidebarOpen = ref(false);

const directorNav = [
  { name: "Vue d'ensemble", href: "/centre/dashboard", icon: "pi-chart-bar" },
  { name: "Succursales", href: "/centre/succursales", icon: "pi-sitemap" },
  { name: "Secrétaires", href: "/centre/secretaires", icon: "pi-users" },
  { name: "Étudiants", href: "/centre/etudiants", icon: "pi-user" },
  { name: "Progression", href: "/centre/progression", icon: "pi-chart-line" },
  {
    name: "Historique crédits",
    href: "/centre/credits-historique",
    icon: "pi-history",
  },
  { name: "Ma licence", href: "/centre/licence", icon: "pi-verified" },
];

const secretaryNav = [
  { name: "Mes étudiants", href: "/centre/etudiants", icon: "pi-user" },
  {
    name: "Nouvel étudiant",
    href: "/centre/etudiants/nouveau",
    icon: "pi-user-plus",
  },
  { name: "Progression", href: "/centre/progression", icon: "pi-chart-line" },
  {
    name: "Historique crédits",
    href: "/centre/credits-historique",
    icon: "pi-history",
  },
];

const navItems = computed(() =>
  authStore.isDirector ? directorNav : secretaryNav,
);

const roleLabel = computed(() => {
  if (authStore.isDirector) return "Directeur de centre";
  if (authStore.isSecretary) return "Secrétaire";
  return "Centre";
});

const pageMeta: Record<string, { title: string; subtitle: string }> = {
  "/centre/dashboard": {
    title: "Vue d'ensemble",
    subtitle: "Quota et statut de votre licence",
  },
  "/centre/succursales": {
    title: "Succursales",
    subtitle: "Gestion de vos points de formation",
  },
  "/centre/secretaires": {
    title: "Secrétaires",
    subtitle: "Comptes de gestion par succursale",
  },
  "/centre/etudiants": {
    title: "Étudiants",
    subtitle: "Comptes étudiants inscrits",
  },
  "/centre/etudiants/nouveau": {
    title: "Nouvel étudiant",
    subtitle: "Créer un compte étudiant",
  },
  "/centre/progression": {
    title: "Progression",
    subtitle: "Scores et activité des étudiants",
  },
  "/centre/licence": {
    title: "Ma licence",
    subtitle: "Détails et attestation",
  },
  "/centre/credits-historique": {
    title: "Historique des crédits",
    subtitle: "Audit des ajustements de crédits IA",
  },
};

const pageTitle = computed(
  () => pageMeta[route.path]?.title || "Espace Centre",
);
const pageSubtitle = computed(() => pageMeta[route.path]?.subtitle || "");
const userInitial = computed(() =>
  (authStore.userName || "C").charAt(0).toUpperCase(),
);

watch(
  () => route.path,
  () => {
    sidebarOpen.value = false;
  },
);

const handleLogout = async () => {
  authStore.logout();
  await navigateTo("/");
};
</script>
