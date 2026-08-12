<!-- components/admin/ImportLogPanel.vue -->
<template>
  <div v-if="error" class="rounded-lg bg-danger-50 border border-danger-100 px-3 py-2 text-sm text-danger-700">
    <i class="pi pi-times-circle mr-1.5" />{{ error }}
  </div>

  <div v-else-if="summary || log?.length" class="rounded-lg bg-hover border border-line px-3 py-2 space-y-1">
    <p v-if="summary" class="text-sm font-semibold text-ink flex items-center gap-1.5">
      <i class="pi pi-check-circle text-success-600" />{{ summary }}
    </p>
    <ul v-if="log?.length" class="text-xs text-ink-secondary font-mono space-y-0.5 max-h-48 overflow-y-auto">
      <li v-for="(line, i) in log" :key="i">{{ line }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  log?: string[];
  summary?: string | null;
  error?: string | null;
}>();
</script>