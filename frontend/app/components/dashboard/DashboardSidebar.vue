<template>
  <aside class="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 lg:block">
    <div class="flex flex-col h-full">
      <!-- Logo -->
      <div class="flex items-center gap-3 px-6 py-4 border-b">
        <div class="w-10 h-10 bg-linear-to-br from-yellow-400 to-orange-400 rounded-xl flex items-center justify-center">
          <i class="pi pi-graduation-cap text-xl text-gray-900"></i>
        </div>
        <span class="text-xl font-bold text-gray-900">DeutschTest</span>
      </div>
      
      <!-- Navigation -->
      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <NuxtLink
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-teal-50 hover:text-teal-700 transition-colors font-medium"
          active-class="bg-teal-100 text-teal-700"
          @click="$emit('navigate')"
        >
          <i :class="['pi', item.icon, 'text-lg']"></i>
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>
      
      <!-- User Section -->
      <div class="border-t p-4">
        <div class="flex items-center gap-3 mb-3 px-2">
          <Avatar 
            :label="authStore.userName[0]?.toUpperCase()" 
            shape="circle"
            size="large"
            class="bg-teal-600 text-white"
          />
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-gray-900 truncate">
              {{ authStore.userName }}
            </p>
            <p class="text-xs text-gray-500 truncate">
              {{ authStore.userEmail }}
            </p>
          </div>
        </div>
        
        <Button 
          label="Déconnexion"
          icon="pi pi-sign-out"
          severity="secondary"
          outlined
          class="w-full"
          @click="handleLogout"
        />
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
const authStore = useAuthStore();

defineEmits(['navigate']);

const menuItems = ref([
  {
    label: 'Tableau de bord',
    icon: 'pi-th-large',
    to: '/dashboard',
  },
  {
    label: 'Examens',
    icon: 'pi-book',
    to: '/dashboard/examens',
  },
  {
    label: 'Mes résultats',
    icon: 'pi-chart-line',
    to: '/dashboard/resultats',
  },
  {
    label: 'Profil',
    icon: 'pi-user',
    to: '/dashboard/profil',
  },
   {
    label: 'Factures',
    icon: 'pi-credit-card',
    to: '/dashboard/factures',
  },
  {
    label: 'Paramètres',
    icon: 'pi-cog',
    to: '/dashboard/settings',
  },
]);

const handleLogout = () => {
  authStore.logout();
};
</script>