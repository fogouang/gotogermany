<template>
  <div class="bg-yellow-50 border border-yellow-200 rounded-xl overflow-hidden">
    <div class="px-4 py-2 border-b border-yellow-200 flex items-center gap-2">
      <i class="pi pi-pencil text-yellow-600 text-xs"></i>
      <span class="text-xs font-medium text-yellow-700">Mes notes (préparation)</span>
    </div>
    <Textarea
      :modelValue="answer?.text || ''"
      placeholder="Notez vos idées ici..."
      class="w-full border-0 bg-transparent resize-none p-4 text-sm focus:ring-0 focus:outline-none"
      :rows="6"
      @update:modelValue="(val) => $emit('answer', { text: val })"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{ question: any; answer: any }>()
defineEmits<{ answer: [value: any] }>()
</script>