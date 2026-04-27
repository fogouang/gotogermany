<template>
  <div class="space-y-6">

    <!-- Stats rapides -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-users text-teal-600"></i>
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">{{ usersStore.users.length || '—' }}</p>
            <p class="text-xs text-gray-500">Utilisateurs</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-list text-blue-600"></i>
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">—</p>
            <p class="text-xs text-gray-500">Sessions</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-building text-purple-600"></i>
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">{{ partnersStore.partners.length || '—' }}</p>
            <p class="text-xs text-gray-500">Partenaires</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
            <i class="pi pi-tag text-amber-600"></i>
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">{{ promoCodesStore.codes.length || '—' }}</p>
            <p class="text-xs text-gray-500">Codes promo</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bienvenue -->
    <div class="bg-linear-to-br from-teal-600 to-teal-800 rounded-xl p-6 text-white">
      <h2 class="text-lg font-semibold mb-1">
        Bienvenue, {{ authStore.userName }} 👋
      </h2>
      <p class="text-sm text-teal-100">
        Panel d'administration DeutschTest
      </p>
    </div>

    <!-- Raccourcis -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <NuxtLink
        to="/admin/users"
        class="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md hover:border-teal-200 transition-all flex items-center gap-4"
      >
        <div class="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
          <i class="pi pi-users text-teal-600"></i>
        </div>
        <div>
          <p class="font-semibold text-gray-900">Utilisateurs</p>
          <p class="text-xs text-gray-400">Gérer les comptes</p>
        </div>
        <i class="pi pi-arrow-right text-gray-300 ml-auto"></i>
      </NuxtLink>

      <NuxtLink
        to="/admin/partners"
        class="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md hover:border-teal-200 transition-all flex items-center gap-4"
      >
        <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
          <i class="pi pi-building text-purple-600"></i>
        </div>
        <div>
          <p class="font-semibold text-gray-900">Partenaires</p>
          <p class="text-xs text-gray-400">Centres affiliés</p>
        </div>
        <i class="pi pi-arrow-right text-gray-300 ml-auto"></i>
      </NuxtLink>

      <NuxtLink
        to="/admin/promo-codes"
        class="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md hover:border-teal-200 transition-all flex items-center gap-4"
      >
        <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
          <i class="pi pi-tag text-amber-600"></i>
        </div>
        <div>
          <p class="font-semibold text-gray-900">Codes Promo</p>
          <p class="text-xs text-gray-400">Réductions & commissions</p>
        </div>
        <i class="pi pi-arrow-right text-gray-300 ml-auto"></i>
      </NuxtLink>
    </div>

    <!-- Utilisateurs récents -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-semibold text-gray-900">Utilisateurs récents</h3>
        <NuxtLink to="/admin/users" class="text-xs text-teal-600 hover:underline">
          Voir tout →
        </NuxtLink>
      </div>
      <div v-if="usersStore.loading" class="flex justify-center py-8">
        <ProgressSpinner style="width: 40px; height: 40px" />
      </div>
      <table v-else class="w-full text-sm">
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="user in recentUsers"
            :key="user.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <td class="px-5 py-3">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-xs shrink-0">
                  {{ user.full_name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-gray-900 text-sm">{{ user.full_name }}</p>
                  <p class="text-xs text-gray-400">{{ user.email }}</p>
                </div>
              </div>
            </td>
            <td class="px-5 py-3 text-xs text-gray-400 hidden sm:table-cell">
              {{ formatDate(user.created_at) }}
            </td>
            <td class="px-5 py-3">
              <Tag
                :value="user.is_active ? 'Actif' : 'Inactif'"
                :severity="user.is_active ? 'success' : 'danger'"
              />
            </td>
          </tr>
          <tr v-if="recentUsers.length === 0">
            <td colspan="3" class="px-5 py-8 text-center text-gray-400 text-sm">
              Aucun utilisateur
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'admin',
})

const authStore = useAuthStore()
const usersStore = useAdminUsersStore()
const partnersStore = useAdminPartnersStore()
const promoCodesStore = useAdminPromoCodesStore()

const recentUsers = computed(() =>
  [...usersStore.users]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
)

const formatDate = (d: string) =>
  new Date(d).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })

onMounted(async () => {
  await Promise.all([
    usersStore.users.length === 0 ? usersStore.fetchUsers() : Promise.resolve(),
    partnersStore.partners.length === 0 ? partnersStore.fetchPartners() : Promise.resolve(),
    promoCodesStore.codes.length === 0 ? promoCodesStore.fetchCodes() : Promise.resolve(),
  ])
})
</script>