<template>
  <div v-if="bank" class="rounded-card border border-primary/20 overflow-hidden">
    <button
      type="button"
      class="w-full flex items-center justify-between gap-3 px-4 py-3 bg-primary/5 hover:bg-primary/10 transition-colors"
      :aria-expanded="expanded"
      :aria-controls="panelId"
      @click="expanded = !expanded"
    >
      <span class="flex items-center gap-2 text-sm font-semibold text-ink min-w-0">
        <i class="pi pi-book text-primary shrink-0"></i>
        <span class="truncate">
          Sprachliche Mittel
          <span v-if="bank.title" class="font-normal text-muted">· {{ bank.title }}</span>
        </span>
      </span>
      <i :class="['pi text-primary text-xs shrink-0', expanded ? 'pi-chevron-up' : 'pi-chevron-down']"></i>
    </button>

    <div
      v-if="expanded"
      :id="panelId"
      :class="[
        'px-4 py-4 bg-card border-t border-primary/10 grid gap-4',
        bank.categories.length > 1 ? 'lg:grid-cols-2' : '',
      ]"
    >
      <div v-for="cat in bank.categories" :key="cat.label">
        <p class="text-xs font-semibold uppercase tracking-wide text-muted mb-1.5">
          {{ cat.label }}
        </p>
        <ul class="space-y-1">
          <li
            v-for="(phrase, i) in cat.phrases"
            :key="i"
            class="flex gap-2 text-sm text-ink leading-relaxed"
          >
            <i class="pi pi-circle-fill text-[4px] text-primary mt-2.5 shrink-0"></i>
            <span>{{ phrase }}</span>
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
const panelId = useId();

const bank = computed(() =>
  props.mittelKey ? SPRACHLICHE_MITTEL[props.mittelKey] || null : null,
);
</script>