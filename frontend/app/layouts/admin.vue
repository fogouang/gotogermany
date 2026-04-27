<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar Admin -->
    <aside class="fixed top-0 left-0 z-40 w-64 h-screen bg-gray-900 text-white">
      <div class="h-full px-4 py-6 overflow-y-auto pb-32">
        <!-- Logo -->
        <div class="flex items-center gap-3 mb-8">
          <div class="w-10 h-10 bg-linear-to-br from-teal-600 to-teal-800 rounded-xl flex items-center justify-center">
            <i class="pi pi-shield text-white text-xl"></i>
          </div>
          <div>
            <span class="text-lg font-bold">DeutschTest</span>
            <p class="text-xs text-gray-400 leading-none">Admin Panel</p>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="space-y-1">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mb-2">
            Général
          </p>
          <NuxtLink
            v-for="item in mainNav"
            :key="item.name"
            :to="item.href"
            class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            active-class="!bg-teal-600 !text-white"
          >
            <i :class="['pi text-sm', item.icon]"></i>
            <span class="text-sm font-medium">{{ item.name }}</span>
          </NuxtLink>

          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mt-5 mb-2">
            Partenariat
          </p>
          <NuxtLink
            v-for="item in partnerNav"
            :key="item.name"
            :to="item.href"
            class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            active-class="!bg-teal-600 !text-white"
          >
            <i :class="['pi text-sm', item.icon]"></i>
            <span class="text-sm font-medium">{{ item.name }}</span>
          </NuxtLink>

          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mt-5 mb-2">
            Configuration
          </p>
          <NuxtLink
            v-for="item in configNav"
            :key="item.name"
            :to="item.href"
            class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
            active-class="!bg-teal-600 !text-white"
          >
            <i :class="['pi text-sm', item.icon]"></i>
            <span class="text-sm font-medium">{{ item.name }}</span>
          </NuxtLink>
        </nav>
      </div>

      <!-- Admin info -->
      <div class="absolute bottom-0 left-0 right-0 p-4 bg-gray-900 border-t border-gray-800">
        <div class="p-3 bg-gray-800 rounded-lg">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-9 h-9 bg-teal-600 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0">
              {{ adminInitial }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold truncate">{{ authStore.userName || 'Admin' }}</p>
              <p class="text-xs text-gray-400 truncate">{{ authStore.userEmail }}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <Button
              label="Site"
              icon="pi pi-external-link"
              text
              size="small"
              class="flex-1 justify-center! text-gray-300! text-xs!"
              @click="navigateTo('/dashboard')"
            />
            <Button
              label="Déconnexion"
              icon="pi pi-sign-out"
              text
              size="small"
              class="flex-1 justify-center! text-red-400! text-xs!"
              @click="authStore.logout()"
            />
          </div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="ml-64 min-h-screen flex flex-col">
      <!-- Top bar -->
      <header class="sticky top-0 z-30 bg-white border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-gray-900">{{ pageTitle }}</h1>
            <p class="text-xs text-gray-400 mt-0.5">{{ pageSubtitle }}</p>
          </div>
          <Tag value="Admin" severity="success" icon="pi pi-shield" />
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const authStore = useAuthStore()

const mainNav = [
  { name: 'Dashboard', href: '/admin', icon: 'pi-chart-bar' },
  { name: 'Utilisateurs', href: '/admin/users', icon: 'pi-users' },
  { name: 'Examens', href: '/admin/exams', icon: 'pi-book' },
  { name: 'Sessions', href: '/admin/sessions', icon: 'pi-list' },
  { name: 'Plans', href: '/admin/plans', icon: 'pi-tag' },
  { name: 'Paiements', href: '/admin/paiements', icon: 'pi-credit-card' }
]

const partnerNav = [
  { name: 'Partenaires', href: '/admin/partners', icon: 'pi-building' },
  { name: 'Codes Promo', href: '/admin/promo-code', icon: 'pi-tag' },
]

const configNav = [
  { name: 'Paramètres', href: '/admin/settings', icon: 'pi-cog' },
]

const pageMeta: Record<string, { title: string; subtitle: string }> = {
  '/admin': { title: 'Dashboard', subtitle: "Vue d'ensemble de la plateforme" },
  '/admin/users': { title: 'Utilisateurs', subtitle: 'Gestion des comptes et accès' },
  '/admin/exams': { title: 'Examens', subtitle: 'Gestion du contenu' },
  '/admin/sessions': { title: 'Sessions', subtitle: 'Historique des examens passés' },
  '/admin/partners': { title: 'Partenaires', subtitle: 'Centres et affiliés' },
  '/admin/promo-code': { title: 'Codes Promo', subtitle: 'Gestion des réductions et commissions' },
  '/admin/settings': { title: 'Paramètres', subtitle: 'Configuration de la plateforme' },
  '/admin/plans': { title: 'Plans', subtitle: 'Configuration des prix' },
  '/admin/paiements': { title: 'Factures', subtitle: 'Gestion des factures' },
}

const pageTitle = computed(() => pageMeta[route.path]?.title || 'Admin')
const pageSubtitle = computed(() => pageMeta[route.path]?.subtitle || '')
const adminInitial = computed(() => (authStore.userName || 'A').charAt(0).toUpperCase())
</script>