<template>
  <footer class="bg-white border-t border-gray-200 sticky bottom-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-2">

      <!-- Précédent -->
      <div class="flex justify-start shrink-0">
        <Button
          v-if="!isFirstTeil"
          label="Précédent"
          icon="pi pi-arrow-left"
          outlined
          @click="$emit('prev')"
        />
        <div v-else class="w-10" />
      </div>

      <!-- Indicateur central -->
      <div class="text-center flex-1">
        <p class="text-xs text-gray-500">
          {{ answeredInTeil }} / {{ totalInTeil }} réponses
        </p>
        <ProgressBar
          :value="teilProgress"
          :showValue="false"
          class="w-24 h-1 mt-1 mx-auto"
        />
      </div>

      <!-- Suivant / Soumettre -->
      <div class="flex justify-end shrink-0">
        <Button
          v-if="!isLastTeil"
          label="Suivant"
          icon="pi pi-arrow-right"
          iconPos="right"
          @click="$emit('next')"
        />
        <Button
          v-else
          label="Terminer"
          icon="pi pi-check"
          severity="success"
          @click="$emit('submit')"
        />
      </div>

    </div>
  </footer>
</template>

<script setup lang="ts">
defineEmits<{ prev: []; next: []; submit: [] }>()

const props = defineProps<{
  isFirstTeil: boolean
  isLastTeil: boolean
  answeredInTeil: number
  totalInTeil: number
}>()

const teilProgress = computed(() =>
  props.totalInTeil > 0
    ? Math.round((props.answeredInTeil / props.totalInTeil) * 100)
    : 0
)
</script>