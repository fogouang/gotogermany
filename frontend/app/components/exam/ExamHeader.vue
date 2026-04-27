<template>
  <header class="bg-white shadow-md sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo et nom de l'examen -->
        <div class="flex items-center gap-3">
          <i class="pi pi-flag text-2xl text-indigo-600"></i>
          <div>
            <h1 class="text-lg font-bold text-gray-900">DeutschTest</h1>
            <p class="text-xs text-gray-500">{{ currentModule }}</p>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="hidden md:flex items-center gap-3 flex-1 max-w-md mx-8">
          <span class="text-sm text-gray-600">{{ Math.round(progress) }}%</span>
          <ProgressBar 
            :value="progress" 
            :showValue="false"
            class="flex-1"
          />
        </div>

        <!-- Timer -->
        <div class="flex items-center gap-4">
          <div 
            class="flex items-center gap-2 px-4 py-2 rounded-lg"
            :class="timeRemaining < 300 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'"
          >
            <i class="pi pi-clock text-lg"></i>
            <span class="font-mono font-bold text-lg">
              {{ formatTime(timeRemaining) }}
            </span>
          </div>

          <!-- Menu options -->
          <Button
            icon="pi pi-ellipsis-v"
            text
            @click="toggleMenu"
          />
        </div>
      </div>
    </div>

    <!-- Warning dialog si temps presque écoulé -->
    <Dialog 
      v-model:visible="showTimeWarning" 
      header="Temps presque écoulé!" 
      :modal="true"
      :closable="false"
    >
      <p class="text-gray-700">
        Il vous reste moins de 5 minutes pour terminer cette section.
      </p>
      <template #footer>
        <Button label="Continuer" @click="showTimeWarning = false" />
      </template>
    </Dialog>
  </header>
</template>

<script setup lang="ts">
const props = defineProps<{
  timeRemaining: number
  currentModule?: string
  progress: number
}>()

const showTimeWarning = ref(false)
const hasShownWarning = ref(false)

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const toggleMenu = () => {
  // Menu options (pause, quitter, etc.)
}

// Watcher pour afficher warning à 5min
watch(() => props.timeRemaining, (newTime) => {
  if (newTime <= 300 && !hasShownWarning.value) {
    showTimeWarning.value = true
    hasShownWarning.value = true
  }
})
</script>