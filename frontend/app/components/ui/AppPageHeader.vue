<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    /** Petit titre doré au-dessus, ex. "Finances" */
    eyebrow?: string;
    subtitle?: string;
    /** Lien de retour (affiche une flèche à gauche du titre) */
    backTo?: string;
    backLabel?: string;
  }>(),
  {
    backLabel: "Retour",
  },
);
</script>

<template>
  <header
    class="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between"
  >
    <div class="flex min-w-0 items-start gap-3">
      <NuxtLink
        v-if="backTo"
        :to="backTo"
        :aria-label="backLabel"
        class="mt-1 flex size-10 shrink-0 items-center justify-center rounded-leaf border border-line bg-card text-muted shadow-soft transition-colors hover:border-primary/30 hover:text-primary"
      >
        <i class="pi pi-arrow-left text-sm" />
      </NuxtLink>

      <div class="min-w-0 space-y-1">
        <p
          v-if="eyebrow"
          class="inline-flex items-center gap-2 font-heading text-xs font-semibold uppercase tracking-[0.18em] text-primary"
        >
          <span class="h-px w-6 bg-accent-500" />
          {{ eyebrow }}
        </p>
        <h1 class="truncate font-heading text-2xl font-bold text-ink sm:text-3xl">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="text-sm text-muted">{{ subtitle }}</p>
        <slot name="meta" />
      </div>
    </div>

    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2 sm:shrink-0">
      <slot name="actions" />
    </div>
  </header>
</template>