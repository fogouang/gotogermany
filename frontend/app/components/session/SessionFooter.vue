<template>
  <footer class="bg-white border-t border-gray-200 sticky bottom-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-4">

      <!-- Précédent -->
      <Button
        :label="isFirstTeil ? '' : 'Teil précédent'"
        :icon="isFirstTeil ? '' : 'pi pi-arrow-left'"
        :disabled="isFirstTeil"
        outlined
        @click="$emit('prev')"
      />

      <!-- Indicateur central -->
      <div class="text-center">
        <p class="text-xs text-gray-500">
          {{ answeredInTeil }} / {{ totalInTeil }} réponses
        </p>
        <ProgressBar
          :value="teilProgress"
          :showValue="false"
          class="w-32 h-1 mt-1"
        />
      </div>

      <!-- Suivant / Soumettre -->
      <div>
        <Button
          v-if="!isLastTeil"
          label="Teil suivant"
          icon="pi pi-arrow-right"
          iconPos="right"
          @click="$emit('next')"
        />
        <Button
          v-else
          label="Terminer l'examen"
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