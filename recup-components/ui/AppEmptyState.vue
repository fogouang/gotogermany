<script setup lang="ts">
withDefaults(
  defineProps<{
    message: string;
    title?: string;
    icon?: string;
    /** "dashed" : bordure pointillée (liste vide), "plain" : carte simple */
    variant?: "dashed" | "plain";
    /** Version compacte pour une petite zone (carte, onglet) */
    compact?: boolean;
  }>(),
  {
    icon: "pi pi-inbox",
    variant: "dashed",
    compact: false,
  },
);
</script>

<template>
  <div
    class="flex flex-col items-center gap-3 rounded-card bg-card text-center"
    :class="[
      variant === 'dashed' ? 'border border-dashed border-line' : 'border border-line shadow-soft',
      compact ? 'px-4 py-8' : 'px-6 py-12 sm:py-16',
    ]"
  >
    <span
      class="flex items-center justify-center rounded-leaf bg-primary-50 text-primary-700"
      :class="compact ? 'size-10' : 'size-12'"
    >
      <i :class="[icon, compact ? 'text-base' : 'text-xl']" />
    </span>

    <div class="max-w-sm space-y-1">
      <p v-if="title" class="font-heading font-semibold text-ink">{{ title }}</p>
      <p class="text-sm text-muted">{{ message }}</p>
    </div>

    <div v-if="$slots.default" class="mt-2 flex flex-wrap justify-center gap-2">
      <slot />
    </div>
  </div>
</template>