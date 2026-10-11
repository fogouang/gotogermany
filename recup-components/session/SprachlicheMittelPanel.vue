<template>
  <div v-if="bank" class="border border-primary-100 rounded-xl overflow-hidden">
    <button
      class="w-full flex items-center justify-between px-4 py-3 bg-primary-50 hover:bg-primary-100 transition-colors"
      @click="expanded = !expanded"
    >
      <span class="flex items-center gap-2 text-sm font-semibold text-primary-800">
        <i class="pi pi-book"></i>
        Sprachliche Mittel-{{ bank.title }}
      </span>
      <i
        :class="['pi text-primary-600 text-xs', expanded ? 'pi-chevron-up' : 'pi-chevron-down']"
      ></i>
    </button>

    <div v-if="expanded" class="px-4 py-3 bg-white space-y-3">
      <div v-for="cat in bank.categories" :key="cat.label">
        <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
          {{ cat.label }}
        </p>
        <ul class="space-y-0.5">
          <li
            v-for="(phrase, i) in cat.phrases"
            :key="i"
            class="text-sm text-gray-700 leading-relaxed"
          >
            · {{ phrase }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SPRACHLICHE_MITTEL } from "#shared/sprachlicheMittel";

const props = defineProps<{
  mittelKey: string | null;
  defaultExpanded?: boolean;
}>();

const expanded = ref(props.defaultExpanded ?? false);

const bank = computed(() =>
  props.mittelKey ? SPRACHLICHE_MITTEL[props.mittelKey] || null : null,
);
</script>