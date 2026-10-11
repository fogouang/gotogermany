<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    eyebrow?: string;
    icon?: string;
    watermark?: string;
    center?: boolean;
  }>(),
  { center: false },
);
</script>

<template>
  <section class="bg-hero relative overflow-hidden">
    <span
      v-if="watermark"
      aria-hidden="true"
      class="pointer-events-none absolute top-1/2 -translate-y-1/2 select-none whitespace-nowrap font-heading text-[5rem] font-extrabold leading-none tracking-tighter text-transparent opacity-15 [-webkit-text-stroke:1.5px_var(--color-ink)] sm:text-[9rem] lg:text-[11rem] dark:opacity-20"
      :class="center ? 'left-1/2 -translate-x-1/2' : '-right-2'"
    >
      {{ watermark }}
    </span>

    <div
      class="relative mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:py-20"
      :class="center && 'text-center'"
    >
      <span
        v-if="eyebrow"
        class="inline-flex items-center gap-2 rounded-full border border-accent-500/30 bg-accent-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-accent-700 dark:text-accent-400"
      >
        <i v-if="icon" :class="[icon, 'text-xs']" />
        {{ eyebrow }}
      </span>

      <h1
        class="mt-4 font-heading text-3xl font-extrabold text-ink sm:text-5xl"
      >
        {{ title }}
      </h1>

      <p
        v-if="subtitle"
        class="mt-4 max-w-2xl text-base text-muted sm:text-lg"
        :class="center && 'mx-auto'"
      >
        {{ subtitle }}
      </p>

      <slot />
    </div>

    <div
      class="flag-stripe absolute inset-x-0 bottom-0 h-1"
      aria-hidden="true"
    />
  </section>
</template>
