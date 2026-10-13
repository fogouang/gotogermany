<!-- components/admin/ImportLogPanel.vue -->
<template>
  <div
    v-if="error"
    class="rounded-leaf border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-600"
  >
    <i class="pi pi-times-circle mr-1.5" />{{ error }}
  </div>

  <div v-else-if="summary || log?.length" class="space-y-1 rounded-leaf border border-line bg-card-2 px-3 py-2">
    <p v-if="summary" class="flex items-center gap-1.5 text-sm font-semibold text-ink">
      <i class="pi pi-check-circle text-emerald-600" />{{ summary }}
    </p>
    <ul v-if="log?.length" class="max-h-48 space-y-0.5 overflow-y-auto font-mono text-xs text-muted">
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