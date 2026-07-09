<!-- components/centre/ModuleBarChart.vue -->
<template>
  <div class="space-y-3">
    <div v-for="mod in modules" :key="mod.module_name" class="flex items-center gap-3">
      <span class="text-sm text-gray-600 w-28 shrink-0">{{ mod.module_name }}</span>
      <div class="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
        <div
          class="h-3 rounded-full transition-all duration-500"
          :class="barColor(mod.average_score)"
          :style="{ width: `${mod.average_score ?? 0}%` }"
        ></div>
      </div>
      <span class="text-sm font-semibold w-16 text-right shrink-0" :class="textColor(mod.average_score)">
        {{ mod.average_score !== null ? mod.average_score.toFixed(0) + '%' : '—' }}
      </span>
    </div>

    <div v-if="modules.length === 0" class="text-center text-sm text-gray-400 py-4">
      Aucune donnée par module pour l'instant.
    </div>
  </div>
</template>

<script setup lang="ts">
interface ModuleScore {
  module_name: string;
  average_score: number | null;
}

defineProps<{ modules: ModuleScore[] }>();

function barColor(score: number | null) {
  if (score === null) return "bg-gray-300";
  if (score >= 60) return "bg-emerald-500";
  return "bg-amber-500";
}

function textColor(score: number | null) {
  if (score === null) return "text-gray-400";
  if (score >= 60) return "text-emerald-600";
  return "text-amber-600";
}
</script>