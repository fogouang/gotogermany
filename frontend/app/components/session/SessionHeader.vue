<template>
  <header class="bg-white border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">

      <!-- Gauche : quitter + module info -->
      <div class="flex items-center gap-3">
        <button
          class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-500"
          @click="$emit('exit')"
        >
          <i class="pi pi-times text-sm"></i>
        </button>
        <div class="hidden sm:block">
          <p class="text-sm font-semibold text-gray-900 leading-tight">
            {{ examName }}
          </p>
          <p class="text-xs text-gray-500 leading-tight">
            {{ moduleName }} — {{ teilLabel }}
          </p>
        </div>
      </div>

      <!-- Centre : progression teile -->
      <div class="flex items-center gap-1">
        <div
          v-for="(teil, i) in teile"
          :key="i"
          :class="[
            'h-2 rounded-full transition-all',
            i < currentTeilIndex
              ? 'bg-teal-600'
              : i === currentTeilIndex
                ? 'bg-teal-400'
                : 'bg-gray-200',
            teile.length <= 5 ? 'w-8' : 'w-4',
          ]"
        />
      </div>

      <!-- Droite : timer -->
      <div
        :class="[
          'flex items-center gap-2 px-3 py-1.5 rounded-lg font-mono text-sm font-bold transition-colors',
          timeRemaining < 120
            ? 'bg-red-100 text-red-700 animate-pulse'
            : timeRemaining < 300
              ? 'bg-amber-100 text-amber-700'
              : 'bg-gray-100 text-gray-800',
        ]"
      >
        <i class="pi pi-clock text-xs"></i>
        <span>{{ formattedTime }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
defineEmits<{ exit: [] }>()

const props = defineProps<{
  examName: string
  moduleName: string
  currentTeilIndex: number
  teile: any[]
  timeRemaining: number
}>()

const teilLabel = computed(() => {
  const n = props.currentTeilIndex + 1
  const total = props.teile.length
  return `Teil ${n} / ${total}`
})

const formattedTime = computed(() => {
  const m = Math.floor(props.timeRemaining / 60)
  const s = props.timeRemaining % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})
</script>