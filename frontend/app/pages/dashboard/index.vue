<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">
        Bonjour, {{ authStore.userName }} 👋
      </h1>
      <p class="text-gray-600 mt-2">
        Bienvenue sur votre tableau de bord
      </p>
    </div>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <Card v-for="stat in stats" :key="stat.label">
        <template #content>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">{{ stat.label }}</p>
              <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
              <p v-if="stat.change" class="text-xs mt-1" :class="stat.changeColor">
                <i :class="['pi', stat.changeIcon, 'text-xs']"></i>
                {{ stat.change }}
              </p>
            </div>
            <div :class="['w-14 h-14 rounded-xl flex items-center justify-center', stat.bgColor]">
              <i :class="['pi', stat.icon, 'text-2xl', stat.iconColor]"></i>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Quick Start -->
      <Card class="lg:col-span-2">
        <template #title>
          <div class="flex items-center justify-between">
            <span>Commencer un examen</span>
            <Button 
              label="Voir tout"
              text
              size="small"
              @click="navigateTo('/dashboard/examens')"
            />
          </div>
        </template>
        <template #content>
          <div v-if="examsStore.loading" class="text-center py-8">
            <ProgressSpinner style="width: 50px; height: 50px" />
          </div>
          
          <div v-else-if="examsStore.catalog.length === 0" class="text-center py-8 text-gray-500">
            <i class="pi pi-inbox text-4xl mb-4"></i>
            <p>Aucun examen disponible</p>
          </div>
          
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card 
              v-for="exam in examsStore.catalog.slice(0, 4)" 
              :key="exam.id"
              class="hover:shadow-md transition-shadow cursor-pointer"
              @click="navigateTo(`/dashboard/examens/${exam.slug}`)"
            >
              <template #content>
                <div class="flex items-start justify-between mb-3">
                  <div>
                    <h3 class="font-semibold text-gray-900">{{ exam.name }}</h3>
                    <p class="text-xs text-gray-500 mt-1">{{ exam.provider }}</p>
                  </div>
                  <Tag :value="exam.levels?.length + ' niveaux'" severity="info" />
                </div>
                <p class="text-sm text-gray-600 line-clamp-2">
                  {{ exam.description || 'Préparez-vous efficacement pour cet examen' }}
                </p>
              </template>
            </Card>
          </div>
        </template>
      </Card>
      
      <!-- Progress / Activity -->
      <Card>
        <template #title>Progression</template>
        <template #content>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm mb-2">
                <span class="text-gray-600">Niveau B1</span>
                <span class="font-semibold">75%</span>
              </div>
              <ProgressBar :value="75" :showValue="false" />
            </div>
            
            <div>
              <div class="flex justify-between text-sm mb-2">
                <span class="text-gray-600">Niveau B2</span>
                <span class="font-semibold">40%</span>
              </div>
              <ProgressBar :value="40" :showValue="false" />
            </div>
            
            <div>
              <div class="flex justify-between text-sm mb-2">
                <span class="text-gray-600">Niveau C1</span>
                <span class="font-semibold">10%</span>
              </div>
              <ProgressBar :value="10" :showValue="false" />
            </div>
          </div>
          
          <Divider />
          
          <div class="space-y-3">
            <h4 class="font-semibold text-sm text-gray-900">Activité récente</h4>
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <i class="pi pi-check text-green-600"></i>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium">Goethe B1 - Hören</p>
                <p class="text-xs text-gray-500">Il y a 2 heures</p>
              </div>
              <span class="text-sm font-semibold text-green-600">87%</span>
            </div>
            
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <i class="pi pi-check text-blue-600"></i>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium">TestDaF - Lesen</p>
                <p class="text-xs text-gray-500">Hier</p>
              </div>
              <span class="text-sm font-semibold text-blue-600">92%</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useExamsStore } from '~/stores/exams';

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
});

const authStore = useAuthStore();
const examsStore = useExamsStore();

const stats = ref([
  { 
    label: 'Examens complétés', 
    value: '12', 
    icon: 'pi-check-circle', 
    bgColor: 'bg-green-100', 
    iconColor: 'text-green-600',
    change: '+2 ce mois',
    changeColor: 'text-green-600',
    changeIcon: 'pi-arrow-up'
  },
  { 
    label: 'Score moyen', 
    value: '85%', 
    icon: 'pi-chart-line', 
    bgColor: 'bg-blue-100', 
    iconColor: 'text-blue-600',
    change: '+5% vs mois dernier',
    changeColor: 'text-blue-600',
    changeIcon: 'pi-arrow-up'
  },
  { 
    label: 'Temps total', 
    value: '24h', 
    icon: 'pi-clock', 
    bgColor: 'bg-purple-100', 
    iconColor: 'text-purple-600',
    change: '8h ce mois',
    changeColor: 'text-gray-600',
    changeIcon: 'pi-minus'
  },
  { 
    label: 'Niveau actuel', 
    value: 'B2', 
    icon: 'pi-star', 
    bgColor: 'bg-yellow-100', 
    iconColor: 'text-yellow-600'
  },
]);

// Charger les examens au montage
onMounted(async () => {
  await examsStore.fetchCatalog();
});
</script>